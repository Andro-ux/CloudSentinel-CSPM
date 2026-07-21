import sys
sys.path.insert(0, r'C:\Users\vinit\Desktop\CloudSentinel_phase3\CloudSentinel')

import pytest

from backend.plugins.exceptions import (
    DuplicatePluginError,
    InvalidPluginError,
    PluginLifecycleError,
    PluginNotFoundError,
)
from backend.plugins.interfaces import IProviderPlugin
from backend.plugins.manager import PluginManager
from backend.plugins.models import PluginManifest, ProviderMetadata
from backend.plugins.registry import CapabilityRegistry, ProviderRegistry


class MockPlugin(IProviderPlugin):

    def __init__(self, provider_id="mock", validate_result=True):

        self._provider_id = provider_id

        self._validate_result = validate_result

    def get_metadata(self) -> ProviderMetadata:

        return ProviderMetadata(
            provider_id=self._provider_id,
            name=f"Mock {self._provider_id}",
            version="1.0.0",
            supported_services=["compute", "storage"],
            supported_collectors=["mock_collector"],
            supported_normalizers=["mock_normalizer"],
            authentication_methods=["token"],
            capabilities=["scanning"],
        )

    def scan(self):

        return []

    def get_assets(self):

        return []

    def validate(self) -> bool:

        return self._validate_result

    def get_capabilities(self):

        return ["scanning"]

    def get_supported_services(self):

        return ["compute", "storage"]


class FailingPlugin(IProviderPlugin):

    def get_metadata(self) -> ProviderMetadata:

        return ProviderMetadata(
            provider_id="failing",
            name="Failing Plugin",
        )

    def scan(self):

        raise NotImplementedError()

    def get_assets(self):

        raise NotImplementedError()

    def validate(self) -> bool:

        raise RuntimeError("Validation failed")

    def get_capabilities(self):

        return []

    def get_supported_services(self):

        return []


@pytest.fixture
def provider_registry():

    return ProviderRegistry()


@pytest.fixture
def capability_registry():

    return CapabilityRegistry()


@pytest.fixture
def plugin_manager(provider_registry, capability_registry) -> PluginManager:

    return PluginManager(
        provider_registry=provider_registry,
        capability_registry=capability_registry,
    )


class TestProviderRegistry:

    def test_register_plugin(self, provider_registry):

        plugin = MockPlugin("test")

        provider_registry.register(plugin)

        assert provider_registry.is_registered("test")

    def test_register_duplicate_raises(self, provider_registry):

        plugin = MockPlugin("test")

        provider_registry.register(plugin)

        with pytest.raises(DuplicatePluginError):

            provider_registry.register(plugin)

    def test_register_invalid_raises(self, provider_registry):

        plugin = FailingPlugin()

        with pytest.raises(InvalidPluginError):

            provider_registry.register(plugin)

    def test_get_plugin(self, provider_registry):

        plugin = MockPlugin("test")

        provider_registry.register(plugin)

        assert provider_registry.get("test") == plugin

    def test_get_missing_raises(self, provider_registry):

        with pytest.raises(PluginNotFoundError):

            provider_registry.get("missing")

    def test_get_metadata(self, provider_registry):

        plugin = MockPlugin("test")

        provider_registry.register(plugin)

        metadata = provider_registry.get_metadata("test")

        assert metadata.provider_id == "test"

        assert metadata.name == "Mock test"

    def test_list_providers(self, provider_registry):

        provider_registry.register(MockPlugin("a"))

        provider_registry.register(MockPlugin("b"))

        assert set(provider_registry.list_providers()) == {"a", "b"}

    def test_unregister(self, provider_registry):

        plugin = MockPlugin("test")

        provider_registry.register(plugin)

        provider_registry.unregister("test")

        assert not provider_registry.is_registered("test")

    def test_unregister_missing_raises(self, provider_registry):

        with pytest.raises(PluginNotFoundError):

            provider_registry.unregister("missing")

    def test_clear(self, provider_registry):

        provider_registry.register(MockPlugin("test"))

        provider_registry.clear()

        assert provider_registry.list_providers() == []


