import sys
sys.path.insert(0, r'C:\Users\vinit\Desktop\CloudSentinel_phase3\CloudSentinel')

import pytest
import time
from fastapi.testclient import TestClient
from backend.api.app import create_app
from backend.security.hashing import hash_password, verify_password
from backend.security.jwt import create_token_pair, decode_token
from backend.security.authentication import AuthenticationManager
from backend.security.exceptions import AuthenticationError
from backend.security.services.user_service import UserService
from backend.security.services.password_service import PasswordService
from backend.security.services.token_service import TokenService
from backend.security.services.session_service import SessionService
from backend.security.services.audit_service import AuditService
from backend.security.services.bootstrap_service import BootstrapService
from backend.config import settings
from backend.database.session import SessionLocal, engine, Base


@pytest.fixture
def db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    import os
    os.environ["BOOTSTRAP_TOKEN"] = "secret-token"
    app = create_app()
    return TestClient(app)


class TestUserService:
    def test_create_and_get_user(self, db):
        service = UserService()
        user = service.create_user(db, "testuser", "hashed")
        assert user.id is not None
        assert user.username == "testuser"
        fetched = service.get_user_by_username(db, "testuser")
        assert fetched.id == user.id

    def test_failed_login_lockout(self, db):
        service = UserService()
        user = service.create_user(db, "lockuser", hash_password("password"))
        for _ in range(5):
            service.increment_failed_login(db, user)
        assert service.is_locked(user) is True

    def test_reset_failed_login(self, db):
        service = UserService()
        user = service.create_user(db, "resetuser", hash_password("password"))
        service.increment_failed_login(db, user)
        service.reset_failed_login(db, user)
        assert user.failed_login_attempts == 0


class TestPasswordService:
    def test_hash_and_verify(self):
        service = PasswordService()
        hashed = service.hash("SecurePass123!")
        assert service.verify("SecurePass123!", hashed) is True
        assert service.verify("WrongPass", hashed) is False

    def test_validate_weak_password(self):
        service = PasswordService()
        with pytest.raises(Exception):
            service.validate_strength("short")

    def test_check_current_password(self, db):
        service = PasswordService()
        user = UserService().create_user(db, "pwuser", service.hash("password"))
        assert service.check_current_password(db, user.id, "password") is True
        assert service.check_current_password(db, user.id, "wrong") is False


class TestTokenService:
    def test_create_and_verify_token_pair(self):
        service = TokenService()
        tokens = service.create_token_pair(1, "user", 1, ["analyst"], "secret")
        assert "access_token" in tokens
        assert "refresh_token" in tokens

        access_payload = service.verify_access_token(tokens["access_token"], "secret")
        assert access_payload["sub"] == "1"
        assert access_payload["type"] == "access"

        refresh_payload = service.verify_refresh_token(tokens["refresh_token"], "secret")
        assert refresh_payload["type"] == "refresh"


class TestSessionService:
    def test_create_and_get_session(self, db):
        service = SessionService()
        session = service.create_session(db, user_id=1, device="test", ip_address="127.0.0.1")
        assert session.id is not None
        fetched = service.get_session(db, session.id)
        assert fetched.user_id == 1

    def test_revoke_session(self, db):
        service = SessionService()
        session = service.create_session(db, user_id=1)
        assert service.revoke_session(db, session.id) is True
        assert service.revoke_session(db, "nonexistent") is False

    def test_create_and_revoke_refresh_token(self, db):
        service = SessionService()
        token = service.create_refresh_token(db, jti="jti1", user_id=1)
        assert token.jti == "jti1"
        assert service.revoke_refresh_token(db, "jti1") is True


class TestAuditService:
    def test_log_and_get_events(self, db):
        service = AuditService()
        event = service.log(
            db,
            event_type="authentication",
            actor_type="user",
            actor_id="1",
            organization_id=1,
            resource_type="auth",
            resource_id="login",
            action="login",
            status="success",
            ip_address="127.0.0.1",
        )
        assert event.id is not None
        events = service.get_events(db, organization_id=1)
        assert len(events) == 1


class TestBootstrapService:
    def test_bootstrap_creates_admin(self, db):
        service = BootstrapService(
            user_service=UserService(),
            password_service=PasswordService(),
            token_service=TokenService(),
            session_service=SessionService(),
            audit_service=AuditService(),
        )
        result = service.bootstrap(
            db=db,
            username="admin",
            password="SecurePass123!",
            bootstrap_token="secret-token",
            expected_bootstrap_token="secret-token",
            secret_key="test-secret",
        )
        assert result["user"].username == "admin"
        assert result["user"].role_ids == ["platform_admin"]

    def test_bootstrap_prevents_duplicate(self, db):
        service = BootstrapService(
            user_service=UserService(),
            password_service=PasswordService(),
            token_service=TokenService(),
            session_service=SessionService(),
            audit_service=AuditService(),
        )
        service.bootstrap(
            db=db,
            username="admin1",
            password="SecurePass123!",
            bootstrap_token="secret-token",
            expected_bootstrap_token="secret-token",
            secret_key="test-secret",
        )
        with pytest.raises(AuthenticationError):
            service.bootstrap(
                db=db,
                username="admin2",
                password="SecurePass123!",
                bootstrap_token="secret-token",
                expected_bootstrap_token="secret-token",
                secret_key="test-secret",
            )


class TestAuthIntegration:
    def test_full_auth_flow(self, client):
        bootstrap = client.post("/api/v1/auth/bootstrap?username=admin&password=SecurePass123!", headers={"Authorization": "Bearer secret-token"})
        assert bootstrap.status_code == 200

        login = client.post("/api/v1/auth/login", data={"username": "admin", "password": "SecurePass123!"})
        assert login.status_code == 200
        tokens = login.json()["data"]

        me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {tokens['access_token']}"})
        assert me.status_code == 200

        refresh = client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
        assert refresh.status_code == 200

        logout = client.post("/api/v1/auth/logout", json={"refresh_token": tokens["refresh_token"]})
        assert logout.status_code == 200
