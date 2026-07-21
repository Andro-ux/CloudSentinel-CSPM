from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from backend.runtime.configuration import RuntimeConfiguration
from backend.runtime.logging import get_logger


logger = get_logger("readiness")


class ReadinessStatus(str, Enum):
    READY = "ready"
    NOT_READY = "not_ready"
    DEGRADED = "degraded"


@dataclass(frozen=True)
class ReadinessCheck:
    name: str
    status: ReadinessStatus
    message: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    checked_at: datetime = None

    def __post_init__(self):
        if self.checked_at is None:
            object.__setattr__(self, "checked_at", datetime.utcnow())


@dataclass(frozen=True)
class ReadinessResponse:
    status: ReadinessStatus
    checks: List[ReadinessCheck] = field(default_factory=list)
    startup_complete: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_ready(self) -> bool:
        return self.status == ReadinessStatus.READY

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "startup_complete": self.startup_complete,
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


class ReadinessService:
    def __init__(self, config: RuntimeConfiguration):
        self.config = config
        self._checks: Dict[str, Callable] = {}
        self._startup_complete = False

    def register_check(self, name: str, check_func: Callable) -> None:
        self._checks[name] = check_func

    def set_startup_complete(self, value: bool = True) -> None:
        self._startup_complete = value

    def check(self) -> ReadinessResponse:
        checks = []
        overall_status = ReadinessStatus.READY

        for name, check_func in self._checks.items():
            try:
                result = check_func()
                if isinstance(result, dict):
                    status = result.get("status", "ready")
                    message = result.get("message")
                    details = result.get("details", {})
                else:
                    status = "ready" if result else "not_ready"
                    message = None
                    details = {}
                readiness_status = ReadinessStatus(status)
                checks.append(ReadinessCheck(name=name, status=readiness_status, message=message, details=details))
                if readiness_status == ReadinessStatus.NOT_READY:
                    overall_status = ReadinessStatus.NOT_READY
                elif readiness_status == ReadinessStatus.DEGRADED and overall_status == ReadinessStatus.READY:
                    overall_status = ReadinessStatus.DEGRADED
            except Exception as exc:
                logger.error(f"Readiness check {name} failed: {exc}")
                checks.append(ReadinessCheck(name=name, status=ReadinessStatus.NOT_READY, message=str(exc)))
                overall_status = ReadinessStatus.NOT_READY

        return ReadinessResponse(
            status=overall_status,
            checks=checks,
            startup_complete=self._startup_complete,
            metadata={
                "app_version": self.config.app_version,
                "api_version": self.config.api_version,
                "environment": self.config.environment.value,
            },
        )
