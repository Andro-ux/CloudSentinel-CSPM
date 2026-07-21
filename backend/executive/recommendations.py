from typing import List

from backend.executive.interfaces import IRecommendationBuilder
from backend.executive.models import Recommendation
from backend.facts.models import FactSet
from backend.rules.models import FindingSet
from backend.risk.models import RiskSet


class RecommendationBuilder(IRecommendationBuilder):

    def build(
        self,
        risks: RiskSet,
        findings: FindingSet,
        facts: FactSet,
    ) -> List[Recommendation]:

        recommendations: List[Recommendation] = []

        seen_titles = set()

        for risk in risks:

            title = risk.recommendation or f"Remediate {risk.finding_id}"

            if title in seen_titles:

                continue

            seen_titles.add(title)

            recommendations.append(

                Recommendation(

                    title=title,

                    priority=risk.priority.value,

                    description=risk.explanation,

                    affected_assets=list(risk.asset_ids),

                    expected_score_improvement=self._estimate_improvement(risk),

                    related_risks=[risk.id],

                )

            )

        recommendations.sort(

            key=lambda r: (-r.expected_score_improvement, r.priority)

        )

        return recommendations

    def _estimate_improvement(self, risk) -> int:

        return min(100 - risk.score, risk.score // 2)
