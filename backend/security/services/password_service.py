from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from backend.security.hashing import (
    hash_password,
    verify_password,
    validate_password_strength,
)
from backend.security.exceptions import AuthenticationError


class PasswordService:
    def hash(self, password: str) -> str:
        return hash_password(password)

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        return verify_password(plain_password, hashed_password)

    def validate_strength(self, password: str) -> None:
        try:
            validate_password_strength(password)
        except ValueError as exc:
            raise AuthenticationError(str(exc))

    def check_current_password(
        self, db: Session, user_id: int, current_password: str
    ) -> bool:
        from backend.database.models import User as DBUser
        user = db.query(DBUser).filter(DBUser.id == user_id).first()
        if not user:
            return False
        return self.verify(current_password, user.hashed_password)
