# Platform Security

## Purpose

This document describes CloudSentinel's identity, authentication, authorization, and platform security architecture.

The security layer wraps the existing REST API without modifying any intelligence engines.

## Architecture

```
Client → FastAPI → Security Middleware → Auth Dependency → SecurityContext → Router → Domain Service
```

### Key Principles

- **Separation of concerns**: Business rules live in the security package, not in FastAPI
- **Dependency injection**: Routers receive `SecurityContext`, never raw JWTs
- **Immutable domain models**: All identity models are frozen dataclasses
- **Explicit authorization**: Every permission check is auditable and testable
- **Provider agnostic**: No hardcoded cloud provider assumptions

## Package Structure

```
backend/security/
├── __init__.py
├── authentication.py      # AuthenticationManager
├── authorization.py       # AuthorizationChecker
├── permissions.py         # PermissionRegistry
├── middleware.py          # SecurityHeadersMiddleware, RateLimitMiddleware
├── exceptions.py          # Security exception hierarchy
├── dependencies.py        # FastAPI DI providers
├── hashing.py             # Password and API key hashing
├── jwt.py                 # JWT token creation and validation
├── api_keys.py            # APIKeyManager
├── audit.py               # AuditLogger
├── rate_limit.py          # RateLimiter
├── models.py              # Immutable domain models
├── services.py            # AuthenticationService, AuthorizationService, AuditService, APIKeyService
├── validators.py          # Input validation utilities
└── rbac/
    ├── __init__.py
    ├── roles.py           # Role definitions
    ├── policies.py        # PermissionPolicy, RBACPolicy
    └── decorators.py      # require_permission, require_role
```

## Identity Model

All identity models are immutable dataclasses (`frozen=True`).

### User

Represents an authenticated user.

```python
@dataclass(frozen=True)
class User:
    id: int
    username: str
    email: Optional[str]
    organization_id: Optional[int]
    role_ids: List[str]
    is_active: bool
    is_superuser: bool
    created_at: datetime
    last_login: Optional[datetime]
    metadata: Dict[str, Any]
```

### Organization

Every user belongs to an organization. Supports future SaaS multi-tenancy.

```python
@dataclass(frozen=True)
class Organization:
    id: int
    name: str
    slug: str
    is_active: bool
    created_at: datetime
    metadata: Dict[str, Any]
```

### Role

Maps to a set of permissions.

```python
@dataclass(frozen=True)
class Role:
    id: str
    name: str
    description: str
    permissions: List[str]
    is_system: bool
    created_at: datetime
    metadata: Dict[str, Any]
```

### Permission

First-class permission objects.

```python
@dataclass(frozen=True)
class Permission:
    id: str
    name: str
    description: str
    resource: str
    action: str
    metadata: Dict[str, Any]
```

### APIKey

Machine-to-machine authentication.

```python
@dataclass(frozen=True)
class APIKey:
    id: str
    name: str
    hashed_secret: str
    user_id: int
    organization_id: int
    permissions: List[str]
    expires_at: Optional[datetime]
    last_used: Optional[datetime]
    created_at: datetime
    metadata: Dict[str, Any]
```

### AuditEvent

Immutable audit trail entry.

```python
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
    ip_address: Optional[str]
    user_agent: Optional[str]
    request_id: Optional[str]
    details: Dict[str, Any]
    timestamp: datetime
```

### Session

Tracks authenticated sessions for refresh token management.

```python
@dataclass(frozen=True)
class Session:
    id: str
    user_id: int
    organization_id: int
    refresh_token_jti: str
    expires_at: datetime
    created_at: datetime
    metadata: Dict[str, Any]
```

### TokenPair

Access and refresh token bundle.

```python
@dataclass(frozen=True)
class TokenPair:
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int = 3600
```

## SecurityContext

Single immutable object passed to every protected endpoint.

