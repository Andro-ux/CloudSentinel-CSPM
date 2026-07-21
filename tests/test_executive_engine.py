import sys
sys.path.insert(0, r'C:\Users\vinit\Desktop\CloudSentinel_phase3\CloudSentinel')

import pytest
from datetime import datetime

from backend.correlation.asset_index import AssetIndex
from backend.correlation.builders.relationship_builder import RelationshipBuilder
from backend.correlation.graph_builder import GraphBuilder
from backend.correlation.relationship_mapper import RelationshipMapper
from backend.executive.engine import ExecutiveEngine
from backend.executive.exceptions import DashboardBuildError, EmptyScanError, InvalidScoreStrategy
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
    grade_from_score,
)
from backend.executive.strategies.weighted_score import ScoreWeights, WeightedScoreStrategy
from backend.facts.engine import FactEngine
from backend.facts.extractors.compute import ComputeFactsExtractor
from backend.facts.extractors.iam import IAMFactsExtractor
from backend.facts.extractors.logging import LoggingFactsExtractor
from backend.facts.extractors.network import NetworkFactsExtractor
from backend.facts.extractors.storage import StorageFactsExtractor
from backend.facts.registry import FactRegistry
from backend.knowledge.engine import KnowledgeEngine
from backend.risk.engine import RiskEngine
from backend.rules.engine import RuleEngine
from backend.risk.models import Priority, Risk, RiskSet
from backend.rules.models import Finding, FindingSet, RuleMetadata, Severity
from backend.rules.registry import RuleRegistry
from backend.rules.rules.admin_service_account import AdminServiceAccountRule
from backend.rules.rules.audit_logs import AuditLoggingRule
from backend.rules.rules.flow_logs import FlowLogsRule
from backend.rules.rules.metadata_service import MetadataServiceRule
from backend.rules.rules.open_firewall import OpenFirewallRule
from backend.rules.rules.public_bucket import PublicBucketRule
from backend.rules.rules.public_vm import PublicVMRule
from backend.rules.rules.shielded_vm import ShieldedVMRule
from backend.rules.rules.unused_service_account import UnusedServiceAccountRule
from backend.providers.mock_provider import MockProvider


@pytest.fixture
def full_scan_result():
    provider = MockProvider()
    assets = provider.get_assets()
    graph_builder = GraphBuilder()
    graph_builder.add_assets(assets)
    relationships = RelationshipMapper().map(graph_builder.index)
    graph = graph_builder.build(relationships)
    knowledge = KnowledgeEngine(graph)

    fact_registry = FactRegistry()
    fact_registry.register(NetworkFactsExtractor())
    fact_registry.register(ComputeFactsExtractor())
    fact_registry.register(StorageFactsExtractor())
    fact_registry.register(IAMFactsExtractor())
    fact_registry.register(LoggingFactsExtractor())
    fact_engine = FactEngine(knowledge, fact_registry)
    fact_set = fact_engine.extract()

    rule_registry = RuleRegistry()
    rule_registry.register(PublicVMRule())
    rule_registry.register(PublicBucketRule())
    rule_registry.register(OpenFirewallRule())
    rule_registry.register(ShieldedVMRule())
    rule_registry.register(MetadataServiceRule())
    rule_registry.register(AdminServiceAccountRule())
    rule_registry.register(UnusedServiceAccountRule())
    rule_registry.register(FlowLogsRule())
    rule_registry.register(AuditLoggingRule())
    rule_engine = RuleEngine(rule_registry)
    finding_set = rule_engine.evaluate(fact_set)

    risk_engine = RiskEngine()
    risk_set = risk_engine.evaluate(finding_set)

    engine = ExecutiveEngine()
    dashboard = engine.build_dashboard(
        knowledge=knowledge,
        fact_set=fact_set,
        finding_set=finding_set,
        risk_set=risk_set,
        assets=assets,
    )
    return dashboard


class TestGradeFromScore:

    def test_grade_a(self):
        assert grade_from_score(100) == "A"
        assert grade_from_score(90) == "A"
        assert grade_from_score(95) == "A"

    def test_grade_b(self):
        assert grade_from_score(89) == "B"
        assert grade_from_score(80) == "B"

    def test_grade_c(self):
        assert grade_from_score(79) == "C"
        assert grade_from_score(70) == "C"

    def test_grade_d(self):
        assert grade_from_score(69) == "D"
        assert grade_from_score(60) == "D"

    def test_grade_f(self):
        assert grade_from_score(59) == "F"
        assert grade_from_score(0) == "F"


