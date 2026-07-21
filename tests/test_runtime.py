import sys
sys.path.insert(0, r'C:\Users\vinit\Desktop\CloudSentinel_phase3\CloudSentinel')

import pytest
from datetime import datetime
from fastapi.testclient import TestClient

from backend.api.app import create_app
from backend.runtime.configuration import RuntimeConfiguration, Environment, LogFormat, JWTConfig, DatabaseConfig, LoggingConfig
from backend.runtime.health import HealthService, HealthStatus, HealthResponse
from backend.runtime.readiness import ReadinessStatus, ReadinessService
from backend.runtime.metrics import MetricsCollector, MetricsSnapshot
from backend.runtime.lifecycle import LifecycleManager, LifecycleEventType
from backend.runtime.logging import configure_logging, get_logger
from backend.runtime.validation import ConfigurationValidator
from backend.runtime.manager import RuntimeManager


@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)


class TestRuntimeConfiguration:
    def test_default_configuration(self):
        config = RuntimeConfiguration()
        assert config.environment == Environment.DEVELOPMENT
        assert config.debug is False
        assert config.api_version == "v1"
        assert config.app_version == "0.11.0"

    def test_configuration_immutable(self):
        config = RuntimeConfiguration()
        with pytest.raises(AttributeError):
            config.environment = Environment.PRODUCTION

    def test_database_config_defaults(self):
        config = RuntimeConfiguration()
        assert config.database.url == "sqlite:///cloudsentinel.db"
        assert config.database.pool_size == 5

    def test_jwt_config_defaults(self):
        config = RuntimeConfiguration()
        assert config.jwt.secret_key == "dev-secret-key-change-in-production"
        assert config.jwt.algorithm == "HS256"

    def test_logging_config_defaults(self):
        config = RuntimeConfiguration()
        assert config.logging.level == "INFO"
        assert config.logging.format == LogFormat.TEXT

    def test_environment_override(self):
        config = RuntimeConfiguration(environment=Environment.PRODUCTION)
        assert config.environment == Environment.PRODUCTION

    def test_metadata_populated(self):
        config = RuntimeConfiguration()
        assert "loaded_at" in config.metadata
        assert config.metadata["source"] == "default"


class TestHealthService:
    def test_healthy_service(self):
        config = RuntimeConfiguration()
        service = HealthService(config)
        service.register_check("test", lambda: {"status": "healthy", "message": "OK"})
        response = service.check()
        assert response.status == HealthStatus.HEALTHY
        assert response.is_healthy is True

    def test_unhealthy_service(self):
        config = RuntimeConfiguration()
        service = HealthService(config)
        service.register_check("test", lambda: {"status": "unhealthy", "message": "Failed"})
        response = service.check()
        assert response.status == HealthStatus.UNHEALTHY
        assert response.is_unhealthy is True

    def test_degraded_service(self):
        config = RuntimeConfiguration()
        service = HealthService(config)
        service.register_check("test1", lambda: {"status": "healthy"})
        service.register_check("test2", lambda: {"status": "degraded"})
        response = service.check()
        assert response.status == HealthStatus.DEGRADED
        assert response.is_degraded is True

    def test_mixed_checks(self):
        config = RuntimeConfiguration()
        service = HealthService(config)
        service.register_check("db", lambda: {"status": "healthy"})
        service.register_check("cache", lambda: {"status": "unhealthy", "message": "timeout"})
        response = service.check()
        assert response.status == HealthStatus.UNHEALTHY
        assert len(response.checks) == 2

    def test_check_handles_exception(self):
        config = RuntimeConfiguration()
        service = HealthService(config)
        service.register_check("failing", lambda: (_ for _ in ()).throw(Exception("boom")))
        response = service.check()
        assert response.status == HealthStatus.UNHEALTHY

    def test_health_response_to_dict(self):
        config = RuntimeConfiguration()
        service = HealthService(config)
        service.register_check("test", lambda: True)
        response = service.check()
        data = response.to_dict()
        assert "status" in data
        assert "checks" in data
        assert "metadata" in data


