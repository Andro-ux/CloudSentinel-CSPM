from pydantic import BaseModel
from typing import Optional, Any, Dict, List


class FindingSchema(BaseModel):
    id: str
    rule_id: str
    title: str
    description: str
    severity: str
    category: str
    service: str
    resource_id: str
    asset_ids: List[str]
    fact_ids: List[str]
    recommendation: str
    references: List[str]
    evidence: Dict[str, Any]
    risk_score: int


class FindingListResponse(BaseModel):
    items: List[FindingSchema]
    total: int
    page: int
    page_size: int
