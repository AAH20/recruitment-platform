"""Security middleware for the application."""
from __future__ import annotations

import json
import time
import uuid
from typing import TYPE_CHECKING, Any

from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware

from recruitment_platform.security.auth import verify_token
from recruitment_platform.security.rate_limit import rate_limiter

if TYPE_CHECKING:
    from fastapi import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        response = await call_next(request)

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=()"
        )
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
        response.headers["Pragma"] = "no-cache"

        return response


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add unique request ID for tracing."""

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)

        return response


class AuthMiddleware(BaseHTTPMiddleware):
    """Authentication middleware - enforces JWT token validation on protected routes.

    Public routes (no auth required):
    - /health, /ready (health checks)
    - /api/auth/login, /api/auth/register (authentication)
    - /docs, /redoc, /openapi.json (API documentation)
    - / (root)
    """

    PUBLIC_PATHS = {
        "/",
        "/health",
        "/ready",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/api/auth/login",
        "/api/auth/register",
    }

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        # Allow public paths
        if request.url.path in self.PUBLIC_PATHS:
            return await call_next(request)

        # Extract and validate JWT token
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = auth_header.split(" ", 1)[1]
        payload = verify_token(token)

        # Attach user info to request state
        request.state.user = {
            "id": payload.get("sub"),
            "email": payload.get("email"),
            "roles": payload.get("roles", []),
        }

        return await call_next(request)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware - applies sliding window rate limiting per client IP."""

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        # Skip rate limiting for health checks
        if request.url.path in {"/health", "/ready"}:
            return await call_next(request)

        await rate_limiter.check_rate_limit(request)
        return await call_next(request)


class InputSanitizationMiddleware(BaseHTTPMiddleware):
    """Input sanitization middleware - sanitizes request body to prevent injection attacks.

    Recursively sanitizes string values in JSON request bodies by:
    - Escaping HTML entities
    - Removing null bytes
    - Stripping control characters
    """

    MAX_BODY_SIZE = 10 * 1024 * 1024  # 10 MB limit

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        # Only process requests with a body
        if request.method in ("POST", "PUT", "PATCH"):
            content_length = request.headers.get("content-length")
            if content_length and int(content_length) > self.MAX_BODY_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail="Request body too large",
                )

            content_type = request.headers.get("content-type", "")
            if "application/json" in content_type:
                try:
                    body = await request.body()
                    if body:
                        data = json.loads(body)
                        sanitized = self._sanitize(data)
                        # Replace request body with sanitized version
                        request._body = json.dumps(sanitized).encode("utf-8")
                except json.JSONDecodeError:
                    pass  # Let FastAPI handle invalid JSON
                except Exception:
                    pass  # Don't block requests on sanitization errors

        return await call_next(request)

    def _sanitize(self, data: Any) -> Any:
        """Recursively sanitize data structure."""
        if isinstance(data, str):
            return self._sanitize_string(data)
        elif isinstance(data, dict):
            return {k: self._sanitize(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._sanitize(item) for item in data]
        return data

    def _sanitize_string(self, text: str) -> str:
        """Sanitize a single string value."""
        import html

        # Escape HTML entities
        sanitized = html.escape(text)
        # Remove null bytes
        sanitized = sanitized.replace("\x00", "")
        # Remove control characters (except newlines and tabs)
        sanitized = "".join(
            char for char in sanitized if ord(char) >= 32 or char in "\n\t\r"
        )
        return sanitized


class CORSMiddleware:
    """CORS configuration."""

    def __init__(
        self,
        allow_origins: list[str] | None = None,
        allow_methods: list[str] | None = None,
        allow_headers: list[str] | None = None,
        allow_credentials: bool = True,
        max_age: int = 600,
    ) -> None:
        self.allow_origins = allow_origins or ["*"]
        self.allow_methods = allow_methods or ["*"]
        self.allow_headers = allow_headers or ["*"]
        self.allow_credentials = allow_credentials
        self.max_age = max_age