class TestScoreBreakdown:

    def test_total_deductions(self):
        breakdown = ScoreBreakdown(
            base_score=100,
            deductions={"network": 10, "identity": 5},
        )
        assert breakdown.total_deductions() == 15

    def test_final_score(self):
        breakdown = ScoreBreakdown(
            base_score=100,
            deductions={"network": 10, "identity": 5},
        )
        assert breakdown.final_score() == 85

    def test_final_score_floor_at_zero(self):
        breakdown = ScoreBreakdown(
            base_score=100,
            deductions={"network": 150},
        )
        assert breakdown.final_score() == 0

    def test_empty_deductions(self):
        breakdown = ScoreBreakdown()
        assert breakdown.total_deductions() == 0
        assert breakdown.final_score() == 100


class TestSecurityDimensions:

    def test_dimension_scores(self):
        dimensions = SecurityDimensions(
            network=90, identity=80, storage=70, logging=60, compute=50
        )
        assert dimensions.network == 90
        assert dimensions.identity == 80
        assert dimensions.storage == 70

    def test_to_dict(self):
        dimensions = SecurityDimensions(network=90, identity=80)
        d = dimensions.to_dict()
        assert d["network"] == 90
        assert d["identity"] == 80


class TestSecurityScore:

    def test_security_score_creation(self):
        score = SecurityScore(
            overall=85,
            dimensions=SecurityDimensions(network=90, identity=80),
            breakdown=ScoreBreakdown(base_score=100, deductions={"network": 10}),
            grade="B",
        )
        assert score.overall == 85
        assert score.grade == "B"

    def test_to_dict(self):
        score = SecurityScore(
            overall=85,
            dimensions=SecurityDimensions(network=90, identity=80),
            breakdown=ScoreBreakdown(base_score=100, deductions={"network": 10}),
            grade="B",
        )
        d = score.to_dict()
        assert d["overall"] == 85
        assert d["grade"] == "B"
        assert "dimensions" in d
        assert "breakdown" in d


class TestExecutiveMetrics:

    def test_metrics_creation(self):
        metrics = ExecutiveMetrics(
            total_assets=10,
            findings_by_severity={"HIGH": 2},
            risks_by_priority={"HIGH": 1},
            average_risk=45.5,
            highest_risk=80,
        )
        assert metrics.total_assets == 10
        assert metrics.average_risk == 45.5

    def test_to_dict(self):
        metrics = ExecutiveMetrics(total_assets=5)
        d = metrics.to_dict()
        assert d["total_assets"] == 5


class TestInsight:

    def test_insight_creation(self):
        insight = Insight(
            id="insight-1",
            title="Test Insight",
            description="Description",
            severity="HIGH",
            category="Network",
            business_impact="High impact",
            recommendation="Fix it",
        )
        assert insight.id == "insight-1"
        assert insight.related_risks == []

    def test_to_dict(self):
        insight = Insight(
            id="insight-1",
            title="Test",
            description="Desc",
            severity="HIGH",
            category="Network",
            business_impact="Impact",
            recommendation="Fix",
        )
        d = insight.to_dict()
        assert d["id"] == "insight-1"
        assert d["severity"] == "HIGH"


class TestRecommendation:

    def test_recommendation_creation(self):
        rec = Recommendation(
            title="Test Rec",
            priority="HIGH",
            description="Description",
            affected_assets=["asset-1"],
            expected_score_improvement=10,
        )
        assert rec.title == "Test Rec"
        assert rec.expected_score_improvement == 10

    def test_to_dict(self):
        rec = Recommendation(
            title="Test",
            priority="HIGH",
            description="Desc",
        )
        d = rec.to_dict()
        assert d["title"] == "Test"
        assert d["priority"] == "HIGH"


class TestExecutiveNarrative:

    def test_narrative_creation(self):
        narrative = ExecutiveNarrative(
            summary="Summary",
            top_risks_summary="Risks",
            recommendation_summary="Recs",
            score_explanation="Score",
        )
        assert narrative.summary == "Summary"

    def test_to_dict(self):
        narrative = ExecutiveNarrative(
            summary="Summary",
            top_risks_summary="Risks",
            recommendation_summary="Recs",
            score_explanation="Score",
        )
        d = narrative.to_dict()
        assert d["summary"] == "Summary"
        assert "metadata" in d


class TestExecutiveSummary:

    def test_summary_creation(self, full_scan_result):
        summary = full_scan_result.summary
        assert summary.total_assets >= 0
        assert isinstance(summary.security_score, SecurityScore)


