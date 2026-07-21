from pydantic import BaseModel
from typing import Optional, Any, Dict, List


class RiskSchema(BaseModel):
    id: str
    finding_id: str
    asset_ids: List[str]
    score: int
    priority: str
    category: str
    severity: str
    explanation: str
    contributing_factors: List[str]
    recommendation: str
    metadata: Dict[str, Any]


class RiskListResponse(BaseModel):
    items: List[RiskSchema]
    total: int
    page: int
    page_size: int
