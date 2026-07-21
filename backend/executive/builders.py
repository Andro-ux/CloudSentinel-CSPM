from typing import Dict, List

from backend.executive.interfaces import (
    IDashboardBuilder,
    IInsightBuilder,
    IMetricsBuilder,
    IRecommendationBuilder,
    INarrativeBuilder,
)
from backend.executive.models import (
    ExecutiveDashboard,
    ExecutiveMetrics,
    ExecutiveNarrative,
    ExecutiveSummary,
    Insight,
    Recommendation,
)
from backend.risk.models import Risk


class MetricsBuilder(IMetricsBuilder):

    def build(
        self,
        assets,
        findings,
        risks,
        facts,
        attack_paths,
    ) -> ExecutiveMetrics:

        asset_count = len(assets) if assets else 0

        findings_by_severity: Dict[str, int] = {}

        for finding in findings:

            severity = finding.severity.value

            findings_by_severity[severity] = findings_by_severity.get(severity, 0) + 1

        risks_by_priority: Dict[str, int] = {}

        risk_scores: List[int] = []

        for risk in risks:

            priority = risk.priority.value

            risks_by_priority[priority] = risks_by_priority.get(priority, 0) + 1

            risk_scores.append(risk.score)

        average_risk = (

            sum(risk_scores) / len(risk_scores)

            if risk_scores

            else 0.0

        )

        highest_risk = max(risk_scores) if risk_scores else 0

        facts_by_category: Dict[str, int] = {}

        for fact in facts:

            category = fact.category

            facts_by_category[category] = facts_by_category.get(category, 0) + 1

        internet_exposed = sum(

            1 for risk in risks

            if "public" in risk.explanation.lower()

        )

        identity_risks = sum(1 for risk in risks if risk.category == "IAM")

        storage_risks = sum(1 for risk in risks if risk.category == "Storage")

        network_risks = sum(1 for risk in risks if risk.category == "Network")

        logging_risks = sum(1 for risk in risks if risk.category == "Logging")

        compute_risks = sum(1 for risk in risks if risk.category == "Compute")

        assets_by_type: Dict[str, int] = {}

        assets_by_provider: Dict[str, int] = {}

        for asset in assets:

            resource_type = getattr(asset, "resource_type", "Unknown")

            provider = getattr(asset, "properties", {}).get("cloud", "unknown")

            assets_by_type[resource_type] = assets_by_type.get(resource_type, 0) + 1

            assets_by_provider[provider] = assets_by_provider.get(provider, 0) + 1

        return ExecutiveMetrics(
            total_assets=asset_count,
            assets_by_provider=assets_by_provider,
            assets_by_type=assets_by_type,
            facts_by_category=facts_by_category,
            findings_by_severity=findings_by_severity,
            risks_by_priority=risks_by_priority,
            average_risk=round(average_risk, 2),
            highest_risk=highest_risk,
            internet_exposed_assets=internet_exposed,
            identity_risks=identity_risks,
            storage_risks=storage_risks,
            network_risks=network_risks,
            logging_risks=logging_risks,
            compute_risks=compute_risks,
        )


class InsightBuilder(IInsightBuilder):

    def build(
        self,
        risks,
        findings,
        facts,
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


class RecommendationBuilder(IRecommendationBuilder):

    def build(
        self,
        risks,
        findings,
        facts,
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


class NarrativeBuilder(INarrativeBuilder):

    def __init__(self, strategy=None):

        self.strategy = strategy

    def build(self, dashboard: ExecutiveSummary) -> ExecutiveNarrative:

        if self.strategy:

            return self.strategy.generate_narrative(dashboard)

        score = dashboard.security_score

        total_assets = dashboard.total_assets

        total_findings = dashboard.total_findings

        total_risks = dashboard.total_risks

        summary = (
            f"CloudSentinel analyzed {total_assets} cloud assets and identified "
            f"{total_findings} findings, resulting in {total_risks} prioritized risks. "
            f"The environment currently has a Security Score of {score.overall} "
            f"(Grade {score.grade})."
        )

        top_risks = dashboard.top_risks[:3]

        if top_risks:

            risk_descriptions = [

                f"{risk.finding_id} (score: {risk.score}, priority: {risk.priority.value})"

                for risk in top_risks

            ]

            top_risks_summary = "Top risks: " + "; ".join(risk_descriptions) + "."

        else:

            top_risks_summary = "No critical risks were identified."

        recommendations = dashboard.recommendations[:3]

        if recommendations:

            rec_descriptions = [

                f"{rec.title} (expected improvement: +{rec.expected_score_improvement})"

                for rec in recommendations

            ]

            recommendation_summary = "Top recommendations: " + "; ".join(rec_descriptions) + "."

        else:

            recommendation_summary = "No immediate recommendations available."

        dimensions = dashboard.dimensions.to_dict()

        dimension_descriptions = [

            f"{dimension}: {value}/100"

            for dimension, value in dimensions.items()

            if dimension != "overall"

        ]

        score_explanation = (
            f"Security Score breakdown: {', '.join(dimension_descriptions)}. "
            f"Overall score derived from dimension averages with deductions "
            f"applied for identified risks."
        )

        return ExecutiveNarrative(
            summary=summary,
            top_risks_summary=top_risks_summary,
            recommendation_summary=recommendation_summary,
            score_explanation=score_explanation,
            metadata={"strategy": "DefaultNarrativeStrategy"},
        )


class DashboardBuilder(IDashboardBuilder):

    def build(
        self,
        summary: ExecutiveSummary,
        security_score,
        dimensions,
        breakdown,
        metrics: ExecutiveMetrics,
        risks: List[Risk],
        recommendations: List[Recommendation],
        insights: List[Insight],
        narrative: ExecutiveNarrative,
    ) -> ExecutiveDashboard:

        top_risks = risks[:5] if risks else []

        return ExecutiveDashboard(
            summary=summary,
            security_score=security_score,
            security_dimensions=dimensions,
            score_breakdown=breakdown,
            metrics=metrics,
            top_risks=top_risks,
            recommendations=recommendations,
            insights=insights,
            executive_narrative=narrative,
        )
