from typing import Optional, Dict, Any, List
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from backend.security.models import User, Organization, APIKey, SecurityContext
from backend.security.rbac.policies import RBACPolicy, PermissionPolicy
from backend.security.rbac.roles import DEFAULT_ROLES
from backend.security.exceptions import AuthenticationError, InvalidAPIKeyError

security = HTTPBearer(auto_error=False)

_rbac_policy = RBACPolicy()
_rbac_policy.load_default_roles({role_id: role.permissions for role_id, role in DEFAULT_ROLES.items()})


def get_security_context(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> SecurityContext:
    context = SecurityContext(
        request_id=request.headers.get("X-Request-ID", str(__import__('uuid').uuid4())),
        correlation_id=request.headers.get("X-Correlation-ID", str(__import__('uuid').uuid4())),
    )
    if not credentials:
        return context
    token = credentials.credentials
    if token.startswith("sk_"):
        return _authenticate_api_key(context, token)
    return _authenticate_jwt(context, token)


def _authenticate_jwt(context: SecurityContext, token: str) -> SecurityContext:
    from backend.security.jwt import decode_token, verify_token_type
    from backend.config import settings
    secret_key = getattr(settings, "JWT_SECRET_KEY", None)
    if not secret_key:
        return context
    try:
        payload = decode_token(token, secret_key)
        verify_token_type(payload, "access")
        user_id = int(payload.get("sub", 0))
        organization_id = int(payload.get("org_id", 0))
        role_ids = payload.get("role_ids", [])
        permissions = _rbac_policy.get_effective_permissions(role_ids)
        return SecurityContext(
            user=User(
                id=user_id,
                username=payload.get("username", ""),
                organization_id=organization_id,
                role_ids=role_ids,
            ),
            organization=Organization(id=organization_id, name="", slug=""),
            role_ids=role_ids,
            permissions=permissions,
            auth_method="jwt",
            request_id=context.request_id,
            correlation_id=context.correlation_id,
        )
    except Exception:
        pass
    return context


def _authenticate_api_key(context: SecurityContext, api_key_id: str) -> SecurityContext:
    from backend.security.api_keys import APIKeyManager
    api_key = APIKeyManager().get_api_key(api_key_id)
    if not api_key:
        return context
    permissions = set(api_key.permissions)
    return SecurityContext(
        user=User(id=api_key.user_id, username=f"api-key:{api_key.name}"),
        organization=Organization(id=api_key.organization_id, name="", slug=""),
        role_ids=[],
        permissions=permissions,
        auth_method="api_key",
        request_id=context.request_id,
        correlation_id=context.correlation_id,
        api_key=api_key,
    )


def get_current_security_context() -> SecurityContext:
    return get_security_context


def require_permissions(permissions: List[str]):
    def dependency(context: SecurityContext = Depends(get_security_context)):
        if not context.is_authenticated():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        for permission in permissions:
            if not context.has_permission(permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {permission}",
                )
        return context
    return dependency


def require_roles(role_ids: List[str]):
    def dependency(context: SecurityContext = Depends(get_security_context)):
        if not context.is_authenticated():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        for role_id in role_ids:
            if not context.has_role(role_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Role required: {role_id}",
                )
        return context
    return dependency
