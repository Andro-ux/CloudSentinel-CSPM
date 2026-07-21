from typing import Optional
from datetime import datetime

from backend.security.exceptions import AuthenticationError
from backend.security.services.user_service import UserService
from backend.security.services.password_service import PasswordService
from backend.security.services.token_service import TokenService
from backend.security.services.session_service import SessionService
from backend.security.services.audit_service import AuditService
from backend.security.models import User, Organization, Session as SessionModel


class BootstrapService:
    def __init__(
        self,
        user_service: UserService,
        password_service: PasswordService,
        token_service: TokenService,
        session_service: SessionService,
        audit_service: AuditService,
    ):
        self.user_service = user_service
        self.password_service = password_service
        self.token_service = token_service
        self.session_service = session_service
        self.audit_service = audit_service

    def bootstrap(
        self,
        db,
        username: str,
        password: str,
        bootstrap_token: Optional[str],
        expected_bootstrap_token: Optional[str],
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        secret_key: Optional[str] = None,
    ) -> dict:
        if not expected_bootstrap_token:
            raise AuthenticationError("Bootstrap is not configured on this server")
        if not bootstrap_token or bootstrap_token != expected_bootstrap_token:
            raise AuthenticationError("Invalid bootstrap token")

        if self.user_service.count_users(db) > 0:
            raise AuthenticationError(
                "Bootstrap is not allowed when users already exist"
            )

        self.password_service.validate_strength(password)
        hashed = self.password_service.hash(password)
        user = self.user_service.create_user(db, username, hashed)

        organization = Organization(id=1, name="Default", slug="default")
        session = self.session_service.create_session(
            db, user_id=user.id, ip_address=ip_address
        )

        token_data = self.token_service.create_token_pair(
            user_id=user.id,
            username=user.username,
            organization_id=organization.id,
            role_ids=["platform_admin"],
            secret_key=secret_key or "dev-secret-key-change-in-production",
        )

        refresh_payload = self.token_service.verify_refresh_token(
            token_data["refresh_token"], secret_key or "dev-secret-key-change-in-production"
        )
        refresh_jti = refresh_payload.get("jti")

        self.session_service.create_refresh_token(
            db,
            jti=refresh_jti,
            user_id=user.id,
            device=None,
            ip_address=ip_address,
        )

        self.audit_service.log(
            db,
            event_type="authentication",
            actor_type="user",
            actor_id=str(user.id),
            organization_id=organization.id,
            resource_type="auth",
            resource_id="bootstrap",
            action="bootstrap",
            status="success",
            ip_address=ip_address,
            user_agent=user_agent,
            severity="high",
            details={"username": username},
        )

        return {
            "user": User(
                id=user.id,
                username=user.username,
                organization_id=organization.id,
                role_ids=["platform_admin"],
            ),
            "organization": organization,
            "tokens": token_data,
            "session": session,
        }
