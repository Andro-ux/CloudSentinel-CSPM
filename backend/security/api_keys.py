from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from backend.security.models import APIKey
from backend.security.hashing import hash_api_key_secret, generate_api_key_secret
from backend.security.exceptions import InvalidAPIKeyError


class APIKeyManager:
    def __init__(self):
        self._api_keys: Dict[str, APIKey] = {}

    def create_api_key(
        self,
        name: str,
        user_id: int,
        organization_id: int,
        permissions: List[str],
        expires_at: Optional[datetime] = None,
    ) -> Tuple[APIKey, str]:
        secret = generate_api_key_secret()
        hashed_secret = hash_api_key_secret(secret)
        api_key_id = str(__import__('uuid').uuid4())
        api_key = APIKey(
            id=api_key_id,
            name=name,
            hashed_secret=hashed_secret,
            user_id=user_id,
            organization_id=organization_id,
            permissions=permissions,
            expires_at=expires_at,
            created_at=datetime.utcnow(),
        )
        self._api_keys[api_key_id] = api_key
        return api_key, secret

    def verify_api_key(self, api_key_id: str, secret: str) -> Optional[APIKey]:
        api_key = self._api_keys.get(api_key_id)
        if not api_key:
            return None
        if api_key.expires_at and api_key.expires_at < datetime.utcnow():
            return None
        if api_key.hashed_secret != hash_api_key_secret(secret):
            return None
        return api_key

    def get_api_key(self, api_key_id: str) -> Optional[APIKey]:
        return self._api_keys.get(api_key_id)

    def delete_api_key(self, api_key_id: str) -> bool:
        if api_key_id in self._api_keys:
            del self._api_keys[api_key_id]
            return True
        return False

    def list_api_keys(self, organization_id: int) -> List[APIKey]:
        return [key for key in self._api_keys.values() if key.organization_id == organization_id]


api_key_manager = APIKeyManager()
