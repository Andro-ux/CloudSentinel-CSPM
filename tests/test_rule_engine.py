import sys
sys.path.insert(0, r'C:\Users\vinit\Desktop\CloudSentinel_phase3\CloudSentinel')

import pytest

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
from backend.facts.models import Fact, FactSet, FactType
from backend.knowledge.engine import KnowledgeEngine
from backend.rules.engine import RuleEngine
from backend.rules.exceptions import FindingNotFound, RuleExecutionError
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
def fact_set():
    provider = MockProvider()
    assets = provider.get_assets()
    graph_builder = GraphBuilder()
    graph_builder.add_assets(assets)
    relationships = RelationshipMapper().map(graph_builder.index)
    graph = graph_builder.build(relationships)
    knowledge = KnowledgeEngine(graph)

    registry = FactRegistry()
    registry.register(NetworkFactsExtractor())
    registry.register(ComputeFactsExtractor())
    registry.register(StorageFactsExtractor())
    registry.register(IAMFactsExtractor())
    registry.register(LoggingFactsExtractor())
    engine = FactEngine(knowledge, registry)
    return engine.extract()


@pytest.fixture
def finding_set(fact_set):
    registry = RuleRegistry()
    registry.register(PublicVMRule())
    registry.register(PublicBucketRule())
    registry.register(OpenFirewallRule())
    registry.register(ShieldedVMRule())
    registry.register(MetadataServiceRule())
    registry.register(AdminServiceAccountRule())
    registry.register(UnusedServiceAccountRule())
    registry.register(FlowLogsRule())
    registry.register(AuditLoggingRule())
    engine = RuleEngine(registry)
    return engine.evaluate(fact_set)


class TestSeverityEnum:

    def test_severity_values(self):
        assert Severity.CRITICAL.value == "CRITICAL"
        assert Severity.HIGH.value == "HIGH"
        assert Severity.MEDIUM.value == "MEDIUM"
        assert Severity.LOW.value == "LOW"
        assert Severity.INFO.value == "INFO"

    def test_severity_members(self):
        expected = {"CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"}
        assert set(member.value for member in Severity) == expected


class TestRuleMetadata:

    def test_metadata_creation(self):
        metadata = RuleMetadata(
            rule_id="CS-RULE-001",
            name="Test Rule",
            description="Test description",
            version="1.0.0",
            author="CloudSentinel Core",
        )
        assert metadata.rule_id == "CS-RULE-001"
        assert metadata.name == "Test Rule"
        assert metadata.description == "Test description"
        assert metadata.version == "1.0.0"
        assert metadata.author == "CloudSentinel Core"

    def test_metadata_defaults(self):
        metadata = RuleMetadata(
            rule_id="CS-RULE-001",
            name="Test Rule",
            description="Test description",
        )
        assert metadata.version == "1.0.0"
        assert metadata.author == "CloudSentinel Core"


class TestFindingImmutability:

    def test_finding_is_frozen(self, fact_set):
        registry = RuleRegistry()
        registry.register(PublicVMRule())
        engine = RuleEngine(registry)
        findings = engine.evaluate(fact_set)
        if findings:
            finding = findings.findings[0]
            with pytest.raises(AttributeError):
                finding.id = "changed"

    def test_finding_to_dict(self, fact_set):
        registry = RuleRegistry()
        registry.register(PublicVMRule())
        engine = RuleEngine(registry)
        findings = engine.evaluate(fact_set)
        if findings:
            finding = findings.findings[0]
            d = finding.to_dict()
            assert d["id"] == finding.id
            assert d["rule_id"] == finding.rule_id
            assert d["severity"] == finding.severity.value
            assert "asset_ids" in d
            assert "fact_ids" in d


