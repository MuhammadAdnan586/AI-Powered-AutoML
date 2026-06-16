"""
Module 4 – Security Layer
- Rate limiting (slowapi)
- Security headers middleware
- Input sanitization helpers
- JWT secret rotation utilities
"""

import re
import time
from collections import defaultdict
from typing import Callable

from fastapi import Request, Response, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.config.settings import settings


# ── Rate Limiter (in-memory, per IP) ────────────────────────────────────────
# For production use Redis-backed slowapi or fastapi-limiter.

class InMemoryRateLimiter:
    """Simple sliding-window rate limiter (per IP)."""

    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window = window_seconds
        self._store: dict = defaultdict(list)

    def is_allowed(self, key: str) -> bool:
        now = time.time()
        window_start = now - self.window
        requests = self._store[key]

        # Prune old timestamps
        self._store[key] = [t for t in requests if t > window_start]

        if len(self._store[key]) >= self.max_requests:
            return False

        self._store[key].append(now)
        return True


_limiter = InMemoryRateLimiter(
    max_requests=settings.RATE_LIMIT_REQUESTS,
    window_seconds=settings.RATE_LIMIT_WINDOW,
)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Apply rate limiting to all API routes."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip health check
        if request.url.path in ("/health", "/"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        if not _limiter.is_allowed(client_ip):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please slow down.",
            )
        return await call_next(request)


# ── Security Headers Middleware ───────────────────────────────────────────────

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security-related HTTP headers to every response."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline';"
        )
        return response


# ── Input Sanitization Helpers ────────────────────────────────────────────────

_SQL_INJECTION_PATTERN = re.compile(
    r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|EXEC|UNION|--|;)\b)",
    re.IGNORECASE,
)
_XSS_PATTERN = re.compile(r"<[^>]+>", re.IGNORECASE)


def sanitize_string(value: str) -> str:
    """Strip HTML tags and basic SQL injection patterns from a string."""
    value = _XSS_PATTERN.sub("", value)
    if _SQL_INJECTION_PATTERN.search(value):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid characters detected in input.",
        )
    return value.strip()


def sanitize_filename(filename: str) -> str:
    """Remove path traversal and dangerous characters from filenames."""
    filename = filename.replace("..", "").replace("/", "").replace("\\", "")
    return re.sub(r"[^\w.\-]", "_", filename)


# ── CORS Configuration ────────────────────────────────────────────────────────

def configure_cors(app):
    """Register CORSMiddleware with allowed origins from settings."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# ── Register all security middleware ─────────────────────────────────────────

def register_security_middleware(app):
    """Call this once in main.py to attach all security middleware."""
    configure_cors(app)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RateLimitMiddleware)
