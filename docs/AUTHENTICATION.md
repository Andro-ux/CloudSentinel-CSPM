# CloudSentinel Authentication Architecture

## Overview

CloudSentinel uses a single, enterprise-grade authentication system built on JWT tokens with refresh token rotation. All authentication flows through one security subsystem with no duplicate implementations.

## Architecture

```
Frontend
    ↓
Auth Router (/api/v1/auth/*)
    ↓
AuthenticationManager
    ↓
Hashing (backend/security/hashing.py)
    ↓
JWT (backend/security/jwt.py)
    ↓
RBAC (backend/security/rbac/*)
    ↓
Database
```

## Core Components

### AuthenticationManager

**Location:** `backend/security/authentication.py`

The single class responsible for all authentication operations:
- `bootstrap()` - Create first administrator
- `login()` - Authenticate user and issue tokens
- `refresh_access_token()` - Issue new access token
- `logout()` - Invalidate refresh token
- `create_user()` - Create new user
- `change_password()` - Update user password
- `get_user_by_username()` - Retrieve user information

### Password Hashing

**Location:** `backend/security/hashing.py`

Single implementation using PBKDF2-HMAC-SHA256:
- 100,000 iterations
- 16-byte random salt
- Salted hash format: `salt_hex$hash_hex`

Functions:
- `hash_password(password)` → hashed string
- `verify_password(plain, hashed)` → boolean
- `validate_password_strength(password)` → raises ValueError if weak
- `hash_api_key_secret(secret)` → SHA256 hash
- `generate_api_key_secret()` → secure random secret

### JWT Tokens

**Location:** `backend/security/jwt.py`

Token pair generation with:
- Access tokens: 60 minute expiry
- Refresh tokens: 7 day expiry
- HS256 algorithm
- Unique JTI for each token
- Token type claims (`access` / `refresh`)

Functions:
- `create_token_pair()` → access + refresh tokens
- `decode_token()` → payload validation
- `verify_token_type()` → ensure correct token type

### RBAC

**Location:** `backend/security/rbac/`

Role-Based Access Control with:
- Default roles: `platform_admin`, `analyst`
- Permission inheritance
- Effective permission calculation

### SecurityContext

**Location:** `backend/security/models.py`

Immutable dataclass containing:
- User information
- Organization
- Role IDs
- Permissions
- Authentication method

## Authentication Flow

### Bootstrap Flow

```
1. POST /api/v1/auth/bootstrap?username=admin&password=secure123
2. Check User.count() == 0
3. Validate password strength (min 12 chars)
4. Hash password
5. Create user in database
6. Assign platform_admin role
7. Generate JWT token pair
8. Return tokens + user info
```

**Only works when no users exist.** Returns 403 Forbidden if users already exist.

### Login Flow

```
1. POST /api/v1/auth/login (form data: username, password)
2. AuthenticationManager.login()
3. Verify password hash
4. Create session
5. Generate JWT token pair
6. Store refresh token in memory
7. Return tokens + user info
```

### Refresh Flow

```
1. POST /api/v1/auth/refresh (JSON: {refresh_token})
2. Validate refresh token exists in memory
3. Decode and verify refresh token JWT
4. Generate new token pair
5. Replace old refresh token with new one
6. Return new tokens
```

### Logout Flow

```
1. POST /api/v1/auth/logout (JSON: {refresh_token})
2. Remove refresh token from memory
3. Return success
```

## API Endpoints

### POST /api/v1/auth/bootstrap

Create first administrator (one-time only).

**Query Parameters:**
- `username` (string, required)
- `password` (string, required)

**Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "...",
    "refresh_token": "...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "user": {
      "id": 1,
      "username": "admin",
      "organization_id": 1
    }
  }
}
```

**Errors:**
- `400 Bad Request` - Weak password
- `403 Forbidden` - Users already exist

### POST /api/v1/auth/login

Authenticate user.

**Request:** Form data
- `username` (string, required)
- `password` (string, required)

**Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "...",
    "refresh_token": "...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "user": {
      "id": 1,
      "username": "admin",
      "organization_id": 1
    }
  }
}
```

**Errors:**
- `401 Unauthorized` - Invalid credentials

### POST /api/v1/auth/refresh

Refresh access token.

**Request:** JSON body
- `refresh_token` (string, required)

**Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "...",
    "refresh_token": "...",
    "token_type": "Bearer",
    "expires_in": 3600
  }
}
```

**Errors:**
- `401 Unauthorized` - Invalid refresh token

### POST /api/v1/auth/logout

Invalidate refresh token.

**Request:** JSON body
- `refresh_token` (string, required)

**Response:**
```json
{
  "success": true,
  "data": {
    "message": "Logged out successfully"
  }
}
```

### GET /api/v1/auth/me

Get current user information.

**Headers:** `Authorization: Bearer <access_token>`

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "admin",
    "organization_id": 1,
    "role_ids": ["platform_admin"],
    "permissions": ["dashboard.read", "assets.read", ...]
  }
}
```

