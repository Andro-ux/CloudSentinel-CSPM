from typing import Dict, Any
from datetime import datetime


class SecurityMetrics:
    def __init__(self):
        self._metrics: Dict[str, Any] = {
            "successful_logins": 0,
            "failed_logins": 0,
            "locked_accounts": 0,
            "active_sessions": 0,
            "token_refreshes": 0,
            "bootstrap_usage": 0,
            "password_changes": 0,
            "average_login_latency_ms": 0.0,
            "login_latencies": [],
        }

    def increment(self, metric: str, amount: int = 1) -> None:
        if metric in self._metrics:
            self._metrics[metric] += amount

    def record_login_latency(self, latency_ms: float) -> None:
        self._metrics["login_latencies"].append(latency_ms)
        if len(self._metrics["login_latencies"]) > 1000:
            self._metrics["login_latencies"] = self._metrics["login_latencies"][-1000:]
        if self._metrics["login_latencies"]:
            self._metrics["average_login_latency_ms"] = sum(self._metrics["login_latencies"]) / len(self._metrics["login_latencies"])

    def get_metrics(self) -> Dict[str, Any]:
        return dict(self._metrics)

    def to_prometheus_format(self) -> str:
        lines = []
        for key, value in self._metrics.items():
            if isinstance(value, (int, float)):
                lines.append(f"cloudsentinel_security_{key} {value}")
        return "\n".join(lines)


security_metrics = SecurityMetrics()
