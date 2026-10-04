"""Tests for authentication middleware."""

import pytest
from fastapi.testclient import TestClient


class TestAuthMiddleware:
    """Test authentication middleware."""

    def test_unauthenticated_request(self, client: TestClient):
        """Test request without authentication."""
        response = client.get("/api/protected")
        assert response.status_code == 401

    def test_invalid_token(self, client: TestClient):
        """Test request with invalid token."""
        response = client.get(
            "/api/protected",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401

    def test_expired_token(self, client: TestClient):
        """Test request with expired token."""
        response = client.get(
            "/api/protected",
            headers={"Authorization": "Bearer expired_token"}
        )
        assert response.status_code == 401

    def test_malformed_token(self, client: TestClient):
        """Test request with malformed token."""
        response = client.get(
            "/api/protected",
            headers={"Authorization": "NotBearer token"}
        )
        assert response.status_code == 401

    def test_missing_auth_header(self, client: TestClient):
        """Test request without auth header."""
        response = client.get("/api/protected")
        assert response.status_code == 401
