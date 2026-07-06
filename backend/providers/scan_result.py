from dataclasses import dataclass, field
from typing import List, Dict
from backend.scoring.score_engine import ScoreEngine


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
    score: Dict = field(default_factory=dict)

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

    def calculate_score(self):

        engine = ScoreEngine(
            self.findings
        )

        self.score = engine.calculate()            