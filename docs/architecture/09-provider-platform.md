# Provider Platform & Plugin Framework

## Purpose

The Provider Platform transforms CloudSentinel from an AWS-centric implementation into a provider-agnostic platform capable of supporting multiple cloud providers through a clean, extensible plugin system.

This is an architectural enhancement only. The intelligence pipeline remains unchanged.

## Architecture

```
                CloudSentinel Core
                        │
        ┌───────────────┼───────────────┐
        │               │               │
      AWS           Azure            GCP
     Plugin         Plugin          Plugin
        │               │               │
   Collectors      Collectors      Collectors
        │               │               │
   Normalizers     Normalizers     Normalizers
        └───────────────┼───────────────┘
                        │
             Unified Asset Model
                        │
             Security Intelligence
                        │
                 Executive Dashboard
```

## Package Structure

```
backend/plugins/
├── __init__.py
├── interfaces.py
├── exceptions.py
├── models.py
├── registry.py
├── manager.py
├── aws/
│   └── __init__.py
├── azure/
│   └── __init__.py
└── gcp/
    └── __init__.py
```

## Core Interfaces

### IProviderPlugin

The common interface all provider plugins must implement:

```python
class IProviderPlugin(ABC):
    @abstractmethod
    def get_metadata(self) -> ProviderMetadata:
        pass

    @abstractmethod
    def scan(self) -> Any:
        pass

    @abstractmethod
    def get_assets(self) -> List[Any]:
        pass

    @abstractmethod
    def validate(self) -> bool:
        pass
```

## Plugin Manager

The `PluginManager` is responsible for:

- Plugin registration and lifecycle
- Plugin lookup by provider ID
- Manifest management
- Validation orchestration
- Capability delegation

### Usage

```python
from backend.plugins.manager import PluginManager
from backend.plugins.gcp import GCPPlugin

manager = PluginManager()
manager.register_plugin(GCPPlugin())

plugin = manager.get_plugin("gcp")
result = plugin.scan()
assets = plugin.get_assets()
```

## Provider Registry

The `ProviderRegistry` maintains the registry of all available plugins:

- `register(plugin)` — Register a new plugin
- `unregister(provider_id)` — Remove a plugin
- `get(provider_id)` — Retrieve a plugin
- `get_metadata(provider_id)` — Retrieve plugin metadata
- `list_providers()` — List all registered provider IDs
- `is_registered(provider_id)` — Check if provider is registered

## Capability Registry

The `CapabilityRegistry` tracks capabilities per provider:

- `register_capabilities(provider_id, capabilities)` — Register capabilities
- `get_capabilities(provider_id)` — Get capabilities for a provider
- `has_capability(provider_id, capability_name)` — Check capability
- `list_all_capabilities()` — List all capabilities by provider

## Provider Metadata

Each plugin exposes immutable metadata:

```python
@dataclass(frozen=True)
class ProviderMetadata:
    provider_id: str
    name: str
    version: str = "1.0.0"
    description: str = ""
    author: str = "CloudSentinel Core"
    supported_services: List[str]
    supported_collectors: List[str]
    supported_normalizers: List[str]
    authentication_methods: List[str]
    capabilities: List[str]
    metadata: Dict[str, Any]
```

## Plugin Manifest

Each registered plugin receives a manifest:

```python
@dataclass(frozen=True)
class PluginManifest:
    provider_id: str
    entry_point: str
    version: str = "1.0.0"
    dependencies: List[str]
    metadata: Dict[str, Any]
```

## Exception Hierarchy

- `PluginError` — Base exception
  - `PluginRegistrationError` — Registration failures
  - `PluginNotFoundError` — Plugin not found
  - `InvalidPluginError` — Invalid plugin state
  - `PluginLifecycleError` — Lifecycle operation failures
  - `DuplicatePluginError` — Duplicate registration

## Built-in Plugins

### GCP Plugin

- Provider ID: `gcp`
- Status: Production-ready
- Services: compute, storage, iam, vpc, subnet, firewall, logging
- Collectors: gcp_compute_collector, gcp_storage_collector, gcp_iam_collector, etc.
- Normalizers: gcp_compute, gcp_storage, gcp_iam, etc.

### AWS Plugin

- Provider ID: `aws`
- Status: Scaffolded
- Services: ec2, s3, iam, vpc, subnet, security_group, lambda, rds, eks
- Collectors: Not yet implemented
- Normalizers: Not yet implemented

### Azure Plugin

- Provider ID: `azure`
- Status: Scaffolded
- Services: compute, storage, iam, vnet, subnet, nsg, key_vault
- Collectors: Not yet implemented
- Normalizers: Not yet implemented

### Mock Plugin

- Provider ID: `mock`
- Status: Production-ready (for testing)
- Services: compute, storage, iam, vpc, subnet

## Extension Guide

### Adding a New Provider

1. Create a new plugin package under `backend/plugins/`:

```
backend/plugins/oracle/
└── __init__.py
```

2. Implement the `IProviderPlugin` interface:

```python
from backend.plugins.interfaces import IProviderPlugin
from backend.plugins.models import ProviderMetadata

class OraclePlugin(IProviderPlugin):
    def get_metadata(self) -> ProviderMetadata:
        return ProviderMetadata(
            provider_id="oracle",
            name="Oracle Cloud",
            supported_services=["compute", "storage", "iam"],
            capabilities=["scanning"],
        )

    def scan(self):
        # Implement scan logic
        pass

    def get_assets(self):
        # Return normalized assets
        pass

    def validate(self) -> bool:
        return True
```

3. Register the plugin in `backend/providers/factory.py`:

```python
from backend.plugins.oracle import OraclePlugin

_plugin_manager.register_plugin(OraclePlugin())
```

### Adding a New Capability

Capabilities are declared in the plugin's `ProviderMetadata`:

```python
def get_metadata(self) -> ProviderMetadata:
    return ProviderMetadata(
        provider_id="mycloud",
        name="My Cloud",
        capabilities=["scanning", "compliance", "monitoring"],
    )
```

The `CapabilityRegistry` automatically tracks these capabilities.

## Dependency Rules

The following layers must never import provider implementations directly:

- Knowledge Engine
- Fact Engine
- Rule Engine
- Risk Engine
- Executive Intelligence

They consume normalized models only.

## Testing

The plugin framework test suite (`tests/test_plugin_framework.py`) contains 46 tests covering:

- Provider registration and lookup
- Duplicate registration handling
- Invalid plugin rejection
- Lifecycle management
- Metadata serialization
- Capability registry
- Plugin manager operations
- Extension points
- Edge cases and large-scale registration

## Code Quality

- Full type hints
- Immutable domain models (`@dataclass(frozen=True)`)
- No circular imports
- No global mutable state
- Clear package boundaries
- Comprehensive error handling
- Strategy and registry patterns
