# Fact Engine

The Fact Engine transforms cloud infrastructure knowledge into immutable security facts. It sits between the Knowledge Engine and the Rule Engine, establishing the security vocabulary of CloudSentinel.

## Architecture

```
Infrastructure
      ↓
Knowledge (Graph + Queries)
      ↓
Facts (Immutable Security Truths)
      ↓
Rules (Compliance / Misconfiguration Detection)
      ↓
Risk (Business Context)
      ↓
Executive Intelligence
```

## Responsibilities

- Receive an `IKnowledgeEngine`
- Execute registered extractors
- Return an immutable `FactSet`
- **Never** calculate findings
- **Never** calculate risk
- **Never** generate reports

## Fact Model

Facts are immutable `@dataclass(frozen=True)` objects with the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Unique fact identifier |
| `asset_id` | `str` | Asset this fact describes |
| `fact_type` | `FactType` | Canonical fact type from enum |
| `severity` | `str` | CRITICAL, HIGH, MEDIUM, LOW, INFO |
| `provider` | `str` | Cloud provider (gcp, aws, azure) |
| `category` | `str` | Network, Compute, Storage, IAM, Logging |
| `evidence` | `Evidence` | Structured evidence dataclass |
| `metadata` | `Dict[str, Any]` | Additional context |
| `description` | `str` | Human-readable description |

### Evidence Model

Evidence is a dedicated frozen dataclass:

| Field | Type | Description |
|-------|------|-------------|
| `provider` | `str` | Cloud provider |
| `source` | `str` | Source of evidence (e.g., `asset.security`) |
| `attribute` | `str` | Specific attribute (e.g., `public_ip`) |
| `value` | `Any` | Observed value |
| `timestamp` | `Optional[datetime]` | When evidence was collected |

## FactType Enum

The `FactType` enum is the canonical vocabulary for security facts:

- `PUBLIC_VM`
- `PUBLIC_SUBNET`
- `PUBLIC_BUCKET`
- `UNENCRYPTED_BUCKET`
- `OPEN_FIREWALL`
- `ADMIN_SERVICE_ACCOUNT`
- `UNUSED_SERVICE_ACCOUNT`
- `OVER_PRIVILEGED_IDENTITY`
- `FLOW_LOGS_DISABLED`
- `AUDIT_LOGGING_DISABLED`
- `METADATA_SERVICE_ENABLED`
- `SHIELDED_VM_DISABLED`
- `INTERNET_REACHABLE`
- `VERSIONING_DISABLED`

## FactSet

`FactSet` is a lightweight, read-only container with:

- Iteration over all facts
- `find_by_asset(asset_id)` — O(1) lookup
- `find_by_type(fact_type)` — O(1) lookup
- `contains(fact)` — membership test
- `statistics()` — count by fact type
- `grouped_by_type()` — facts grouped by `FactType`
- `grouped_by_asset()` — facts grouped by asset ID

## Fact Registry

The `FactRegistry` automatically discovers and executes extractors:

1. **Registration** — Extractors are registered with the registry
2. **Execution** — All extractors run in sequence
3. **Merging** — Results are merged into a single list
4. **Duplicate prevention** — Facts with duplicate IDs are skipped
5. **Isolation** — One failing extractor does not stop the pipeline; `ExtractorError` is raised

## Extractors

Each extractor understands one domain:

| Extractor | Domain | Fact Types |
|-----------|--------|------------|
| `NetworkFactsExtractor` | Networking | `PUBLIC_VM`, `PUBLIC_SUBNET`, `INTERNET_REACHABLE`, `OPEN_FIREWALL` |
| `ComputeFactsExtractor` | Compute | `SHIELDED_VM_DISABLED`, `METADATA_SERVICE_ENABLED` |
| `StorageFactsExtractor` | Storage | `PUBLIC_BUCKET`, `UNENCRYPTED_BUCKET`, `VERSIONING_DISABLED` |
| `IAMFactsExtractor` | Identity | `ADMIN_SERVICE_ACCOUNT`, `UNUSED_SERVICE_ACCOUNT`, `OVER_PRIVILEGED_IDENTITY` |
| `LoggingFactsExtractor` | Logging | `AUDIT_LOGGING_DISABLED`, `FLOW_LOGS_DISABLED` |

## Lifecycle

```
GraphBuilder
    ↓ build Graph
KnowledgeEngine
    ↓ initialize caches
FactRegistry
    ↓ execute extractors
FactEngine
    ↓ produce immutable facts
FactSet
    ↓ available to Rule Engine
```

## Usage

```python
from backend.facts.engine import FactEngine
from backend.facts.extractors.network import NetworkFactsExtractor
from backend.facts.extractors.compute import ComputeFactsExtractor
from backend.facts.extractors.storage import StorageFactsExtractor
from backend.facts.extractors.iam import IAMFactsExtractor
from backend.facts.extractors.logging import LoggingFactsExtractor
from backend.facts.registry import FactRegistry

registry = FactRegistry()
registry.register(NetworkFactsExtractor())
registry.register(ComputeFactsExtractor())
registry.register(StorageFactsExtractor())
registry.register(IAMFactsExtractor())
registry.register(LoggingFactsExtractor())

fact_engine = FactEngine(knowledge, registry)
fact_set = fact_engine.extract()

# Query facts
public_vms = fact_set.find_by_type(FactType.PUBLIC_VM)
vm_facts = fact_set.find_by_asset("vm-frontend")
stats = fact_set.statistics()
```

## Extending

To add a new fact type:

1. Add the type to `FactType` enum in `backend/facts/models.py`
2. Add emission logic in the appropriate extractor
3. Update tests

To add a new extractor:

1. Implement `IFactExtractor` in `backend/facts/extractors/`
2. Register it in `CorrelationEngine.correlate()`
3. Add tests

## Performance

- Fact extraction: O(N × E) where N is assets and E is extractors
- Fact lookup by asset: O(1)
- Fact lookup by type: O(1)
- Duplicate prevention: O(F) where F is total facts