class TestExecutiveDashboard:

    def test_dashboard_creation(self, full_scan_result):
        assert isinstance(full_scan_result, ExecutiveDashboard)
        assert full_scan_result.security_score is not None
        assert full_scan_result.metrics is not None
        assert full_scan_result.insights is not None
        assert full_scan_result.recommendations is not None
        assert full_scan_result.executive_narrative is not None

    def test_dashboard_to_dict(self, full_scan_result):
        d = full_scan_result.to_dict()
        assert "security_score" in d
        assert "metrics" in d
        assert "insights" in d
        assert "recommendations" in d
        assert "executive_narrative" in d
        assert "generated_at" in d


class TestWeightedScoreStrategy:

    def test_calculate_score_returns_security_score(self):
        strategy = WeightedScoreStrategy()
        score = strategy.calculate_score([], [], [], [])
        assert isinstance(score, SecurityScore)

    def test_score_with_findings(self):
        strategy = WeightedScoreStrategy()
        finding = _make_finding(Severity.HIGH, "Test", ["asset-1"], category="Network")
        score = strategy.calculate_score([finding], [], [], [])
        assert isinstance(score, SecurityScore)
        assert score.overall <= 100
        assert score.overall >= 0

    def test_score_with_custom_weights(self):
        weights = ScoreWeights(
            network_deduction=20,
            identity_deduction=15,
        )
        strategy = WeightedScoreStrategy(weights)
        score = strategy.calculate_score([], [], [], [])
        assert isinstance(score, SecurityScore)

    def test_score_breakdown_created(self):
        strategy = WeightedScoreStrategy()
        score = strategy.calculate_score([], [], [], [])
        assert isinstance(score.breakdown, ScoreBreakdown)

    def test_dimensions_created(self):
        strategy = WeightedScoreStrategy()
        score = strategy.calculate_score([], [], [], [])
        assert isinstance(score.dimensions, SecurityDimensions)

    def test_grade_assigned(self):
        strategy = WeightedScoreStrategy()
        score = strategy.calculate_score([], [], [], [])
        assert score.grade in ["A", "B", "C", "D", "F"]

    def test_empty_inputs(self):
        strategy = WeightedScoreStrategy()
        score = strategy.calculate_score([], [], [], [])
        assert score.overall == 100
        assert score.grade == "A"


class TestMetricsBuilder:

    def test_build_metrics(self):
        from backend.executive.builders import MetricsBuilder
        builder = MetricsBuilder()
        assets = [_make_asset("asset-1", "Compute", "VM")]
        finding = _make_finding(Severity.HIGH, "Test", ["asset-1"], category="Network")
        finding_set = FindingSet([finding])
        risk = _make_risk(Severity.HIGH, ["asset-1"], category="Network")
        risk_set = RiskSet([risk])
        metrics = builder.build(assets, finding_set, risk_set, FindingSet([]), [])
        assert isinstance(metrics, ExecutiveMetrics)
        assert metrics.total_assets == 1
        assert metrics.network_risks == 1

    def test_metrics_empty(self):
        from backend.executive.builders import MetricsBuilder
        builder = MetricsBuilder()
        metrics = builder.build([], FindingSet([]), RiskSet([]), FindingSet([]), [])
        assert metrics.total_assets == 0
        assert metrics.average_risk == 0.0


class TestInsightBuilder:

    def test_build_insights(self):
        from backend.executive.insights import InsightBuilder
        builder = InsightBuilder()
        risk = _make_risk(Severity.HIGH, ["asset-1"], category="Network")
        risk_set = RiskSet([risk])
        insights = builder.build(risk_set, FindingSet([]), FindingSet([]))
        assert len(insights) >= 1
        assert isinstance(insights[0], Insight)

    def test_no_duplicate_insights(self):
        from backend.executive.insights import InsightBuilder
        builder = InsightBuilder()
        risk = _make_risk(Severity.HIGH, ["asset-1"], category="Network")
        risk_set = RiskSet([risk, risk])
        insights = builder.build(risk_set, FindingSet([]), FindingSet([]))
        titles = [i.title for i in insights]
        assert len(titles) == len(set(titles))


