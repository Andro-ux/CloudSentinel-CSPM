from datetime import datetime
from typing import Dict, List, Optional

from backend.executive.builders import (
    DashboardBuilder,
    InsightBuilder,
    MetricsBuilder,
    NarrativeBuilder,
    RecommendationBuilder,
)
from backend.executive.exceptions import DashboardBuildError, EmptyScanError, InvalidScoreStrategy
from backend.executive.interfaces import (
    IDashboardBuilder,
    IInsightBuilder,
    INarrativeBuilder,
    INarrativeStrategy,
    IMetricsBuilder,
    IRecommendationBuilder,
    IScoreStrategy,
)
from backend.executive.models import (
    ExecutiveDashboard,
    ExecutiveMetrics,
    ExecutiveNarrative,
    ExecutiveSummary,
    Insight,
    Recommendation,
    SecurityDimensions,
    SecurityScore,
    ScoreBreakdown,
)
from backend.executive.strategies.narrative import DefaultNarrativeStrategy
from backend.executive.strategies.weighted_score import WeightedScoreStrategy
from backend.facts.models import FactSet
from backend.knowledge.interfaces import IKnowledgeEngine
from backend.rules.models import FindingSet
from backend.risk.models import RiskSet


class ExecutiveEngine:

    def __init__(
        self,
        score_strategy: IScoreStrategy = None,
        narrative_strategy: INarrativeStrategy = None,
        metrics_builder: IMetricsBuilder = None,
        insight_builder: IInsightBuilder = None,
        recommendation_builder: IRecommendationBuilder = None,
        narrative_builder: INarrativeBuilder = None,
        dashboard_builder: IDashboardBuilder = None,
    ):

        self.score_strategy = score_strategy or WeightedScoreStrategy()

        self.narrative_strategy = narrative_strategy or DefaultNarrativeStrategy()

        self.metrics_builder = metrics_builder or MetricsBuilder()

        self.insight_builder = insight_builder or InsightBuilder()

        self.recommendation_builder = recommendation_builder or RecommendationBuilder()

        self.narrative_builder = narrative_builder or NarrativeBuilder(narrative_strategy)

        self.dashboard_builder = dashboard_builder or DashboardBuilder()

    def build_dashboard(
        self,
        knowledge: IKnowledgeEngine,
        fact_set: FactSet,
        finding_set: FindingSet,
        risk_set: RiskSet,
        assets,
    ) -> ExecutiveDashboard:

        asset_list = list(assets) if assets else []

        finding_list = list(finding_set) if finding_set else []

        risk_list = list(risk_set) if risk_set else []

        if not asset_list and not finding_list and not risk_list:

            return self._build_empty_dashboard(fact_set)

        try:

            security_score = self.score_strategy.calculate_score(
                findings=finding_set.findings if finding_set else [],
                risks=risk_set.risks if risk_set else [],
                facts=fact_set.facts if fact_set else [],
                assets=assets,
            )

        except Exception as exc:

            raise InvalidScoreStrategy(self.score_strategy.__class__.__name__)

        dimensions = security_score.dimensions

        breakdown = security_score.breakdown

        try:

            metrics = self.metrics_builder.build(
                assets=assets or [],
                findings=finding_set,
                risks=risk_set,
                facts=fact_set,
                attack_paths=[],
            )

        except Exception as exc:

            raise DashboardBuildError("MetricsBuilder", exc)

        try:

            insights = self.insight_builder.build(
                risks=risk_set,
                findings=finding_set,
                facts=fact_set,
            )

        except Exception as exc:

            raise DashboardBuildError("InsightBuilder", exc)

        try:

            recommendations = self.recommendation_builder.build(
                risks=risk_set,
                findings=finding_set,
                facts=fact_set,
            )

        except Exception as exc:

            raise DashboardBuildError("RecommendationBuilder", exc)

        summary = ExecutiveSummary(
            total_assets=metrics.total_assets,
            total_findings=len(finding_set) if finding_set else 0,
            total_facts=len(fact_set) if fact_set else 0,
            total_risks=len(risk_set) if risk_set else 0,
            security_score=security_score,
            top_risks=risk_set.top_n(5) if risk_set else [],
            dimensions=dimensions,
            metrics=metrics,
            insights=insights,
            recommendations=recommendations,
            narrative=ExecutiveNarrative(
                summary="",
                top_risks_summary="",
                recommendation_summary="",
                score_explanation="",
            ),
        )

        try:

            narrative = self.narrative_builder.build(summary)

        except Exception as exc:

            raise DashboardBuildError("NarrativeBuilder", exc)

        summary_with_narrative = ExecutiveSummary(
            total_assets=summary.total_assets,
            total_findings=summary.total_findings,
            total_facts=summary.total_facts,
            total_risks=summary.total_risks,
            security_score=summary.security_score,
            top_risks=summary.top_risks,
            dimensions=summary.dimensions,
            metrics=summary.metrics,
            insights=summary.insights,
            recommendations=summary.recommendations,
            narrative=narrative,
            generated_at=summary.generated_at,
            metadata=summary.metadata,
        )

        try:

            dashboard = self.dashboard_builder.build(
                summary=summary_with_narrative,
                security_score=security_score,
                dimensions=dimensions,
                breakdown=breakdown,
                metrics=metrics,
                risks=risk_set.risks if risk_set else [],
                recommendations=recommendations,
                insights=insights,
                narrative=narrative,
            )

        except Exception as exc:

            raise DashboardBuildError("DashboardBuilder", exc)

        return dashboard

    def _build_empty_dashboard(self, fact_set) -> ExecutiveDashboard:

        empty_score = SecurityScore(
            overall=100,
            dimensions=SecurityDimensions(),
            breakdown=ScoreBreakdown(),
            grade="A",
        )

        empty_metrics = ExecutiveMetrics()

        empty_narrative = ExecutiveNarrative(
            summary="No cloud assets were analyzed.",
            top_risks_summary="No risks were identified.",
            recommendation_summary="No recommendations available.",
            score_explanation="Security Score is 100 because no risks were found.",
        )

        empty_summary = ExecutiveSummary(
            total_assets=0,
            total_findings=0,
            total_facts=len(fact_set) if fact_set else 0,
            total_risks=0,
            security_score=empty_score,
            top_risks=[],
            dimensions=SecurityDimensions(),
            metrics=empty_metrics,
            insights=[],
            recommendations=[],
            narrative=empty_narrative,
        )

        return ExecutiveDashboard(
            summary=empty_summary,
            security_score=empty_score,
            security_dimensions=SecurityDimensions(),
            score_breakdown=ScoreBreakdown(),
            metrics=empty_metrics,
            top_risks=[],
            recommendations=[],
            insights=[],
            executive_narrative=empty_narrative,
        )
