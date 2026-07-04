import logging
from sqlalchemy.orm import Session
from backend.database.models import Finding, ScanHistory, Account
from backend.database.session import SessionLocal
from datetime import datetime

from backend.collectors.iam_collector import collect_iam_users, collect_iam_credential_report
from backend.collectors.s3_collector import collect_s3_buckets
from backend.collectors.ec2_collector import collect_security_groups
from backend.collectors.cloudtrail_collector import collect_trails

from backend.normalizers.iam import normalize_iam_user, normalize_credential_report
from backend.normalizers.s3 import normalize_s3_bucket
from backend.normalizers.ec2 import normalize_security_group
from backend.normalizers.cloudtrail import normalize_cloudtrail

from backend.rules.iam_rules import evaluate_iam_user, evaluate_iam_credential
from backend.rules.s3_rules import evaluate_s3_bucket
from backend.rules.ec2_rules import evaluate_security_group
from backend.rules.cloudtrail_rules import evaluate_cloudtrail
from backend.rules.correlation import correlate_findings

from backend.integrations.slack import notify_slack
from backend.integrations.jira import create_jira_ticket
from backend.utils.aws import get_boto3_client_for_account, get_boto3_client, AssumeRoleError
from backend.exceptions import CollectorError
from backend.inventory.manager import sync_asset

logger = logging.getLogger("cloudsentinel.engine")


def run_scan(account_id: int = None):
    """Runs a scan for a single account (if account_id given) or, if account_id is
    None, falls back to the legacy single-account mode using env-based static
    credentials (useful for local dev without onboarding an Account row)."""
    db = SessionLocal()
    try:
        if account_id is not None:
            account = db.query(Account).filter(Account.id == account_id).first()
            if not account:
                logger.error(f"run_scan called with unknown account_id={account_id}")
                return
            _scan_account(db, account)
        else:
            _scan_legacy_env_account(db)
    finally:
        db.close()


def run_scan_all_accounts():
    """Loops every non-disabled account and scans it. Used by the scheduler."""
    db = SessionLocal()
    try:
        accounts = db.query(Account).filter(Account.status != "DISABLED").all()
        for account in accounts:
            _scan_account(db, account)
    finally:
        db.close()


def _scan_account(db: Session, account: Account):
    try:
        iam_client = get_boto3_client_for_account(account, "iam")
        s3_client = get_boto3_client_for_account(account, "s3")
        ec2_client = get_boto3_client_for_account(account, "ec2")
        cloudtrail_client = get_boto3_client_for_account(account, "cloudtrail")
    except AssumeRoleError as e:
        logger.error(f"Scan failed for account {account.id} ({account.name}): could not assume role: {e}")
        account.status = "FAILED"
        account.last_error = f"AssumeRole failed: {e}"
        account.last_scan_status = "FAILED"
        account.last_scan_at = datetime.utcnow()
        db.add(ScanHistory(
            account_id=account.id, findings_count=0, status="FAILED",
            error_message=str(e), timestamp=datetime.utcnow(),
        ))
        db.commit()
        return

    findings, collector_errors = _collect_and_evaluate(
    db=db,
    account_id=account.id,
    iam_client=iam_client,
    s3_client=s3_client,
    ec2_client=ec2_client,
    cloudtrail_client=cloudtrail_client,
)

    findings = correlate_findings(findings)
    save_findings(db, findings, account_id=account.id)

    account.status = "VERIFIED"
    account.last_error = "; ".join(collector_errors) if collector_errors else None
    account.last_scan_status = "PARTIAL" if collector_errors else "SUCCESS"
    account.last_scan_at = datetime.utcnow()
    db.add(ScanHistory(
        account_id=account.id, findings_count=len(findings), status="PARTIAL" if collector_errors else "SUCCESS",
        timestamp=datetime.utcnow(),
    ))
    db.commit()
    logger.info(f"Scan complete for account {account.id} ({account.name}): {len(findings)} findings")


