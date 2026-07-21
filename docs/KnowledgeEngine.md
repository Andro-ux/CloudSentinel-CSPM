# Knowledge Engine

The Knowledge Engine is the central query layer of CloudSentinel's graph-based security model. It provides a stable, high-level contract for querying the knowledge graph, hiding graph implementation details from consumers.

## Responsibilities

- Hold the authoritative `Graph` object
- Expose high-level query methods
- Cache frequently accessed indexes
- Hide graph implementation details
- **Never** create findings
- **Never** calculate risk
- **Never** generate reports

## Public API

### `KnowledgeEngine`

```python
from backend.knowledge.engine import KnowledgeEngine

knowledge = KnowledgeEngine(graph)
```

#### Methods

| Method | Description |
|--------|-------------|
| `find_asset(asset_id)` | Return `AssetNode` by ID. Raises `AssetNotFound` if missing. |
| `find_assets(service=None, resource_type=None)` | Return assets filtered by service and/or resource type. |
| `find_neighbors(asset_id, relations=None)` | Return neighbor `AssetNode`s, optionally filtered by relation types. |
| `find_paths(source, target)` | Return all paths from `source` to `target`. |
| `find_public_assets()` | Return all assets with `security.public_ip == True`. |
| `find_assets_with_relation(relation)` | Return `(source, target)` tuples for a given relation type. |
| `asset_exists(asset_id)` | Return `True` if the asset exists in the graph. |
| `get_adjacency()` | Return the adjacency dictionary for traversal. |
| `get_edges()` | Return all `Relationship` objects. |

### Exceptions

| Exception | Description |
|-----------|-------------|
| `AssetNotFound` | Raised when querying a non-existent asset. |
| `GraphNotInitialized` | Raised when querying before graph initialization. |
| `InvalidRelationship` | Raised when a relationship fails validation. |

## Query Lifecycle

```
GraphBuilder
    ↓ build Graph
KnowledgeEngine
    ↓ initialize caches
GraphQuery
    ↓ answer queries
AttackPathEngine / Consumers
```

1. `GraphBuilder` constructs the `Graph` from assets and relationships.
2. `KnowledgeEngine` receives the `Graph` and initializes caches.
3. `GraphQuery` performs efficient lookups using precomputed indexes.
4. Consumers (e.g., `AttackPathEngine`) ask high-level questions.

## Graph Ownership

`GraphBuilder` is the **sole** constructor of the graph. No other component should assemble nodes, edges, or adjacency structures. The `Graph` object is immutable after construction.

## Example Usage

```python
from backend.knowledge.engine import KnowledgeEngine

# Build graph (typically done by CorrelationEngine)
graph = graph_builder.build(relationships)
knowledge = KnowledgeEngine(graph)

# Query assets
vm = knowledge.find_asset("vm-frontend")
subnets = knowledge.find_assets(resource_type="Subnet")
public = knowledge.find_public_assets()

# Query relationships
neighbors = knowledge.find_neighbors(vm.id, relations=["IN_SUBNET"])
paths = knowledge.find_paths("vm-frontend", "prod-vpc")
```

## Performance

- Asset lookup: O(1)
- Neighbor lookup: O(k) where k is the degree of the node
- Service/type queries: O(1) via cached indexes
- Path queries: O(V + E) via BFS

Cached indexes are built once during initialization and reused across queries.
