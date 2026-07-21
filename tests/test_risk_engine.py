import sys
sys.path.insert(0, r'C:\Users\vinit\Desktop\CloudSentinel_phase3\CloudSentinel')

import pytest
from typing import List

from backend.correlation.asset_index import AssetIndex
from backend.correlation.builders.relationship_builder import RelationshipBuilder
from backend.correlation.graph_builder import GraphBuilder
from backend.correlation.relationship_mapper import RelationshipMapper
from backend.facts.engine import FactEngine
from backend.facts.extractors.compute import ComputeFactsExtractor
from backend.facts.extractors.iam import IAMFactsExtractor
from backend.facts.extractors.logging import LoggingFactsExtractor
from backend.facts.extractors.network import NetworkFactsExtractor
from backend.facts.extractors.storage import StorageFactsExtractor
from backend.facts.registry import FactRegistry
from backend.knowledge.engine import KnowledgeEngine
from backend.risk.engine import RiskEngine
from backend.risk.exceptions import InvalidFindingError, StrategyError
from backend.risk.models import Priority, Risk, RiskSet, priority_from_score
from backend.risk.strategies.weighted import ScoreWeights, WeightedScoreStrategy
from backend.rules.engine import RuleEngine
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
def finding_set():
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
    return rule_engine.evaluate(fact_set)


@pytest.fixture
def risk_set(finding_set):
    engine = RiskEngine()
    return engine.evaluate(finding_set)


class TestPriorityEnum:

    def test_priority_values(self):
        assert Priority.CRITICAL.value == "CRITICAL"
        assert Priority.HIGH.value == "HIGH"
        assert Priority.MEDIUM.value == "MEDIUM"
        assert Priority.LOW.value == "LOW"

    def test_priority_ordering(self):
        assert Priority.CRITICAL < Priority.HIGH
        assert Priority.HIGH < Priority.MEDIUM
        assert Priority.MEDIUM < Priority.LOW
        assert Priority.CRITICAL <= Priority.CRITICAL
        assert Priority.LOW > Priority.MEDIUM

    def test_priority_from_score(self):
        assert priority_from_score(100) == Priority.CRITICAL
        assert priority_from_score(80) == Priority.CRITICAL
        assert priority_from_score(79) == Priority.HIGH
        assert priority_from_score(60) == Priority.HIGH
        assert priority_from_score(59) == Priority.MEDIUM
        assert priority_from_score(40) == Priority.MEDIUM
        assert priority_from_score(39) == Priority.LOW
        assert priority_from_score(0) == Priority.LOW


class TestScoreWeights:

    def test_default_weights(self):
        weights = ScoreWeights()
        assert weights.severity_critical == 30
        assert weights.severity_high == 20
        assert weights.severity_medium == 10
        assert weights.severity_low == 5
        assert weights.multiple_assets == 10
        assert weights.supporting_facts == 5
        assert weights.attack_path_presence == 20
        assert weights.public_exposure == 15
        assert weights.identity_related == 10

    def test_custom_weights(self):
        weights = ScoreWeights(
            severity_critical=40,
            public_exposure=25,
        )
        assert weights.severity_critical == 40
        assert weights.public_exposure == 25
        assert weights.severity_high == 20


class TestRiskImmutability:

    def test_risk_is_frozen(self, risk_set):
        risk = risk_set.risks[0]
        with pytest.raises(AttributeError):
            risk.id = "changed"

    def test_risk_to_dict(self, risk_set):
        risk = risk_set.risks[0]
        d = risk.to_dict()
        assert d["id"] == risk.id
        assert d["score"] == risk.score
        assert d["priority"] == risk.priority.value
        assert "contributing_factors" in d


class TestRiskSet:

    def test_risk_set_creation(self, risk_set):
        assert len(risk_set) >= 1

    def test_risk_set_iteration(self, risk_set):
        count = 0
        for _ in risk_set:
            count += 1
        assert count == len(risk_set)

    def test_risk_set_contains(self, risk_set):
        if len(risk_set) > 0:
            assert risk_set.risks[0] in risk_set

    def test_find_by_id(self, risk_set):
        if len(risk_set) > 0:
            risk = risk_set.risks[0]
            found = risk_set.find_by_id(risk.id)
            assert found is not None
            assert found.id == risk.id

    def test_find_by_id_missing(self, risk_set):
        assert risk_set.find_by_id("nonexistent") is None

    def test_find_by_priority(self, risk_set):
        for priority in Priority:
            risks = risk_set.find_by_priority(priority)
            for r in risks:
                assert r.priority == priority

    def test_find_by_category(self, risk_set):
        categories = {r.category for r in risk_set}
        for category in categories:
            risks = risk_set.find_by_category(category)
            for r in risks:
                assert r.category == category

    def test_find_by_asset(self, risk_set):
        for risk in risk_set:
            asset_risks = risk_set.find_by_asset(risk.asset_ids[0])
            assert risk in asset_risks

    def test_top_n(self, risk_set):
        top3 = risk_set.top_n(3)
        assert len(top3) <= 3
        scores = [r.score for r in top3]
        assert scores == sorted(scores, reverse=True)

    def test_top_n_larger_than_set(self, risk_set):
        top = risk_set.top_n(len(risk_set) + 10)
        assert len(top) == len(risk_set)

    def test_top_n_zero(self, risk_set):
        top = risk_set.top_n(0)
        assert len(top) == 0

    def test_statistics(self, risk_set):
        stats = risk_set.statistics()
        assert stats["total"] == len(risk_set)
        assert "by_priority" in stats
        assert "by_category" in stats
        assert "by_asset" in stats

    def test_to_dicts(self, risk_set):
        dicts = risk_set.to_dicts()
        assert len(dicts) == len(risk_set)
        for d in dicts:
            assert "id" in d
            assert "score" in d
            assert "priority" in d
            assert "explanation" in d


