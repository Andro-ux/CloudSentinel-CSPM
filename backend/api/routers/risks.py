from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List, Any
from backend.api.dependencies import get_scan_service
from backend.api.responses import create_paginated_response
from backend.services.scan_service import ScanService


router = APIRouter()


@router.get(
    "/risks",
    response_model=dict,
    tags=["Risks"],
    summary="List risks",
    description="Returns a paginated list of prioritized risks with optional filtering and sorting.",
)
def list_risks(
    priority: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    min_score: Optional[int] = Query(None, ge=0, le=100),
    max_score: Optional[int] = Query(None, ge=0, le=100),
    sort_by: Optional[str] = Query(None),
    order: str = Query("desc", regex="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    scan_service: ScanService = Depends(get_scan_service),
):
    try:
        result = scan_service.run_scan()
        items = []
        if result and result.risk_set:
            for risk in result.risk_set.risks:
                risk_dict = risk.to_dict()
                if priority and risk_dict.get("priority", "").lower() != priority.lower():
                    continue
                if category and risk_dict.get("category", "").lower() != category.lower():
                    continue
                if min_score is not None and risk_dict.get("score", 0) < min_score:
                    continue
                if max_score is not None and risk_dict.get("score", 0) > max_score:
                    continue
                items.append(risk_dict)
            if sort_by:
                reverse = order == "desc"
                items.sort(key=lambda x: x.get(sort_by, 0), reverse=reverse)
        total = len(items)
        start = (page - 1) * page_size
        end = start + page_size
        paginated = items[start:end]
        return create_paginated_response(paginated, page, page_size, total)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
