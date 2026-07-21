from typing import Optional, Dict, Any, List
from datetime import datetime

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


class AuthenticationService:
    def __init__(self, rbac_policy):
        self.rbac_policy = rbac_policy
        self._sessions: Dict[str, Session] = {}

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        from backend.database.session import SessionLocal
        from backend.database.models import User as DBUser
        from backend.security.hashing import verify_password
        db = SessionLocal()
        try:
            db_user = db.query(DBUser).filter(DBUser.username == username).first()
            if not db_user:
                return None
            if not verify_password(password, db_user.hashed_password):
                return None
            return User(
                id=db_user.id,
                username=db_user.username,
                is_active=True,
            )
        finally:
            db.close()

    def create_session(self, user: User, organization: Organization) -> Session:
        session_id = str(__import__('uuid').uuid4())
        session = Session(
            id=session_id,
            user_id=user.id,
            organization_id=organization.id,
            refresh_token_jti=str(__import__('uuid').uuid4()),
            expires_at=__import__('datetime').datetime.utcnow() + __import__('datetime').timedelta(days=7),
        )
        self._sessions[session.id] = session
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        return self._sessions.get(session_id)


class AuthorizationService:
    def __init__(self, rbac_policy):
        self.rbac_policy = rbac_policy

    def get_effective_permissions(self, role_ids: List[str]) -> List[str]:
        return sorted(self.rbac_policy.get_effective_permissions(role_ids))

    def check_permission(self, role_ids: List[str], permission: str) -> bool:
        return self.rbac_policy.has_permission(role_ids, permission)


class AuditService:
    def __init__(self):
        self._events: List[AuditEvent] = []

    def log(
        self,
        event_type: str,
        actor_type: str,
        actor_id: str,
        organization_id: int,
        resource_type: str,
        resource_id: str,
        action: str,
        status: str,
        ip_address: str = None,
        user_agent: str = None,
        request_id: str = None,
        details: Dict[str, Any] = None,
    ) -> AuditEvent:
        event = AuditEvent(
            id=str(__import__('uuid').uuid4()),
            event_type=event_type,
            actor_type=actor_type,
            actor_id=actor_id,
            organization_id=organization_id,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            status=status,
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
            details=details or {},
        )
        self._events.append(event)
        return event

    def get_events(self, organization_id: int = None) -> List[AuditEvent]:
        if organization_id is None:
            return list(self._events)
        return [e for e in self._events if e.organization_id == organization_id]


class APIKeyService:
    def __init__(self):
        self._api_keys: Dict[str, APIKey] = {}

    def create_api_key(
        self,
        name: str,
        user_id: int,
        organization_id: int,
        permissions: List[str],
        secret: str,
        expires_at: datetime = None,
    ) -> tuple[APIKey, str]:
        from backend.security.hashing import hash_api_key_secret
        api_key_id = str(__import__('uuid').uuid4())
        hashed_secret = hash_api_key_secret(secret)
        api_key = APIKey(
            id=api_key_id,
            name=name,
            hashed_secret=hashed_secret,
            user_id=user_id,
            organization_id=organization_id,
            permissions=permissions,
            expires_at=expires_at,
        )
        self._api_keys[api_key_id] = api_key
        return api_key, secret

    def verify_api_key(self, api_key_id: str, secret: str) -> Optional[APIKey]:
        from backend.security.hashing import hash_api_key_secret
        api_key = self._api_keys.get(api_key_id)
        if not api_key:
            return None
        if api_key.expires_at and api_key.expires_at < __import__('datetime').datetime.utcnow():
            return None
        if api_key.hashed_secret != hash_api_key_secret(secret):
            return None
        api_key.last_used = __import__('datetime').datetime.utcnow()
        return api_key

    def get_api_key(self, api_key_id: str) -> Optional[APIKey]:
        return self._api_keys.get(api_key_id)

    def delete_api_key(self, api_key_id: str) -> bool:
        if api_key_id in self._api_keys:
            del self._api_keys[api_key_id]
            return True
        return False