class TestMetricsCollector:
    def test_record_metric(self):
        collector = MetricsCollector()
        collector.record("test_metric", 42.0)
        assert collector.get_latest("test_metric") == 42.0

    def test_increment_metric(self):
        collector = MetricsCollector()
        collector.increment("counter", 1.0)
        collector.increment("counter", 2.0)
        assert collector.get_latest("counter") == 3.0

    def test_metric_history(self):
        collector = MetricsCollector()
        collector.record("metric", 1.0)
        collector.record("metric", 2.0)
        collector.record("metric", 3.0)
        history = collector.get_history("metric")
        assert len(history) == 3
        assert history[0].value == 1.0
        assert history[2].value == 3.0

    def test_metric_labels(self):
        collector = MetricsCollector()
        collector.record("api_requests", 1.0, labels={"method": "GET", "endpoint": "/health"})
        history = collector.get_history("api_requests")
        assert history[0].labels["method"] == "GET"

    def test_metric_unit(self):
        collector = MetricsCollector()
        collector.record("latency", 0.5, unit="seconds")
        history = collector.get_history("latency")
        assert history[0].unit == "seconds"

    def test_snapshot(self):
        collector = MetricsCollector()
        collector.increment("scan_count", 5)
        collector.increment("api_requests", 100)
        snapshot = collector.snapshot()
        assert snapshot.scan_count == 5
        assert snapshot.api_requests == 100

    def test_reset(self):
        collector = MetricsCollector()
        collector.increment("metric", 10)
        collector.reset()
        assert collector.get_latest("metric") == 0.0
        assert len(collector.get_history("metric")) == 0


class TestLifecycleManager:
    def test_startup(self):
        config = RuntimeConfiguration()
        manager = LifecycleManager(config)
        manager.startup()
        assert manager.is_started is True

    def test_double_startup(self):
        config = RuntimeConfiguration()
        manager = LifecycleManager(config)
        manager.startup()
        manager.startup()
        assert manager.is_started is True

    def test_shutdown(self):
        config = RuntimeConfiguration()
        manager = LifecycleManager(config)
        manager.startup()
        manager.shutdown()
        assert manager.is_shutdown is True

    def test_events_recorded(self):
        config = RuntimeConfiguration()
        manager = LifecycleManager(config)
        manager.startup()
        manager.shutdown()
        events = manager.events
        assert len(events) == 4  # 2 startup + 2 shutdown

    def test_event_types(self):
        config = RuntimeConfiguration()
        manager = LifecycleManager(config)
        manager.startup()
        event_types = [e.event_type for e in manager.events]
        assert LifecycleEventType.STARTUP in event_types

    def test_reload(self):
        config = RuntimeConfiguration()
        manager = LifecycleManager(config)
        manager.startup()
        manager.reload()
        assert manager.is_started is True

    def test_handler_registration(self):
        config = RuntimeConfiguration()
        manager = LifecycleManager(config)
        called = []
        def handler(event):
            called.append(event)
        manager.register_handler(LifecycleEventType.STARTUP, handler)
        manager.startup()
        assert len(called) >= 1


class TestRuntimeManager:
    def test_singleton(self):
        manager1 = RuntimeManager()
        manager2 = RuntimeManager()
        assert manager1 is manager2

    def test_startup(self):
        manager = RuntimeManager()
        manager.startup()
        assert manager.is_running is True
        manager.shutdown()

    def test_shutdown(self):
        manager = RuntimeManager()
        manager.startup()
        manager.shutdown()
        assert manager.is_running is False

    def test_uptime(self):
        manager = RuntimeManager()
        manager.startup()
        uptime = manager.uptime_seconds
        assert uptime >= 0
        manager.shutdown()

    def test_register_health_check(self):
        manager = RuntimeManager()
        manager.register_health_check("test", lambda: True)
        results = manager.run_health_checks()
        assert "test" in results

    def test_register_readiness_check(self):
        manager = RuntimeManager()
        manager.register_readiness_check("test", lambda: True)
        results = manager.run_readiness_checks()
        assert "test" in results


