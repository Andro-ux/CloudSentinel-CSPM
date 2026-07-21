from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass(frozen=True)
class ProviderMetadata:

    provider_id: str

    name: str

    version: str = "1.0.0"

    description: str = ""

    author: str = "CloudSentinel Core"

    supported_services: List[str] = field(default_factory=list)

    supported_collectors: List[str] = field(default_factory=list)

    supported_normalizers: List[str] = field(default_factory=list)

    authentication_methods: List[str] = field(default_factory=list)

    capabilities: List[str] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:

        return {

            "provider_id": self.provider_id,

            "name": self.name,

            "version": self.version,

            "description": self.description,

            "author": self.author,

            "supported_services": list(self.supported_services),

            "supported_collectors": list(self.supported_collectors),

            "supported_normalizers": list(self.supported_normalizers),

            "authentication_methods": list(self.authentication_methods),

            "capabilities": list(self.capabilities),

            "metadata": dict(self.metadata),

        }


@dataclass(frozen=True)
class PluginManifest:

    provider_id: str

    entry_point: str

    version: str = "1.0.0"

    dependencies: List[str] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:

        return {

            "provider_id": self.provider_id,

            "entry_point": self.entry_point,

            "version": self.version,

            "dependencies": list(self.dependencies),

            "metadata": dict(self.metadata),

        }
