from typing import List

from backend.executive.interfaces import IInsightBuilder
from backend.executive.models import Insight
from backend.facts.models import FactSet
from backend.rules.models import FindingSet
from backend.risk.models import RiskSet


class InsightBuilder(IInsightBuilder):

    def build(
        self,
        risks: RiskSet,
        findings: FindingSet,
        facts: FactSet,
    ) -> List[Insight]:

        insights: List[Insight] = []

        seen_titles = set()

        for risk in risks:

            title = self._insight_title(risk)

            if title in seen_titles:

                continue

            seen_titles.add(title)

            insights.append(

                Insight(

                    id=f"insight-{risk.id}",

                    title=title,

                    description=risk.explanation,

                    severity=risk.severity,

                    category=risk.category,

                    business_impact=self._business_impact(risk),

                    recommendation=risk.recommendation,

                    related_risks=[risk.id],

                )

            )

        return insights

    def _insight_title(self, risk) -> str:

        return f"Risk Alert: {risk.finding_id}"

    def _business_impact(self, risk) -> str:

        if risk.priority.value == "CRITICAL":

            return "Immediate business impact potential."

        if risk.priority.value == "HIGH":

            return "Significant business impact potential."

        return "Limited business impact potential."
