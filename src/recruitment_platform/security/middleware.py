"""Security middleware for the application."""
from __future__ import annotations

import json
import time
import uuid
from typing import TYPE_CHECKING, Any

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from recruitment_platform.security.rate_limit import rate_limiter

if TYPE_CHECKING:
    from fastapi import Response


def _json_error(
    status_code: int, detail: str, headers: dict[str, str] | None = None
) -> JSONResponse:
    """Build an error JSONResponse.

    Middleware must RETURN errors rather than raise them: an HTTPException
    raised inside BaseHTTPMiddleware.dispatch propagates above Starlette's
    ExceptionMiddleware (which only wraps the router), so it surfaces as an
    unhandled 500 instead of the intended status code.
    """
    return JSONResponse(
        status_code=status_code, content={"detail": detail}, headers=headers or {}
    )


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
    - /health, /ready, /health/live, /health/ready, /health/startup (probes)
    - /api/health, /api/ready (health router is mounted under the /api prefix)
    - /api/auth/login, /api/auth/register (authentication)
    - /docs, /redoc, /openapi.json (API documentation)
    - / (root)
    """

    PUBLIC_PATHS = frozenset(
        {
            "/",
            "/health",
            "/ready",
            # Deployment manifests probe these (k8s/base, k8s/, helm/values.yaml).
            # Without them every liveness/readiness/startup probe fails and the
            # pod never becomes ready.
            "/health/live",
            "/health/ready",
            "/health/startup",
            "/live",
            "/readyz",
            "/livez",
            # The health router is included with prefix="/api" (see api/router.py),
            # so its real paths are /api/health and /api/ready.
            "/api/health",
            "/api/ready",
            "/api/v1/health",
            "/api/v1/ready",
            "/api/v1/health/live",
            "/api/v1/health/ready",
            # Docs and schema.
            "/docs",
            "/docs/oauth2-redirect",
            "/redoc",
            "/openapi.json",
            "/favicon.ico",
            # Auth entrypoints - these cannot require a token.
            "/api/auth/login",
            "/api/auth/register",
        }
    )

    @classmethod
    def is_public(cls, path: str) -> bool:
        """Return True if the path may be reached without authentication."""
        if path in cls.PUBLIC_PATHS:
            return True
        # Also allow prefix variants so versioned/proxied probe paths
        # (e.g. /api/v1/health/live) stay public.
        return path.rstrip("/") in cls.PUBLIC_PATHS

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        # Allow public paths
        if self.is_public(request.url.path):
            return await call_next(request)

        # Extract and validate JWT token
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return _json_error(
                status.HTTP_401_UNAUTHORIZED,
                "Authentication required",
                {"WWW-Authenticate": "Bearer"},
            )

        token = auth_header.split(" ", 1)[1]
        from recruitment_platform.security.auth import verify_token

        try:
            payload = verify_token(token)
        except HTTPException as exc:
            # Return (do not raise) so the client gets 401, not an opaque 500.
            return _json_error(
                exc.status_code,
                exc.detail,
                dict(exc.headers or {}) or None,
            )

        # Attach user info to request state
        request.state.user = {
            "id": payload.get("sub"),
            "email": payload.get("email"),
            "roles": payload.get("roles", []),
        }

        return await call_next(request)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware - applies sliding window rate limiting per client IP.

    Health/readiness endpoints are exempt so orchestrator probes are never
    throttled. The health router is mounted under the /api prefix, so both the
    bare and prefixed paths must be exempt.
    """

    EXEMPT_PATHS = frozenset(
        {
            "/health",
            "/ready",
            "/health/live",
            "/health/ready",
            "/health/startup",
            "/livez",
            "/readyz",
            "/api/health",
            "/api/ready",
            "/api/v1/health",
            "/api/v1/ready",
        }
    )

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        # Skip rate limiting for health checks
        path = request.url.path
        if path in self.EXEMPT_PATHS or path.rstrip("/") in self.EXEMPT_PATHS:
            return await call_next(request)

        try:
            await rate_limiter.check_rate_limit(request)
        except HTTPException as exc:
            # Return (do not raise) so clients get a real 429 with Retry-After.
            return _json_error(
                exc.status_code,
                exc.detail,
                dict(exc.headers or {}) or None,
            )
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
                return _json_error(
                    status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    "Request body too large",
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
