from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import uuid

from backend.security.exceptions import InvalidTokenError

ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7
ALGORITHM = "HS256"


def create_token_pair(
    user_id: int,
    username: str,
    organization_id: int,
    role_ids: list,
    secret_key: str,
    access_token_expire: int = ACCESS_TOKEN_EXPIRE_MINUTES,
    refresh_token_expire: int = REFRESH_TOKEN_EXPIRE_DAYS,
) -> dict:
    now = datetime.utcnow()
    access_expires = now + timedelta(minutes=access_token_expire)
    refresh_expires = now + timedelta(days=refresh_token_expire)
    access_jti = str(uuid.uuid4())
    refresh_jti = str(uuid.uuid4())
    access_payload = {
        "sub": str(user_id),
        "username": username,
        "org_id": str(organization_id),
        "role_ids": role_ids,
        "jti": access_jti,
        "type": "access",
        "exp": access_expires,
        "iat": now,
    }
    refresh_payload = {
        "sub": str(user_id),
        "org_id": str(organization_id),
        "jti": refresh_jti,
        "type": "refresh",
        "exp": refresh_expires,
        "iat": now,
    }
    try:
        import jwt
        access_token = jwt.encode(access_payload, secret_key, algorithm=ALGORITHM)
        refresh_token = jwt.encode(refresh_payload, secret_key, algorithm=ALGORITHM)
    except ImportError:
        raise InvalidTokenError("PyJWT is not installed")
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
        "expires_in": access_token_expire * 60,
        "access_token_expires_at": access_expires.isoformat(),
        "refresh_token_expires_at": refresh_expires.isoformat(),
    }


def decode_token(token: str, secret_key: str) -> dict:
    try:
        import jwt
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        return payload
    except Exception as exc:
        raise InvalidTokenError(f"Token decode failed: {exc}")


def verify_token_type(payload: dict, expected_type: str) -> None:
    token_type = payload.get("type")
    if token_type != expected_type:
        raise InvalidTokenError(f"Invalid token type: expected {expected_type}, got {token_type}")
