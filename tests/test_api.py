import sys
sys.path.insert(0, r'C:\Users\vinit\Desktop\CloudSentinel_phase3\CloudSentinel')

import pytest
from fastapi.testclient import TestClient
from backend.api.app import create_app


@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)


class TestHealthEndpoint:
    def test_health_check(self, client):
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "healthy"
        assert "timestamp" in data["data"]
        assert data["data"]["api_version"] == "v1"

    def test_health_response_metadata(self, client):
        response = client.get("/api/v1/health")
        data = response.json()
        assert "metadata" in data
        assert data["metadata"]["api_version"] == "v1"


class TestProvidersEndpoint:
    def test_list_providers(self, client):
        response = client.get("/api/v1/providers")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "metadata" in data
        assert data["metadata"]["total"] >= 3

    def test_providers_include_gcp(self, client):
        response = client.get("/api/v1/providers")
        data = response.json()
        provider_ids = [p["provider_id"] for p in data["data"]]
        assert "gcp" in provider_ids
        assert "aws" in provider_ids
        assert "azure" in provider_ids

    def test_provider_metadata_structure(self, client):
        response = client.get("/api/v1/providers")
        data = response.json()
        provider = data["data"][0]
        assert "provider_id" in provider
        assert "name" in provider
        assert "version" in provider
        assert "supported_services" in provider
        assert "capabilities" in provider


class TestCapabilitiesEndpoint:
    def test_list_capabilities(self, client):
        response = client.get("/api/v1/capabilities")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert data["metadata"]["total"] >= 3

    def test_capabilities_include_scanning(self, client):
        response = client.get("/api/v1/capabilities")
        data = response.json()
        all_caps = []
        for item in data["data"]:
            all_caps.extend(item["capabilities"])
        assert "scanning" in all_caps


class TestDashboardEndpoint:
    def test_get_dashboard(self, client):
        response = client.get("/api/v1/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "security_score" in data["data"]
        assert "metrics" in data["data"]
        assert "insights" in data["data"]
        assert "recommendations" in data["data"]
        assert "executive_narrative" in data["data"]

    def test_dashboard_security_score_structure(self, client):
        response = client.get("/api/v1/dashboard")
        data = response.json()
        score = data["data"]["security_score"]
        assert "overall" in score
        assert "grade" in score
        assert "dimensions" in score
        assert "breakdown" in score
        assert 0 <= score["overall"] <= 100
        assert score["grade"] in ["A", "B", "C", "D", "F"]

    def test_dashboard_metadata(self, client):
        response = client.get("/api/v1/dashboard")
        data = response.json()
        assert "generated_at" in data["metadata"]
        assert data["metadata"]["api_version"] == "v1"

    def test_dashboard_summary_structure(self, client):
        response = client.get("/api/v1/dashboard")
        data = response.json()
        summary = data["data"]["summary"]
        assert "total_assets" in summary
        assert "total_findings" in summary
        assert "total_risks" in summary
        assert "security_score" in summary


class TestAssetsEndpoint:
    def test_list_assets(self, client):
        response = client.get("/api/v1/assets")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "metadata" in data
        assert "pagination" in data["metadata"]

    def test_assets_pagination(self, client):
        response = client.get("/api/v1/assets?page=1&page_size=10")
        data = response.json()
        assert data["metadata"]["pagination"]["page"] == 1
        assert data["metadata"]["pagination"]["page_size"] == 10

    def test_assets_pagination_meta(self, client):
        response = client.get("/api/v1/assets?page=1&page_size=10")
        data = response.json()
        pagination = data["metadata"]["pagination"]
        assert "total" in pagination
        assert "has_next" in pagination
        assert "has_previous" in pagination

    def test_get_asset_by_id(self, client):
        response = client.get("/api/v1/assets/test-asset-id")
        assert response.status_code in [200, 404]

    def test_assets_filter_by_provider(self, client):
        response = client.get("/api/v1/assets?provider=gcp")
        assert response.status_code == 200

    def test_assets_filter_by_type(self, client):
        response = client.get("/api/v1/assets?asset_type=compute")
        assert response.status_code == 200

    def test_assets_search(self, client):
        response = client.get("/api/v1/assets?search=test")
        assert response.status_code == 200


class TestFindingsEndpoint:
    def test_list_findings(self, client):
        response = client.get("/api/v1/findings")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "metadata" in data

    def test_findings_pagination(self, client):
        response = client.get("/api/v1/findings?page=1&page_size=10")
        data = response.json()
        assert data["metadata"]["pagination"]["page_size"] == 10

    def test_findings_filter_by_severity(self, client):
        response = client.get("/api/v1/findings?severity=HIGH")
        assert response.status_code == 200
        data = response.json()
        for finding in data["data"]:
            assert finding["severity"].upper() == "HIGH"

    def test_findings_filter_by_category(self, client):
        response = client.get("/api/v1/findings?category=Network")
        assert response.status_code == 200

    def test_findings_filter_by_provider(self, client):
        response = client.get("/api/v1/findings?provider=gcp")
        assert response.status_code == 200

    def test_findings_filter_by_asset(self, client):
        response = client.get("/api/v1/findings?asset=test-asset")
        assert response.status_code == 200

    def test_findings_response_structure(self, client):
        response = client.get("/api/v1/findings")
        data = response.json()
        if data["data"]:
            finding = data["data"][0]
            assert "id" in finding
            assert "title" in finding
            assert "severity" in finding
            assert "category" in finding


class TestRisksEndpoint:
    def test_list_risks(self, client):
        response = client.get("/api/v1/risks")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "metadata" in data

    def test_risks_pagination(self, client):
        response = client.get("/api/v1/risks?page=1&page_size=10")
        data = response.json()
        assert data["metadata"]["pagination"]["page_size"] == 10

    def test_risks_filter_by_priority(self, client):
        response = client.get("/api/v1/risks?priority=HIGH")
        assert response.status_code == 200

    def test_risks_filter_by_category(self, client):
        response = client.get("/api/v1/risks?category=Network")
        assert response.status_code == 200

    def test_risks_filter_by_score_range(self, client):
        response = client.get("/api/v1/risks?min_score=0&max_score=100")
        assert response.status_code == 200

    def test_risks_sorting(self, client):
        response = client.get("/api/v1/risks?sort_by=score&order=desc")
        assert response.status_code == 200

    def test_risks_response_structure(self, client):
        response = client.get("/api/v1/risks")
        data = response.json()
        if data["data"]:
            risk = data["data"][0]
            assert "id" in risk
            assert "priority" in risk
            assert "score" in risk
            assert "category" in risk


class TestGraphEndpoint:
    def test_get_graph(self, client):
        response = client.get("/api/v1/graph")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "nodes" in data["data"]
        assert "edges" in data["data"]
        assert "metadata" in data["data"]

    def test_graph_metadata(self, client):
        response = client.get("/api/v1/graph")
        data = response.json()
        metadata = data["data"]["metadata"]
        assert "total_nodes" in metadata
        assert "total_edges" in metadata
        assert "generated_at" in metadata
        assert metadata["api_version"] == "v1"


class TestErrorHandling:
    def test_404_error(self, client):
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404

    def test_method_not_allowed(self, client):
        response = client.post("/api/v1/health")
        assert response.status_code == 405

    def test_invalid_page_parameter(self, client):
        response = client.get("/api/v1/assets?page=0")
        assert response.status_code == 422

    def test_invalid_page_size_parameter(self, client):
        response = client.get("/api/v1/assets?page_size=200")
        assert response.status_code == 422


class TestOpenAPI:
    def test_openapi_json(self, client):
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "paths" in data
        assert "/api/v1/health" in data["paths"]
        assert "/api/v1/dashboard" in data["paths"]
        assert "/api/v1/assets" in data["paths"]
        assert "/api/v1/findings" in data["paths"]
        assert "/api/v1/risks" in data["paths"]
        assert "/api/v1/graph" in data["paths"]
        assert "/api/v1/providers" in data["paths"]
        assert "/api/v1/capabilities" in data["paths"]

    def test_docs_endpoint(self, client):
        response = client.get("/docs")
        assert response.status_code == 200

    def test_openapi_tags(self, client):
        response = client.get("/openapi.json")
        data = response.json()
        tags = [t["name"] for t in data.get("tags", [])]
        assert "Dashboard" in tags
        assert "Assets" in tags
        assert "Findings" in tags
        assert "Risks" in tags
        assert "Graph" in tags
        assert "Providers" in tags
        assert "Capabilities" in tags
        assert "Health" in tags


class TestResponseEnvelope:
    def test_success_envelope_structure(self, client):
        response = client.get("/api/v1/health")
        data = response.json()
        assert "success" in data
        assert "data" in data
        assert "metadata" in data
        assert data["success"] is True

    def test_metadata_includes_api_version(self, client):
        response = client.get("/api/v1/health")
        data = response.json()
        assert data["metadata"]["api_version"] == "v1"

    def test_metadata_includes_generated_at(self, client):
        response = client.get("/api/v1/health")
        data = response.json()
        assert "generated_at" in data["metadata"]


class TestVersioning:
    def test_all_endpoints_under_v1(self, client):
        response = client.get("/openapi.json")
        data = response.json()
        paths = list(data["paths"].keys())
        for path in paths:
            assert path.startswith("/api/v1/"), f"Endpoint {path} is not versioned"

    def test_no_unversioned_endpoints(self, client):
        response = client.get("/openapi.json")
        data = response.json()
        paths = list(data["paths"].keys())
        for path in paths:
            assert path.startswith("/api/v1/"), f"Endpoint {path} is unversioned"
