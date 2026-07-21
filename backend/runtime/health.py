from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime

from backend.runtime.configuration import RuntimeConfiguration
from backend.runtime.logging import get_logger


logger = get_logger("health")


class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass(frozen=True)
class HealthCheck:
    name: str
    status: HealthStatus
    message: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    checked_at: datetime = None

    def __post_init__(self):
        if self.checked_at is None:
            object.__setattr__(self, "checked_at", datetime.utcnow())


@dataclass(frozen=True)
class HealthResponse:
    status: HealthStatus
    checks: List[HealthCheck] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_healthy(self) -> bool:
        return self.status == HealthStatus.HEALTHY

    @property
    def is_degraded(self) -> bool:
        return self.status == HealthStatus.DEGRADED

    @property
    def is_unhealthy(self) -> bool:
        return self.status == HealthStatus.UNHEALTHY

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "checks": [
                {
                    "name": check.name,
                    "status": check.status.value,
                    "message": check.message,
                    "details": check.details,
                    "checked_at": check.checked_at.isoformat() if check.checked_at else None,
                }
                for check in self.checks
            ],
            "metadata": self.metadata,
        }


class HealthService:
    def __init__(self, config: RuntimeConfiguration):
        self.config = config
        self._checks: Dict[str, Callable] = {}

    def register_check(self, name: str, check_func: Callable) -> None:
        self._checks[name] = check_func

    def check(self) -> HealthResponse:
        checks = []
        overall_status = HealthStatus.HEALTHY

        for name, check_func in self._checks.items():
            try:
                result = check_func()
                if isinstance(result, dict):
                    status = result.get("status", "healthy")
                    message = result.get("message")
                    details = result.get("details", {})
                else:
                    status = "healthy" if result else "unhealthy"
                    message = None
                    details = {}
                health_status = HealthStatus(status)
                checks.append(HealthCheck(name=name, status=health_status, message=message, details=details))
                if health_status == HealthStatus.UNHEALTHY:
                    overall_status = HealthStatus.UNHEALTHY
                elif health_status == HealthStatus.DEGRADED and overall_status == HealthStatus.HEALTHY:
                    overall_status = HealthStatus.DEGRADED
            except Exception as exc:
                logger.error(f"Health check {name} failed: {exc}")
                checks.append(HealthCheck(name=name, status=HealthStatus.UNHEALTHY, message=str(exc)))
                overall_status = HealthStatus.UNHEALTHY

        return HealthResponse(
            status=overall_status,
            checks=checks,
            metadata={
                "app_version": self.config.app_version,
                "api_version": self.config.api_version,
                "environment": self.config.environment.value,
            },
        )