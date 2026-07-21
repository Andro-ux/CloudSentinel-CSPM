from fastapi import APIRouter, Depends
from backend.api.dependencies import get_plugin_manager
from backend.plugins.manager import PluginManager


router = APIRouter()


@router.get(
    "/providers",
    response_model=dict,
    tags=["Providers"],
    summary="List registered providers",
    description="Returns all registered cloud provider plugins with their metadata.",
)
def list_providers(plugin_manager: PluginManager = Depends(get_plugin_manager)):
    providers = []
    for provider_id in plugin_manager.list_plugins():
        metadata = plugin_manager.get_metadata(provider_id)
        providers.append({
            "provider_id": metadata.provider_id,
            "name": metadata.name,
            "version": metadata.version,
            "description": metadata.description,
            "supported_services": metadata.supported_services,
            "capabilities": metadata.capabilities,
            "authentication_methods": metadata.authentication_methods,
        })
    return {
        "success": True,
        "data": providers,
        "metadata": {
            "total": len(providers),
            "generated_at": __import__('datetime').datetime.utcnow().isoformat(),
            "api_version": "v1",
        },
    }