class TestCapabilityRegistry:

    def test_register_capabilities(self, capability_registry):

        capabilities = [ProviderMetadata("p", "P").capabilities]

        capability_registry.register_capabilities("p", ["scanning", "fact_engine"])

        assert capability_registry.has_capability("p", "scanning")

        assert not capability_registry.has_capability("p", "rule_engine")

    def test_get_capabilities_empty(self, capability_registry):

        assert capability_registry.get_capabilities("missing") == []

    def test_list_all_capabilities(self, capability_registry):

        capability_registry.register_capabilities("p1", ["scanning"])

        capability_registry.register_capabilities("p2", ["fact_engine"])

        all_caps = capability_registry.list_all_capabilities()

        assert "p1" in all_caps

        assert "p2" in all_caps

    def test_clear(self, capability_registry):

        capability_registry.register_capabilities("p", ["scanning"])

        capability_registry.clear()

        assert capability_registry.list_all_capabilities() == {}


class TestPluginManager:

    def test_register_plugin(self, plugin_manager):

        plugin = MockPlugin("test")

        plugin_manager.register_plugin(plugin)

        assert plugin_manager.get_plugin("test") == plugin

    def test_register_duplicate_raises(self, plugin_manager):

        plugin = MockPlugin("test")

        plugin_manager.register_plugin(plugin)

        with pytest.raises(DuplicatePluginError):

            plugin_manager.register_plugin(plugin)

    def test_register_invalid_raises(self, plugin_manager):

        plugin = FailingPlugin()

        with pytest.raises((InvalidPluginError, PluginLifecycleError)):

            plugin_manager.register_plugin(plugin)

    def test_unregister_plugin(self, plugin_manager):

        plugin = MockPlugin("test")

        plugin_manager.register_plugin(plugin)

        plugin_manager.unregister_plugin("test")

        with pytest.raises(PluginNotFoundError):

            plugin_manager.get_plugin("test")

    def test_unregister_missing_raises(self, plugin_manager):

        with pytest.raises(PluginNotFoundError):

            plugin_manager.unregister_plugin("missing")

    def test_list_plugins(self, plugin_manager):

        plugin_manager.register_plugin(MockPlugin("a"))

        plugin_manager.register_plugin(MockPlugin("b"))

        assert set(plugin_manager.list_plugins()) == {"a", "b"}

    def test_get_metadata(self, plugin_manager):

        plugin = MockPlugin("test")

        plugin_manager.register_plugin(plugin)

        metadata = plugin_manager.get_metadata("test")

        assert metadata.provider_id == "test"

    def test_get_manifest(self, plugin_manager):

        plugin = MockPlugin("test")

        plugin_manager.register_plugin(plugin)

        manifest = plugin_manager.get_manifest("test")

        assert isinstance(manifest, PluginManifest)

        assert manifest.provider_id == "test"

    def test_list_manifests(self, plugin_manager):

        plugin_manager.register_plugin(MockPlugin("a"))

        plugin_manager.register_plugin(MockPlugin("b"))

        manifests = plugin_manager.list_manifests()

        assert len(manifests) == 2

    def test_validate_plugin(self, plugin_manager):

        plugin = MockPlugin("test")

        plugin_manager.register_plugin(plugin)

        assert plugin_manager.validate_plugin("test") is True

    def test_get_supported_services(self, plugin_manager):

        plugin = MockPlugin("test")

        plugin_manager.register_plugin(plugin)

        services = plugin_manager.get_supported_services("test")

        assert "compute" in services

    def test_has_capability(self, plugin_manager):

        plugin = MockPlugin("test")

        plugin_manager.register_plugin(plugin)

        assert plugin_manager.has_capability("test", "scanning") is True

        assert plugin_manager.has_capability("test", "rule_engine") is False

    def test_clear(self, plugin_manager):

        plugin_manager.register_plugin(MockPlugin("test"))

        plugin_manager.clear()

        assert plugin_manager.list_plugins() == []


class TestPluginMetadata:

    def test_metadata_creation(self):

        metadata = ProviderMetadata(
            provider_id="test",
            name="Test Provider",
            version="2.0.0",
            description="Test",
            author="Test Author",
            supported_services=["compute"],
            supported_collectors=["collector"],
            supported_normalizers=["normalizer"],
            authentication_methods=["key"],
            capabilities=["scanning"],
            metadata={"key": "value"},
        )

        assert metadata.provider_id == "test"

        assert metadata.version == "2.0.0"

    def test_metadata_to_dict(self):

        metadata = ProviderMetadata(
            provider_id="test",
            name="Test",
        )

        d = metadata.to_dict()

        assert d["provider_id"] == "test"

        assert "supported_services" in d

    def test_metadata_immutable(self):

        metadata = ProviderMetadata(
            provider_id="test",
            name="Test",
        )

        with pytest.raises(AttributeError):

            metadata.provider_id = "changed"

    def test_manifest_creation(self):

        manifest = PluginManifest(
            provider_id="test",
            entry_point="backend.plugins.test",
            version="1.0.0",
            dependencies=[],
            metadata={},
        )

        assert manifest.provider_id == "test"

    def test_manifest_to_dict(self):

        manifest = PluginManifest(
            provider_id="test",
            entry_point="backend.plugins.test",
        )

        d = manifest.to_dict()

        assert d["entry_point"] == "backend.plugins.test"


