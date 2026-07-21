from fastapi import APIRouter, Depends, HTTPException
from backend.api.dependencies import get_scan_service, get_executive_engine
from backend.api.schemas.dashboard import DashboardResponseSchema
from backend.services.scan_service import ScanService
from backend.executive.engine import ExecutiveEngine


router = APIRouter()


@router.get(
    "/dashboard",
    response_model=dict,
    tags=["Dashboard"],
    summary="Get executive dashboard",
    description="Returns the executive dashboard with security score, metrics, insights, and recommendations.",
)
def get_dashboard(
    scan_service: ScanService = Depends(get_scan_service),
    executive_engine: ExecutiveEngine = Depends(get_executive_engine),
):
    try:
        result = scan_service.run_scan()
        if not result or not result.dashboard:
            raise HTTPException(status_code=404, detail="No dashboard available")
        dashboard = result.dashboard
        return {
            "success": True,
            "data": {
                "summary": {
                    "total_assets": dashboard.summary.total_assets,
                    "total_findings": dashboard.summary.total_findings,
                    "total_facts": dashboard.summary.total_facts,
                    "total_risks": dashboard.summary.total_risks,
                    "security_score": {
                        "overall": dashboard.summary.security_score.overall,
                        "grade": dashboard.summary.security_score.grade,
                        "dimensions": dashboard.summary.security_score.dimensions.to_dict(),
                        "breakdown": {
                            "base_score": dashboard.summary.security_score.breakdown.base_score,
                            "deductions": dict(dashboard.summary.security_score.breakdown.deductions),
                            "total_deductions": dashboard.summary.security_score.breakdown.total_deductions(),
                            "final_score": dashboard.summary.security_score.breakdown.final_score(),
                        },
                    },
                    "top_risks": [r.to_dict() for r in dashboard.summary.top_risks],
                    "dimensions": dashboard.summary.dimensions.to_dict(),
                    "metrics": dashboard.summary.metrics.to_dict(),
                    "insights": [i.to_dict() for i in dashboard.summary.insights],
                    "recommendations": [r.to_dict() for r in dashboard.summary.recommendations],
                    "narrative": dashboard.summary.narrative.to_dict(),
                    "generated_at": dashboard.summary.generated_at.isoformat(),
                    "metadata": dict(dashboard.summary.metadata),
                },
                "security_score": {
                    "overall": dashboard.security_score.overall,
                    "grade": dashboard.security_score.grade,
                    "dimensions": dashboard.security_score.dimensions.to_dict(),
                    "breakdown": {
                        "base_score": dashboard.security_score.breakdown.base_score,
                        "deductions": dict(dashboard.security_score.breakdown.deductions),
                        "total_deductions": dashboard.security_score.breakdown.total_deductions(),
                        "final_score": dashboard.security_score.breakdown.final_score(),
                    },
                },
                "security_dimensions": dashboard.security_dimensions.to_dict(),
                "score_breakdown": {
                    "base_score": dashboard.score_breakdown.base_score,
                    "deductions": dict(dashboard.score_breakdown.deductions),
                    "total_deductions": dashboard.score_breakdown.total_deductions(),
                    "final_score": dashboard.score_breakdown.final_score(),
                },
                "metrics": dashboard.metrics.to_dict(),
                "top_risks": [r.to_dict() for r in dashboard.top_risks],
                "recommendations": [r.to_dict() for r in dashboard.recommendations],
                "insights": [i.to_dict() for i in dashboard.insights],
                "executive_narrative": dashboard.executive_narrative.to_dict(),
                "generated_at": dashboard.generated_at.isoformat(),
                "metadata": dict(dashboard.metadata),
            },
            "metadata": {
                "generated_at": dashboard.generated_at.isoformat(),
                "api_version": "v1",
            },
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
