import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(round(process_time, 4))
        return response


class CORSMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            headers = {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Authorization, Content-Type",
            }
            if scope["method"] == "OPTIONS":
                async def send_preflight(message):
                    if message["type"] == "http.response.start":
                        message["headers"] = [(k.encode(), v.encode()) for k, v in headers.items()]
                    await send(message)
                await send_preflight({
                    "type": "http.response.start",
                    "status": 204,
                })
                await send({
                    "type": "http.response.body",
                    "body": b"",
                })
                return
        await self.app(scope, receive, send)