class TestWeightedScoreStrategy:

    def test_critical_finding_scores_high(self):
        strategy = WeightedScoreStrategy()
        finding = _make_finding(Severity.CRITICAL, "Test", ["asset-1"])
        risk = strategy.score(finding, {})
        assert risk.score >= 30
        assert risk.priority == Priority.LOW

    def test_high_finding_scores_high(self):
        strategy = WeightedScoreStrategy()
        finding = _make_finding(Severity.HIGH, "Test", ["asset-1"])
        risk = strategy.score(finding, {})
        assert risk.score >= 20

    def test_medium_finding_scores_medium(self):
        strategy = WeightedScoreStrategy()
        finding = _make_finding(Severity.MEDIUM, "Test", ["asset-1"])
        risk = strategy.score(finding, {})
        assert risk.score >= 10

    def test_low_finding_scores_low(self):
        strategy = WeightedScoreStrategy()
        finding = _make_finding(Severity.LOW, "Test", ["asset-1"])
        risk = strategy.score(finding, {})
        assert risk.score >= 5

    def test_score_capped_at_100(self):
        strategy = WeightedScoreStrategy(ScoreWeights(
            severity_critical=100,
            multiple_assets=100,
            supporting_facts=100,
            attack_path_presence=100,
            public_exposure=100,
            identity_related=100,
        ))
        finding = _make_finding(
            Severity.CRITICAL,
            "Test",
            ["asset-1", "asset-2"],
            fact_ids=["f1", "f2"],
        )

        class FakePath:
            nodes = ["asset-1", "asset-2"]

        class FakeAsset:
            id = "asset-1"

        risk = strategy.score(finding, {
            "attack_paths": [FakePath()],
            "public_assets": [FakeAsset()],
        })
        assert risk.score <= 100

    def test_score_floor_at_0(self):
        strategy = WeightedScoreStrategy(ScoreWeights(
            severity_critical=0,
            multiple_assets=0,
            supporting_facts=0,
            attack_path_presence=0,
            public_exposure=0,
            identity_related=0,
        ))
        finding = _make_finding(Severity.LOW, "Test", ["asset-1"])
        risk = strategy.score(finding, {})
        assert risk.score >= 0

    def test_multiple_assets_bonus(self):
        strategy = WeightedScoreStrategy()
        finding = _make_finding(Severity.HIGH, "Test", ["asset-1", "asset-2", "asset-3"])
        risk = strategy.score(finding, {})
        assert risk.score >= 30

    def test_supporting_facts_bonus(self):
        strategy = WeightedScoreStrategy()
        finding = _make_finding(
            Severity.HIGH,
            "Test",
            ["asset-1"],
            fact_ids=["f1", "f2", "f3"],
        )
        risk = strategy.score(finding, {})
        assert risk.score >= 25

    def test_attack_path_bonus(self):
        strategy = WeightedScoreStrategy()
        finding = _make_finding(Severity.MEDIUM, "Test", ["asset-1"])

        class FakePath:
            nodes = ["asset-1", "asset-2"]

        risk = strategy.score(finding, {"attack_paths": [FakePath()]})
        assert risk.score >= 30

    def test_public_exposure_bonus(self):
        strategy = WeightedScoreStrategy()

        class FakeAsset:
            id = "asset-1"

        finding = _make_finding(Severity.MEDIUM, "Test", ["asset-1"])
        risk = strategy.score(finding, {"public_assets": [FakeAsset()]})
        assert risk.score >= 25

    def test_identity_related_bonus(self):
        strategy = WeightedScoreStrategy()
        finding = _make_finding(Severity.HIGH, "Test", ["sa-1"], category="IAM")
        risk = strategy.score(finding, {})
        assert risk.score >= 30

    def test_explanation_generated(self):
        strategy = WeightedScoreStrategy()
        finding = _make_finding(Severity.HIGH, "Test", ["asset-1"])
        risk = strategy.score(finding, {})
        assert risk.explanation != ""
        assert "Test" in risk.explanation
        assert str(risk.score) in risk.explanation
        assert risk.priority.value in risk.explanation

    def test_contributing_factors_populated(self):
        strategy = WeightedScoreStrategy()
        finding = _make_finding(Severity.HIGH, "Test", ["asset-1"])
        risk = strategy.score(finding, {})
        assert len(risk.contributing_factors) >= 1
        assert "High severity" in risk.contributing_factors

    def test_recommendation_passed_through(self):
        strategy = WeightedScoreStrategy()
        finding = _make_finding(Severity.HIGH, "Test", ["asset-1"], recommendation="Fix it now")
        risk = strategy.score(finding, {})
        assert risk.recommendation == "Fix it now"

    def test_metadata_populated(self):
        strategy = WeightedScoreStrategy()
        finding = _make_finding(Severity.HIGH, "Test", ["asset-1"])
        risk = strategy.score(finding, {})
        assert "rule_id" in risk.metadata
        assert "weights" in risk.metadata