class TestFindingSet:

    def test_finding_set_creation(self, finding_set):
        assert len(finding_set) >= 1

    def test_finding_set_iteration(self, finding_set):
        count = 0
        for _ in finding_set:
            count += 1
        assert count == len(finding_set)

    def test_finding_set_contains(self, finding_set):
        if len(finding_set) > 0:
            assert finding_set.findings[0] in finding_set

    def test_find_by_id(self, finding_set):
        if len(finding_set) > 0:
            f = finding_set.findings[0]
            found = finding_set.find_by_id(f.id)
            assert found is not None
            assert found.id == f.id

    def test_find_by_id_missing(self, finding_set):
        assert finding_set.find_by_id("nonexistent") is None

    def test_find_by_severity(self, finding_set):
        high_findings = finding_set.find_by_severity(Severity.HIGH)
        assert len(high_findings) >= 1
        for f in high_findings:
            assert f.severity == Severity.HIGH

    def test_find_by_asset(self, finding_set):
        asset_findings = finding_set.find_by_asset("vm-frontend")
        for f in asset_findings:
            assert "vm-frontend" in f.asset_ids

    def test_find_by_rule(self, finding_set):
        rule_findings = finding_set.find_by_rule("CS-RULE-001")
        for f in rule_findings:
            assert f.rule_id == "CS-RULE-001"

    def test_statistics(self, finding_set):
        stats = finding_set.statistics()
        assert stats["total"] == len(finding_set)
        assert "by_severity" in stats
        assert "by_rule" in stats
        assert "by_asset" in stats

    def test_to_dicts(self, finding_set):
        dicts = finding_set.to_dicts()
        assert len(dicts) == len(finding_set)
        for d in dicts:
            assert "id" in d
            assert "severity" in d
            assert "rule_id" in d


class TestRuleRegistry:

    def test_register_rule(self):
        registry = RuleRegistry()
        registry.register(PublicVMRule())
        assert len(registry.rules) == 1

    def test_duplicate_prevention(self, fact_set):
        registry = RuleRegistry()
        registry.register(PublicVMRule())
        registry.register(PublicVMRule())
        engine = RuleEngine(registry)
        findings = engine.evaluate(fact_set)
        ids = [f.id for f in findings]
        assert len(ids) == len(set(ids))

    def test_failure_isolation(self, fact_set):
        class BadRule:
            @property
            def metadata(self):
                return RuleMetadata(
                    rule_id="BAD-RULE",
                    name="Bad Rule",
                    description="Fails",
                )

            def evaluate(self, fact_set):
                raise RuntimeError("fail")

        registry = RuleRegistry()
        registry.register(PublicVMRule())
        registry.register(BadRule())
        engine = RuleEngine(registry)
        with pytest.raises(RuleExecutionError) as exc_info:
            engine.evaluate(fact_set)
        assert "BAD-RULE" in str(exc_info.value)


class TestPublicVMRule:

    def test_produces_high_finding(self, fact_set):
        registry = RuleRegistry()
        registry.register(PublicVMRule())
        engine = RuleEngine(registry)
        findings = engine.evaluate(fact_set)
        public_vm_findings = findings.find_by_rule("CS-RULE-001")
        assert len(public_vm_findings) >= 1
        for f in public_vm_findings:
            assert f.severity == Severity.HIGH
            assert f.category == "Network"

    def test_metadata(self):
        rule = PublicVMRule()
        assert rule.metadata.rule_id == "CS-RULE-001"
        assert rule.metadata.name == "Public VM Detected"
        assert rule.metadata.version == "1.0.0"
        assert rule.metadata.author == "CloudSentinel Core"


class TestPublicBucketRule:

    def test_produces_critical_finding(self, fact_set):
        registry = RuleRegistry()
        registry.register(PublicBucketRule())
        engine = RuleEngine(registry)
        findings = engine.evaluate(fact_set)
        bucket_findings = findings.find_by_rule("CS-RULE-002")
        for f in bucket_findings:
            assert f.severity == Severity.CRITICAL
            assert f.category == "Storage"

    def test_requires_both_conditions(self, fact_set):
        registry = RuleRegistry()
        registry.register(PublicBucketRule())
        engine = RuleEngine(registry)
        findings = engine.evaluate(fact_set)
        for f in findings.find_by_rule("CS-RULE-002"):
            fact_types = {ft.value for ft in [fact.fact_type for fact in f.facts]}
            assert "PUBLIC_BUCKET" in fact_types
            assert "UNENCRYPTED_BUCKET" in fact_types


