from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from backend.runtime.configuration import RuntimeConfiguration
from backend.runtime.logging import get_logger


logger = get_logger("lifecycle")


class LifecycleEventType(str, Enum):
    STARTUP = "startup"
    SHUTDOWN = "shutdown"
    RELOAD = "reload"
    HEALTH_CHECK = "health_check"
    ERROR = "error"


@dataclass(frozen=True)
class LifecycleEvent:
    event_type: LifecycleEventType
    component: str
    message: str
    timestamp: datetime = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.timestamp is None:
            object.__setattr__(self, "timestamp", datetime.utcnow())


class LifecycleManager:
    def __init__(self, config: RuntimeConfiguration):
        self.config = config
        self._started = False
        self._shutdown = False
        self._events: List[LifecycleEvent] = []
        self._handlers: Dict[LifecycleEventType, List[Callable]] = {}

    def register_handler(self, event_type: LifecycleEventType, handler: Callable) -> None:
        self._handlers.setdefault(event_type, []).append(handler)

    def emit(self, event_type: LifecycleEventType, component: str, message: str, **metadata) -> None:
        event = LifecycleEvent(
            event_type=event_type,
            component=component,
            message=message,
            metadata=metadata,
        )
        self._events.append(event)
        logger.info(
            f"[{event_type.value}] {component}: {message}",
            extra={"lifecycle_event": event},
        )
        for handler in self._handlers.get(event_type, []):
            try:
                handler(event)
            except Exception as exc:
                logger.error(f"Lifecycle handler failed: {exc}")

    def startup(self) -> None:
        if self._started:
            return
        self.emit(LifecycleEventType.STARTUP, "runtime", "Starting runtime manager")
        self._started = True
        self.emit(LifecycleEventType.STARTUP, "runtime", "Runtime manager started")

    def shutdown(self) -> None:
        if self._shutdown:
            return
        self.emit(LifecycleEventType.SHUTDOWN, "runtime", "Shutting down runtime manager")
        self._shutdown = True
        self.emit(LifecycleEventType.SHUTDOWN, "runtime", "Runtime manager shut down")

    def reload(self) -> None:
        self.emit(LifecycleEventType.RELOAD, "runtime", "Reloading configuration")
        self._started = False
        self.startup()

    @property
    def is_started(self) -> bool:
        return self._started

    @property
    def is_shutdown(self) -> bool:
        return self._shutdown

    @property
    def events(self) -> List[LifecycleEvent]:
        return list(self._events)
