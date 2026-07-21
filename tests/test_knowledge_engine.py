import sys
sys.path.insert(0, r'C:\Users\vinit\Desktop\CloudSentinel_phase3\CloudSentinel')

import pytest

from backend.correlation.asset_index import AssetIndex
from backend.correlation.builders.relationship_builder import RelationshipBuilder
from backend.correlation.graph_builder import GraphBuilder
from backend.correlation.models import AssetNode, Relationship
from backend.correlation.relationship_mapper import RelationshipMapper
from backend.correlation.relationship_types import RelationshipType
from backend.knowledge.engine import KnowledgeEngine
from backend.knowledge.exceptions import AssetNotFound, GraphNotInitialized
from backend.providers.mock_provider import MockProvider
from backend.services.scan_service import ScanService


@pytest.fixture
def mock_scan_result():
    provider = MockProvider()
    result = provider.scan()
    assets = provider.get_assets()
    return assets, result


@pytest.fixture
def knowledge_engine(mock_scan_result):
    assets, _ = mock_scan_result
    graph_builder = GraphBuilder()
    graph_builder.add_assets(assets)
    relationships = RelationshipMapper().map(graph_builder.index)
    graph = graph_builder.build(relationships)
    return KnowledgeEngine(graph)


class TestKnowledgeEngineInitialization:

    def test_uninitialized_raises(self):
        engine = KnowledgeEngine.__new__(KnowledgeEngine)
        engine._initialized = False

        with pytest.raises(GraphNotInitialized):
            engine.find_asset("any")

    def test_initialized_from_scan(self, knowledge_engine):
        assert knowledge_engine._initialized is True


class TestAssetLookup:

    def test_find_existing_asset(self, knowledge_engine):
        asset = knowledge_engine.find_asset("vm-frontend")
        assert asset.name == "frontend-vm"
        assert asset.service == "Compute"
        assert asset.resource_type == "VM"

    def test_find_missing_asset_raises(self, knowledge_engine):
        with pytest.raises(AssetNotFound):
            knowledge_engine.find_asset("does-not-exist")

    def test_asset_exists_true(self, knowledge_engine):
        assert knowledge_engine.asset_exists("vm-frontend") is True

    def test_asset_exists_false(self, knowledge_engine):
        assert knowledge_engine.asset_exists("does-not-exist") is False


class TestAssetQueries:

    def test_find_assets_by_service(self, knowledge_engine):
        computes = knowledge_engine.find_assets(service="Compute")
        assert len(computes) == 2
        assert all(a.service == "Compute" for a in computes)

    def test_find_assets_by_type(self, knowledge_engine):
        subnets = knowledge_engine.find_assets(resource_type="Subnet")
        assert len(subnets) == 2
        assert all(a.resource_type == "Subnet" for a in subnets)

    def test_find_assets_by_service_and_type(self, knowledge_engine):
        vpcs = knowledge_engine.find_assets(service="Network", resource_type="VPC")
        assert len(vpcs) == 1
        assert vpcs[0].name == "prod-vpc"

    def test_find_all_assets(self, knowledge_engine):
        all_assets = knowledge_engine.find_assets()
        assert len(all_assets) == 10


class TestNeighborLookup:

    def test_find_neighbors_vm(self, knowledge_engine):
        neighbors = knowledge_engine.find_neighbors("vm-frontend")
        neighbor_ids = {n.id for n in neighbors}
        assert "sa-001" in neighbor_ids
        assert "subnet-001" in neighbor_ids
        assert "vpc-001" in neighbor_ids

    def test_find_neighbors_filtered_by_relation(self, knowledge_engine):
        neighbors = knowledge_engine.find_neighbors(
            "vm-frontend",
            relations=["IN_SUBNET"]
        )
        assert len(neighbors) == 1
        assert neighbors[0].id == "subnet-001"

    def test_find_neighbors_missing_asset(self, knowledge_engine):
        neighbors = knowledge_engine.find_neighbors("does-not-exist")
        assert neighbors == []


class TestPathQueries:

    def test_find_paths_existing(self, knowledge_engine):
        paths = knowledge_engine.find_paths("vm-frontend", "vpc-001")
        assert len(paths) >= 1
        assert any("vm-frontend" in p and "vpc-001" in p for p in paths)

    def test_find_paths_no_path(self, knowledge_engine):
        paths = knowledge_engine.find_paths("bucket-001", "bucket-002")
        assert paths == []

    def test_find_paths_same_node(self, knowledge_engine):
        paths = knowledge_engine.find_paths("vm-frontend", "vm-frontend")
        assert len(paths) == 1
        assert paths[0] == ["vm-frontend"]


class TestPublicAssets:

    def test_find_public_assets(self, knowledge_engine):
        public = knowledge_engine.find_public_assets()
        assert len(public) >= 1
        public_ids = {a.id for a in public}
        assert "vm-frontend" in public_ids

    def test_find_public_assets_cached(self, knowledge_engine):
        public1 = knowledge_engine.find_public_assets()
        public2 = knowledge_engine.find_public_assets()
        assert public1 is public2


class TestRelationQueries:

    def test_find_assets_with_relation(self, knowledge_engine):
        in_subnet = knowledge_engine.find_assets_with_relation("IN_SUBNET")
        assert len(in_subnet) >= 1
        sources = {s for s, t in in_subnet}
        assert "vm-frontend" in sources

    def test_find_assets_with_missing_relation(self, knowledge_engine):
        result = knowledge_engine.find_assets_with_relation("NONEXISTENT")
        assert result == []


class TestCacheCorrectness:

    def test_service_index_cached(self, knowledge_engine):
        idx1 = knowledge_engine.cache.get_service_index()
        idx2 = knowledge_engine.cache.get_service_index()
        assert idx1 is idx2

    def test_type_index_cached(self, knowledge_engine):
        idx1 = knowledge_engine.cache.get_type_index()
        idx2 = knowledge_engine.cache.get_type_index()
        assert idx1 is idx2

    def test_public_assets_cached_after_call(self, knowledge_engine):
        knowledge_engine.find_public_assets()
        assert knowledge_engine.cache.get_public_assets() is not None


class TestEndToEndIntegration:

    def test_full_scan_unchanged(self):
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
