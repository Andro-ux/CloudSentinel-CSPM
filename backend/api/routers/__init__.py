from fastapi import APIRouter
from backend.api.routers import (
    auth,
    assets,
    capabilities,
    dashboard,
    findings,
    graph,
    health,
    providers,
    risks,
)

router = APIRouter()

router.include_router(auth.router)
router.include_router(dashboard.router)
router.include_router(assets.router)
router.include_router(findings.router)
router.include_router(risks.router)
router.include_router(graph.router)
router.include_router(providers.router)
router.include_router(capabilities.router)
router.include_router(health.router)
