from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List, Any
from backend.api.dependencies import get_scan_service
from backend.api.responses import create_paginated_response
from backend.services.scan_service import ScanService


router = APIRouter()


@router.get(
    "/findings",
    response_model=dict,
    tags=["Findings"],
    summary="List findings",
    description="Returns a paginated list of security findings with optional filtering.",
)
def list_findings(
    severity: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    provider: Optional[str] = Query(None),
    asset: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    scan_service: ScanService = Depends(get_scan_service),
):
    try:
        result = scan_service.run_scan()
        items = []
        if result and result.findings:
            for finding in result.findings:
                if severity and finding.get("severity", "").lower() != severity.lower():
                    continue
                if category and finding.get("category", "").lower() != category.lower():
                    continue
                if provider and finding.get("provider", "").lower() != provider.lower():
                    continue
                if asset and asset not in finding.get("asset_ids", []):
                    continue
                items.append(finding)
        total = len(items)
        start = (page - 1) * page_size
        end = start + page_size
        paginated = items[start:end]
        return create_paginated_response(paginated, page, page_size, total)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
