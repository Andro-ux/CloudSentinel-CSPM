from typing import List

from backend.plugins.interfaces import IProviderPlugin
from backend.plugins.models import ProviderMetadata


class AzurePlugin(IProviderPlugin):

    def get_metadata(self) -> ProviderMetadata:

        return ProviderMetadata(
            provider_id="azure",
            name="Microsoft Azure",
            version="1.0.0",
            description="Azure security scanning plugin",
            author="CloudSentinel Core",
            supported_services=[
                "compute",
                "storage",
                "iam",
                "vnet",
                "subnet",
                "nsg",
                "key_vault",
            ],
            supported_collectors=[],
            supported_normalizers=[],
            authentication_methods=["service_principal", "managed_identity"],
            capabilities=["scanning", "knowledge_engine", "fact_engine"],
        )

    def scan(self):

        raise NotImplementedError("Azure plugin not yet implemented")

    def get_assets(self) -> List:

        raise NotImplementedError("Azure plugin not yet implemented")

    def validate(self) -> bool:

        return True

    def get_capabilities(self) -> List[str]:

        return ["scanning", "knowledge_engine", "fact_engine"]

    def get_supported_services(self) -> List[str]:

        return self.get_metadata().supported_services
