"""
Request Logging Middleware
Logs every HTTP request + response with timing.
"""

import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.logs_module.logger import get_logger

logger = get_logger("http")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start = time.perf_counter()

        # Log incoming request
        logger.info(
            "Request started",
            extra={
                "method": request.method,
                "path": request.url.path,
                "query": str(request.url.query),
                "client_ip": request.client.host if request.client else "unknown",
            },
        )

        try:
            response = await call_next(request)
        except Exception as exc:
            logger.exception(
                "Unhandled exception during request",
                extra={"path": request.url.path},
            )
            raise

        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)

        logger.info(
            "Request completed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": elapsed_ms,
            },
        )

        # Append server timing header for debugging
        response.headers["X-Process-Time-Ms"] = str(elapsed_ms)
        return response
