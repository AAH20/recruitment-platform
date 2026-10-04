"""Authentication bypass tests for recruitment-platform."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from recruitment_platform.main import app


class TestAuthenticationBypass:
    """Test that authentication cannot be bypassed."""

    @pytest.fixture
    def client(self):
        with TestClient(app) as c:
            yield c

    def test_protected_endpoint_no_auth(self, client):
        """Test that protected endpoints reject unauthenticated requests."""
        protected_endpoints = [
            ("GET", "/api/v1/candidates"),
            ("GET", "/api/v1/jobs"),
            ("GET", "/api/v1/applications"),
            ("GET", "/api/v1/interviews"),
            ("GET", "/api/v1/employers"),
            ("GET", "/api/v1/reports"),
            ("GET", "/api/v1/talent-pools"),
            ("GET", "/api/v1/skills"),
        ]
        for method, path in protected_endpoints:
            resp = client.request(method, path)
            assert resp.status_code in (401, 403), (
                f"Endpoint {path} allowed unauthenticated access with status {resp.status_code}"
            )

    def test_invalid_token_rejected(self, client):
        """Test that invalid tokens are rejected."""
        invalid_tokens = [
            "invalid_token",
            "Bearer invalid",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature",
            "",
            "null",
            "undefined",
        ]
        for token in invalid_tokens:
            resp = client.get(
                "/api/v1/candidates",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert resp.status_code in (401, 403), (
                f"Invalid token '{token}' was accepted"
            )

    def test_expired_token_rejected(self, client):
        """Test that expired tokens are rejected."""
        from datetime import timedelta
        from recruitment_platform.security.auth import create_access_token

        # Create an already-expired token
        expired_token = create_access_token(
            {"sub": "user-123", "email": "test@example.com"},
            expires_delta=timedelta(seconds=-1)
        )
        resp = client.get(
            "/api/v1/candidates",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        assert resp.status_code == 401, "Expired token was accepted"

    def test_malformed_auth_header(self, client):
        """Test that malformed auth headers are rejected."""
        malformed_headers = [
            "Basic dXNlcjpwYXNz",  # Basic auth instead of Bearer
            "Bearer",  # Missing token
            "Bearer ",  # Empty token
            "bearer token",  # Lowercase bearer
            "Token abc123",  # Wrong scheme
        ]
        for header in malformed_headers:
            resp = client.get(
                "/api/v1/candidates",
                headers={"Authorization": header}
            )
            assert resp.status_code in (401, 403), (
                f"Malformed auth header '{header}' was accepted"
            )

    def test_sql_injection_auth_bypass(self, client):
        """Test that SQL injection cannot bypass authentication."""
        # Try to bypass auth with SQL injection in email
        resp = client.post(
            "/api/v1/auth/login",
            json={
                "email": "admin'--",
                "password": "anything"
            }
        )
        assert resp.status_code == 401, "SQL injection bypassed authentication"

    def test_no_auth_header_variations(self, client):
        """Test various ways to try to bypass auth header."""
        # Try with empty Authorization header
        resp = client.get(
            "/api/v1/candidates",
            headers={"Authorization": ""}
        )
        assert resp.status_code in (401, 403)

        # Try with None-like values
        resp = client.get(
            "/api/v1/candidates",
            headers={"Authorization": "Bearer null"}
        )
        assert resp.status_code in (401, 403)
