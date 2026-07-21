from typing import Optional, Dict, Any
from backend.runtime.configuration import RuntimeConfiguration, Environment
from backend.runtime.logging import get_logger


logger = get_logger("validation")


class ConfigurationValidator:
    @staticmethod
    def validate(config: RuntimeConfiguration) -> Dict[str, Any]:
        errors = []
        warnings = []

        if not config.app_version:
            errors.append("APP_VERSION is required")
        if not config.api_version:
            errors.append("API_VERSION is required")
        if config.environment == Environment.PRODUCTION:
            if config.jwt.secret_key == "dev-secret-key-change-in-production":
                errors.append("JWT_SECRET_KEY must be set in production")
            if len(config.jwt.secret_key) < 32:
                errors.append("JWT_SECRET_KEY must be at least 32 characters in production")
            if "sqlite" in config.database.url.lower():
                warnings.append("SQLite is not recommended for production")

        if not config.jwt.secret_key:
            errors.append("JWT_SECRET_KEY is required")
        if config.jwt.algorithm not in ["HS256", "HS384", "HS512"]:
            errors.append(f"Unsupported JWT algorithm: {config.jwt.algorithm}")
        if config.jwt.access_token_expire_minutes <= 0:
            errors.append("ACCESS_TOKEN_EXPIRE_MINUTES must be positive")
        if config.jwt.refresh_token_expire_days <= 0:
            errors.append("REFRESH_TOKEN_EXPIRE_DAYS must be positive")
        if not config.database.url:
            errors.append("DATABASE_URL is required")
        if config.database.pool_size < 1:
            errors.append("Database pool_size must be at least 1")
        if config.redis_url and not config.redis_url.startswith(("redis://", "rediss://")):
            errors.append("REDIS_URL must start with redis:// or rediss://")
        if not config.plugin.path:
            errors.append("PLUGIN_PATH is required")
        import os
        if config.plugin.path and not os.path.isdir(config.plugin.path):
            errors.append(f"Plugin path does not exist: {config.plugin.path}")
        if config.worker_enabled and not config.redis_url:
            errors.append("Redis is required when worker is enabled")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }
