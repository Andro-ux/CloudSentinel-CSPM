# Enterprise REST API

## Purpose

The Enterprise REST API exposes CloudSentinel capabilities through stable, versioned, typed endpoints. It is a translation layer between the CloudSentinel domain model and external clients.

The API does not implement security logic or business logic. All intelligence comes from existing engines.

## Architecture

```
Client → FastAPI → Router → Dependency → Domain Service → Response Envelope
```

### Key Principles

- **Read-only**: No create/update/delete operations in this sprint
- **Versioned**: All endpoints live under `/api/v1/`
- **Typed**: Every endpoint uses Pydantic schemas
- **Provider agnostic**: No provider-specific logic in routers
- **Extensible**: Future versions coexist without breaking changes

## Package Structure

```
backend/api/
├── __init__.py
├── app.py
├── dependencies.py
├── exceptions.py
├── middleware.py
├── pagination.py
├── filters.py
├── responses.py
├── version.py
├── routers/
│   ├── __init__.py
│   ├── dashboard.py
│   ├── assets.py
│   ├── findings.py
│   ├── risks.py
│   ├── graph.py
│   ├── providers.py
│   ├── capabilities.py
│   └── health.py
└── schemas/
    ├── __init__.py
    ├── common.py
    ├── dashboard.py
    ├── asset.py
    ├── finding.py
    ├── risk.py
    ├── provider.py
    └── capability.py
```

## Response Envelope

Every successful response uses a consistent envelope:

```json
{
  "success": true,
  "data": {},
  "metadata": {
    "generated_at": "...",
    "api_version": "v1"
  }
}
```

Paginated responses include pagination metadata:

```json
{
  "success": true,
  "data": [],
  "metadata": {
    "pagination": {
      "page": 1,
      "page_size": 25,
      "total": 100,
      "has_next": true,
      "has_previous": false
    },
    "generated_at": "...",
    "api_version": "v1"
  }
}
```

## Error Responses

Errors follow the same structure:

```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Asset not found",
    "details": null
  }
}
```

### Error Codes

| Code | Status | Description |
|------|--------|-------------|
| `NOT_FOUND` | 404 | Resource not found |
| `VALIDATION_ERROR` | 422 | Invalid request parameters |
| `INTERNAL_ERROR` | 500 | Server error |

## Endpoints

### Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/health` | Platform health check |

### Dashboard

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/dashboard` | Executive dashboard |

### Assets

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/assets` | List assets (paginated, filterable, sortable) |
| GET | `/api/v1/assets/{asset_id}` | Get asset by ID |

**Query Parameters:**
- `page` (int, default: 1)
- `page_size` (int, default: 25, max: 100)
- `provider` (string, optional)
- `asset_type` (string, optional)
- `search` (string, optional)

### Findings

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/findings` | List findings (paginated, filterable) |

**Query Parameters:**
- `page` (int, default: 1)
- `page_size` (int, default: 25, max: 100)
- `severity` (string, optional)
- `category` (string, optional)
- `provider` (string, optional)
- `asset` (string, optional)

### Risks

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/risks` | List risks (paginated, filterable, sortable) |

**Query Parameters:**
- `page` (int, default: 1)
- `page_size` (int, default: 25, max: 100)
- `priority` (string, optional)
- `category` (string, optional)
- `min_score` (int, optional)
- `max_score` (int, optional)
- `sort_by` (string, optional)
- `order` (string, default: "desc")

### Graph

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/graph` | Knowledge graph (nodes, edges, metadata) |

### Providers

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/providers` | List registered providers |

Returns provider metadata from the PluginManager. No hardcoded providers.

### Capabilities

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/capabilities` | List provider capabilities |

## Pagination

All list endpoints support pagination:

- `page`: Current page number (1-indexed)
- `page_size`: Items per page (1-100)
- `total`: Total number of items
- `has_next`: Whether more pages exist
- `has_previous`: Whether previous pages exist

## Filtering

Reusable filter classes enforce consistent query parameter validation:

- `AssetFilters`: provider, asset_type, search
- `FindingFilters`: severity, category, provider, asset
- `RiskFilters`: priority, category, min_score, max_score

## Sorting

Supported on risks endpoint:

- `sort_by`: Field name to sort by
- `order`: `asc` or `desc`

## Middleware

- **Request Logging**: Logs every request with timing
- **Request ID**: Generates unique request IDs
- **CORS**: Configurable CORS headers
- **Exception Translation**: Converts exceptions to standardized error responses

## Dependency Injection

Routers receive dependencies via FastAPI's DI system:

- `get_scan_service()` → `ScanService`
- `get_plugin_manager()` → `PluginManager`
- `get_executive_engine()` → `ExecutiveEngine`
- `get_provider_plugin(provider_id)` → `IProviderPlugin`

Routers never instantiate engines directly.

## DTO Layer

Domain models are never exposed directly. Every endpoint maps to explicit API schemas:

```
Domain Model → Pydantic Schema → JSON
```

This prevents API breakage when domain models evolve.

## Extension Guide

### Adding a New Endpoint

1. Create a schema in `backend/api/schemas/`
2. Create a router in `backend/api/routers/`
3. Register the router in `backend/api/app.py`
4. Add dependency if needed in `backend/api/dependencies.py`

### Adding a New Version

1. Create `backend/api/v2/` directory
2. Copy and modify routers as needed
3. Register v2 router alongside v1 in `app.py`

## OpenAPI

The API generates production-quality OpenAPI documentation:

- `/docs` — Swagger UI
- `/redoc` — ReDoc
- `/openapi.json` — Raw OpenAPI spec

Every endpoint includes:
- Summary
- Description
- Tags
- Response models
- Error models

## Testing

The API test suite (`tests/test_api.py`) contains 46 tests covering:

- Every endpoint
- Pagination
- Filtering
- Sorting
- Response envelopes
- OpenAPI generation
- Dependency injection
- Error responses
- Invalid requests
- Serialization
- Health endpoint
- Provider endpoint
- Capability endpoint
- Dashboard endpoint

## Code Quality

- Full type hints
- Pydantic response schemas
- No duplicated routing logic
- No circular imports
- Clear package boundaries
- Comprehensive OpenAPI documentation
- Consistent response contracts
