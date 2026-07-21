from typing import List, Optional, Set
from backend.security.models import User, Organization, APIKey, SecurityContext
from backend.security.rbac.policies import RBACPolicy
from backend.security.rbac.roles import DEFAULT_ROLES

_rbac_policy = RBACPolicy()
_rbac_policy.load_default_roles({role_id: role.permissions for role_id, role in DEFAULT_ROLES.items()})


class AuthorizationChecker:
    def __init__(self, rbac_policy: RBACPolicy = None):
        self.rbac_policy = rbac_policy or _rbac_policy

    def get_effective_permissions(self, role_ids: List[str]) -> Set[str]:
        return self.rbac_policy.get_effective_permissions(role_ids)

    def has_permission(self, role_ids: List[str], permission: str) -> bool:
        return self.rbac_policy.has_permission(role_ids, permission)

    def has_role(self, role_ids: List[str], required_role: str) -> bool:
        return required_role in role_ids

    def is_authorized(self, security_context: SecurityContext, required_permission: str) -> bool:
        if not security_context.is_authenticated():
            return False
        return self.has_permission(security_context.role_ids, required_permission)

    def build_security_context(
        self,
        user: Optional[User] = None,
        organization: Optional[Organization] = None,
        role_ids: List[str] = None,
        permissions: List[str] = None,
        auth_method: str = "none",
        request_id: str = None,
        correlation_id: str = None,
        session_id: str = None,
        api_key: Optional[APIKey] = None,
    ) -> SecurityContext:
        if permissions is None:
            permissions = list(self.get_effective_permissions(role_ids or []))
        return SecurityContext(
            user=user,
            organization=organization,
            role_ids=role_ids or [],
            permissions=permissions,
            auth_method=auth_method,
            request_id=request_id,
            correlation_id=correlation_id,
            session_id=session_id,
            api_key=api_key,
        )
