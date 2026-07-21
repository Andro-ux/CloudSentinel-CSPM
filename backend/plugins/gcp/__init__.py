from typing import List

from backend.plugins.interfaces import IProviderPlugin
from backend.plugins.models import ProviderMetadata


class GCPPlugin(IProviderPlugin):

    def get_metadata(self) -> ProviderMetadata:

        return ProviderMetadata(
            provider_id="gcp",
            name="Google Cloud Platform",
            version="1.0.0",
            description="GCP security scanning plugin",
            author="CloudSentinel Core",
            supported_services=[
                "compute",
                "storage",
                "iam",
                "vpc",
                "subnet",
                "firewall",
                "logging",
            ],
            supported_collectors=[
                "gcp_compute_collector",
                "gcp_storage_collector",
                "gcp_iam_collector",
                "gcp_vpc_collector",
                "gcp_subnet_collector",
                "gcp_firewall_collector",
            ],
            supported_normalizers=[
                "gcp_compute",
                "gcp_storage",
                "gcp_iam",
                "gcp_vpc",
                "gcp_subnet",
                "gcp_firewall",
            ],
            authentication_methods=["service_account", "oauth"],
            capabilities=["scanning", "knowledge_engine", "fact_engine"],
        )

    def scan(self):

        from backend.providers.gcp_provider import GCPProvider

        provider = GCPProvider()

        return provider.scan()

    def get_assets(self) -> List:

        from backend.providers.gcp_provider import GCPProvider

        provider = GCPProvider()

        return provider.get_assets()

    def validate(self) -> bool:

        return True

    def get_capabilities(self) -> List[str]:

        return ["scanning", "knowledge_engine", "fact_engine"]

    def get_supported_services(self) -> List[str]:

        return self.get_metadata().supported_services
