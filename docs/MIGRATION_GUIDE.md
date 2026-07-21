# CloudSentinel Authentication Migration Guide

## Overview

This guide documents the migration from legacy authentication to the enterprise security platform in Sprint 4.6.

## What Changed

### Before (Legacy)

- `backend/api/auth.py` - Duplicate hashing/JWT implementation
- `backend/api/routes.py` - Mixed auth and business endpoints
- In-memory refresh tokens (lost on restart)
- No session persistence
- No audit trail
- No account lockout
- No bootstrap token protection

### After (Enterprise)

- `backend/security/services/` - Service-oriented architecture
- `backend/api/routers/auth.py` - Single auth router
- Database-backed sessions and refresh tokens
- Persistent audit trail in `audit_events` table
- Account lockout after 5 failed attempts
- BOOTSTRAP_TOKEN protected bootstrap endpoint
- Clean separation: Authentication ≠ Authorization

## Database Migrations

### New Tables

```sql
-- Sessions table
CREATE TABLE sessions (
    id VARCHAR PRIMARY KEY,
    user_id INTEGER NOT NULL,
    device VARCHAR,
    browser VARCHAR,
    ip_address VARCHAR,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME,
    last_used DATETIME DEFAULT CURRENT_TIMESTAMP,
    revoked BOOLEAN DEFAULT 0
);

-- Refresh tokens table
CREATE TABLE refresh_tokens (
    jti VARCHAR PRIMARY KEY,
    user_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME,
    revoked BOOLEAN DEFAULT 0,
    device VARCHAR,
    ip_address VARCHAR,
    last_used DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Audit events table
CREATE TABLE audit_events (
    id VARCHAR PRIMARY KEY,
    event_type VARCHAR NOT NULL,
    actor_type VARCHAR NOT NULL,
    actor_id VARCHAR NOT NULL,
    organization_id INTEGER DEFAULT 0,
    resource_type VARCHAR NOT NULL,
    resource_id VARCHAR NOT NULL,
    action VARCHAR NOT NULL,
    status VARCHAR NOT NULL,
    ip_address VARCHAR,
    user_agent VARCHAR,
    request_id VARCHAR,
    severity VARCHAR DEFAULT 'info',
    details JSON DEFAULT '{}',
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Modified Tables

```sql
-- Add lockout fields to users
ALTER TABLE users ADD COLUMN failed_login_attempts INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN locked_until DATETIME;
ALTER TABLE users ADD COLUMN password_changed_at DATETIME DEFAULT CURRENT_TIMESTAMP;
```

## API Changes

### New Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/bootstrap` | POST | One-time admin creation (requires BOOTSTRAP_TOKEN) |
| `/api/v1/auth/me` | GET | Current user info |
| `/api/v1/auth/users` | POST | Create new user (authenticated) |
| `/api/v1/auth/password` | PUT | Change password (authenticated) |
| `/api/v1/auth/sessions` | GET | List active sessions |
| `/api/v1/auth/sessions/{id}` | DELETE | Revoke specific session |
| `/api/v1/auth/sessions` | DELETE | Revoke all sessions |

### Changed Endpoints

| Endpoint | Change |
|----------|--------|
| `/api/v1/auth/login` | Now uses service layer, returns sessions |
| `/api/v1/auth/refresh` | Now validates against database |
| `/api/v1/auth/logout` | Now revokes database refresh token |

### Removed Endpoints

| Endpoint | Reason |
|----------|--------|
| `/setup/admin` | Replaced by `/api/v1/auth/bootstrap` |
| `/login` | Moved to `/api/v1/auth/login` |
| `/users` | Moved to `/api/v1/auth/users` |
| `/users/me` | Moved to `/api/v1/auth/me` |
| `/users/me/password` | Moved to `/api/v1/auth/password` |

## Frontend Changes

### Token Format

The response format remains identical:
```json
{
  "success": true,
  "data": {
    "access_token": "...",
    "refresh_token": "...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "user": { ... }
  }
}
```

### Bootstrap Authentication

The bootstrap endpoint now requires a `BOOTSTRAP_TOKEN` via Authorization header:
```javascript
const response = await fetch('/api/v1/auth/bootstrap?username=admin&password=secure123', {
  headers: {
    'Authorization': `Bearer ${process.env.BOOTSTRAP_TOKEN}`
  }
});
```

## Environment Variables

### New Required Variable

```bash
BOOTSTRAP_TOKEN=your-secure-bootstrap-token-here
```

Generate with:
```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

## Rollback Plan

If issues arise:

1. Revert `backend/api/routers/auth.py` to previous version
2. Keep new database tables (they don't affect existing functionality)
3. Frontend contracts remain unchanged

## Verification

After migration:

```bash
# Backend tests
python -m pytest tests/ -q

# Frontend tests
npm test

# Build
npm run build

# Expected: All tests pass, build succeeds
```

## Support

For issues:
1. Check `audit_events` table for authentication failures
2. Verify `BOOTSTRAP_TOKEN` environment variable
3. Ensure database migrations applied
4. Check `JWT_SECRET_KEY` is set and at least 32 characters