**Errors:**
- `401 Unauthorized` - Not authenticated

### POST /api/v1/auth/users

Create new user (requires authentication).

**Headers:** `Authorization: Bearer <access_token>`

**Query Parameters:**
- `username` (string, required)
- `password` (string, required)
- `role_ids` (string, optional, comma-separated)

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 2,
    "username": "newuser",
    "organization_id": 1,
    "role_ids": ["analyst"]
  }
}
```

**Errors:**
- `400 Bad Request` - Username exists or weak password
- `401 Unauthorized` - Not authenticated

### PUT /api/v1/auth/password

Change password (requires authentication).

**Headers:** `Authorization: Bearer <access_token>`

**Request:** JSON body
- `current_password` (string, required)
- `new_password` (string, required)

**Response:**
```json
{
  "success": true,
  "data": {
    "message": "Password updated successfully"
  }
}
```

**Errors:**
- `400 Bad Request` - Invalid current password or weak new password
- `401 Unauthorized` - Not authenticated

## Security Model

### Password Policy

- Minimum length: 12 characters
- Hashing: PBKDF2-HMAC-SHA256
- Iterations: 100,000
- Salt: 16-byte random

### JWT Security

- Algorithm: HS256
- Access token expiry: 60 minutes
- Refresh token expiry: 7 days
- Refresh tokens stored in memory (not database)
- Token rotation on refresh

### RBAC Permissions

Default roles and permissions:

| Role | Permissions |
|------|-------------|
| `platform_admin` | Full access to all resources |
| `analyst` | Read access to dashboard, assets, findings, risks, graph, providers, capabilities |

### Rate Limiting

- 100 requests per 60 seconds per IP
- Applied globally via middleware

### Security Headers

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- Content-Security-Policy varies by environment

## Threat Model

### Threats Mitigated

1. **Brute Force Attacks**
   - Rate limiting (100 req/min)
   - Password hashing with high iteration count

2. **Token Theft**
   - Short-lived access tokens (60 min)
   - Refresh token rotation
   - HTTPS-only transmission (HSTS)

3. **Session Fixation**
   - New token pair on each login/refresh
   - Old refresh tokens invalidated

4. **Information Disclosure**
   - Generic error messages ("Invalid username or password")
   - No user enumeration

5. **CSRF**
   - Bearer token authentication (not cookies)
   - Custom header required

### Threats Not Mitigated

1. **Compromised Client Secret**
   - Frontend stores tokens in localStorage
   - Vulnerable to XSS

2. **Server Memory Loss**
   - Refresh tokens stored in memory
   - Lost on server restart (users must re-login)

## Security Assumptions

1. **HTTPS Everywhere**
   - TLS termination at load balancer
   - HSTS enforced

2. **JWT Secret Security**
   - `JWT_SECRET_KEY` must be at least 32 characters
   - Rotated periodically
   - Never committed to version control

3. **Database Security**
   - SQLite database file protected by filesystem permissions
   - Passwords never stored in plaintext

4. **Network Security**
   - API not exposed directly to internet
   - Behind reverse proxy/WAF in production

## Migration Notes

### From Legacy to Enterprise

**Removed:**
- `backend/api/auth.py` (legacy auth module)
- `POST /setup/admin` endpoint
- `POST /login` endpoint (moved to `/api/v1/auth/login`)
- Duplicate password hashing
- Duplicate JWT generation
- `get_current_user` dependency (replaced by `get_security_context`)

**Added:**
- `POST /api/v1/auth/bootstrap` endpoint
- `POST /api/v1/auth/users` endpoint
- `PUT /api/v1/auth/password` endpoint
- `GET /api/v1/auth/me` endpoint
- `AuthenticationManager` class with all auth operations
- Refresh token rotation
- Audit logging for all auth events

**Frontend Changes:**
- Token field names: `access` → `access_token`, `refresh` → `refresh_token`
- Login URL: `/login` → `/api/v1/auth/login`
- Refresh URL: `/api/v1/auth/refresh` (already correct)

## Testing

All authentication tests pass (19 new tests in `tests/test_auth_consolidated.py`):

- Bootstrap flow
- Duplicate bootstrap prevention
- Weak password rejection
- Login success/failure
- Unknown user rejection
- Token refresh success/failure
- Logout flow
- User creation with auth
- Duplicate user prevention
- Password change success/failure
- Current user retrieval
- Full integration flow
- Password hash consistency
- JWT token lifecycle

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `JWT_SECRET_KEY` | Secret key for JWT signing | `dev-secret-key-change-in-production` |
| `ENVIRONMENT` | Environment mode (`development`/`production`) | `development` |
| `DEBUG` | Debug mode (legacy, use ENVIRONMENT instead) | `true` |

## References

- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
