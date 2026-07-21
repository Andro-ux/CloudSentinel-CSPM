from pydantic import BaseModel
from typing import Optional, Any, Dict, List


class AssetSchema(BaseModel):
    id: str
    service: str
    resource_type: str
    name: str
    properties: Dict[str, Any] = {}
    relationships: List[str] = []


class AssetListResponse(BaseModel):
    items: List[AssetSchema]
    total: int
    page: int
    page_size: int
