from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class User:
    id: int
    username: str
    email: Optional[str] = None
    organization_id: Optional[int] = None
    role_ids: List[str] = field(default_factory=list)
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Role:
    id: str
    name: str
    description: str
    permissions: List[str] = field(default_factory=list)
    is_system: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Permission:
    id: str
    name: str
    description: str
    resource: str
    action: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Organization:
    id: int
    name: str
    slug: str
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class APIKey:
    id: str
    name: str
    hashed_secret: str
    user_id: int
    organization_id: int
    permissions: List[str] = field(default_factory=list)
    expires_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AuditEvent:
    id: str
    event_type: str
    actor_type: str
    actor_id: str
    organization_id: int
    resource_type: str
    resource_id: str
    action: str
    status: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_id: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class Session:
    id: str
    user_id: int
    organization_id: int
    refresh_token_jti: str
    expires_at: datetime
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TokenPair:
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int = 3600


@dataclass(frozen=True)
class SecurityContext:
    user: Optional[User] = None
    organization: Optional[Organization] = None
    role_ids: List[str] = field(default_factory=list)
    permissions: set = field(default_factory=set)
    auth_method: str = "none"
    request_id: str = ""
    correlation_id: str = ""
    session_id: Optional[str] = None
    api_key: Optional[APIKey] = None

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions

    def has_role(self, role_id: str) -> bool:
        return role_id in self.role_ids

    def is_authenticated(self) -> bool:
        return self.user is not None or self.api_key is not None

    def is_superuser(self) -> bool:
        return self.user is not None and self.user.is_superuser

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user.id if self.user else None,
            "username": self.user.username if self.user else None,
            "organization_id": self.organization.id if self.organization else None,
            "role_ids": self.role_ids,
            "permissions": list(self.permissions),
            "auth_method": self.auth_method,
            "request_id": self.request_id,
            "correlation_id": self.correlation_id,
            "session_id": self.session_id,
            "api_key_id": self.api_key.id if self.api_key else None,
        }