class TestOpenFirewallRule:

    def test_produces_high_finding(self, fact_set):
        registry = RuleRegistry()
        registry.register(OpenFirewallRule())
        engine = RuleEngine(registry)
        findings = engine.evaluate(fact_set)
        fw_findings = findings.find_by_rule("CS-RULE-003")
        for f in fw_findings:
            assert f.severity == Severity.HIGH
            assert f.category == "Network"


class TestShieldedVMRule:

    def test_produces_medium_finding(self, fact_set):
        registry = RuleRegistry()
        registry.register(ShieldedVMRule())
        engine = RuleEngine(registry)
        findings = engine.evaluate(fact_set)
        vm_findings = findings.find_by_rule("CS-RULE-004")
        for f in vm_findings:
            assert f.severity == Severity.MEDIUM
            assert f.category == "Compute"


class TestMetadataServiceRule:

    def test_produces_medium_finding(self, fact_set):
        registry = RuleRegistry()
        registry.register(MetadataServiceRule())
        engine = RuleEngine(registry)
        findings = engine.evaluate(fact_set)
        findings = [f for f in findings.find_by_rule("CS-RULE-005")]
        for f in findings:
            assert f.severity == Severity.MEDIUM
            assert f.category == "Compute"


class TestAdminServiceAccountRule:

    def test_produces_high_finding(self, fact_set):
        registry = RuleRegistry()
        registry.register(AdminServiceAccountRule())
        engine = RuleEngine(registry)
        findings = engine.evaluate(fact_set)
        sa_findings = findings.find_by_rule("CS-RULE-006")
        for f in sa_findings:
            assert f.severity == Severity.HIGH
            assert f.category == "IAM"


class TestUnusedServiceAccountRule:

    def test_produces_low_finding(self, fact_set):
        registry = RuleRegistry()
        registry.register(UnusedServiceAccountRule())
        engine = RuleEngine(registry)
        findings = engine.evaluate(fact_set)
        sa_findings = findings.find_by_rule("CS-RULE-007")
        for f in sa_findings:
            assert f.severity == Severity.LOW
            assert f.category == "IAM"


class TestFlowLogsRule:

    def test_produces_medium_finding(self, fact_set):
        registry = RuleRegistry()
        registry.register(FlowLogsRule())
        engine = RuleEngine(registry)
        findings = engine.evaluate(fact_set)
        flow_findings = findings.find_by_rule("CS-RULE-008")
        for f in flow_findings:
            assert f.severity == Severity.MEDIUM
            assert f.category == "Logging"


class TestAuditLoggingRule:

    def test_produces_high_finding(self, fact_set):
        registry = RuleRegistry()
        registry.register(AuditLoggingRule())
        engine = RuleEngine(registry)
        findings = engine.evaluate(fact_set)
        audit_findings = findings.find_by_rule("CS-RULE-009")
        for f in audit_findings:
            assert f.severity == Severity.HIGH
            assert f.category == "Logging"


class TestIntegrationWithFactEngine:

    def test_all_rules_execute(self, fact_set):
        registry = RuleRegistry()
        registry.register(PublicVMRule())
        registry.register(PublicBucketRule())
        registry.register(OpenFirewallRule())
        registry.register(ShieldedVMRule())
        registry.register(MetadataServiceRule())
        registry.register(AdminServiceAccountRule())
        registry.register(UnusedServiceAccountRule())
        registry.register(FlowLogsRule())
        registry.register(AuditLoggingRule())
        engine = RuleEngine(registry)
        findings = engine.evaluate(fact_set)
        assert len(findings) >= 1

    def test_finding_references(self, finding_set):
        for f in finding_set:
            assert f.recommendation != ""
            assert isinstance(f.references, list)

    def test_fact_ids_in_finding(self, fact_set, finding_set):
        for f in finding_set:
            assert len(f.fact_ids) >= 1


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

    def test_findings_are_dicts(self):
        from backend.services.scan_service import ScanService
        service = ScanService()
        result = service.run_scan()
        for finding in result.findings:
            assert isinstance(finding, dict)
            assert "id" in finding
            assert "severity" in finding
            assert "rule_id" in finding

    def test_finding_set_available(self):
        from backend.services.scan_service import ScanService
        service = ScanService()
        result = service.run_scan()
        assert result.fact_set is not None
        assert len(result.fact_set) > 0
