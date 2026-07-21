from typing import Optional

from backend.providers.factory import get_provider
from backend.services.scan_service import ScanService
from backend.executive.engine import ExecutiveEngine
from backend.plugins.manager import PluginManager


def get_scan_service() -> ScanService:
    return ScanService()


def get_plugin_manager() -> PluginManager:
    from backend.plugins.manager import PluginManager
    return PluginManager.get_instance()


def get_provider_plugin(provider_id: str):
    from backend.plugins.manager import PluginManager
    manager = PluginManager.get_instance()
    return manager.get_plugin(provider_id)


def get_executive_engine() -> ExecutiveEngine:
    return ExecutiveEngine()
