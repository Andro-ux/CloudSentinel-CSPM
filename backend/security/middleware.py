import uuid
from datetime import datetime
from typing import Optional, Dict, Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from backend.security.rate_limit import RateLimiter
import os


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )

        environment = os.getenv("ENVIRONMENT", "development").lower()
        if environment == "production":
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "object-src 'none'; "
                "base-uri 'self'; "
                "frame-ancestors 'none';"
            )
        else:
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "img-src 'self' data: https://fastapi.tiangolo.com; "
                "font-src 'self' https://cdn.jsdelivr.net;"
            )

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, rate_limiter: RateLimiter = None, limit: int = 100, window: int = 60):
        super().__init__(app)
        self.rate_limiter = rate_limiter or RateLimiter()
        self.limit = limit
        self.window = window

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        key = f"ratelimit:{client_ip}"
        try:
            self.rate_limiter.check_rate_limit(key, self.limit, self.window)
        except Exception as exc:
            response = Response(
                content=str(exc),
                status_code=429,
                headers={"Retry-After": str(getattr(exc, "retry_after", 60))},
            )
            return response
        return await call_next(request)