```python
@dataclass(frozen=True)
class SecurityContext:
    user: Optional[User]
    organization: Optional[Organization]
    role_ids: List[str]
    permissions: set
    auth_method: str
    request_id: str
    correlation_id: str
    session_id: Optional[str]
    api_key: Optional[APIKey]
```

**Methods:**
- `has_permission(permission: str) -> bool`
- `has_role(role_id: str) -> bool`
- `is_authenticated() -> bool`
- `is_superuser() -> bool`
- `to_dict() -> Dict[str, Any]`

## Authentication

### JWT Authentication

Access tokens and refresh tokens are JWTs signed with HS256.

**Access Token Claims:**
- `sub` — user ID
- `username` — username
- `org_id` — organization ID
- `role_ids` — list of role IDs
- `jti` — unique token ID
- `type` — "access"
- `exp` — expiration timestamp
- `iat` — issued at timestamp

**Refresh Token Claims:**
- `sub` — user ID
- `org_id` — organization ID
- `jti` — unique token ID
- `type` — "refresh"
- `exp` — expiration timestamp
- `iat` — issued at timestamp

**Configuration:**
- Algorithm: HS256
- Access token TTL: 60 minutes (configurable)
- Refresh token TTL: 7 days (configurable)
- Secret key: loaded from `JWT_SECRET_KEY` environment variable (minimum 32 characters)

### Login Flow

```
Client → POST /api/v1/auth/login
    ↓
AuthenticationManager.login(username, password)
    ↓
AuthenticationService.authenticate_user()
    ↓
Hash verification with PBKDF2
    ↓
Create session
    ↓
Create token pair (access + refresh)
    ↓
Return tokens + user info
```

### Refresh Flow

```
Client → POST /api/v1/auth/refresh {refresh_token}
    ↓
AuthenticationManager.refresh_access_token()
    ↓
Validate refresh token JWT
    ↓
Rotate refresh token (old one invalidated)
    ↓
Create new access token
    ↓
Return new tokens
```

### Logout Flow

```
Client → POST /api/v1/auth/logout {refresh_token}
    ↓
AuthenticationManager.logout()
    ↓
Remove refresh token from active store
    ↓
Return success
```

## Password Security

- Passwords are never stored in plain text
- Hashing: PBKDF2 with SHA-256, 100,000 iterations, random 16-byte salt
- Storage format: `salt_hex$hash_hex`
- Minimum password length: 12 characters
- No custom cryptography — uses standard `hashlib`

## RBAC

### Default Roles

| Role | ID | Description |
|------|----|-------------|
| Platform Administrator | `platform_admin` | Full platform access with user management |
| Organization Administrator | `organization_admin` | Full access within an organization |
| Security Engineer | `security_engineer` | Security operations and analysis |
| Analyst | `analyst` | Read-only access to security data |
| Auditor | `auditor` | Read-only access with audit logs |
| Read Only | `read_only` | Minimal read-only access |

### Permissions

Granular permissions in `resource.action` format:

| Permission | Description |
|------------|-------------|
| `dashboard.read` | View executive dashboard |
| `assets.read` | View cloud assets |
| `findings.read` | View security findings |
| `risks.read` | View risk assessments |
| `graph.read` | View knowledge graph |
| `providers.read` | View registered providers |
| `providers.manage` | Manage provider plugins |
| `users.manage` | Manage users |
| `apikey.manage` | Manage API keys |
| `audit.read` | View audit logs |
| `system.admin` | Full system administration |

### Permission Hierarchy

```
platform_admin: all permissions
organization_admin: users.manage, apikey.manage, dashboard.read, assets.read, findings.read, risks.read, graph.read, providers.read, capabilities.read, audit.read
security_engineer: dashboard.read, assets.read, findings.read, risks.read, graph.read, providers.read, capabilities.read
analyst: dashboard.read, assets.read, findings.read, risks.read, graph.read
auditor: dashboard.read, assets.read, findings.read, risks.read, graph.read, audit.read, providers.read
read_only: dashboard.read, assets.read
```

## Organizations

- Every user belongs to an organization
- Every API key is scoped to an organization
- Future SaaS support requires minimal redesign
- Organization ID is embedded in JWT claims

