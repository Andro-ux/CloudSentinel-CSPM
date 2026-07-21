from backend.plugins.manager import PluginManager
from backend.plugins.aws import AWSPlugin
from backend.plugins.azure import AzurePlugin
from backend.plugins.gcp import GCPPlugin
from backend.plugins.interfaces import IProviderPlugin
from backend.plugins.models import ProviderMetadata


class MockPlugin(IProviderPlugin):

    def get_metadata(self) -> ProviderMetadata:

        return ProviderMetadata(
            provider_id="mock",
            name="Mock Provider",
            version="1.0.0",
            description="Mock provider for testing",
            supported_services=["compute", "storage", "iam", "vpc", "subnet"],
            supported_collectors=["mock_collector"],
            supported_normalizers=["mock_normalizer"],
            authentication_methods=["none"],
            capabilities=["scanning"],
        )

    def scan(self):

        from backend.providers.mock_provider import MockProvider

        return MockProvider().scan()

    def get_assets(self):

        from backend.providers.mock_provider import MockProvider

        return MockProvider().get_assets()

    def validate(self) -> bool:

        return True

    def get_capabilities(self):

        return ["scanning"]

    def get_supported_services(self):

        return ["compute", "storage", "iam", "vpc", "subnet"]


_plugin_manager = PluginManager()

_plugin_manager.register_plugin(GCPPlugin())
_plugin_manager.register_plugin(AWSPlugin())
_plugin_manager.register_plugin(AzurePlugin())
_plugin_manager.register_plugin(MockPlugin())


def get_provider(provider: str):

    provider = provider.lower()

    return _plugin_manager.get_plugin(provider)
