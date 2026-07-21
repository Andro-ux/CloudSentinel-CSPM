# CloudSentinel Session Management

## Overview

CloudSentinel implements persistent session management with database-backed sessions and refresh tokens. Sessions survive server restarts and support device management, revocation, and audit logging.

## Session Model

Each session represents a authenticated device/browser combination:

```python
class Session(Base):
    id: str                    # UUID primary key
    user_id: int               # Foreign key to users
    device: Optional[str]      # Device identifier
    browser: Optional[str]     # Browser user agent
    ip_address: Optional[str]  # Login IP address
    created_at: datetime       # Session creation time
    expires_at: Optional[datetime]  # Session expiration
    last_used: datetime        # Last activity timestamp
    revoked: bool              # Soft delete flag
```

## Refresh Token Model

Refresh tokens are stored persistently and rotated on each use:

```python
class RefreshToken(Base):
    jti: str                   # JWT ID (primary key)
    user_id: int               # Foreign key to users
    created_at: datetime       # Token creation time
    expires_at: Optional[datetime]  # Token expiration
    revoked: bool              # Revocation flag
    device: Optional[str]      # Device identifier
    ip_address: Optional[str]  # IP address
    last_used: datetime        # Last refresh timestamp
```

## Session Lifecycle

### Creation

Sessions are created during:
1. Bootstrap (first administrator)
2. Login
3. Token refresh (optional - for tracking)

### Expiration

- Sessions expire after 7 days by default
- Refresh tokens expire after 7 days
- Expired sessions are not automatically deleted (audit trail)

### Revocation

Sessions can be revoked:
1. User logout (specific session)
2. Revoke all sessions (security incident)
3. Admin action
4. Password change

## API Endpoints

### GET /api/v1/auth/sessions

List all active sessions for current user.

**Headers**: `Authorization: Bearer <access_token>`

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "device": "Chrome on Windows",
      "browser": "Mozilla/5.0...",
      "ip_address": "192.168.1.1",
      "created_at": "2024-01-01T00:00:00Z",
      "last_used": "2024-01-01T12:00:00Z",
      "expires_at": "2024-01-08T00:00:00Z"
    }
  ]
}
```

### DELETE /api/v1/auth/sessions/{id}

Revoke a specific session.

**Headers**: `Authorization: Bearer <access_token>`

**Response**:
```json
{
  "success": true,
  "data": {
    "message": "Session revoked"
  }
}
```

### DELETE /api/v1/auth/sessions

Revoke all sessions for current user.

**Headers**: `Authorization: Bearer <access_token>`

**Response**:
```json
{
  "success": true,
  "data": {
    "message": "Revoked 3 sessions"
  }
}
```

## Refresh Token Rotation

Every refresh operation:
1. Validates old refresh token
2. Revokes old refresh token immediately
3. Creates new access token
4. Creates new refresh token
5. Returns both new tokens

This prevents refresh token replay attacks.

## Security Considerations

1. **Session Fixation**: New session ID on every login
2. **Token Replay**: Refresh tokens are single-use (rotated)
3. **Session Hijacking**: IP and device tracking
4. **Audit Trail**: All session events logged
5. **Concurrent Sessions**: Users can have multiple active sessions

## Monitoring

Track these metrics:
- `active_sessions` - Current active session count
- `token_refreshes` - Refresh token usage count
- `revoked_sessions` - Session revocation count
- `concurrent_sessions_per_user` - Average concurrent sessions