class TestPluginIntegration:

    def test_full_lifecycle(self, plugin_manager):

        plugin = MockPlugin("lifecycle")

        plugin_manager.register_plugin(plugin)

        assert plugin_manager.get_plugin("lifecycle") == plugin

        plugin_manager.unregister_plugin("lifecycle")

        with pytest.raises(PluginNotFoundError):

            plugin_manager.get_plugin("lifecycle")

    def test_multiple_plugins(self, plugin_manager):

        plugins = [MockPlugin(f"p{i}") for i in range(5)]

        for plugin in plugins:

            plugin_manager.register_plugin(plugin)

        assert len(plugin_manager.list_plugins()) == 5

        for i in range(5):

            assert plugin_manager.get_plugin(f"p{i}") == plugins[i]

    def test_metadata_available_after_registration(self, plugin_manager):

        plugin = MockPlugin("test")

        plugin_manager.register_plugin(plugin)

        metadata = plugin_manager.get_metadata("test")

        assert metadata.supported_services == ["compute", "storage"]

    def test_capability_registration(self, plugin_manager):

        plugin = MockPlugin("test")

        plugin_manager.register_plugin(plugin)

        assert plugin_manager.has_capability("test", "scanning") is True

        assert plugin_manager.has_capability("test", "rule_engine") is False

    def test_extension_point_new_provider(self, plugin_manager):

        class NewPlugin(IProviderPlugin):

            def get_metadata(self) -> ProviderMetadata:

                return ProviderMetadata(
                    provider_id="new",
                    name="New Provider",
                    supported_services=["service1"],
                )

            def scan(self):

                return []

            def get_assets(self):

                return []

            def validate(self) -> bool:

                return True

            def get_capabilities(self):

                return ["scanning"]

            def get_supported_services(self):

                return ["service1"]

        plugin = NewPlugin()

        plugin_manager.register_plugin(plugin)

        assert plugin_manager.get_plugin("new") == plugin

        assert plugin_manager.has_capability("new", "scanning") is True


class TestPluginSerialization:

    def test_metadata_serialization(self):

        metadata = ProviderMetadata(
            provider_id="test",
            name="Test",
            supported_services=["s1", "s2"],
            capabilities=["c1"],
        )

        d = metadata.to_dict()

        assert d["provider_id"] == "test"

        assert d["supported_services"] == ["s1", "s2"]

        assert d["capabilities"] == ["c1"]

    def test_manifest_serialization(self):

        manifest = PluginManifest(
            provider_id="test",
            entry_point="backend.plugins.test",
            dependencies=["dep1"],
        )

        d = manifest.to_dict()

        assert d["dependencies"] == ["dep1"]


class TestPluginImmutability:

    def test_metadata_is_frozen(self):

        metadata = ProviderMetadata(
            provider_id="test",
            name="Test",
        )

        with pytest.raises(AttributeError):

            metadata.provider_id = "changed"

    def test_manifest_is_frozen(self):

        manifest = PluginManifest(
            provider_id="test",
            entry_point="test",
        )

        with pytest.raises(AttributeError):

            manifest.provider_id = "changed"


class TestPluginEdgeCases:

    def test_empty_registry(self, plugin_manager):

        assert plugin_manager.list_plugins() == []

        assert plugin_manager.list_manifests() == []

    def test_get_missing_manifest_raises(self, plugin_manager):

        with pytest.raises(PluginNotFoundError):

            plugin_manager.get_manifest("missing")

    def test_validate_missing_raises(self, plugin_manager):

        with pytest.raises(PluginNotFoundError):

            plugin_manager.validate_plugin("missing")

    def test_get_supported_services_missing_raises(self, plugin_manager):

        with pytest.raises(PluginNotFoundError):

            plugin_manager.get_supported_services("missing")

    def test_large_scale_registration(self, plugin_manager):

        for i in range(100):

            plugin = MockPlugin(f"p{i}")

            plugin_manager.register_plugin(plugin)

        assert len(plugin_manager.list_plugins()) == 100

        assert len(plugin_manager.list_manifests()) == 100
