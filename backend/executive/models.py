from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class ScoreBreakdown:

    base_score: int = 100

    deductions: Dict[str, int] = field(default_factory=dict)

    def total_deductions(self) -> int:

        return sum(self.deductions.values())

    def final_score(self) -> int:

        return max(0, self.base_score - self.total_deductions())


@dataclass(frozen=True)
class SecurityDimensions:

    network: int = 100

    identity: int = 100

    storage: int = 100

    logging: int = 100

    compute: int = 100

    overall: int = 100

    def to_dict(self) -> Dict[str, int]:

        return {

            "network": self.network,

            "identity": self.identity,

            "storage": self.storage,

            "logging": self.logging,

            "compute": self.compute,

            "overall": self.overall,

        }


@dataclass(frozen=True)
class SecurityScore:

    overall: int

    dimensions: SecurityDimensions

    breakdown: ScoreBreakdown

    grade: str

    def to_dict(self) -> Dict[str, Any]:

        return {

            "overall": self.overall,

            "grade": self.grade,

            "dimensions": self.dimensions.to_dict(),

            "breakdown": {

                "base_score": self.breakdown.base_score,

                "deductions": dict(self.breakdown.deductions),

                "total_deductions": self.breakdown.total_deductions(),

                "final_score": self.breakdown.final_score(),

            },

        }


def grade_from_score(score: int) -> str:

    if score >= 90:

        return "A"

    if score >= 80:

        return "B"

    if score >= 70:

        return "C"

    if score >= 60:

        return "D"

    return "F"


@dataclass(frozen=True)
class ExecutiveMetrics:

    total_assets: int = 0

    assets_by_provider: Dict[str, int] = field(default_factory=dict)

    assets_by_type: Dict[str, int] = field(default_factory=dict)

    facts_by_category: Dict[str, int] = field(default_factory=dict)

    findings_by_severity: Dict[str, int] = field(default_factory=dict)

    risks_by_priority: Dict[str, int] = field(default_factory=dict)

    average_risk: float = 0.0

    highest_risk: int = 0

    internet_exposed_assets: int = 0

    identity_risks: int = 0

    storage_risks: int = 0

    network_risks: int = 0

    logging_risks: int = 0

    compute_risks: int = 0

    def to_dict(self) -> Dict[str, Any]:

        return {

            "total_assets": self.total_assets,

            "assets_by_provider": dict(self.assets_by_provider),

            "assets_by_type": dict(self.assets_by_type),

            "facts_by_category": dict(self.facts_by_category),

            "findings_by_severity": dict(self.findings_by_severity),

            "risks_by_priority": dict(self.risks_by_priority),

            "average_risk": self.average_risk,

            "highest_risk": self.highest_risk,

            "internet_exposed_assets": self.internet_exposed_assets,

            "identity_risks": self.identity_risks,

            "storage_risks": self.storage_risks,

            "network_risks": self.network_risks,

            "logging_risks": self.logging_risks,

            "compute_risks": self.compute_risks,

        }


@dataclass(frozen=True)
class Insight:

    id: str

    title: str

    description: str

    severity: str

    category: str

    business_impact: str

    recommendation: str

    related_risks: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:

        return {

            "id": self.id,

            "title": self.title,

            "description": self.description,

            "severity": self.severity,

            "category": self.category,

            "business_impact": self.business_impact,

            "recommendation": self.recommendation,

            "related_risks": list(self.related_risks),

        }


@dataclass(frozen=True)
class Recommendation:

    title: str

    priority: str

    description: str

    affected_assets: List[str] = field(default_factory=list)

    expected_score_improvement: int = 0

    related_risks: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:

        return {

            "title": self.title,

            "priority": self.priority,

            "description": self.description,

            "affected_assets": list(self.affected_assets),

            "expected_score_improvement": self.expected_score_improvement,

            "related_risks": list(self.related_risks),

        }


@dataclass(frozen=True)
class ExecutiveNarrative:

    summary: str

    top_risks_summary: str

    recommendation_summary: str

    score_explanation: str

    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:

        return {

            "summary": self.summary,

            "top_risks_summary": self.top_risks_summary,

            "recommendation_summary": self.recommendation_summary,

            "score_explanation": self.score_explanation,

            "metadata": dict(self.metadata),

        }


@dataclass(frozen=True)
class ExecutiveSummary:

    total_assets: int

    total_findings: int

    total_facts: int

    total_risks: int

    security_score: SecurityScore

    top_risks: List[Any]  # List[Risk] internally

    dimensions: SecurityDimensions

    metrics: ExecutiveMetrics

    insights: List[Insight]

    recommendations: List[Recommendation]

    narrative: ExecutiveNarrative

    generated_at: datetime = field(default_factory=datetime.utcnow)

    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:

        return {

            "total_assets": self.total_assets,

            "total_findings": self.total_findings,

            "total_facts": self.total_facts,

            "total_risks": self.total_risks,

            "security_score": self.security_score.to_dict(),

            "top_risks": [r.to_dict() for r in self.top_risks],

            "dimensions": self.dimensions.to_dict(),

            "metrics": self.metrics.to_dict(),

            "insights": [i.to_dict() for i in self.insights],

            "recommendations": [r.to_dict() for r in self.recommendations],

            "narrative": self.narrative.to_dict(),

            "generated_at": self.generated_at.isoformat(),

            "metadata": dict(self.metadata),

        }


@dataclass(frozen=True)
class ExecutiveDashboard:

    summary: ExecutiveSummary

    security_score: SecurityScore

    security_dimensions: SecurityDimensions

    score_breakdown: ScoreBreakdown

    metrics: ExecutiveMetrics

    top_risks: List[Any]  # List[Risk]

    recommendations: List[Recommendation]

    insights: List[Insight]

    executive_narrative: ExecutiveNarrative

    generated_at: datetime = field(default_factory=datetime.utcnow)

    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:

        return {

            "summary": self.summary.to_dict(),

            "security_score": self.security_score.to_dict(),

            "security_dimensions": self.security_dimensions.to_dict(),

            "score_breakdown": {

                "base_score": self.score_breakdown.base_score,

                "deductions": dict(self.score_breakdown.deductions),

                "total_deductions": self.score_breakdown.total_deductions(),

                "final_score": self.score_breakdown.final_score(),

            },

            "metrics": self.metrics.to_dict(),

            "top_risks": [r.to_dict() for r in self.top_risks],

            "recommendations": [r.to_dict() for r in self.recommendations],

            "insights": [i.to_dict() for i in self.insights],

            "executive_narrative": self.executive_narrative.to_dict(),

            "generated_at": self.generated_at.isoformat(),

            "metadata": dict(self.metadata),

        }
