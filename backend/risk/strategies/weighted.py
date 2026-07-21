from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from backend.risk.models import Priority, Risk, priority_from_score


@dataclass(frozen=True)
class ScoreWeights:

    severity_critical: int = 30

    severity_high: int = 20

    severity_medium: int = 10

    severity_low: int = 5

    multiple_assets: int = 10

    supporting_facts: int = 5

    attack_path_presence: int = 20

    public_exposure: int = 15

    identity_related: int = 10


class WeightedScoreStrategy:

    def __init__(self, weights: ScoreWeights = None):

        self.weights = weights or ScoreWeights()

    def score(self, finding, context: Dict) -> "Risk":

        from backend.risk.models import Risk, Priority, priority_from_score

        factors = []

        score = 0

        severity = finding.severity.value.upper()

        if severity == "CRITICAL":

            score += self.weights.severity_critical

            factors.append("Critical severity")

        elif severity == "HIGH":

            score += self.weights.severity_high

            factors.append("High severity")

        elif severity == "MEDIUM":

            score += self.weights.severity_medium

            factors.append("Medium severity")

        elif severity == "LOW":

            score += self.weights.severity_low

            factors.append("Low severity")

        asset_count = len(finding.asset_ids)

        if asset_count > 1:

            score += self.weights.multiple_assets

            factors.append(f"Affects {asset_count} assets")

        fact_ids = getattr(finding, "fact_ids", [])

        fact_count = len(fact_ids)

        if fact_count > 1:

            score += self.weights.supporting_facts

            factors.append(f"Supported by {fact_count} facts")

        attack_paths = context.get("attack_paths", [])

        affected_attack_paths = [

            path for path in attack_paths

            if any(asset_id in path.nodes for asset_id in finding.asset_ids)

        ]

        if affected_attack_paths:

            score += self.weights.attack_path_presence

            factors.append("Reachable via attack path")

        public_assets = context.get("public_assets", [])

        public_asset_ids = {a.id for a in public_assets}

        if any(asset_id in public_asset_ids for asset_id in finding.asset_ids):

            score += self.weights.public_exposure

            factors.append("Publicly exposed asset")

        identity_categories = {"IAM", "Identity"}

        if finding.category in identity_categories:

            score += self.weights.identity_related

            factors.append("Identity-related finding")

        score = max(0, min(100, score))

        priority = priority_from_score(score)

        explanation = self._build_explanation(finding, score, priority, factors)

        return Risk(

            id=f"risk-{finding.id}",

            finding_id=finding.id,

            asset_ids=list(finding.asset_ids),

            score=score,

            priority=priority,

            category=finding.category,

            severity=finding.severity.value,

            explanation=explanation,

            contributing_factors=factors,

            recommendation=finding.recommendation,

            metadata={

                "rule_id": finding.rule_id,

                "finding_title": finding.title,

                "weights": {

                    "severity_critical": self.weights.severity_critical,

                    "severity_high": self.weights.severity_high,

                    "severity_medium": self.weights.severity_medium,

                    "severity_low": self.weights.severity_low,

                    "multiple_assets": self.weights.multiple_assets,

                    "supporting_facts": self.weights.supporting_facts,

                    "attack_path_presence": self.weights.attack_path_presence,

                    "public_exposure": self.weights.public_exposure,

                    "identity_related": self.weights.identity_related,

                },

            },

        )

    def _build_explanation(
        self,
        finding,
        score: int,
        priority: Priority,
        factors: List[str],
    ) -> str:

        factor_text = ", ".join(factors) if factors else "no additional factors"

        return (
            f"Finding '{finding.title}' received a risk score of {score}/100 "
            f"with priority {priority.value}. "
            f"Contributing factors: {factor_text}."
        )
