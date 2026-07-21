from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from backend.database.models import User as DBUser
from backend.security.exceptions import AuthenticationError


class UserService:
    def get_user_by_id(self, db: Session, user_id: int) -> Optional[DBUser]:
        return db.query(DBUser).filter(DBUser.id == user_id).first()

    def get_user_by_username(self, db: Session, username: str) -> Optional[DBUser]:
        return db.query(DBUser).filter(DBUser.username == username).first()

    def create_user(self, db: Session, username: str, hashed_password: str) -> DBUser:
        existing = db.query(DBUser).filter(DBUser.username == username).first()
        if existing:
            raise AuthenticationError("Username already exists")
        user = DBUser(username=username, hashed_password=hashed_password)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def increment_failed_login(self, db: Session, user: DBUser) -> None:
        user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
        if user.failed_login_attempts >= 5:
            user.locked_until = datetime.utcnow() + timedelta(minutes=5)
        db.commit()

    def reset_failed_login(self, db: Session, user: DBUser) -> None:
        user.failed_login_attempts = 0
        user.locked_until = None
        db.commit()

    def is_locked(self, user: DBUser) -> bool:
        if user.locked_until and user.locked_until > datetime.utcnow():
            return True
        return False

    def update_password(self, db: Session, user: DBUser, hashed_password: str) -> None:
        user.hashed_password = hashed_password
        user.password_changed_at = datetime.utcnow()
        db.commit()

    def count_users(self, db: Session) -> int:
        return db.query(DBUser).count()
