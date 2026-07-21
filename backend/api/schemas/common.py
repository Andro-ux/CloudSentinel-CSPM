from typing import Optional, Any, List, Dict, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total: int
    has_next: bool
    has_previous: bool


class ResponseMetadata(BaseModel):
    generated_at: str
    api_version: str = "v1"


class Envelope(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    metadata: Optional[Dict[str, Any]] = None


class PaginatedEnvelope(BaseModel, Generic[T]):
    success: bool
    data: List[T]
    metadata: Dict[str, Any]


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[Any] = None


class ErrorEnvelope(BaseModel):
    success: bool = False
    error: ErrorDetail
