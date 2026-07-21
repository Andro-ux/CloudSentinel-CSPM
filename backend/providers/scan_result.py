from dataclasses import dataclass, field
from typing import Any, Dict, List

from backend.reporting.executive_summary import ExecutiveSummary


@dataclass
class ScanResult:

    provider: str

    findings: List[dict] = field(default_factory=list)

    assets: Dict[str, int] = field(default_factory=dict)

    summary: Dict[str, int] = field(default_factory=lambda: {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
    })

    executive_summary: Dict = field(default_factory=dict)

    relationships: List = field(default_factory=list)

    attack_paths: List = field(default_factory=list)

    fact_set: Any = None

    risk_set: Any = None

    dashboard: Any = None

    def calculate_summary(self):

        self.summary = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
        }

        for finding in self.findings:

            severity = finding["severity"].lower()

            if severity in self.summary:

                self.summary[severity] += 1

    def calculate_executive_summary(self):

        self.executive_summary = ExecutiveSummary().generate(
            self
        )