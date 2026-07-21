from fastapi import APIRouter, Depends, HTTPException, status, Request, Body
from fastapi.security import OAuth2PasswordRequestForm
from typing import Optional
from sqlalchemy.orm import Session
from backend.security.authentication import AuthenticationManager
from backend.security.models import SecurityContext, User, Organization
from backend.security.dependencies import get_security_context
from backend.security.rbac.roles import DEFAULT_ROLES
from backend.security.exceptions import AuthenticationError
from backend.config import settings
from backend.database.session import get_db
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordRequestForm

router = APIRouter()
security = HTTPBearer()

_auth_manager = None


def get_auth_manager() -> AuthenticationManager:
    global _auth_manager
    if _auth_manager is None:
        secret_key = getattr(settings, "JWT_SECRET_KEY", "dev-secret-key-change-in-production")
        _auth_manager = AuthenticationManager(secret_key=secret_key)
    return _auth_manager


def get_bootstrap_token() -> Optional[str]:
    return getattr(settings, "BOOTSTRAP_TOKEN", None)


@router.post("/auth/bootstrap", tags=["Authentication"], summary="Bootstrap first administrator")
def bootstrap(
    request: Request,
    username: str,
    password: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
    auth_manager: AuthenticationManager = Depends(get_auth_manager),
):
    bootstrap_token = credentials.credentials
    try:
        result = auth_manager.bootstrap(
            db=db,
            username=username,
            password=password,
            bootstrap_token=bootstrap_token,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        return {
            "success": True,
            "data": {
                "access_token": result["tokens"]["access_token"],
                "refresh_token": result["tokens"]["refresh_token"],
                "token_type": result["tokens"]["token_type"],
                "expires_in": result["tokens"]["expires_in"],
                "user": {
                    "id": result["user"].id,
                    "username": result["user"].username,
                    "organization_id": result["organization"].id,
                },
            },
        }
    except AuthenticationError as exc:
        if "Password must be at least" in str(exc) or "Invalid bootstrap token" in str(exc):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/auth/login", tags=["Authentication"], summary="Login")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    auth_manager: AuthenticationManager = Depends(get_auth_manager),
):
    try:
        result = auth_manager.login(
            db=db,
            username=form_data.username,
            password=form_data.password,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        return {
            "success": True,
            "data": {
                "access_token": result["tokens"]["access_token"],
                "refresh_token": result["tokens"]["refresh_token"],
                "token_type": result["tokens"]["token_type"],
                "expires_in": result["tokens"]["expires_in"],
                "user": {
                    "id": result["user"].id,
                    "username": result["user"].username,
                    "organization_id": result["organization"].id,
                },
            },
        }
    except AuthenticationError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/auth/refresh", tags=["Authentication"], summary="Refresh token")
def refresh(
    refresh_token: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    auth_manager: AuthenticationManager = Depends(get_auth_manager),
):
    try:
        tokens = auth_manager.refresh_access_token(db, refresh_token)
        return {
            "success": True,
            "data": {
                "access_token": tokens["access_token"],
                "refresh_token": tokens["refresh_token"],
                "token_type": tokens["token_type"],
                "expires_in": tokens["expires_in"],
            },
        }
    except AuthenticationError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/auth/logout", tags=["Authentication"], summary="Logout")
def logout(
    refresh_token: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    auth_manager: AuthenticationManager = Depends(get_auth_manager),
    security_context: SecurityContext = Depends(get_security_context),
):
    try:
        auth_manager.logout(db, refresh_token)
        return {"success": True, "data": {"message": "Logged out successfully"}}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/auth/me", tags=["Authentication"], summary="Current user")
def get_me(
    security_context: SecurityContext = Depends(get_security_context),
):
    if not security_context.is_authenticated():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return {
        "success": True,
        "data": {
            "id": security_context.user.id,
            "username": security_context.user.username,
            "organization_id": security_context.organization.id if security_context.organization else None,
            "role_ids": list(security_context.role_ids),
            "permissions": list(security_context.permissions),
        },
    }


@router.post("/auth/users", tags=["Authentication"], summary="Create user")
def create_user(
    username: str,
    password: str,
    role_ids: Optional[str] = None,
    db: Session = Depends(get_db),
    auth_manager: AuthenticationManager = Depends(get_auth_manager),
    security_context: SecurityContext = Depends(get_security_context),
):
    if not security_context.is_authenticated():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    roles = [r.strip() for r in (role_ids or "").split(",") if r.strip()] or ["analyst"]
    try:
        user = auth_manager.create_user(db, username, password, role_ids=roles)
        return {
            "success": True,
            "data": {
                "id": user["id"],
                "username": user["username"],
                "organization_id": user["organization_id"],
                "role_ids": user["role_ids"],
            },
        }
    except AuthenticationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.put("/auth/password", tags=["Authentication"], summary="Change password")
def change_password(
    current_password: str = Body(..., embed=True),
    new_password: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    auth_manager: AuthenticationManager = Depends(get_auth_manager),
    security_context: SecurityContext = Depends(get_security_context),
):
    if not security_context.is_authenticated():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    username = security_context.user.username
    try:
        auth_manager.change_password(db, username, current_password, new_password)
        return {"success": True, "data": {"message": "Password updated successfully"}}
    except AuthenticationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/auth/sessions", tags=["Authentication"], summary="List active sessions")
def list_sessions(
    db: Session = Depends(get_db),
    auth_manager: AuthenticationManager = Depends(get_auth_manager),
    security_context: SecurityContext = Depends(get_security_context),
):
    if not security_context.is_authenticated():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    sessions = auth_manager.get_sessions(db, security_context.user.id)
    return {"success": True, "data": sessions}


@router.delete("/auth/sessions/{session_id}", tags=["Authentication"], summary="Revoke session")
def revoke_session(
    session_id: str,
    db: Session = Depends(get_db),
    auth_manager: AuthenticationManager = Depends(get_auth_manager),
    security_context: SecurityContext = Depends(get_security_context),
):
    if not security_context.is_authenticated():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    success = auth_manager.revoke_session(db, session_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return {"success": True, "data": {"message": "Session revoked"}}


@router.delete("/auth/sessions", tags=["Authentication"], summary="Revoke all sessions")
def revoke_all_sessions(
    db: Session = Depends(get_db),
    auth_manager: AuthenticationManager = Depends(get_auth_manager),
    security_context: SecurityContext = Depends(get_security_context),
):
    if not security_context.is_authenticated():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    count = auth_manager.revoke_all_sessions(db, security_context.user.id)
    return {"success": True, "data": {"message": f"Revoked {count} sessions"}}
