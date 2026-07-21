import sys
sys.path.insert(0, r'C:\Users\vinit\Desktop\CloudSentinel_phase3\CloudSentinel')

import pytest

from backend.correlation.asset_index import AssetIndex
from backend.correlation.builders.relationship_builder import RelationshipBuilder
from backend.correlation.graph_builder import GraphBuilder
from backend.correlation.relationship_mapper import RelationshipMapper
from backend.facts.engine import FactEngine
from backend.facts.exceptions import ExtractorError, FactNotFound, InvalidFactType
from backend.facts.models import Evidence, Fact, FactSet, FactType
from backend.facts.registry import FactRegistry
from backend.knowledge.engine import KnowledgeEngine
from backend.providers.mock_provider import MockProvider


@pytest.fixture
def knowledge():
    provider = MockProvider()
    assets = provider.get_assets()
    graph_builder = GraphBuilder()
    graph_builder.add_assets(assets)
    relationships = RelationshipMapper().map(graph_builder.index)
    graph = graph_builder.build(relationships)
    return KnowledgeEngine(graph)


@pytest.fixture
def fact_set(knowledge):
    registry = FactRegistry()
    registry.register(_make_network_extractor())
    registry.register(_make_compute_extractor())
    registry.register(_make_storage_extractor())
    registry.register(_make_iam_extractor())
    registry.register(_make_logging_extractor())
    engine = FactEngine(knowledge, registry)
    return engine.extract()


def _make_network_extractor():
    from backend.facts.extractors.network import NetworkFactsExtractor
    return NetworkFactsExtractor()


def _make_compute_extractor():
    from backend.facts.extractors.compute import ComputeFactsExtractor
    return ComputeFactsExtractor()


def _make_storage_extractor():
    from backend.facts.extractors.storage import StorageFactsExtractor
    return StorageFactsExtractor()


def _make_iam_extractor():
    from backend.facts.extractors.iam import IAMFactsExtractor
    return IAMFactsExtractor()


def _make_logging_extractor():
    from backend.facts.extractors.logging import LoggingFactsExtractor
    return LoggingFactsExtractor()


class TestFactImmutability:

    def test_fact_is_frozen(self):
        evidence = Evidence(
            provider="test",
            source="test",
            attribute="test",
            value=True,
        )
        fact = Fact(
            id="test-1",
            asset_id="asset-1",
            fact_type=FactType.PUBLIC_VM,
            severity="HIGH",
            provider="test",
            category="Network",
            evidence=evidence,
        )
        with pytest.raises(AttributeError):
            fact.id = "changed"

    def test_evidence_is_frozen(self):
        evidence = Evidence(
            provider="test",
            source="test",
            attribute="test",
            value=True,
        )
        with pytest.raises(AttributeError):
            evidence.provider = "changed"


class TestFactTypeEnum:

    def test_fact_type_values(self):
        assert FactType.PUBLIC_VM.value == "PUBLIC_VM"
        assert FactType.FLOW_LOGS_DISABLED.value == "FLOW_LOGS_DISABLED"
        assert FactType.SHIELDED_VM_DISABLED.value == "SHIELDED_VM_DISABLED"

    def test_fact_type_members(self):
        expected = {
            "PUBLIC_VM",
            "PUBLIC_SUBNET",
            "PUBLIC_BUCKET",
            "UNENCRYPTED_BUCKET",
            "OPEN_FIREWALL",
            "ADMIN_SERVICE_ACCOUNT",
            "UNUSED_SERVICE_ACCOUNT",
            "OVER_PRIVILEGED_IDENTITY",
            "FLOW_LOGS_DISABLED",
            "AUDIT_LOGGING_DISABLED",
            "METADATA_SERVICE_ENABLED",
            "SHIELDED_VM_DISABLED",
            "INTERNET_REACHABLE",
            "VERSIONING_DISABLED",
        }
        assert set(member.value for member in FactType) == expected


class TestEvidenceModel:

    def test_evidence_creation(self):
        evidence = Evidence(
            provider="gcp",
            source="asset.security",
            attribute="public_ip",
            value=True,
        )
        assert evidence.provider == "gcp"
        assert evidence.source == "asset.security"
        assert evidence.attribute == "public_ip"
        assert evidence.value is True
        assert evidence.timestamp is None

    def test_evidence_with_timestamp(self):
        from datetime import datetime
        now = datetime(2024, 1, 1, 12, 0, 0)
        evidence = Evidence(
            provider="gcp",
            source="test",
            attribute="test",
            value="x",
            timestamp=now,
        )
        assert evidence.timestamp == now


