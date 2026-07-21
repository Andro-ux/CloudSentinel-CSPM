from typing import Dict, List, Optional

from backend.plugins.exceptions import (
    InvalidPluginError,
    PluginLifecycleError,
    PluginNotFoundError,
)
from backend.plugins.interfaces import IProviderPlugin
from backend.plugins.models import PluginManifest, ProviderMetadata
from backend.plugins.registry import CapabilityRegistry, ProviderRegistry


class PluginManager:

    _instance = None

    def __init__(
        self,
        provider_registry: ProviderRegistry = None,
        capability_registry: CapabilityRegistry = None,
    ):

        self.provider_registry = provider_registry or ProviderRegistry.get_instance()

        self.capability_registry = capability_registry or CapabilityRegistry.get_instance()

        self._manifests: Dict[str, PluginManifest] = {}

    @classmethod
    def get_instance(cls):

        if cls._instance is None:

            cls._instance = cls()

        return cls._instance

    def register_plugin(self, plugin: IProviderPlugin) -> None:

        metadata = plugin.get_metadata()

        provider_id = metadata.provider_id

        self._validate_plugin(plugin)

        self.provider_registry.register(plugin)

        self.capability_registry.register_capabilities(
            provider_id,
            plugin.get_capabilities(),
        )

        manifest = PluginManifest(
            provider_id=provider_id,
            entry_point=plugin.__class__.__module__,
            version=metadata.version,
            dependencies=[],
            metadata=metadata.metadata,
        )

        self._manifests[provider_id] = manifest

    def unregister_plugin(self, provider_id: str) -> None:

        if provider_id not in self._manifests:

            raise PluginNotFoundError(provider_id)

        self.provider_registry.unregister(provider_id)

        self.capability_registry._capabilities.pop(provider_id, None)

        del self._manifests[provider_id]

    def get_plugin(self, provider_id: str) -> IProviderPlugin:

        return self.provider_registry.get(provider_id)

    def get_metadata(self, provider_id: str) -> ProviderMetadata:

        return self.provider_registry.get_metadata(provider_id)

    def list_plugins(self) -> List[str]:

        return self.provider_registry.list_providers()

    def list_manifests(self) -> List[PluginManifest]:

        return list(self._manifests.values())

    def get_manifest(self, provider_id: str) -> PluginManifest:

        if provider_id not in self._manifests:

            raise PluginNotFoundError(provider_id)

        return self._manifests[provider_id]

    def validate_plugin(self, provider_id: str) -> bool:

        plugin = self.provider_registry.get(provider_id)

        return plugin.validate()

    def get_supported_services(self, provider_id: str) -> List[str]:

        plugin = self.provider_registry.get(provider_id)

        return plugin.get_supported_services()

    def has_capability(self, provider_id: str, capability_name: str) -> bool:

        return self.capability_registry.has_capability(provider_id, capability_name)

    def _validate_plugin(self, plugin: IProviderPlugin) -> None:

        metadata = plugin.get_metadata()

        if not metadata.provider_id:

            raise InvalidPluginError("unknown", "Missing provider_id")

        if not metadata.name:

            raise InvalidPluginError(metadata.provider_id, "Missing name")

        try:

            plugin.validate()

        except Exception as exc:

            raise PluginLifecycleError(
                metadata.provider_id,
                "validation",
                str(exc),
            )

    def clear(self) -> None:

        self.provider_registry.clear()

        self._manifests.clear()
