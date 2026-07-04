from backend.dashboard.history_service import get_dashboard_history
from backend.dashboard.asset_service import get_dashboard_assets
from backend.dashboard.finding_service import get_dashboard_findings
from backend.dashboard.summary_service import get_dashboard_summary

from backend.services.scan_service import ScanService
from backend.providers.factory import get_provider
from backend.config import settings

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from backend.database.session import get_db
from backend.database.models import Finding, ScanHistory, User, Setting, Account
from backend.models.schemas import (
    FindingSchema, ScanResult, SettingSchema, SettingCreate,
    AccountCreate, AccountSchema, TrustPolicyResponse,
    UserCreate, UserSchema, PasswordChange,
)
from backend.rules.engine import run_scan
from backend.api.auth import (
    hash_password, verify_password, create_access_token, get_current_user,
    validate_password_strength,
)
from backend.utils.aws import generate_external_id, assume_role, AssumeRoleError
from backend.utils.iam_policy_templates import (
    build_trust_policy, build_read_only_policy, build_onboarding_instructions,
)

# Ensure tables are created


router = APIRouter()

@router.post("/setup/admin", response_model=UserSchema)
def setup_admin(
    user_in: UserCreate,
    db: Session = Depends(get_db),
):
    """One-time bootstrap endpoint to create the first user. Intentionally unauthenticated -
    that's safe ONLY because it self-disables the moment any user exists in the database.
    This replaces a hardcoded seeded admin account with a setup step the operator controls."""
    existing_user_count = db.query(User).count()
    if existing_user_count > 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Setup has already been completed. Use POST /users (authenticated) to create additional users.",
        )

    validate_password_strength(user_in.password)
    user = User(username=user_in.username, hashed_password=hash_password(user_in.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/users", response_model=UserSchema)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Creates an additional user. Requires an existing authenticated user - this is
    intentionally simple (no role/permission tiers yet) since CloudSentinel currently
    treats all authenticated users as equally trusted operators."""
    existing = db.query(User).filter(User.username == user_in.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists.")

    validate_password_strength(user_in.password)
    user = User(username=user_in.username, hashed_password=hash_password(user_in.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/users/me/password")
def change_own_password(
    payload: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect.")

    validate_password_strength(payload.new_password)
    current_user.hashed_password = hash_password(payload.new_password)
    db.commit()
    return {"status": "Password updated"}

@router.get("/users/me", response_model=UserSchema)
def get_own_user(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password"
        )
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/accounts", response_model=AccountSchema)
def create_account(
    account_in: AccountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    account = Account(
        name=account_in.name,
        aws_account_id=account_in.aws_account_id,
        role_arn=account_in.role_arn,
        external_id=generate_external_id(),
        region=account_in.region or "us-east-1",
        status="PENDING",
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account

@router.get("/accounts", response_model=List[AccountSchema])
def list_accounts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Account).order_by(Account.created_at.desc()).all()

@router.get("/accounts/{account_id}/trust-policy", response_model=TrustPolicyResponse)
def get_trust_policy(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return TrustPolicyResponse(
        account_id=account.id,
        external_id=account.external_id,
        trust_policy=build_trust_policy(account.external_id),
        read_only_policy=build_read_only_policy(),
        instructions=build_onboarding_instructions(account.role_arn, account.external_id),
    )

@router.post("/accounts/{account_id}/verify")
def verify_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    try:
        assume_role(account.role_arn, account.external_id)
        account.status = "VERIFIED"
        account.last_error = None
        db.commit()
        return {"status": "VERIFIED"}
    except AssumeRoleError as e:
        account.status = "FAILED"
        account.last_error = str(e)
        db.commit()
        raise HTTPException(status_code=400, detail=f"Could not assume role: {e}")

@router.delete("/accounts/{account_id}")
def delete_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    db.delete(account)
    db.commit()
    return {"status": "deleted"}

@router.post("/scan", response_model=ScanResult)
def trigger_scan(
    account_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from backend.celery_worker import run_scan_task
    if account_id is not None:
        account = db.query(Account).filter(Account.id == account_id).first()
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        if account.status not in ("VERIFIED",):
            raise HTTPException(status_code=400, detail="Account is not verified. Call /accounts/{id}/verify first.")
    run_scan_task.delay(account_id)
    return ScanResult(status="Scan initiated in background (Celery task queued)", findings_count=0)

@router.get("/findings", response_model=List[FindingSchema])
def get_findings(
    status: str = "ACTIVE",
    account_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Finding).filter(Finding.status == status)
    if account_id is not None:
        query = query.filter(Finding.account_id == account_id)
    findings = query.order_by(Finding.timestamp.desc()).all()
    return findings

@router.get("/findings/{id}", response_model=FindingSchema)
def get_finding(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    finding = db.query(Finding).filter(Finding.id == id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    return finding

@router.post("/findings/{id}/enrich")
def enrich_finding_endpoint(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    finding = db.query(Finding).filter(Finding.id == id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
        
    from backend.integrations.ai_enrichment import enrich_finding
    enrichment = enrich_finding(finding.description, finding.title)
    if enrichment:
        return {"enrichment": enrichment}
    else:
        raise HTTPException(status_code=500, detail="Failed to enrich finding or API key missing")

@router.get("/summary")
def get_summary(
    account_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Finding).filter(Finding.status == "ACTIVE")
    if account_id is not None:
        query = query.filter(Finding.account_id == account_id)
    active_findings = query.all()
    summary = {
        "CRITICAL": 0,
        "HIGH": 0,
        "MEDIUM": 0,
        "LOW": 0
    }
    for f in active_findings:
        if f.severity in summary:
            summary[f.severity] += 1
    return summary

@router.get("/scan-history")
def get_scan_history(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    history = db.query(ScanHistory).order_by(ScanHistory.timestamp.desc()).limit(limit).all()
    return history

@router.get("/settings", response_model=List[SettingSchema])
def get_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    settings = db.query(Setting).all()
    result = []
    for s in settings:
        val = "********" if s.is_encrypted and s.value else s.value
        result.append(SettingSchema(key=s.key, value=val, is_encrypted=s.is_encrypted))
    return result

@router.post("/settings")
def update_setting(
    setting_in: SettingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from backend.utils.crypto import encrypt_value, SENSITIVE_SETTING_KEYS, EncryptionConfigError

    # Never trust the client's is_encrypted flag for known-sensitive keys -
    # force encryption server-side so a buggy/malicious request can't store
    # a secret in plaintext.
    should_encrypt = setting_in.is_encrypted or setting_in.key in SENSITIVE_SETTING_KEYS

    value_to_store = setting_in.value
    if should_encrypt and value_to_store is not None:
        try:
            value_to_store = encrypt_value(value_to_store)
        except EncryptionConfigError as e:
            raise HTTPException(status_code=500, detail=str(e))

    setting = db.query(Setting).filter(Setting.key == setting_in.key).first()
    if setting:
        setting.value = value_to_store
        setting.is_encrypted = should_encrypt
    else:
        setting = Setting(
            key=setting_in.key,
            value=value_to_store,
            is_encrypted=should_encrypt
        )
        db.add(setting)
    db.commit()
    return {"status": "Setting updated"}


@router.post("/scan/gcp")
def scan_gcp():

    service = ScanService()

    result = service.run_scan()

    return {
        "provider": result.provider,
        "assets": result.assets,
        "summary": result.summary,
        "findings": result.findings,
    }

@router.get("/dashboard/summary")
def dashboard_summary(
    db: Session = Depends(get_db),
):

    return get_dashboard_summary(db)

@router.get("/dashboard/findings")
def dashboard_findings(
    severity: str | None = None,
    service: str | None = None,
    limit: int = 25,
    offset: int = 0,
    db: Session = Depends(get_db),
):

    return get_dashboard_findings(
        db=db,
        severity=severity,
        service=service,
        limit=limit,
        offset=offset,
    )    

@router.get("/dashboard/assets")
def dashboard_assets(
    service: str | None = None,
    resource_type: str | None = None,
    limit: int = 25,
    offset: int = 0,
    db: Session = Depends(get_db),
):

    return get_dashboard_assets(
        db=db,
        service=service,
        resource_type=resource_type,
        limit=limit,
        offset=offset,
    )    

@router.get("/dashboard/history")
def dashboard_history(
    limit: int = 20,
    db: Session = Depends(get_db),
):
    return get_dashboard_history(
        db=db,
        limit=limit,
    )    