class TestFactCreation:

    def test_fact_creation(self):
        evidence = Evidence(
            provider="gcp",
            source="test",
            attribute="test",
            value=True,
        )
        fact = Fact(
            id="gcp-PUBLIC_VM-vm-1",
            asset_id="vm-1",
            fact_type=FactType.PUBLIC_VM,
            severity="HIGH",
            provider="gcp",
            category="Network",
            evidence=evidence,
            description="Test fact",
        )
        assert fact.id == "gcp-PUBLIC_VM-vm-1"
        assert fact.asset_id == "vm-1"
        assert fact.fact_type == FactType.PUBLIC_VM
        assert fact.severity == "HIGH"
        assert fact.category == "Network"
        assert fact.description == "Test fact"

    def test_fact_defaults(self):
        evidence = Evidence(
            provider="gcp",
            source="test",
            attribute="test",
            value=True,
        )
        fact = Fact(
            id="test",
            asset_id="a1",
            fact_type=FactType.PUBLIC_VM,
            severity="LOW",
            provider="gcp",
            category="Network",
            evidence=evidence,
        )
        assert fact.metadata == {}
        assert fact.description == ""


class TestFactSet:

    def test_fact_set_creation(self):
        evidence = Evidence("gcp", "s", "a", True)
        facts = [
            Fact("1", "a1", FactType.PUBLIC_VM, "HIGH", "gcp", "Network", evidence),
            Fact("2", "a1", FactType.PUBLIC_SUBNET, "MEDIUM", "gcp", "Network", evidence),
            Fact("3", "a2", FactType.PUBLIC_VM, "HIGH", "gcp", "Network", evidence),
        ]
        fs = FactSet(facts)
        assert len(fs) == 3
        assert list(fs) == list(facts)

    def test_find_by_asset(self):
        evidence = Evidence("gcp", "s", "a", True)
        facts = [
            Fact("1", "a1", FactType.PUBLIC_VM, "HIGH", "gcp", "Network", evidence),
            Fact("2", "a1", FactType.PUBLIC_SUBNET, "MEDIUM", "gcp", "Network", evidence),
            Fact("3", "a2", FactType.PUBLIC_VM, "HIGH", "gcp", "Network", evidence),
        ]
        fs = FactSet(facts)
        a1_facts = fs.find_by_asset("a1")
        assert len(a1_facts) == 2
        a2_facts = fs.find_by_asset("a2")
        assert len(a2_facts) == 1
        empty = fs.find_by_asset("nonexistent")
        assert empty == []

    def test_find_by_type(self):
        evidence = Evidence("gcp", "s", "a", True)
        facts = [
            Fact("1", "a1", FactType.PUBLIC_VM, "HIGH", "gcp", "Network", evidence),
            Fact("2", "a2", FactType.PUBLIC_SUBNET, "MEDIUM", "gcp", "Network", evidence),
            Fact("3", "a3", FactType.PUBLIC_VM, "HIGH", "gcp", "Network", evidence),
        ]
        fs = FactSet(facts)
        vm_facts = fs.find_by_type(FactType.PUBLIC_VM)
        assert len(vm_facts) == 2
        subnet_facts = fs.find_by_type(FactType.PUBLIC_SUBNET)
        assert len(subnet_facts) == 1

    def test_contains(self):
        evidence = Evidence("gcp", "s", "a", True)
        fact = Fact("1", "a1", FactType.PUBLIC_VM, "HIGH", "gcp", "Network", evidence)
        fs = FactSet([fact])
        assert fact in fs
        assert Fact("2", "a1", FactType.PUBLIC_VM, "HIGH", "gcp", "Network", evidence) not in fs

    def test_statistics(self):
        evidence = Evidence("gcp", "s", "a", True)
        facts = [
            Fact("1", "a1", FactType.PUBLIC_VM, "HIGH", "gcp", "Network", evidence),
            Fact("2", "a2", FactType.PUBLIC_VM, "HIGH", "gcp", "Network", evidence),
            Fact("3", "a3", FactType.PUBLIC_SUBNET, "MEDIUM", "gcp", "Network", evidence),
        ]
        fs = FactSet(facts)
        stats = fs.statistics()
        assert stats["PUBLIC_VM"] == 2
        assert stats["PUBLIC_SUBNET"] == 1

    def test_grouped_by_type(self):
        evidence = Evidence("gcp", "s", "a", True)
        facts = [
            Fact("1", "a1", FactType.PUBLIC_VM, "HIGH", "gcp", "Network", evidence),
            Fact("2", "a2", FactType.PUBLIC_SUBNET, "MEDIUM", "gcp", "Network", evidence),
        ]
        fs = FactSet(facts)
        grouped = fs.grouped_by_type()
        assert len(grouped[FactType.PUBLIC_VM]) == 1
        assert len(grouped[FactType.PUBLIC_SUBNET]) == 1

    def test_grouped_by_asset(self):
        evidence = Evidence("gcp", "s", "a", True)
        facts = [
            Fact("1", "a1", FactType.PUBLIC_VM, "HIGH", "gcp", "Network", evidence),
            Fact("2", "a1", FactType.PUBLIC_SUBNET, "MEDIUM", "gcp", "Network", evidence),
        ]
        fs = FactSet(facts)
        grouped = fs.grouped_by_asset()
        assert len(grouped["a1"]) == 2
        assert len(grouped.get("a2", [])) == 0


