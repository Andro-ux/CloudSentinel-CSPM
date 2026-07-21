from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from backend.database.models import Session as DBSession, RefreshToken as DBRefreshToken
from backend.security.models import Session as SessionModel


class SessionService:
    def create_session(
        self,
        db: Session,
        user_id: int,
        device: Optional[str] = None,
        browser: Optional[str] = None,
        ip_address: Optional[str] = None,
        expires_days: int = 7,
    ) -> SessionModel:
        session_id = str(__import__("uuid").uuid4())
        expires_at = datetime.utcnow() + timedelta(days=expires_days)
        db_session = DBSession(
            id=session_id,
            user_id=user_id,
            device=device,
            browser=browser,
            ip_address=ip_address,
            expires_at=expires_at,
        )
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        return SessionModel(
            id=db_session.id,
            user_id=db_session.user_id,
            organization_id=0,
            refresh_token_jti="",
            expires_at=db_session.expires_at,
            created_at=db_session.created_at,
            metadata={
                "device": db_session.device,
                "browser": db_session.browser,
                "ip_address": db_session.ip_address,
            },
        )

    def get_session(self, db: Session, session_id: str) -> Optional[DBSession]:
        return db.query(DBSession).filter(DBSession.id == session_id).first()

    def get_user_sessions(self, db: Session, user_id: int) -> List[DBSession]:
        return (
            db.query(DBSession)
            .filter(DBSession.user_id == user_id, DBSession.revoked == False)
            .all()
        )

    def revoke_session(self, db: Session, session_id: str) -> bool:
        session = db.query(DBSession).filter(DBSession.id == session_id).first()
        if not session:
            return False
        session.revoked = True
        db.commit()
        return True

    def revoke_all_sessions(self, db: Session, user_id: int) -> int:
        sessions = db.query(DBSession).filter(
            DBSession.user_id == user_id, DBSession.revoked == False
        ).all()
        count = 0
        for session in sessions:
            session.revoked = True
            count += 1
        db.commit()
        return count

    def update_last_used(self, db: Session, session_id: str) -> None:
        session = db.query(DBSession).filter(DBSession.id == session_id).first()
        if session:
            session.last_used = datetime.utcnow()
            db.commit()

    def create_refresh_token(
        self,
        db: Session,
        jti: str,
        user_id: int,
        device: Optional[str] = None,
        ip_address: Optional[str] = None,
        expires_days: int = 7,
    ) -> DBRefreshToken:
        expires_at = datetime.utcnow() + timedelta(days=expires_days)
        token = DBRefreshToken(
            jti=jti,
            user_id=user_id,
            device=device,
            ip_address=ip_address,
            expires_at=expires_at,
        )
        db.add(token)
        db.commit()
        db.refresh(token)
        return token

    def get_refresh_token(self, db: Session, jti: str) -> Optional[DBRefreshToken]:
        return db.query(DBRefreshToken).filter(DBRefreshToken.jti == jti).first()

    def revoke_refresh_token(self, db: Session, jti: str) -> bool:
        token = db.query(DBRefreshToken).filter(DBRefreshToken.jti == jti).first()
        if not token:
            return False
        token.revoked = True
        db.commit()
        return True

    def revoke_all_refresh_tokens(self, db: Session, user_id: int) -> int:
        tokens = db.query(DBRefreshToken).filter(
            DBRefreshToken.user_id == user_id, DBRefreshToken.revoked == False
        ).all()
        count = 0
        for token in tokens:
            token.revoked = True
            count += 1
        db.commit()
        return count

    def update_refresh_token_last_used(self, db: Session, jti: str) -> None:
        token = db.query(DBRefreshToken).filter(DBRefreshToken.jti == jti).first()
        if token:
            token.last_used = datetime.utcnow()
            db.commit()
