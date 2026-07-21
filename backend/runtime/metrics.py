from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime


@dataclass(frozen=True)
class MetricValue:
    name: str
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = None
    unit: Optional[str] = None

    def __post_init__(self):
        if self.timestamp is None:
            object.__setattr__(self, "timestamp", datetime.utcnow())


@dataclass(frozen=True)
class MetricsSnapshot:
    scan_count: int = 0
    api_requests: int = 0
    avg_scan_time_seconds: float = 0.0
    plugin_count: int = 0
    assets_processed: int = 0
    findings_generated: int = 0
    risk_calculations: int = 0
    auth_requests: int = 0
    rate_limit_hits: int = 0
    uptime_seconds: float = 0.0
    custom_metrics: Dict[str, float] = field(default_factory=dict)
    collected_at: datetime = None

    def __post_init__(self):
        if self.collected_at is None:
            object.__setattr__(self, "collected_at", datetime.utcnow())


class MetricsCollector:
    def __init__(self):
        self._metrics: Dict[str, List[MetricValue]] = {}
        self._snapshot = MetricsSnapshot()

    def record(self, name: str, value: float, labels: Dict[str, str] = None, unit: str = None) -> None:
        metric = MetricValue(name=name, value=value, labels=labels or {}, unit=unit)
        self._metrics.setdefault(name, []).append(metric)

    def increment(self, name: str, amount: float = 1.0, labels: Dict[str, str] = None) -> None:
        self.record(name, self.get_latest(name) + amount, labels)

    def get_latest(self, name: str) -> float:
        values = self._metrics.get(name, [])
        return values[-1].value if values else 0.0

    def get_history(self, name: str) -> List[MetricValue]:
        return list(self._metrics.get(name, []))

    def snapshot(self) -> MetricsSnapshot:
        return MetricsSnapshot(
            scan_count=int(self.get_latest("scan_count")),
            api_requests=int(self.get_latest("api_requests")),
            avg_scan_time_seconds=self.get_latest("avg_scan_time_seconds"),
            plugin_count=int(self.get_latest("plugin_count")),
            assets_processed=int(self.get_latest("assets_processed")),
            findings_generated=int(self.get_latest("findings_generated")),
            risk_calculations=int(self.get_latest("risk_calculations")),
            auth_requests=int(self.get_latest("auth_requests")),
            rate_limit_hits=int(self.get_latest("rate_limit_hits")),
            uptime_seconds=self.get_latest("uptime_seconds"),
        )

    def reset(self) -> None:
        self._metrics.clear()
