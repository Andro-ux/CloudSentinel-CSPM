from fastapi import APIRouter, Depends
from backend.api.dependencies import get_plugin_manager
from backend.plugins.manager import PluginManager


router = APIRouter()


@router.get(
    "/capabilities",
    response_model=dict,
    tags=["Capabilities"],
    summary="List provider capabilities",
    description="Returns capabilities for all registered providers.",
)
def list_capabilities(plugin_manager: PluginManager = Depends(get_plugin_manager)):
    capabilities = []
    for provider_id in plugin_manager.list_plugins():
        metadata = plugin_manager.get_metadata(provider_id)
        capabilities.append({
            "provider_id": provider_id,
            "capabilities": metadata.capabilities,
            "supported_services": metadata.supported_services,
            "supported_collectors": metadata.supported_collectors,
            "supported_normalizers": metadata.supported_normalizers,
        })
    return {
        "success": True,
        "data": capabilities,
        "metadata": {
            "total": len(capabilities),
            "generated_at": __import__('datetime').datetime.utcnow().isoformat(),
            "api_version": "v1",
        },
    }
