from pydantic import BaseModel
from typing import Optional, Any, Dict, List


class ProviderMetadataSchema(BaseModel):
    provider_id: str
    name: str
    version: str
    description: str
    author: str
    supported_services: List[str]
    supported_collectors: List[str]
    supported_normalizers: List[str]
    authentication_methods: List[str]
    capabilities: List[str]
    metadata: Dict[str, Any]


class ProviderResponseSchema(BaseModel):
    provider_id: str
    name: str
    version: str
    description: str
    supported_services: List[str]
    capabilities: List[str]
    authentication_methods: List[str]


class ProvidersListResponse(BaseModel):
    items: List[ProviderResponseSchema]
    total: int
