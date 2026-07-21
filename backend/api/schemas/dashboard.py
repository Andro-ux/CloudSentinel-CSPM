from pydantic import BaseModel
from typing import Optional, Any, Dict, List


class SecurityScoreSchema(BaseModel):
    overall: int
    grade: str
    dimensions: Dict[str, int]
    breakdown: Dict[str, Any]


class SecurityDimensionsSchema(BaseModel):
    network: int
    identity: int
    storage: int
    logging: int
    compute: int
    overall: int


class ScoreBreakdownSchema(BaseModel):
    base_score: int
    deductions: Dict[str, int]
    total_deductions: int
    final_score: int


class ExecutiveMetricsSchema(BaseModel):
    total_assets: int
    assets_by_provider: Dict[str, int]
    assets_by_type: Dict[str, int]
    facts_by_category: Dict[str, int]
    findings_by_severity: Dict[str, int]
    risks_by_priority: Dict[str, int]
    average_risk: float
    highest_risk: int
    internet_exposed_assets: int
    identity_risks: int
    storage_risks: int
    network_risks: int
    logging_risks: int
    compute_risks: int


class InsightSchema(BaseModel):
    id: str
    title: str
    description: str
    severity: str
    category: str
    business_impact: str
    recommendation: str
    related_risks: List[str]


class RecommendationSchema(BaseModel):
    title: str
    priority: str
    description: str
    affected_assets: List[str]
    expected_score_improvement: int
    related_risks: List[str]


class ExecutiveNarrativeSchema(BaseModel):
    summary: str
    top_risks_summary: str
    recommendation_summary: str
    score_explanation: str


class ExecutiveSummarySchema(BaseModel):
    total_assets: int
    total_findings: int
    total_facts: int
    total_risks: int
    security_score: SecurityScoreSchema
    top_risks: List[Dict[str, Any]]
    dimensions: SecurityDimensionsSchema
    metrics: ExecutiveMetricsSchema
    insights: List[InsightSchema]
    recommendations: List[RecommendationSchema]
    narrative: ExecutiveNarrativeSchema
    generated_at: str
    metadata: Dict[str, Any]


class DashboardResponseSchema(BaseModel):
    summary: ExecutiveSummarySchema
    security_score: SecurityScoreSchema
    security_dimensions: SecurityDimensionsSchema
    score_breakdown: ScoreBreakdownSchema
    metrics: ExecutiveMetricsSchema
    top_risks: List[Dict[str, Any]]
    recommendations: List[RecommendationSchema]
    insights: List[InsightSchema]
    executive_narrative: ExecutiveNarrativeSchema
    generated_at: str
    metadata: Dict[str, Any]
