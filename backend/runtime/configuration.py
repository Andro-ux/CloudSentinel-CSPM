from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any


class Environment(str, Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class LogFormat(str, Enum):
    TEXT = "text"
    JSON = "json"


@dataclass(frozen=True)
class DatabaseConfig:
    url: str
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False


@dataclass(frozen=True)
class JWTConfig:
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7


@dataclass(frozen=True)
class RateLimitConfig:
    enabled: bool = True
    requests_per_minute: int = 100
    burst_size: int = 50


@dataclass(frozen=True)
class CORSConfig:
    allow_origins: List[str] = field(default_factory=lambda: ["*"])
    allow_credentials: bool = True
    allow_methods: List[str] = field(default_factory=lambda: ["*"])
    allow_headers: List[str] = field(default_factory=lambda: ["*"])


@dataclass(frozen=True)
class LoggingConfig:
    level: str = "INFO"
    format: LogFormat = LogFormat.TEXT
    output: str = "console"
    include_request_id: bool = True
    include_correlation_id: bool = True


@dataclass(frozen=True)
class MetricsConfig:
    enabled: bool = True
    endpoint: str = "/metrics"
    include_system_metrics: bool = True


@dataclass(frozen=True)
class PluginConfig:
    path: str = "backend/plugins"
    auto_discover: bool = True
    validate_on_load: bool = True


@dataclass(frozen=True)
class ScanConfig:
    enabled: bool = True
    interval_minutes: int = 60
    max_concurrent_scans: int = 3
    timeout_seconds: int = 300


@dataclass(frozen=True)
class RuntimeConfiguration:
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = False
    api_version: str = "v1"
    app_version: str = "0.11.0"
    database: DatabaseConfig = None
    jwt: JWTConfig = None
    rate_limit: RateLimitConfig = None
    cors: CORSConfig = None
    logging: LoggingConfig = None
    metrics: MetricsConfig = None
    plugin: PluginConfig = None
    scan: ScanConfig = None
    redis_url: Optional[str] = None
    worker_enabled: bool = False
    frontend_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.database is None:
            object.__setattr__(self, "database", DatabaseConfig(url="sqlite:///cloudsentinel.db"))
        if self.jwt is None:
            object.__setattr__(self, "jwt", JWTConfig(secret_key="dev-secret-key-change-in-production"))
        if self.rate_limit is None:
            object.__setattr__(self, "rate_limit", RateLimitConfig())
        if self.cors is None:
            object.__setattr__(self, "cors", CORSConfig())
        if self.logging is None:
            object.__setattr__(self, "logging", LoggingConfig())
        if self.metrics is None:
            object.__setattr__(self, "metrics", MetricsConfig())
        if self.plugin is None:
            object.__setattr__(self, "plugin", PluginConfig())
        if self.scan is None:
            object.__setattr__(self, "scan", ScanConfig())
        if not self.metadata:
            object.__setattr__(self, "metadata", {
                "loaded_at": datetime.utcnow().isoformat(),
                "source": "default",
            })
