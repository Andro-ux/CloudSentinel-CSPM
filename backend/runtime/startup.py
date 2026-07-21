import os
import time
import signal
import sys
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from backend.runtime.configuration import (
    RuntimeConfiguration,
    Environment,
    DatabaseConfig,
    JWTConfig,
    RateLimitConfig,
    CORSConfig,
    LogFormat,
    LoggingConfig,
    MetricsConfig,
    PluginConfig,
    ScanConfig,
)
from backend.runtime.logging import get_logger
from backend.runtime.exceptions import ConfigurationError, DependencyError, StartupError
from backend.runtime.lifecycle import LifecycleManager, LifecycleEventType
from backend.runtime.validation import ConfigurationValidator

logger = get_logger("startup")


class StartupValidator:
    def __init__(self, config: RuntimeConfiguration):
        self.config = config
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_all(self) -> bool:
        self._validate_environment()
        self._validate_jwt()
        self._validate_database()
        self._validate_redis()
        self._validate_plugins()
        self._validate_directories()
        self._validate_worker_config()
        return len(self.errors) == 0

    def _validate_environment(self) -> None:
        if not self.config.app_version:
            self.errors.append("APP_VERSION is required")
        if not self.config.api_version:
            self.errors.append("API_VERSION is required")
        if self.config.environment == Environment.PRODUCTION:
            if self.config.jwt.secret_key == "dev-secret-key-change-in-production":
                self.errors.append("JWT_SECRET_KEY must be set in production")
            if len(self.config.jwt.secret_key) < 32:
                self.errors.append("JWT_SECRET_KEY must be at least 32 characters in production")
            if "sqlite" in self.config.database.url.lower():
                self.warnings.append("SQLite is not recommended for production")

    def _validate_jwt(self) -> None:
        if not self.config.jwt.secret_key:
            self.errors.append("JWT_SECRET_KEY is required")
        if self.config.jwt.algorithm not in ["HS256", "HS384", "HS512"]:
            self.errors.append(f"Unsupported JWT algorithm: {self.config.jwt.algorithm}")
        if self.config.jwt.access_token_expire_minutes <= 0:
            self.errors.append("ACCESS_TOKEN_EXPIRE_MINUTES must be positive")
        if self.config.jwt.refresh_token_expire_days <= 0:
            self.errors.append("REFRESH_TOKEN_EXPIRE_DAYS must be positive")

    def _validate_database(self) -> None:
        if not self.config.database.url:
            self.errors.append("DATABASE_URL is required")
        if self.config.database.pool_size < 1:
            self.errors.append("Database pool_size must be at least 1")

    def _validate_redis(self) -> None:
        if self.config.redis_url:
            if not self.config.redis_url.startswith(("redis://", "rediss://")):
                self.errors.append("REDIS_URL must start with redis:// or rediss://")

    def _validate_plugins(self) -> None:
        if not self.config.plugin.path:
            self.errors.append("PLUGIN_PATH is required")
        if not os.path.isdir(self.config.plugin.path):
            self.errors.append(f"Plugin path does not exist: {self.config.plugin.path}")

    def _validate_directories(self) -> None:
        required_dirs = ["logs", "data"]
        for directory in required_dirs:
            path = os.path.join(os.getcwd(), directory)
            if not os.path.isdir(path):
                try:
                    os.makedirs(path, exist_ok=True)
                    self.warnings.append(f"Created missing directory: {directory}")
                except OSError as exc:
                    self.errors.append(f"Cannot create directory {directory}: {exc}")

    def _validate_worker_config(self) -> None:
        if self.config.worker_enabled:
            if not self.config.redis_url:
                self.errors.append("Redis is required when worker is enabled")

    def get_errors(self) -> List[str]:
        return list(self.errors)

    def get_warnings(self) -> List[str]:
        return list(self.warnings)

    def raise_if_errors(self) -> None:
        if self.errors:
            raise StartupError(f"Startup validation failed: {'; '.join(self.errors)}")


class ConfigurationLoader:
    @staticmethod
    def load() -> RuntimeConfiguration:
        from dotenv import load_dotenv
        load_dotenv()

        env_str = os.getenv("ENVIRONMENT", "development").lower()
        try:
            environment = Environment(env_str)
        except ValueError:
            environment = Environment.DEVELOPMENT

        debug = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")

        database_url = os.getenv("DATABASE_URL", "sqlite:///cloudsentinel.db")
        database_config = DatabaseConfig(
            url=database_url,
            pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
            max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "10")),
            pool_timeout=int(os.getenv("DB_POOL_TIMEOUT", "30")),
            pool_recycle=int(os.getenv("DB_POOL_RECYCLE", "3600")),
            echo=os.getenv("DB_ECHO", "false").lower() in ("true", "1", "yes"),
        )

        jwt_config = JWTConfig(
            secret_key=os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production"),
            algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
            access_token_expire_minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")),
            refresh_token_expire_days=int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")),
        )

        rate_limit_config = RateLimitConfig(
            enabled=os.getenv("RATE_LIMIT_ENABLED", "true").lower() in ("true", "1", "yes"),
            requests_per_minute=int(os.getenv("RATE_LIMIT_RPM", "100")),
            burst_size=int(os.getenv("RATE_LIMIT_BURST", "50")),
        )

        cors_config = CORSConfig(
            allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
            allow_credentials=os.getenv("CORS_CREDENTIALS", "true").lower() in ("true", "1", "yes"),
            allow_methods=os.getenv("CORS_METHODS", "*").split(","),
            allow_headers=os.getenv("CORS_HEADERS", "*").split(","),
        )

        log_format_str = os.getenv("LOG_FORMAT", "text").lower()
        try:
            log_format = LogFormat(log_format_str)
        except ValueError:
            log_format = LogFormat.TEXT

        logging_config = LoggingConfig(
            level=os.getenv("LOG_LEVEL", "INFO"),
            format=log_format,
            output=os.getenv("LOG_OUTPUT", "console"),
            include_request_id=os.getenv("LOG_REQUEST_ID", "true").lower() in ("true", "1", "yes"),
            include_correlation_id=os.getenv("LOG_CORRELATION_ID", "true").lower() in ("true", "1", "yes"),
        )

        metrics_config = MetricsConfig(
            enabled=os.getenv("METRICS_ENABLED", "true").lower() in ("true", "1", "yes"),
            endpoint=os.getenv("METRICS_ENDPOINT", "/metrics"),
            include_system_metrics=os.getenv("METRICS_SYSTEM", "true").lower() in ("true", "1", "yes"),
        )

        plugin_config = PluginConfig(
            path=os.getenv("PLUGIN_PATH", "backend/plugins"),
            auto_discover=os.getenv("PLUGIN_AUTO_DISCOVER", "true").lower() in ("true", "1", "yes"),
            validate_on_load=os.getenv("PLUGIN_VALIDATE", "true").lower() in ("true", "1", "yes"),
        )

        scan_config = ScanConfig(
            enabled=os.getenv("SCAN_ENABLED", "true").lower() in ("true", "1", "yes"),
            interval_minutes=int(os.getenv("SCAN_INTERVAL_MINUTES", "60")),
            max_concurrent_scans=int(os.getenv("SCAN_MAX_CONCURRENT", "3")),
            timeout_seconds=int(os.getenv("SCAN_TIMEOUT_SECONDS", "300")),
        )

        config = RuntimeConfiguration(
            environment=environment,
            debug=debug,
            api_version=os.getenv("API_VERSION", "v1"),
            app_version=os.getenv("APP_VERSION", "0.11.0"),
            database=database_config,
            jwt=jwt_config,
            rate_limit=rate_limit_config,
            cors=cors_config,
            logging=logging_config,
            metrics=metrics_config,
            plugin=plugin_config,
            scan=scan_config,
            redis_url=os.getenv("REDIS_URL"),
            worker_enabled=os.getenv("WORKER_ENABLED", "false").lower() in ("true", "1", "yes"),
            frontend_url=os.getenv("FRONTEND_URL"),
            metadata={
                "loaded_at": datetime.utcnow().isoformat(),
                "source": "environment",
            },
        )

        return config
