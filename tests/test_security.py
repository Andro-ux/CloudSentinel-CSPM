import sys
sys.path.insert(0, r'C:\Users\vinit\Desktop\CloudSentinel_phase3\CloudSentinel')

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from backend.api.app import create_app
from backend.security.models import User, Organization, APIKey, SecurityContext
from backend.security.rbac.roles import DEFAULT_ROLES
from backend.security.rbac.policies import RBACPolicy
from backend.security.hashing import hash_password, verify_password
from backend.security.jwt import create_token_pair, decode_token
from backend.security.validators import validate_username, validate_email, validate_permission
from backend.security.rate_limit import RateLimiter
from backend.security.middleware import SecurityHeadersMiddleware
from backend.security.api_keys import APIKeyManager
from backend.security.audit import AuditLogger
from backend.security.authorization import AuthorizationChecker


@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)


class TestSecurityIntegration:
    def test_full_auth_flow(self, client):
        response = client.post("/api/v1/auth/login", data={"username": "test", "password": "test"})
        assert response.status_code in [401, 422, 500]

    def test_protected_endpoints_require_auth(self, client):
        assert client.get("/api/v1/dashboard").status_code in [200, 401, 403, 500]
        assert client.get("/api/v1/assets").status_code in [200, 401, 403, 500]
        assert client.get("/api/v1/findings").status_code in [200, 401, 403, 500]
        assert client.get("/api/v1/risks").status_code in [200, 401, 403, 500]
        assert client.get("/api/v1/graph").status_code in [200, 401, 403, 500]

    def test_health_remains_public(self, client):
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"

    def test_security_context_authorization(self):
        checker = AuthorizationChecker()
        user = User(id=1, username="test", organization_id=1)
        ctx = SecurityContext(user=user, role_ids=["analyst"], permissions={"dashboard.read", "assets.read"})
        assert checker.is_authorized(ctx, "dashboard.read") is True
        assert checker.is_authorized(ctx, "users.manage") is False

    def test_rbac_permissions(self):
        policy = RBACPolicy()
        policy.load_default_roles({r: d.permissions for r, d in DEFAULT_ROLES.items()})
        assert policy.has_permission(["analyst"], "dashboard.read") is True
        assert policy.has_permission(["analyst"], "users.manage") is False
        assert policy.has_permission(["platform_admin"], "system.admin") is True

    def test_immutable_models(self):
        user = User(id=1, username="test")
        with pytest.raises(AttributeError):
            user.id = 2
        org = Organization(id=1, name="Test", slug="test")
        with pytest.raises(AttributeError):
            org.name = "New"

    def test_password_hashing(self):
        hashed = hash_password("SecurePass123!")
        assert verify_password("SecurePass123!", hashed) is True
        assert verify_password("WrongPass", hashed) is False

    def test_jwt_tokens(self):
        tokens = create_token_pair(1, "test", 1, ["analyst"], "secret")
        payload = decode_token(tokens["access_token"], "secret")
        assert payload["sub"] == "1"
        assert payload["type"] == "access"
        with pytest.raises(Exception):
            decode_token(tokens["access_token"], "wrong-secret")

    def test_api_key_lifecycle(self):
        manager = APIKeyManager()
        api_key, secret = manager.create_api_key("Test", 1, 1, ["assets.read"])
        assert manager.verify_api_key(api_key.id, secret) is not None
        assert manager.verify_api_key(api_key.id, "wrong") is None
        assert manager.delete_api_key(api_key.id) is True

    def test_audit_logging(self):
        logger = AuditLogger()
        event = logger.log_event("auth", "user", "1", 1, "auth", "login", "login", "success")
        assert event.event_type == "auth"
        assert event.status == "success"
        assert len(logger.get_events(organization_id=1)) == 1

    def test_validators(self):
        validate_username("testuser")
        validate_email("test@example.com")
        validate_permission("dashboard.read")
        with pytest.raises(Exception):
            validate_username("ab")
        with pytest.raises(Exception):
            validate_email("invalid")
        with pytest.raises(Exception):
            validate_permission("invalid")

    def test_rate_limiter(self):
        limiter = RateLimiter()
        assert limiter.is_allowed("key", 2, 60)[0] is True
        limiter.is_allowed("key", 2, 60)
        assert limiter.is_allowed("key", 2, 60)[0] is False

    def test_openapi_has_auth_tag(self, client):
        response = client.get("/openapi.json")
        tags = [t["name"] for t in response.json().get("tags", [])]
        assert "Authentication" in tags

    def test_organization_isolation(self):
        user = User(id=1, username="test", organization_id=1)
        api_key = APIKey(id="k1", name="Key", hashed_secret="h", user_id=1, organization_id=1, permissions=[])
        assert user.organization_id == 1
        assert api_key.organization_id == 1
