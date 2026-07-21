from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import uuid

from backend.security.jwt import (
    create_token_pair,
    decode_token,
    verify_token_type,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
    ALGORITHM,
)
from backend.security.exceptions import AuthenticationError


class TokenService:
    def create_token_pair(
        self,
        user_id: int,
        username: str,
        organization_id: int,
        role_ids: list,
        secret_key: str,
    ) -> dict:
        return create_token_pair(
            user_id=user_id,
            username=username,
            organization_id=organization_id,
            role_ids=role_ids,
            secret_key=secret_key,
        )

    def decode_token(self, token: str, secret_key: str) -> dict:
        try:
            return decode_token(token, secret_key)
        except Exception as exc:
            raise AuthenticationError(f"Invalid token: {exc}")

    def verify_access_token(self, token: str, secret_key: str) -> dict:
        payload = self.decode_token(token, secret_key)
        verify_token_type(payload, "access")
        return payload

    def verify_refresh_token(self, token: str, secret_key: str) -> dict:
        payload = self.decode_token(token, secret_key)
        verify_token_type(payload, "refresh")
        return payload

    def generate_jti(self) -> str:
        return str(uuid.uuid4())
