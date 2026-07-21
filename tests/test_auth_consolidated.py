import sys
sys.path.insert(0, r'C:\Users\vinit\Desktop\CloudSentinel_phase3\CloudSentinel')

import pytest
from fastapi.testclient import TestClient

from backend.api.app import create_app
from backend.security.hashing import hash_password, verify_password
from backend.security.jwt import create_token_pair, decode_token
from backend.security.authentication import AuthenticationManager
from backend.config import settings
from backend.database.session import SessionLocal, engine, Base


@pytest.fixture
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    import os
    os.environ["BOOTSTRAP_TOKEN"] = "test-bootstrap-token"
    app = create_app()
    return TestClient(app)


class TestAuthBootstrap:
    def test_bootstrap_creates_first_admin(self, client):
        response = client.post("/api/v1/auth/bootstrap?username=admin&password=SuperSecure123!", headers={"Authorization": "Bearer test-bootstrap-token"})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]
        assert data["data"]["user"]["username"] == "admin"

    def test_bootstrap_prevents_duplicate(self, client):
        client.post("/api/v1/auth/bootstrap?username=admin1&password=SuperSecure123!", headers={"Authorization": "Bearer test-bootstrap-token"})
        response = client.post("/api/v1/auth/bootstrap?username=admin2&password=SuperSecure123!", headers={"Authorization": "Bearer test-bootstrap-token"})
        assert response.status_code == 403

    def test_bootstrap_rejects_weak_password(self, client):
        response = client.post("/api/v1/auth/bootstrap?username=admin&password=short", headers={"Authorization": "Bearer test-bootstrap-token"})
        assert response.status_code in [400, 403, 422]


class TestAuthLogin:
    def test_login_success(self, client):
        client.post("/api/v1/auth/bootstrap?username=admin&password=SuperSecure123!", headers={"Authorization": "Bearer test-bootstrap-token"})
        response = client.post("/api/v1/auth/login", data={"username": "admin", "password": "SuperSecure123!"})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]
        assert data["data"]["token_type"] == "Bearer"
        assert data["data"]["user"]["username"] == "admin"

    def test_login_wrong_password(self, client):
        client.post("/api/v1/auth/bootstrap?username=admin&password=SuperSecure123!", headers={"Authorization": "Bearer test-bootstrap-token"})
        response = client.post("/api/v1/auth/login", data={"username": "admin", "password": "wrong"})
        assert response.status_code == 401

    def test_login_unknown_user(self, client):
        response = client.post("/api/v1/auth/login", data={"username": "nonexistent", "password": "SuperSecure123!"})
        assert response.status_code == 401


class TestAuthRefresh:
    def test_refresh_token_success(self, client):
        bootstrap_response = client.post("/api/v1/auth/bootstrap?username=admin&password=SuperSecure123!", headers={"Authorization": "Bearer test-bootstrap-token"})
        tokens = bootstrap_response.json()["data"]
        response = client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]

    def test_refresh_invalid_token(self, client):
        response = client.post("/api/v1/auth/refresh", json={"refresh_token": "invalid"})
        assert response.status_code == 401


class TestAuthLogout:
    def test_logout_success(self, client):
        bootstrap_response = client.post("/api/v1/auth/bootstrap?username=admin&password=SuperSecure123!", headers={"Authorization": "Bearer test-bootstrap-token"})
        tokens = bootstrap_response.json()["data"]
        response = client.post("/api/v1/auth/logout", json={"refresh_token": tokens["refresh_token"]})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestAuthUsers:
    def test_create_user_requires_auth(self, client):
        response = client.post("/api/v1/auth/users?username=newuser&password=SuperSecure123!")
        assert response.status_code == 401

    def test_create_user_success(self, client):
        bootstrap_response = client.post("/api/v1/auth/bootstrap?username=admin&password=SuperSecure123!", headers={"Authorization": "Bearer test-bootstrap-token"})
        tokens = bootstrap_response.json()["data"]
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        response = client.post("/api/v1/auth/users?username=newuser&password=SuperSecure123!", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["username"] == "newuser"

    def test_create_duplicate_user_fails(self, client):
        bootstrap_response = client.post("/api/v1/auth/bootstrap?username=admin&password=SuperSecure123!", headers={"Authorization": "Bearer test-bootstrap-token"})
        tokens = bootstrap_response.json()["data"]
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        client.post("/api/v1/auth/users?username=duplicate&password=SuperSecure123!", headers=headers)
        response = client.post("/api/v1/auth/users?username=duplicate&password=SuperSecure123!", headers=headers)
        assert response.status_code == 400


class TestAuthPassword:
    def test_change_password_success(self, client):
        bootstrap_response = client.post("/api/v1/auth/bootstrap?username=admin&password=SuperSecure123!", headers={"Authorization": "Bearer test-bootstrap-token"})
        tokens = bootstrap_response.json()["data"]
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        response = client.put(
            "/api/v1/auth/password",
            json={"current_password": "SuperSecure123!", "new_password": "NewSecure123!"},
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_change_password_wrong_current(self, client):
        bootstrap_response = client.post("/api/v1/auth/bootstrap?username=admin&password=SuperSecure123!", headers={"Authorization": "Bearer test-bootstrap-token"})
        tokens = bootstrap_response.json()["data"]
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        response = client.put(
            "/api/v1/auth/password",
            json={"current_password": "wrong", "new_password": "NewSecure123!"},
            headers=headers,
        )
        assert response.status_code == 400


class TestAuthMe:
    def test_get_current_user(self, client):
        bootstrap_response = client.post("/api/v1/auth/bootstrap?username=admin&password=SuperSecure123!", headers={"Authorization": "Bearer test-bootstrap-token"})
        tokens = bootstrap_response.json()["data"]
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["username"] == "admin"

    def test_get_current_user_unauthorized(self, client):
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401


class TestAuthIntegration:
    def test_full_auth_flow(self, client):
        bootstrap = client.post("/api/v1/auth/bootstrap?username=admin&password=SuperSecure123!", headers={"Authorization": "Bearer test-bootstrap-token"})
        assert bootstrap.status_code == 200

        login = client.post("/api/v1/auth/login", data={"username": "admin", "password": "SuperSecure123!"})
        assert login.status_code == 200
        tokens = login.json()["data"]

        me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {tokens['access_token']}"})
        assert me.status_code == 200

        refresh = client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
        assert refresh.status_code == 200

        logout = client.post("/api/v1/auth/logout", json={"refresh_token": tokens["refresh_token"]})
        assert logout.status_code == 200

    def test_password_hash_consistency(self):
        password = "TestPassword123!"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True
        assert verify_password("wrong", hashed) is False

    def test_jwt_token_lifecycle(self):
        tokens = create_token_pair(1, "testuser", 1, ["analyst"], "test-secret-key")
        payload = decode_token(tokens["access_token"], "test-secret-key")
        assert payload["sub"] == "1"
        assert payload["type"] == "access"
        assert payload["username"] == "testuser"
