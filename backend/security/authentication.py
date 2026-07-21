from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

from backend.security.models import (
    User,
    Organization,
    APIKey,
    AuditEvent,
    Session,
    TokenPair,
    SecurityContext,
)
from backend.security.exceptions import AuthenticationError, InvalidAPIKeyError
from backend.security.services.user_service import UserService
from backend.security.services.password_service import PasswordService
from backend.security.services.token_service import TokenService
from backend.security.services.session_service import SessionService
from backend.security.services.audit_service import AuditService
from backend.security.services.bootstrap_service import BootstrapService
from backend.security.hashing import hash_password, verify_password, validate_password_strength
from backend.database.session import SessionLocal
from backend.database.models import User as DBUser


class AuthenticationManager:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self._user_service = UserService()
        self._password_service = PasswordService()
        self._token_service = TokenService()
        self._session_service = SessionService()
        self._audit_service = AuditService()
        self._bootstrap_service = BootstrapService(
            user_service=self._user_service,
            password_service=self._password_service,
            token_service=self._token_service,
            session_service=self._session_service,
            audit_service=self._audit_service,
        )

    def bootstrap(
        self,
        db,
        username: str,
        password: str,
        bootstrap_token: Optional[str] = None,
        ip_address: str = None,
        user_agent: str = None,
    ) -> dict:
        from backend.config import settings
        expected_bootstrap_token = getattr(settings, "BOOTSTRAP_TOKEN", None)
        return self._bootstrap_service.bootstrap(
            db=db,
            username=username,
            password=password,
            bootstrap_token=bootstrap_token,
            expected_bootstrap_token=expected_bootstrap_token,
            ip_address=ip_address,
            user_agent=user_agent,
            secret_key=self.secret_key,
        )

    def login(
        self, db, username: str, password: str, ip_address: str = None, user_agent: str = None
    ) -> dict:
        db_user = self._user_service.get_user_by_username(db, username)
        if not db_user:
            self._audit_service.log(
                db,
                event_type="authentication",
                actor_type="user",
                actor_id=username,
                organization_id=0,
                resource_type="auth",
                resource_id="login",
                action="login",
                status="failed",
                ip_address=ip_address,
                user_agent=user_agent,
                severity="medium",
                details={"reason": "user_not_found"},
            )
            raise AuthenticationError("Invalid username or password")

        if self._user_service.is_locked(db_user):
            self._audit_service.log(
                db,
                event_type="authentication",
                actor_type="user",
                actor_id=str(db_user.id),
                organization_id=0,
                resource_type="auth",
                resource_id="login",
                action="login",
                status="failed",
                ip_address=ip_address,
                user_agent=user_agent,
                severity="high",
                details={"reason": "account_locked"},
            )
            raise AuthenticationError(
                "Account is locked due to too many failed login attempts"
            )

        if not self._password_service.verify(password, db_user.hashed_password):
            self._user_service.increment_failed_login(db, db_user)
            self._audit_service.log(
                db,
                event_type="authentication",
                actor_type="user",
                actor_id=str(db_user.id),
                organization_id=0,
                resource_type="auth",
                resource_id="login",
                action="login",
                status="failed",
                ip_address=ip_address,
                user_agent=user_agent,
                severity="medium",
                details={"reason": "invalid_password"},
            )
            raise AuthenticationError("Invalid username or password")

        self._user_service.reset_failed_login(db, db_user)

        role_ids = getattr(db_user, "role_ids", None) or ["analyst"]
        organization_id = getattr(db_user, "organization_id", None) or 1
        organization = Organization(id=organization_id, name="", slug="")
        session = self._session_service.create_session(
            db, user_id=db_user.id, ip_address=ip_address
        )

        token_data = self._token_service.create_token_pair(
            user_id=db_user.id,
            username=db_user.username,
            organization_id=organization.id,
            role_ids=role_ids,
            secret_key=self.secret_key,
        )

        refresh_payload = self._token_service.verify_refresh_token(
            token_data["refresh_token"], self.secret_key
        )
        refresh_jti = refresh_payload.get("jti")

        self._session_service.create_refresh_token(
            db,
            jti=refresh_jti,
            user_id=db_user.id,
            device=None,
            ip_address=ip_address,
        )

        self._audit_service.log(
            db,
            event_type="authentication",
            actor_type="user",
            actor_id=str(db_user.id),
            organization_id=organization.id,
            resource_type="auth",
            resource_id="login",
            action="login",
            status="success",
            ip_address=ip_address,
            user_agent=user_agent,
            severity="info",
            details={"session_id": session.id},
        )

        return {
            "user": User(
                id=db_user.id,
                username=db_user.username,
                organization_id=organization_id,
                role_ids=role_ids,
            ),
            "organization": organization,
            "tokens": token_data,
            "session": session,
        }

    def refresh_access_token(self, db, refresh_token: str) -> dict:
        try:
            payload = self._token_service.verify_refresh_token(
                refresh_token, self.secret_key
            )
        except AuthenticationError:
            self._audit_service.log(
                db,
                event_type="authentication",
                actor_type="user",
                actor_id="unknown",
                organization_id=0,
                resource_type="auth",
                resource_id="refresh",
                action="token_refresh",
                status="failed",
                severity="medium",
                details={"reason": "invalid_refresh_token"},
            )
            raise AuthenticationError("Invalid refresh token")

        jti = payload.get("jti")
        db_token = self._session_service.get_refresh_token(db, jti)
        if not db_token or db_token.revoked:
            raise AuthenticationError("Invalid refresh token")

        user_id = int(payload.get("sub", 0))
        username = payload.get("username", "")
        organization_id = int(payload.get("org_id", 0))
        role_ids = payload.get("role_ids", [])

        self._session_service.revoke_refresh_token(db, jti)

        new_tokens = self._token_service.create_token_pair(
            user_id=user_id,
            username=username,
            organization_id=organization_id,
            role_ids=role_ids,
            secret_key=self.secret_key,
        )

        new_refresh_payload = self._token_service.verify_refresh_token(
            new_tokens["refresh_token"], self.secret_key
        )
        new_refresh_jti = new_refresh_payload.get("jti")

        self._session_service.create_refresh_token(
            db,
            jti=new_refresh_jti,
            user_id=user_id,
            device=db_token.device,
            ip_address=db_token.ip_address,
        )

        self._audit_service.log(
            db,
            event_type="authentication",
            actor_type="user",
            actor_id=str(user_id),
            organization_id=organization_id,
            resource_type="auth",
            resource_id="refresh",
            action="token_refresh",
            status="success",
            severity="info",
        )

        return new_tokens

    def logout(self, db, refresh_token: str) -> None:
        try:
            payload = self._token_service.verify_refresh_token(
                refresh_token, self.secret_key
            )
            jti = payload.get("jti")
            self._session_service.revoke_refresh_token(db, jti)
        except AuthenticationError:
            pass

    def get_current_user_from_token(self, token: str) -> Optional[User]:
        try:
            payload = self._token_service.verify_access_token(token, self.secret_key)
            return User(
                id=int(payload.get("sub", 0)),
                username=payload.get("username", ""),
                organization_id=int(payload.get("org_id", 0)),
                role_ids=payload.get("role_ids", []),
            )
        except AuthenticationError:
            return None

    def get_user_by_username(self, db, username: str) -> Optional[dict]:
        db_user = self._user_service.get_user_by_username(db, username)
        if not db_user:
            return None
        return {
            "id": db_user.id,
            "username": db_user.username,
            "hashed_password": db_user.hashed_password,
            "organization_id": getattr(db_user, "organization_id", None) or 1,
            "role_ids": getattr(db_user, "role_ids", None) or ["analyst"],
        }

    def create_user(self, db, username: str, password: str, role_ids: List[str] = None) -> dict:
        self._password_service.validate_strength(password)
        hashed = self._password_service.hash(password)
        db_user = self._user_service.create_user(db, username, hashed)
        return {
            "id": db_user.id,
            "username": db_user.username,
            "organization_id": getattr(db_user, "organization_id", None) or 1,
            "role_ids": role_ids or ["analyst"],
        }

    def change_password(self, db, username: str, current_password: str, new_password: str) -> bool:
        db_user = self._user_service.get_user_by_username(db, username)
        if not db_user:
            raise AuthenticationError("User not found")
        if not self._password_service.verify(current_password, db_user.hashed_password):
            raise AuthenticationError("Current password is incorrect")
        self._password_service.validate_strength(new_password)
        hashed = self._password_service.hash(new_password)
        self._user_service.update_password(db, db_user, hashed)
        return True

    def get_sessions(self, db, user_id: int) -> List[dict]:
        sessions = self._session_service.get_user_sessions(db, user_id)
        return [
            {
                "id": s.id,
                "device": s.device,
                "browser": s.browser,
                "ip_address": s.ip_address,
                "created_at": s.created_at.isoformat() if s.created_at else None,
                "last_used": s.last_used.isoformat() if s.last_used else None,
                "expires_at": s.expires_at.isoformat() if s.expires_at else None,
            }
            for s in sessions
        ]

    def revoke_session(self, db, session_id: str) -> bool:
        return self._session_service.revoke_session(db, session_id)

    def revoke_all_sessions(self, db, user_id: int) -> int:
        return self._session_service.revoke_all_sessions(db, user_id)

    def verify_api_key(self, api_key_id: str, secret: str) -> Optional[APIKey]:
        return _api_key_service.verify_api_key(api_key_id, secret)

    def create_api_key(self, name: str, user_id: int, organization_id: int, permissions: List[str]) -> tuple[APIKey, str]:
        api_key, secret = _api_key_service.create_api_key(
            name=name,
            user_id=user_id,
            organization_id=organization_id,
            permissions=permissions,
            secret=__import__('backend.security.hashing', fromlist=['generate_api_key_secret']).generate_api_key_secret(),
        )
        return api_key, secret

    def revoke_api_key(self, api_key_id: str, user_id: int, organization_id: int) -> bool:
        result = _api_key_service.delete_api_key(api_key_id)
        return result

    def get_audit_events(self, db, organization_id: int = None) -> List[AuditEvent]:
        return self._audit_service.get_events(db, organization_id=organization_id)
