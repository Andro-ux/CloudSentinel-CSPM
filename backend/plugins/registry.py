from typing import Dict, List, Optional

from backend.plugins.exceptions import (
    DuplicatePluginError,
    InvalidPluginError,
    PluginNotFoundError,
)
from backend.plugins.interfaces import IProviderPlugin
from backend.plugins.models import ProviderMetadata


class ProviderRegistry:

    _instance = None

    def __init__(self):

        self._providers: Dict[str, IProviderPlugin] = {}

        self._metadata: Dict[str, ProviderMetadata] = {}

    @classmethod
    def get_instance(cls):

        if cls._instance is None:

            cls._instance = cls()

        return cls._instance

    def register(self, plugin: IProviderPlugin) -> None:

        metadata = plugin.get_metadata()

        provider_id = metadata.provider_id

        if provider_id in self._providers:

            raise DuplicatePluginError(provider_id)

        try:

            is_valid = plugin.validate()

        except Exception as exc:

            raise InvalidPluginError(provider_id, str(exc))

        if not is_valid:

            raise InvalidPluginError(provider_id, "Validation failed")

        self._providers[provider_id] = plugin

        self._metadata[provider_id] = metadata

    def unregister(self, provider_id: str) -> None:

        if provider_id not in self._providers:

            raise PluginNotFoundError(provider_id)

        del self._providers[provider_id]

        del self._metadata[provider_id]

    def get(self, provider_id: str) -> IProviderPlugin:

        if provider_id not in self._providers:

            raise PluginNotFoundError(provider_id)

        return self._providers[provider_id]

    def get_metadata(self, provider_id: str) -> ProviderMetadata:

        if provider_id not in self._metadata:

            raise PluginNotFoundError(provider_id)

        return self._metadata[provider_id]

    def list_providers(self) -> List[str]:

        return list(self._providers.keys())

    def list_metadata(self) -> List[ProviderMetadata]:

        return list(self._metadata.values())

    def is_registered(self, provider_id: str) -> bool:

        return provider_id in self._providers

    def clear(self) -> None:

        self._providers.clear()

        self._metadata.clear()


class CapabilityRegistry:

    _instance = None

    def __init__(self):

        self._capabilities: Dict[str, List[str]] = {}

    @classmethod
    def get_instance(cls):

        if cls._instance is None:

            cls._instance = cls()

        return cls._instance

    def register_capabilities(self, provider_id: str, capabilities: List[str]) -> None:

        self._capabilities[provider_id] = capabilities

    def get_capabilities(self, provider_id: str) -> List[str]:

        return self._capabilities.get(provider_id, [])

    def list_all_capabilities(self) -> Dict[str, List[str]]:

        return dict(self._capabilities)

    def has_capability(self, provider_id: str, capability_name: str) -> bool:

        capabilities = self._capabilities.get(provider_id, [])

        return capability_name in capabilities

    def clear(self) -> None:

        self._capabilities.clear()
