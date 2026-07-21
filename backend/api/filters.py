from fastapi import Query
from typing import Optional


class PaginationParams:
    def __init__(
        self,
        page: int = Query(1, ge=1),
        page_size: int = Query(25, ge=1, le=100),
    ):
        self.page = page
        self.page_size = page_size
        self.offset = (page - 1) * page_size


class SortParams:
    def __init__(
        self,
        sort_by: Optional[str] = Query(None),
        order: str = Query("asc", regex="^(asc|desc)$"),
    ):
        self.sort_by = sort_by
        self.order = order


class AssetFilters:
    def __init__(
        self,
        provider: Optional[str] = Query(None),
        asset_type: Optional[str] = Query(None),
        search: Optional[str] = Query(None),
    ):
        self.provider = provider
        self.asset_type = asset_type
        self.search = search


class FindingFilters:
    def __init__(
        self,
        severity: Optional[str] = Query(None),
        category: Optional[str] = Query(None),
        provider: Optional[str] = Query(None),
        asset: Optional[str] = Query(None),
    ):
        self.severity = severity
        self.category = category
        self.provider = provider
        self.asset = asset


class RiskFilters:
    def __init__(
        self,
        priority: Optional[str] = Query(None),
        category: Optional[str] = Query(None),
        min_score: Optional[int] = Query(None, ge=0, le=100),
        max_score: Optional[int] = Query(None, ge=0, le=100),
    ):
        self.priority = priority
        self.category = category
        self.min_score = min_score
        self.max_score = max_score
