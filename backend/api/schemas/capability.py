from pydantic import BaseModel
from typing import Optional, Any, Dict, List


class CapabilitySchema(BaseModel):
    name: str
    version: str
    description: str
    metadata: Dict[str, Any]


class CapabilityResponseSchema(BaseModel):
    provider_id: str
    capabilities: List[str]
    supported_services: List[str]


class CapabilitiesListResponse(BaseModel):
    items: List[CapabilityResponseSchema]
    total: int
