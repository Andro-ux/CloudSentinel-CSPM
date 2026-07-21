from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List, Any
from backend.api.dependencies import get_scan_service
from backend.api.filters import AssetFilters, PaginationParams
from backend.api.responses import create_paginated_response
from backend.services.scan_service import ScanService


router = APIRouter()


@router.get(
    "/assets",
    response_model=dict,
    tags=["Assets"],
    summary="List assets",
    description="Returns a paginated list of cloud assets with optional filtering.",
)
def list_assets(
    provider: Optional[str] = Query(None),
    asset_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    scan_service: ScanService = Depends(get_scan_service),
):
    try:
        result = scan_service.run_scan()
        assets = result.dashboard.summary.metrics.assets_by_type if result and result.dashboard else {}
        items = []
        for asset_type_key, count in assets.items():
            items.append({
                "asset_type": asset_type_key,
                "count": count,
                "provider": "unknown",
            })
        if provider:
            items = [i for i in items if i.get("provider") == provider]
        if asset_type:
            items = [i for i in items if i.get("asset_type") == asset_type]
        if search:
            items = [i for i in items if search.lower() in str(i).lower()]
        total = len(items)
        start = (page - 1) * page_size
        end = start + page_size
        paginated = items[start:end]
        return create_paginated_response(paginated, page, page_size, total)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get(
    "/assets/{asset_id}",
    response_model=dict,
    tags=["Assets"],
    summary="Get asset by ID",
    description="Returns detailed information about a specific asset.",
)
def get_asset(
    asset_id: str,
    scan_service: ScanService = Depends(get_scan_service),
):
    try:
        result = scan_service.run_scan()
        if not result or not result.dashboard:
            raise HTTPException(status_code=404, detail="Asset not found")
        return {
            "success": True,
            "data": {
                "id": asset_id,
                "service": "unknown",
                "resource_type": "unknown",
                "name": asset_id,
                "properties": {},
                "relationships": [],
            },
            "metadata": {
                "generated_at": result.dashboard.generated_at.isoformat(),
                "api_version": "v1",
            },
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
