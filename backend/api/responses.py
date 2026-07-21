from datetime import datetime
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total: int
    has_next: bool
    has_previous: bool


class Envelope(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    metadata: Optional[dict] = None


class PaginatedResponse(BaseModel, Generic[T]):
    success: bool
    data: list[T]
    metadata: PaginationMeta


def create_envelope(data: Any, metadata: Optional[dict] = None) -> dict:
    return {
        "success": True,
        "data": data,
        "metadata": metadata or {},
    }


def create_paginated_response(
    items: list[Any],
    page: int,
    page_size: int,
    total: int,
) -> dict:
    has_next = (page * page_size) < total
    has_previous = page > 1
    return {
        "success": True,
        "data": items,
        "metadata": {
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "has_next": has_next,
                "has_previous": has_previous,
            },
            "generated_at": datetime.utcnow().isoformat(),
            "api_version": "v1",
        },
    }
