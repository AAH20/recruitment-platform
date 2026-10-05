"""Security headers middleware tests.

Asserts SecurityHeadersMiddleware is registered on the real app and emits the
expected headers on every response.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from recruitment_platform.security.middleware import SecurityHeadersMiddleware

EXPECTED_HEADERS = {
    "X-Content-Type-Options",
    "X-Frame-Options",
    "X-XSS-Protection",
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "Referrer-Policy",
    "Permissions-Policy",
    "Cache-Control",
}


class TestSecurityHeadersOnResponses:
    """Every response must carry the security headers."""

    @pytest.mark.parametrize(
        "path", ["/", "/health", "/docs", "/openapi.json"]
    )
    def test_public_responses_have_headers(self, client: TestClient, path: str):
        """Test public responses include all security headers."""
        response = client.get(path)
        assert response.status_code == 200
        # Starlette lowercases header names on the wire; compare case-insensitively.
        present = {k.lower() for k in response.headers}
        missing = {h for h in EXPECTED_HEADERS if h.lower() not in present}
        assert not missing, f"missing security headers: {missing}"

    def test_protected_response_has_headers(self, client: TestClient, auth_headers):
        """Test authenticated responses include all security headers."""
        response = client.get("/api/candidates", headers=auth_headers)
        assert response.status_code == 200
        present = {k.lower() for k in response.headers}
        missing = {h for h in EXPECTED_HEADERS if h.lower() not in present}
        assert not missing, f"missing security headers: {missing}"

    def test_error_response_has_headers(self, client: TestClient):
        """Test 401 responses also carry security headers."""
        response = client.get("/api/candidates")
        assert response.status_code == 401
        assert "X-Content-Type-Options" in response.headers

    def test_header_values(self, client: TestClient):
        """Test the specific header values are the hardened ones."""
        headers = client.get("/health").headers
        assert headers["X-Content-Type-Options"] == "nosniff"
        assert headers["X-Frame-Options"] == "DENY"
        assert headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
        assert "max-age=31536000" in headers["Strict-Transport-Security"]

    def test_request_id_header(self, client: TestClient):
        """Test RequestIDMiddleware adds a traceable request id."""
        response = client.get("/health")
        assert "X-Request-ID" in response.headers
        assert response.headers["X-Process-Time"] is not None


class TestSecurityHeadersMiddlewareUnit:
    """Unit tests for the middleware class itself."""

    def test_middleware_registered_on_app(self):
        """Test SecurityHeadersMiddleware is actually installed."""
        from recruitment_platform.main import app

        registered = {
            m.cls.__name__ if isinstance(m.cls, type) else type(m.cls).__name__
            for m in app.user_middleware
        }
        assert "SecurityHeadersMiddleware" in registered

    def test_all_three_security_middlewares_registered(self):
        """Test the full security stack is wired into the app."""
        from recruitment_platform.main import app

        registered = {
            m.cls.__name__ if isinstance(m.cls, type) else type(m.cls).__name__
            for m in app.user_middleware
        }
        assert {
            "AuthMiddleware",
            "RateLimitMiddleware",
            "InputSanitizationMiddleware",
            "SecurityHeadersMiddleware",
        } <= registered