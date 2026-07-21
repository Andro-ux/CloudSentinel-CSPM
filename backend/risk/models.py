from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class Priority(str, Enum):

    CRITICAL = "CRITICAL"

    HIGH = "HIGH"

    MEDIUM = "MEDIUM"

    LOW = "LOW"

    def __lt__(self, other):

        order = {self.CRITICAL: 0, self.HIGH: 1, self.MEDIUM: 2, self.LOW: 3}

        return order[self] < order[other]

    def __le__(self, other):

        return self == other or self < other

    def __gt__(self, other):

        return not self <= other

    def __ge__(self, other):

        return not self < other


def priority_from_score(score: int) -> Priority:

    if score >= 80:

        return Priority.CRITICAL

    if score >= 60:

        return Priority.HIGH

    if score >= 40:

        return Priority.MEDIUM

    return Priority.LOW


@dataclass(frozen=True)
class Risk:

    id: str

    finding_id: str

    asset_ids: List[str]

    score: int

    priority: Priority

    category: str

    severity: str

    explanation: str

    contributing_factors: List[str]

    recommendation: str

    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:

        return {

            "id": self.id,

            "finding_id": self.finding_id,

            "asset_ids": self.asset_ids,

            "score": self.score,

            "priority": self.priority.value,

            "category": self.category,

            "severity": self.severity,

            "explanation": self.explanation,

            "contributing_factors": self.contributing_factors,

            "recommendation": self.recommendation,

            "metadata": self.metadata,

        }


class RiskSet:

    def __init__(self, risks: List[Risk]):

        self._risks = tuple(risks)

        self._by_id: Dict[str, Risk] = {}

        self._by_priority: Dict[Priority, List[Risk]] = {}

        self._by_category: Dict[str, List[Risk]] = {}

        self._by_asset: Dict[str, List[Risk]] = {}

        for risk in self._risks:

            self._by_id[risk.id] = risk

            self._by_priority.setdefault(
                risk.priority,
                []
            ).append(risk)

            self._by_category.setdefault(
                risk.category,
                []
            ).append(risk)

            for asset_id in risk.asset_ids:

                self._by_asset.setdefault(
                    asset_id,
                    []
                ).append(risk)

    @property
    def risks(self) -> tuple:

        return self._risks

    def __iter__(self):

        return iter(self._risks)

    def __len__(self) -> int:

        return len(self._risks)

    def __contains__(self, risk: Risk) -> bool:

        return risk in self._risks

    def find_by_id(self, risk_id: str) -> Optional[Risk]:

        return self._by_id.get(risk_id)

    def find_by_priority(self, priority: Priority) -> List[Risk]:

        return list(self._by_priority.get(priority, []))

    def find_by_category(self, category: str) -> List[Risk]:

        return list(self._by_category.get(category, []))

    def find_by_asset(self, asset_id: str) -> List[Risk]:

        return list(self._by_asset.get(asset_id, []))

    def top_n(self, n: int) -> List[Risk]:

        return sorted(
            self._risks,
            key=lambda r: (-r.score, r.id)
        )[:n]

    def statistics(self) -> Dict[str, Any]:

        priority_counts: Dict[str, int] = {}

        for priority, risks in self._by_priority.items():

            priority_counts[priority.value] = len(risks)

        return {

            "total": len(self._risks),

            "by_priority": priority_counts,

            "by_category": {

                category: len(risks)

                for category, risks in self._by_category.items()

            },

            "by_asset": {

                asset_id: len(risks)

                for asset_id, risks in self._by_asset.items()

            },

        }

    def to_dicts(self) -> List[Dict[str, Any]]:

        return [r.to_dict() for r in self._risks]