class TestFactRegistry:

    def test_register_extractor(self):
        registry = FactRegistry()
        registry.register(_make_network_extractor())
        assert len(registry.extractors) == 1

    def test_duplicate_prevention(self):
        from backend.facts.extractors.network import NetworkFactsExtractor
        registry = FactRegistry()
        registry.register(NetworkFactsExtractor())
        registry.register(NetworkFactsExtractor())
        knowledge = _build_knowledge()
        facts = registry.extract(knowledge)
        ids = [f.id for f in facts]
        assert len(ids) == len(set(ids))

    def test_extractor_isolation(self):
        class BadExtractor:
            @property
            def fact_types(self):
                return [FactType.PUBLIC_VM]

            def extract(self, knowledge):
                raise RuntimeError("fail")

        registry = FactRegistry()
        registry.register(_make_network_extractor())
        registry.register(BadExtractor())
        knowledge = _build_knowledge()
        with pytest.raises(ExtractorError) as exc_info:
            registry.extract(knowledge)
        assert "BadExtractor" in str(exc_info.value)


class TestFactEngineIntegration:

    def test_fact_set_populated(self, fact_set):
        assert len(fact_set) > 0

    def test_find_public_vm_facts(self, fact_set):
        vm_facts = fact_set.find_by_type(FactType.PUBLIC_VM)
        assert len(vm_facts) >= 1
        asset_ids = {f.asset_id for f in vm_facts}
        assert "vm-frontend" in asset_ids

    def test_find_flow_logs_disabled(self, fact_set):
        facts = fact_set.find_by_type(FactType.FLOW_LOGS_DISABLED)
        assert len(facts) >= 1
        asset_ids = {f.asset_id for f in facts}
        assert "subnet-001" in asset_ids

    def test_find_shielded_vm_disabled(self, fact_set):
        facts = fact_set.find_by_type(FactType.SHIELDED_VM_DISABLED)
        assert len(facts) >= 1

    def test_find_versioning_disabled(self, fact_set):
        facts = fact_set.find_by_type(FactType.VERSIONING_DISABLED)
        assert len(facts) >= 1

    def test_find_admin_service_account(self, fact_set):
        facts = fact_set.find_by_type(FactType.ADMIN_SERVICE_ACCOUNT)
        assert len(facts) >= 1

    def test_find_unused_service_account(self, fact_set):
        facts = fact_set.find_by_type(FactType.UNUSED_SERVICE_ACCOUNT)
        assert len(facts) >= 1

    def test_find_over_privileged_identity(self, fact_set):
        facts = fact_set.find_by_type(FactType.OVER_PRIVILEGED_IDENTITY)
        assert len(facts) >= 1

    def test_find_public_subnet(self, fact_set):
        facts = fact_set.find_by_type(FactType.PUBLIC_SUBNET)
        assert len(facts) >= 1

    def test_find_public_bucket(self, fact_set):
        facts = fact_set.find_by_type(FactType.PUBLIC_BUCKET)
        assert len(facts) >= 1

    def test_find_audit_logging_disabled(self, fact_set):
        facts = fact_set.find_by_type(FactType.AUDIT_LOGGING_DISABLED)
        assert len(facts) >= 1

    def test_find_metadata_service_enabled(self, fact_set):
        facts = fact_set.find_by_type(FactType.METADATA_SERVICE_ENABLED)
        assert len(facts) >= 1

    def test_query_by_asset(self, fact_set):
        vm_frontend_facts = fact_set.find_by_asset("vm-frontend")
        assert len(vm_frontend_facts) >= 1
        types = {f.fact_type for f in vm_frontend_facts}
        assert FactType.PUBLIC_VM in types
        assert FactType.SHIELDED_VM_DISABLED in types

    def test_fact_evidence_correctness(self, fact_set):
        for fact in fact_set:
            assert fact.evidence.provider != ""
            assert fact.evidence.source != ""
            assert fact.evidence.attribute != ""
            assert fact.evidence.value is not None

    def test_no_duplicate_fact_ids(self, fact_set):
        ids = [f.id for f in fact_set]
        assert len(ids) == len(set(ids))

    def test_fact_categories(self, fact_set):
        categories = {f.category for f in fact_set}
        expected = {"Network", "Compute", "Storage", "IAM", "Logging"}
        assert categories == expected

    def test_fact_severities(self, fact_set):
        severities = {f.severity for f in fact_set}
        assert severities.issubset({"CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"})


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

    def test_fact_set_available_in_result(self):
        from backend.services.scan_service import ScanService
        service = ScanService()
        result = service.run_scan()
        assert result.fact_set is not None
        assert len(result.fact_set) > 0


def _build_knowledge():
    provider = MockProvider()
    assets = provider.get_assets()
    graph_builder = GraphBuilder()
    graph_builder.add_assets(assets)
    relationships = RelationshipMapper().map(graph_builder.index)
    graph = graph_builder.build(relationships)
    return KnowledgeEngine(graph)