class TestRecommendationBuilder:

    def test_build_recommendations(self):
        from backend.executive.recommendations import RecommendationBuilder
        builder = RecommendationBuilder()
        risk = _make_risk(Severity.HIGH, ["asset-1"], category="Network")
        risk_set = RiskSet([risk])
        recs = builder.build(risk_set, FindingSet([]), FindingSet([]))
        assert len(recs) >= 1
        assert isinstance(recs[0], Recommendation)

    def test_recommendations_sorted_by_impact(self):
        from backend.executive.recommendations import RecommendationBuilder
        builder = RecommendationBuilder()
        risk1 = _make_risk(Severity.HIGH, ["asset-1"], category="Network", score=90)
        risk2 = _make_risk(Severity.LOW, ["asset-2"], category="Storage", score=10)
        risk_set = RiskSet([risk1, risk2])
        recs = builder.build(risk_set, FindingSet([]), FindingSet([]))
        improvements = [r.expected_score_improvement for r in recs]
        assert improvements == sorted(improvements, reverse=True)


class TestNarrativeBuilder:

    def test_build_narrative(self, full_scan_result):
        from backend.executive.narrative import NarrativeBuilder
        builder = NarrativeBuilder()
        narrative = builder.build(full_scan_result)
        assert isinstance(narrative, ExecutiveNarrative)
        assert narrative.summary != ""

    def test_custom_strategy(self):
        from backend.executive.narrative import NarrativeBuilder
        from backend.executive.strategies.narrative import INarrativeStrategy

        class CustomStrategy(INarrativeStrategy):
            def generate_narrative(self, dashboard):
                return ExecutiveNarrative(
                    summary="Custom",
                    top_risks_summary="Custom",
                    recommendation_summary="Custom",
                    score_explanation="Custom",
                )

        builder = NarrativeBuilder(CustomStrategy())
        dashboard = ExecutiveDashboard(
            summary=ExecutiveSummary(
                total_assets=1,
                total_findings=1,
                total_facts=1,
                total_risks=1,
                security_score=SecurityScore(
                    overall=100,
                    dimensions=SecurityDimensions(),
                    breakdown=ScoreBreakdown(),
                    grade="A",
                ),
                top_risks=[],
                dimensions=SecurityDimensions(),
                metrics=ExecutiveMetrics(),
                insights=[],
                recommendations=[],
                narrative=ExecutiveNarrative("", "", "", ""),
            ),
            security_score=SecurityScore(
                overall=100,
                dimensions=SecurityDimensions(),
                breakdown=ScoreBreakdown(),
                grade="A",
            ),
            security_dimensions=SecurityDimensions(),
            score_breakdown=ScoreBreakdown(),
            metrics=ExecutiveMetrics(),
            top_risks=[],
            recommendations=[],
            insights=[],
            executive_narrative=ExecutiveNarrative("", "", "", ""),
        )
        narrative = builder.build(dashboard)
        assert narrative.summary == "Custom"


class TestDashboardBuilder:

    def test_build_dashboard(self):
        from backend.executive.builders import DashboardBuilder
        builder = DashboardBuilder()
        summary = ExecutiveSummary(
            total_assets=1,
            total_findings=1,
            total_facts=1,
            total_risks=1,
            security_score=SecurityScore(
                overall=100,
                dimensions=SecurityDimensions(),
                breakdown=ScoreBreakdown(),
                grade="A",
            ),
            top_risks=[],
            dimensions=SecurityDimensions(),
            metrics=ExecutiveMetrics(),
            insights=[],
            recommendations=[],
            narrative=ExecutiveNarrative("", "", "", ""),
        )
        dashboard = builder.build(
            summary=summary,
            security_score=summary.security_score,
            dimensions=summary.dimensions,
            breakdown=summary.security_score.breakdown,
            metrics=summary.metrics,
            risks=[],
            recommendations=[],
            insights=[],
            narrative=summary.narrative,
        )
        assert isinstance(dashboard, ExecutiveDashboard)
        assert dashboard.security_score == summary.security_score


