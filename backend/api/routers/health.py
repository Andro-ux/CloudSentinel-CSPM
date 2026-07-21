from fastapi import APIRouter
from datetime import datetime


router = APIRouter()


@router.get(
    "/health",
    response_model=dict,
    tags=["Health"],
    summary="Health check",
    description="Returns platform health status.",
)
def health_check():
    return {
        "success": True,
        "data": {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "api_version": "v1",
        },
        "metadata": {
            "generated_at": datetime.utcnow().isoformat(),
            "api_version": "v1",
        },
    }