def _scan_legacy_env_account(db: Session):
    """Single-account mode using whatever static credentials are in the environment.
    No Account row, no account_id on findings. Intended for local development only."""
    try:
        findings, collector_errors = _collect_and_evaluate(
    db=db,
    account_id=0,
    iam_client=get_boto3_client("iam"),
    s3_client=get_boto3_client("s3"),
    ec2_client=get_boto3_client("ec2"),
    cloudtrail_client=get_boto3_client("cloudtrail"),
)
        findings = correlate_findings(findings)
        save_findings(db, findings, account_id=None)
        db.add(ScanHistory(account_id=None, findings_count=len(findings), status="PARTIAL" if collector_errors else "SUCCESS", timestamp=datetime.utcnow()))
        db.commit()
    except Exception as e:
        logger.error(f"Legacy env-credential scan failed: {e}")
        db.add(ScanHistory(account_id=None, findings_count=0, status="FAILED", error_message=str(e), timestamp=datetime.utcnow()))
        db.commit()


def _collect_and_evaluate(
    db,
    account_id,
    iam_client,
    s3_client,
    ec2_client,
    cloudtrail_client,
):
    findings = []
    collector_errors = []

    active_resource_ids = set()

    try:
        users = collect_iam_users(iam_client)
        for user in users:
            active_resource_ids.add(user["UserId"])
            sync_asset(
    db=db,
    account_id=account_id,
    service="IAM",
    resource_type="User",
    resource_id=user["UserId"],
    name=user["UserName"],
    arn=user.get("Arn", ""),
    configuration=user,
)
            norm = normalize_iam_user(user)
            findings.extend(evaluate_iam_user(norm))
        cred_report = collect_iam_credential_report(iam_client)
        norm_creds = normalize_credential_report(cred_report)
        for cred in norm_creds:
            findings.extend(evaluate_iam_credential(cred))
    except CollectorError as e:
        logger.error(str(e))
        collector_errors.append(str(e))

    try:
        buckets = collect_s3_buckets(s3_client)
        for bucket in buckets:
            active_resource_ids.add(bucket["Name"])
            # TODO: Migrate S3 inventory to sync_asset()
            norm = normalize_s3_bucket(bucket)
            findings.extend(evaluate_s3_bucket(norm))
    except CollectorError as e:
        logger.error(str(e))
        collector_errors.append(str(e))

    try:
        sgs = collect_security_groups(ec2_client)
        for sg in sgs:
            norm = normalize_security_group(sg)
            findings.extend(evaluate_security_group(norm))
    except CollectorError as e:
        logger.error(str(e))
        collector_errors.append(str(e))

    try:
        trails = collect_trails(cloudtrail_client)
        for trail in trails:
            norm = normalize_cloudtrail(trail)
            findings.extend(evaluate_cloudtrail(norm))
    except CollectorError as e:
        logger.error(str(e))
        collector_errors.append(str(e))

    return findings, collector_errors


def save_findings(db: Session, new_findings: list, account_id: int = None):
    new_ids = [f['id'] for f in new_findings]

    base_query = db.query(Finding).filter(Finding.status == 'ACTIVE', Finding.account_id == account_id)

    # 1. Stale Active findings for this account not present in new scan are marked RESOLVED
    if new_ids:
        base_query.filter(Finding.id.notin_(new_ids)).update(
            {Finding.status: 'RESOLVED'}, synchronize_session=False
        )
    else:
        base_query.update({Finding.status: 'RESOLVED'}, synchronize_session=False)

    # 2. Fetch existing matching findings (active or resolved) for this account in a single batch query
    existing_findings = (
        db.query(Finding)
        .filter(Finding.id.in_(new_ids), Finding.account_id == account_id)
        .all() if new_ids else []
    )
    existing_map = {f.id: f for f in existing_findings}

    for nf in new_findings:
        nf_id = nf['id']
        if nf_id in existing_map:
            existing = existing_map[nf_id]
            if existing.status == 'RESOLVED':
                existing.status = 'ACTIVE'
                existing.timestamp = datetime.utcnow()
        else:
            finding = Finding(
                id=nf_id,
                account_id=account_id,
                severity=nf['severity'],
                service=nf['service'],
                resource_id=nf['resource_id'],
                title=nf['title'],
                description=nf['description'],
                recommendation=nf['recommendation'],
                status='ACTIVE',
                timestamp=datetime.utcnow()
            )
            db.add(finding)

            if finding.severity == 'CRITICAL':
                try:
                    notify_slack(finding)
                except Exception as e:
                    logger.error(f"Failed to send Slack alert: {e}")
                try:
                    create_jira_ticket(finding)
                except Exception as e:
                    logger.error(f"Failed to create Jira ticket: {e}")

    db.commit()