class TestExecutiveEngine:

    def test_build_dashboard_returns_dashboard(self, full_scan_result):
        assert isinstance(full_scan_result, ExecutiveDashboard)

    def test_build_dashboard_with_empty_scan(self):
        engine = ExecutiveEngine()
        dashboard = engine.build_dashboard(
            knowledge=None,
            fact_set=FindingSet([]),
            finding_set=FindingSet([]),
            risk_set=RiskSet([]),
            assets=[],
        )
        assert isinstance(dashboard, ExecutiveDashboard)
        assert dashboard.summary.total_assets == 0
        assert dashboard.summary.total_risks == 0

    def test_build_dashboard_with_custom_strategy(self):
        strategy = WeightedScoreStrategy(ScoreWeights(network_deduction=20))
        engine = ExecutiveEngine(score_strategy=strategy)
        provider = MockProvider()
        assets = provider.get_assets()
        graph_builder = GraphBuilder()
        graph_builder.add_assets(assets)
        relationships = RelationshipMapper().map(graph_builder.index)
        graph = graph_builder.build(relationships)
        knowledge = KnowledgeEngine(graph)

        fact_registry = FactRegistry()
        fact_registry.register(NetworkFactsExtractor())
        fact_registry.register(ComputeFactsExtractor())
        fact_registry.register(StorageFactsExtractor())
        fact_registry.register(IAMFactsExtractor())
        fact_registry.register(LoggingFactsExtractor())
        fact_engine = FactEngine(knowledge, fact_registry)
        fact_set = fact_engine.extract()

        rule_registry = RuleRegistry()
        rule_registry.register(PublicVMRule())
        rule_registry.register(PublicBucketRule())
        rule_registry.register(OpenFirewallRule())
        rule_registry.register(ShieldedVMRule())
        rule_registry.register(MetadataServiceRule())
        rule_registry.register(AdminServiceAccountRule())
        rule_registry.register(UnusedServiceAccountRule())
        rule_registry.register(FlowLogsRule())
        rule_registry.register(AuditLoggingRule())
        rule_engine = RuleEngine(rule_registry)
        finding_set = rule_engine.evaluate(fact_set)

        risk_engine = RiskEngine()
        risk_set = risk_engine.evaluate(finding_set)

        dashboard = engine.build_dashboard(
            knowledge=knowledge,
            fact_set=fact_set,
            finding_set=finding_set,
            risk_set=risk_set,
            assets=assets,
        )
        assert isinstance(dashboard, ExecutiveDashboard)


class TestImmutability:

    def test_dashboard_is_immutable(self, full_scan_result):
        with pytest.raises(AttributeError):
            full_scan_result.security_score = None

    def test_metrics_immutable(self, full_scan_result):
        with pytest.raises(AttributeError):
            full_scan_result.metrics.total_assets = 999

    def test_narrative_immutable(self, full_scan_result):
        with pytest.raises(AttributeError):
            full_scan_result.executive_narrative.summary = "changed"


class TestSerialization:

    def test_dashboard_to_dict(self, full_scan_result):
        d = full_scan_result.to_dict()
        assert isinstance(d, dict)
        assert "security_score" in d
        assert "metrics" in d
        assert "insights" in d
        assert "recommendations" in d
        assert "executive_narrative" in d

    def test_metrics_to_dict(self, full_scan_result):
        d = full_scan_result.metrics.to_dict()
        assert isinstance(d, dict)
        assert "total_assets" in d
        assert "risks_by_priority" in d

    def test_insight_to_dict(self, full_scan_result):
        if full_scan_result.insights:
            d = full_scan_result.insights[0].to_dict()
            assert isinstance(d, dict)
            assert "id" in d
            assert "title" in d

    def test_recommendation_to_dict(self, full_scan_result):
        if full_scan_result.recommendations:
            d = full_scan_result.recommendations[0].to_dict()
            assert isinstance(d, dict)
            assert "title" in d
            assert "priority" in d

    def test_narrative_to_dict(self, full_scan_result):
        d = full_scan_result.executive_narrative.to_dict()
        assert isinstance(d, dict)
        assert "summary" in d
        assert "top_risks_summary" in d


class TestIntegrationWithRiskEngine:

    def test_dashboard_reflects_risks(self, full_scan_result):
        assert full_scan_result.summary.total_risks >= 0

    def test_top_risks_populated(self, full_scan_result):
        assert len(full_scan_result.top_risks) <= 5

    def test_recommendations_linked_to_risks(self, full_scan_result):
        for rec in full_scan_result.recommendations:
            assert isinstance(rec.related_risks, list)

    def test_insights_linked_to_risks(self, full_scan_result):
        for insight in full_scan_result.insights:
            assert isinstance(insight.related_risks, list)

    def test_metrics_reflect_findings(self, full_scan_result):
        total_findings = sum(full_scan_result.metrics.findings_by_severity.values())
        assert total_findings == full_scan_result.summary.total_findings