## API Keys

- Secure machine-to-machine authentication
- Displayed only once at creation
- Hashed secrets stored (SHA-256)
- Supports expiration
- Supports custom permissions
- Supports organization scoping

**Lifecycle:**
1. Create — generates secret, stores hash, returns plaintext secret once
2. Use — sent as `Bearer sk_<api_key_id>` or as credential
3. Verify — compares hash, checks expiration
4. Revoke — deletes from store

## Audit Logging

Every sensitive operation produces an immutable audit event.

**Logged Events:**
- Login / Logout
- Token Refresh
- API Key Created / Deleted
- Permission Change
- Role Assignment
- Failed Login
- Unauthorized Access
- Configuration Change

**Audit Event Fields:**
- `id` — unique event ID
- `event_type` — authentication, authorization, configuration
- `actor_type` — user, api_key, system
- `actor_id` — user or API key ID
- `organization_id` — organization scope
- `resource_type` — auth, apikey, user, etc.
- `resource_id` — specific resource ID
- `action` — create, delete, login, etc.
- `status` — success, failed
- `ip_address` — client IP
- `user_agent` — client user agent
- `request_id` — request correlation ID
- `details` — arbitrary metadata
- `timestamp` — event time

## Rate Limiting

Reusable rate limiter supporting per-user, per-API-key, and per-IP limits.

**Configuration:**
- Window: 60 seconds
- Limit: 100 requests per window
- Policy is configurable per endpoint

## Security Headers

Middleware applies modern security headers:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Content-Security-Policy: default-src 'self'`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`

## Dependency Injection

FastAPI dependencies enforce authentication and authorization:

```python
from backend.security.dependencies import (
    get_security_context,
    require_permissions,
    require_roles,
)

@router.get("/dashboard")
def get_dashboard(
    context: SecurityContext = Depends(require_permissions(["dashboard.read"])),
):
    # context is guaranteed to be authenticated and authorized
    pass
```

Routers never manually inspect JWTs or tokens.

## Validation

All inputs are validated:

- **Usernames**: 3+ characters, alphanumeric, underscores, hyphens
- **Email**: RFC-compliant format
- **Passwords**: Minimum 12 characters
- **Permissions**: `resource.action` format
- **Roles**: Must be one of the defined system roles
- **JWT**: Signature, expiration, type validation
- **API Keys**: Format, expiration, hash verification

## Extension Guide

### Adding a New Permission

1. Define the permission in the appropriate role in `backend/security/rbac/roles.py`
2. Use `require_permissions(["new.permission"])` on the endpoint
3. Document in the API OpenAPI spec

### Adding a New Role

1. Define `RoleDefinition` in `backend/security/rbac/roles.py`
2. Add to `DEFAULT_ROLES`
3. Assign permissions

### Adding a New Authentication Method

1. Extend `SecurityContext.auth_method`
2. Add authentication logic in `backend/security/dependencies.py`
3. The `SecurityContext` abstraction ensures routers remain unchanged

### Future Identity Providers

Extension points reserved for:
- OAuth2 / OpenID Connect
- SAML
- LDAP / Active Directory
- Azure Entra ID
- Okta
- Google Workspace
- GitHub Enterprise
- SCIM
- MFA / WebAuthn / Passkeys

## Testing

Security tests (`tests/test_security.py`) cover:
- Full auth flow (login, refresh, logout)
- Protected endpoints
- Health endpoint remains public
- Security context authorization
- RBAC permissions
- Immutable models
- Password hashing
- JWT tokens
- API key lifecycle
- Audit logging
- Input validation
- Rate limiting
- OpenAPI integration
- Organization isolation

## Constraints

The security layer:
- Does not modify Plugin Framework, Knowledge Engine, Fact Engine, Rule Engine, Risk Engine, or Executive Intelligence
- Wraps the API without changing the intelligence pipeline
- Is provider-agnostic
- Is extensible for future capabilities
