from typing import List

from backend.executive.interfaces import INarrativeStrategy
from backend.executive.models import (
    ExecutiveDashboard,
    ExecutiveNarrative,
)


class DefaultNarrativeStrategy(INarrativeStrategy):

    def generate_narrative(
        self,
        dashboard: ExecutiveDashboard,
    ) -> ExecutiveNarrative:

        score = dashboard.security_score

        total_assets = dashboard.summary.total_assets

        total_findings = dashboard.summary.total_findings

        total_risks = dashboard.summary.total_risks

        top_risks = dashboard.summary.top_risks

        recommendations = dashboard.recommendations

        summary = (
            f"CloudSentinel analyzed {total_assets} cloud assets and identified "
            f"{total_findings} findings, resulting in {total_risks} prioritized risks. "
            f"The environment currently has a Security Score of {score.overall} "
            f"(Grade {score.grade})."
        )

        top_risks_summary = self._build_top_risks_summary(top_risks)

        recommendation_summary = self._build_recommendation_summary(recommendations)

        score_explanation = self._build_score_explanation(score)

        return ExecutiveNarrative(
            summary=summary,
            top_risks_summary=top_risks_summary,
            recommendation_summary=recommendation_summary,
            score_explanation=score_explanation,
            metadata={
                "strategy": self.__class__.__name__,
            },
        )

    def _build_top_risks_summary(self, top_risks) -> str:

        if not top_risks:

            return "No critical risks were identified."

        risk_descriptions = []

        for risk in top_risks[:3]:

            risk_descriptions.append(

                f"{risk.finding_id} (score: {risk.score}, priority: {risk.priority.value})"

            )

        return "Top risks: " + "; ".join(risk_descriptions) + "."

    def _build_recommendation_summary(self, recommendations) -> str:

        if not recommendations:

            return "No immediate recommendations available."

        top_recs = recommendations[:3]

        rec_descriptions = []

        for rec in top_recs:

            rec_descriptions.append(

                f"{rec.title} (expected improvement: +{rec.expected_score_improvement})"

            )

        return "Top recommendations: " + "; ".join(rec_descriptions) + "."

    def _build_score_explanation(self, score) -> str:

        dimensions = score.dimensions.to_dict()

        dimension_descriptions = []

        for dimension, value in dimensions.items():

            if dimension != "overall":

                dimension_descriptions.append(

                    f"{dimension}: {value}/100"

                )

        return (
            f"Security Score breakdown: {', '.join(dimension_descriptions)}. "
            f"Overall score derived from dimension averages with deductions "
            f"applied for identified risks."
        )