class TestWidgetModels:

    def test_security_score_widget_data(self, full_scan_result):
        score_dict = full_scan_result.security_score.to_dict()
        assert "overall" in score_dict
        assert "grade" in score_dict
        assert "dimensions" in score_dict
        assert "breakdown" in score_dict

    def test_dimension_widget_data(self, full_scan_result):
        dim_dict = full_scan_result.security_dimensions.to_dict()
        assert "network" in dim_dict
        assert "identity" in dim_dict
        assert "storage" in dim_dict
        assert "overall" in dim_dict

    def test_risk_distribution_widget_data(self, full_scan_result):
        risk_dist = full_scan_result.metrics.risks_by_priority
        assert isinstance(risk_dist, dict)

    def test_top_risk_widget_data(self, full_scan_result):
        for risk in full_scan_result.top_risks:
            assert hasattr(risk, "id")
            assert hasattr(risk, "score")
            assert hasattr(risk, "priority")

    def test_recommendation_widget_data(self, full_scan_result):
        for rec in full_scan_result.recommendations:
            assert hasattr(rec, "title")
            assert hasattr(rec, "priority")
            assert hasattr(rec, "expected_score_improvement")


class TestEdgeCases:

    def test_empty_findings(self):
        engine = ExecutiveEngine()
        dashboard = engine.build_dashboard(
            knowledge=None,
            fact_set=FindingSet([]),
            finding_set=FindingSet([]),
            risk_set=RiskSet([]),
            assets=[],
        )
        assert isinstance(dashboard, ExecutiveDashboard)

    def test_large_scan(self):
        assets = [_make_asset(f"asset-{i}", "Compute", "VM") for i in range(100)]
        findings = [
            _make_finding(Severity.HIGH, f"Finding {i}", [f"asset-{i}"], category="Network")
            for i in range(100)
        ]
        risks = [_make_risk(Severity.HIGH, [f"asset-{i}"], category="Network") for i in range(100)]
        engine = ExecutiveEngine()
        dashboard = engine.build_dashboard(
            knowledge=None,
            fact_set=FindingSet([]),
            finding_set=FindingSet(findings),
            risk_set=RiskSet(risks),
            assets=assets,
        )
        assert isinstance(dashboard, ExecutiveDashboard)
        assert dashboard.metrics.total_assets == 100


class TestStrategyReplacement:

    def test_replace_score_strategy(self):
        strategy = WeightedScoreStrategy(ScoreWeights(network_deduction=5))
        engine = ExecutiveEngine(score_strategy=strategy)
        assert engine.score_strategy == strategy

    def test_replace_narrative_strategy(self):
        from backend.executive.strategies.narrative import INarrativeStrategy

        class CustomStrategy(INarrativeStrategy):
            def generate_narrative(self, dashboard):
                return ExecutiveNarrative(
                    summary="Custom",
                    top_risks_summary="Custom",
                    recommendation_summary="Custom",
                    score_explanation="Custom",
                )

        strategy = CustomStrategy()
        engine = ExecutiveEngine(narrative_strategy=strategy)
        assert engine.narrative_strategy == strategy


class TestEndToEndIntegration:

    def test_full_scan_with_dashboard(self):
        from backend.services.scan_service import ScanService
        service = ScanService()
        result = service.run_scan()
        assert result.dashboard is not None
        assert isinstance(result.dashboard, ExecutiveDashboard)
        assert result.dashboard.security_score is not None
        assert result.dashboard.metrics is not None

    def test_dashboard_generated_at(self):
        from backend.services.scan_service import ScanService
        service = ScanService()
        result = service.run_scan()
        assert result.dashboard.generated_at is not None
        assert isinstance(result.dashboard.generated_at, datetime)


def _make_asset(asset_id, service, resource_type):
    from backend.correlation.models import AssetNode
    return AssetNode(
        id=asset_id,
        service=service,
        resource_type=resource_type,
        name=asset_id,
        properties={"cloud": "gcp"},
    )


def _make_finding(severity, title, asset_ids, category="Network", recommendation="Fix it"):
    return Finding(
        id=f"finding-{'-'.join(asset_ids)}",
        rule_id="CS-RULE-001",
        title=title,
        description=f"Description for {title}",
        severity=severity,
        category=category,
        asset_ids=asset_ids,
        facts=[],
        recommendation=recommendation,
        references=[],
        evidence={},
    )


def _make_risk(severity, asset_ids, category="Network", score=50):
    from backend.risk.models import Priority, Risk, RiskSet, Priority
    return Risk(
        id=f"risk-{'-'.join(asset_ids)}",
        finding_id=f"finding-{'-'.join(asset_ids)}",
        asset_ids=asset_ids,
        score=score,
        priority=Priority.LOW,
        category=category,
        severity=severity.value,
        explanation=f"Risk explanation for {asset_ids}",
        contributing_factors=[],
        recommendation="Fix it",
    )