class TestConfigurationValidation:
    def test_valid_configuration(self):
        config = RuntimeConfiguration()
        result = ConfigurationValidator.validate(config)
        assert result["valid"] is True

    def test_missing_app_version(self):
        config = RuntimeConfiguration(app_version="")
        result = ConfigurationValidator.validate(config)
        assert not result["valid"]
        assert any("APP_VERSION" in e for e in result["errors"])

    def test_production_jwt_warning(self):
        config = RuntimeConfiguration(
            environment=Environment.PRODUCTION,
            jwt=JWTConfig(secret_key="dev-secret-key-change-in-production"),
        )
        result = ConfigurationValidator.validate(config)
        assert any("JWT_SECRET_KEY" in e for e in result["errors"])

    def test_short_jwt_key_production(self):
        config = RuntimeConfiguration(
            environment=Environment.PRODUCTION,
            jwt=JWTConfig(secret_key="short"),
        )
        result = ConfigurationValidator.validate(config)
        assert any("32 characters" in e for e in result["errors"])

    def test_sqlite_production_warning(self):
        config = RuntimeConfiguration(
            environment=Environment.PRODUCTION,
            database=DatabaseConfig(url="sqlite:///prod.db"),
        )
        result = ConfigurationValidator.validate(config)
        assert any("SQLite" in w for w in result["warnings"])

    def test_invalid_database_url(self):
        config = RuntimeConfiguration(database=DatabaseConfig(url=""))
        result = ConfigurationValidator.validate(config)
        assert not result["valid"]

    def test_invalid_jwt_algorithm(self):
        config = RuntimeConfiguration(jwt=JWTConfig(secret_key="secret", algorithm="INVALID"))
        result = ConfigurationValidator.validate(config)
        assert not result["valid"]

    def test_negative_token_expiry(self):
        config = RuntimeConfiguration(jwt=JWTConfig(secret_key="secret", access_token_expire_minutes=-1))
        result = ConfigurationValidator.validate(config)
        assert not result["valid"]

    def test_worker_requires_redis(self):
        config = RuntimeConfiguration(
            worker_enabled=True,
            redis_url=None,
        )
        result = ConfigurationValidator.validate(config)
        assert not result["valid"]
        assert any("Redis" in e for e in result["errors"])


class TestStructuredLogging:
    def test_logger_creation(self):
        configure_logging()
        logger = get_logger("test")
        assert logger is not None
        assert logger.name == "cloudsentinel.test"

    def test_json_log_format(self):
        config = RuntimeConfiguration(logging=LoggingConfig(format=LogFormat.JSON))
        configure_logging(config)
        logger = get_logger("test_json")
        assert logger is not None

    def test_text_log_format(self):
        config = RuntimeConfiguration(logging=LoggingConfig(format=LogFormat.TEXT))
        configure_logging(config)
        logger = get_logger("test_text")
        assert logger is not None


class TestIntegrationWithAPI:
    def test_health_endpoint_accessible(self, client):
        response = client.get("/api/v1/health")
        assert response.status_code == 200

    def test_metrics_in_health_response(self, client):
        response = client.get("/api/v1/health")
        assert response.status_code == 200


class TestRuntimeEdgeCases:
    def test_metrics_empty_history(self):
        collector = MetricsCollector()
        assert collector.get_latest("nonexistent") == 0.0
        assert len(collector.get_history("nonexistent")) == 0

    def test_health_no_checks(self):
        config = RuntimeConfiguration()
        service = HealthService(config)
        response = service.check()
        assert response.status == HealthStatus.HEALTHY
        assert len(response.checks) == 0

    def test_readiness_not_ready(self):
        config = RuntimeConfiguration()
        service = ReadinessService(config)
        service.register_check("failing", lambda: False)
        response = service.check()
        assert response.status == ReadinessStatus.NOT_READY

    def test_manager_double_shutdown(self):
        manager = RuntimeManager()
        manager.startup()
        manager.shutdown()
        manager.shutdown()  # Should not raise
        assert manager.is_running is False