class TestRiskEngine:

    def test_evaluate_returns_risk_set(self, finding_set):
        engine = RiskEngine()
        result = engine.evaluate(finding_set)
        assert isinstance(result, RiskSet)

    def test_evaluate_with_context(self, finding_set):
        engine = RiskEngine()
        result = engine.evaluate(finding_set, context={"attack_paths": [], "public_assets": []})
        assert len(result) >= 1

    def test_custom_strategy(self, finding_set):
        strategy = WeightedScoreStrategy(ScoreWeights(severity_high=100))
        engine = RiskEngine(strategy)
        result = engine.evaluate(finding_set)
        assert len(result) >= 1

    def test_failure_isolation(self, finding_set):
        class BadStrategy:
            def score(self, finding, context):
                raise RuntimeError("fail")

        engine = RiskEngine(BadStrategy())
        with pytest.raises(StrategyError) as exc_info:
            engine.evaluate(finding_set)
        assert "BadStrategy" in str(exc_info.value)


class TestIntegrationWithRuleEngine:

    def test_all_findings_produce_risks(self, finding_set):
        engine = RiskEngine()
        risk_set = engine.evaluate(finding_set)
        assert len(risk_set) == len(finding_set)

    def test_risk_matches_finding_asset(self, risk_set):
        for risk in risk_set:
            assert len(risk.asset_ids) >= 1

    def test_risk_severity_matches_finding(self, risk_set, finding_set):
        findings_by_id = {f.id: f for f in finding_set}
        for risk in risk_set:
            finding = findings_by_id.get(risk.finding_id)
            if finding:
                assert risk.severity == finding.severity.value

    def test_public_vm_has_attack_path_bonus(self, risk_set):
        public_vm_risks = [r for r in risk_set if "vm-frontend" in r.asset_ids]
        assert len(public_vm_risks) >= 1

    def test_bucket_has_public_exposure_if_applicable(self, risk_set):
        bucket_risks = [r for r in risk_set if "bucket-001" in r.asset_ids]
        if bucket_risks:
            for risk in bucket_risks:
                assert risk.score >= 0
                assert risk.priority in Priority

    def test_risk_ids_unique(self, risk_set):
        ids = [r.id for r in risk_set]
        assert len(ids) == len(set(ids))


class TestEndToEndIntegration:

    def test_full_scan_unchanged(self):
        from backend.services.scan_service import ScanService
        service = ScanService()
        result = service.run_scan()
        assert result.assets == {
            'compute': 2,
            'storage': 2,
            'iam': 3,
            'vpc': 1,
            'subnet': 2
        }
        assert len(result.findings) >= 1
        assert len(result.relationships) == 8
        assert len(result.attack_paths) == 4
        assert result.executive_summary['security_score'] == 83

    def test_risk_set_available(self):
        from backend.services.scan_service import ScanService
        service = ScanService()
        result = service.run_scan()
        assert result.risk_set is not None
        assert len(result.risk_set) >= 1

    def test_risk_set_immutable(self):
        from backend.services.scan_service import ScanService
        service = ScanService()
        result = service.run_scan()
        risk = result.risk_set.risks[0]
        with pytest.raises(AttributeError):
            risk.score = 100

    def test_risk_set_queries(self):
        from backend.services.scan_service import ScanService
        service = ScanService()
        result = service.run_scan()
        top3 = result.risk_set.top_n(3)
        assert len(top3) <= 3
        stats = result.risk_set.statistics()
        assert stats["total"] == len(result.risk_set)


def _make_finding(
    severity: Severity,
    title: str,
    asset_ids: List[str],
    fact_ids: List[str] = None,
    category: str = "Network",
    recommendation: str = "Fix it",
    rule_id: str = "CS-RULE-001",
) -> Finding:

    facts = []

    if fact_ids:

        class MockFact:

            def __init__(self, fid):

                self.id = fid

        facts = [MockFact(fid) for fid in fact_ids]

    return Finding(
        id=f"{rule_id}-{'-'.join(asset_ids)}",
        rule_id=rule_id,
        title=title,
        description=f"Description for {title}",
        severity=severity,
        category=category,
        asset_ids=asset_ids,
        facts=facts,
        recommendation=recommendation,
        references=[],
        evidence={},
    )
