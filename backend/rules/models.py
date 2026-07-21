from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class Severity(str, Enum):

    CRITICAL = "CRITICAL"

    HIGH = "HIGH"

    MEDIUM = "MEDIUM"

    LOW = "LOW"

    INFO = "INFO"


@dataclass(frozen=True)
class RuleMetadata:

    rule_id: str

    name: str

    description: str

    version: str = "1.0.0"

    author: str = "CloudSentinel Core"


@dataclass(frozen=True)
class Finding:

    id: str

    rule_id: str

    title: str

    description: str

    severity: Severity

    category: str

    asset_ids: List[str]

    facts: List[Any]  # List[Fact] internally, serialized to IDs in to_dict()

    recommendation: str

    references: List[str]

    evidence: Dict[str, Any]

    service: str = ""

    resource_id: str = ""

    risk_score: int = 0

    def to_dict(self) -> Dict[str, Any]:

        return {

            "id": self.id,

            "rule_id": self.rule_id,

            "title": self.title,

            "description": self.description,

            "severity": self.severity.value,

            "category": self.category,

            "service": self.service,

            "resource_id": self.resource_id,

            "asset_ids": self.asset_ids,

            "fact_ids": [

                f.id if hasattr(f, "id") else str(f)

                for f in self.facts

            ],

            "recommendation": self.recommendation,

            "references": self.references,

            "evidence": self.evidence,

            "risk_score": self.risk_score,

        }

    @property
    def fact_ids(self) -> List[str]:

        return [

            f.id if hasattr(f, "id") else str(f)

            for f in self.facts

        ]


class FindingSet:

    def __init__(self, findings: List[Finding]):

        self._findings = tuple(findings)

        self._by_id: Dict[str, Finding] = {}

        self._by_severity: Dict[Severity, List[Finding]] = {}

        self._by_asset: Dict[str, List[Finding]] = {}

        self._by_rule: Dict[str, List[Finding]] = {}

        for finding in self._findings:

            self._by_id[finding.id] = finding

            self._by_severity.setdefault(
                finding.severity,
                []
            ).append(finding)

            for asset_id in finding.asset_ids:

                self._by_asset.setdefault(
                    asset_id,
                    []
                ).append(finding)

            self._by_rule.setdefault(
                finding.rule_id,
                []
            ).append(finding)

    @property
    def findings(self) -> tuple:

        return self._findings

    def __iter__(self):

        return iter(self._findings)

    def __len__(self) -> int:

        return len(self._findings)

    def __contains__(self, finding: Finding) -> bool:

        return finding in self._findings

    def find_by_id(self, finding_id: str) -> Optional[Finding]:

        return self._by_id.get(finding_id)

    def find_by_severity(self, severity: Severity) -> List[Finding]:

        return list(self._by_severity.get(severity, []))

    def find_by_asset(self, asset_id: str) -> List[Finding]:

        return list(self._by_asset.get(asset_id, []))

    def find_by_rule(self, rule_id: str) -> List[Finding]:

        return list(self._by_rule.get(rule_id, []))

    def statistics(self) -> Dict[str, Any]:

        severity_counts: Dict[str, int] = {}

        for severity, findings in self._by_severity.items():

            severity_counts[severity.value] = len(findings)

        return {

            "total": len(self._findings),

            "by_severity": severity_counts,

            "by_rule": {

                rule_id: len(findings)

                for rule_id, findings in self._by_rule.items()

            },

            "by_asset": {

                asset_id: len(findings)

                for asset_id, findings in self._by_asset.items()

            },

        }

    def to_dicts(self) -> List[Dict[str, Any]]:

        return [f.to_dict() for f in self._findings]
