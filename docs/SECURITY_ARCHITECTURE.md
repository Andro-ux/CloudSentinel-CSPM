# CloudSentinel Security Architecture

## Overview

CloudSentinel uses a single, enterprise-grade security platform built on service-oriented architecture. All authentication, authorization, and security operations flow through one cohesive subsystem with clear separation of concerns.

## Architecture Principles

1. **Single Responsibility**: Each service has one job
2. **Separation of Concerns**: Authentication ≠ Authorization ≠ Auditing
3. **Persistence**: All state stored in database, not memory
4. **Observability**: Every security event is audited
5. **Extensibility**: MFA-ready interfaces for future enterprise features

## Component Diagram

```
Frontend
    │
    ▼
Auth Router (/api/v1/auth/*)
    │
    ▼
AuthenticationManager (Orchestrator)
    │
    ├──► UserService
    ├──► PasswordService
    ├──► TokenService
    ├──► SessionService
    ├──► AuditService
    └──► BootstrapService
    │
    ▼
RBAC (Authorization)
    │
    ▼
Database
```

## Service Layer

### AuthenticationManager

**Role**: Orchestrator only. Delegates all business logic to services.

**Location**: `backend/security/authentication.py`

**Responsibilities**:
- Coordinate service calls for login, logout, refresh, bootstrap
- Pass database sessions to services
- Aggregate results from multiple services
- No business logic implementation

### UserService

**Location**: `backend/security/services/user_service.py`

**Responsibilities**:
- User CRUD operations
- User lookup by username/ID
- Failed login tracking
- Account lockout management
- Password change timestamp tracking

### PasswordService

**Location**: `backend/security/services/password_service.py`

**Responsibilities**:
- Password hashing (PBKDF2-HMAC-SHA256)
- Password verification
- Password strength validation
- Current password verification
- Future: password history, breach checking

### TokenService

**Location**: `backend/security/services/token_service.py`

**Responsibilities**:
- JWT token pair creation
- JWT verification
- Token type validation
- JTI generation
- No business logic

### SessionService

**Location**: `backend/security/services/session_service.py`

**Responsibilities**:
- Persistent session creation and management
- Refresh token storage and revocation
- Session listing and revocation
- Device/IP tracking
- Session expiry management

### AuditService

**Location**: `backend/security/services/audit_service.py`

**Responsibilities**:
- Immutable audit event logging
- Event querying and filtering
- All security actions generate audit events
- Database-backed audit trail

### BootstrapService

**Location**: `backend/security/services/bootstrap_service.py`

**Responsibilities**:
- One-time administrator creation
- BOOTSTRAP_TOKEN validation
- User count verification
- Password strength enforcement
- Self-disabling after first user

## Data Flow

### Login Flow

```
1. Client sends credentials
2. AuthRouter calls AuthenticationManager.login()
3. AuthenticationManager:
   a. UserService.get_user_by_username()
   b. UserService.is_locked() → lockout check
   c. PasswordService.verify()
   d. UserService.increment_failed_login() or reset_failed_login()
   e. SessionService.create_session()
   f. TokenService.create_token_pair()
   g. SessionService.create_refresh_token()
   h. AuditService.log(LOGIN_SUCCESS)
4. Return tokens + user info
```

### Refresh Flow

```
1. Client sends refresh_token
2. AuthRouter calls AuthenticationManager.refresh_access_token()
3. AuthenticationManager:
   a. TokenService.verify_refresh_token()
   b. SessionService.get_refresh_token()
   c. SessionService.revoke_refresh_token()
   d. TokenService.create_token_pair() (new tokens)
   e. SessionService.create_refresh_token() (new refresh token)
   f. AuditService.log(TOKEN_REFRESH)
4. Return new tokens
```

### Bootstrap Flow

```
1. Client sends credentials + BOOTSTRAP_TOKEN
2. AuthRouter validates BOOTSTRAP_TOKEN from Authorization header
3. BootstrapService.bootstrap():
   a. Verify BOOTSTRAP_TOKEN matches
   b. UserService.count_users() == 0
   c. PasswordService.validate_strength()
   d. PasswordService.hash()
   e. UserService.create_user()
   f. SessionService.create_session()
   g. TokenService.create_token_pair()
   h. SessionService.create_refresh_token()
   i. AuditService.log(BOOTSTRAP_USED)
4. Return tokens + admin user
```

## Security Guarantees

1. **No duplicate implementations**: Single hashing, single JWT, single user management
2. **Persistent state**: Sessions and refresh tokens survive server restarts
3. **Immutable audit trail**: All security events logged to database
4. **Account lockout**: 5 failed attempts → 5 minute lockout
5. **Token rotation**: Refresh tokens rotate on every use
6. **Bootstrap protection**: Requires BOOTSTRAP_TOKEN, self-disabling
7. **Separation of concerns**: Authentication ≠ Authorization

## Extension Points

### MFA Integration

Add MFA by extending `AuthenticationManager.login()`:
1. After password verification, check for MFA requirement
2. Return `mfa_required: true` with temporary token
3. Client prompts for TOTP/WebAuthn
4. Verify MFA and issue final tokens

### SSO/OIDC Integration

Add OIDC by creating `OAuth2Service`:
1. Implement token exchange
2. Map OIDC claims to CloudSentinel user model
3. Use existing `TokenService` for JWT creation

### API Key Rotation

Extend `APIKeyService` to support:
1. Automatic rotation
2. Expiration notifications
3. Usage tracking

## Database Schema

```
users
  ├── id (PK)
  ├── username (unique)
  ├── hashed_password
  ├── failed_login_attempts
  ├── locked_until
  └── password_changed_at

sessions
  ├── id (PK)
  ├── user_id (FK)
  ├── device
  ├── browser
  ├── ip_address
  ├── created_at
  ├── expires_at
  ├── last_used
  └── revoked

refresh_tokens
  ├── jti (PK)
  ├── user_id (FK)
  ├── created_at
  ├── expires_at
  ├── revoked
  ├── device
  ├── ip_address
  └── last_used

audit_events
  ├── id (PK)
  ├── event_type
  ├── actor_type
  ├── actor_id
  ├── organization_id
  ├── resource_type
  ├── resource_id
  ├── action
  ├── status
  ├── ip_address
  ├── user_agent
  ├── request_id
  ├── severity
  ├── details (JSON)
  └── timestamp
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `JWT_SECRET_KEY` | JWT signing secret (min 32 chars) | Yes |
| `BOOTSTRAP_TOKEN` | One-time bootstrap authentication | Yes |
| `ENVIRONMENT` | `development` or `production` | No |
| `DATABASE_URL` | Database connection string | No |
