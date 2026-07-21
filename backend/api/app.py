from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.security.middleware import SecurityHeadersMiddleware, RateLimitMiddleware
from backend.security.rate_limit import RateLimiter
from backend.api.middleware import RequestLoggingMiddleware
from backend.api.routers import (
    assets,
    auth,
    capabilities,
    dashboard,
    findings,
    graph,
    health,
    providers,
    risks,
)


def create_app() -> FastAPI:
    app = FastAPI(
        title="CloudSentinel API",
        description="Enterprise Cloud Security Intelligence Platform",
        version="1.0.0",
        openapi_tags=[
            {"name": "Dashboard", "description": "Executive dashboard and security posture"},
            {"name": "Assets", "description": "Cloud asset inventory and metadata"},
            {"name": "Findings", "description": "Security findings from rule evaluation"},
            {"name": "Risks", "description": "Prioritized risk assessments"},
            {"name": "Graph", "description": "Knowledge graph relationships and attack paths"},
            {"name": "Providers", "description": "Registered cloud provider plugins"},
            {"name": "Capabilities", "description": "Provider capabilities and supported services"},
            {"name": "Health", "description": "Platform health and status"},
            {"name": "Authentication", "description": "Authentication and token management"},
        ],
    )

    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RateLimitMiddleware, rate_limiter=RateLimiter(), limit=100, window=60)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(dashboard.router, prefix="/api/v1")
    app.include_router(assets.router, prefix="/api/v1")
    app.include_router(findings.router, prefix="/api/v1")
    app.include_router(risks.router, prefix="/api/v1")
    app.include_router(graph.router, prefix="/api/v1")
    app.include_router(providers.router, prefix="/api/v1")
    app.include_router(capabilities.router, prefix="/api/v1")
    app.include_router(health.router, prefix="/api/v1")

    return app
