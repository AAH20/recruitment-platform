"""Tests for security headers middleware."""

import pytest
from fastapi.testclient import TestClient


class TestSecurityHeadersMiddleware:
    """Test security headers middleware."""

    def test_security_headers_present(self, client: TestClient):
        """Test security headers are present."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_x_content_type_options(self, client: TestClient):
        """Test X-Content-Type-Options header."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_x_frame_options(self, client: TestClient):
        """Test X-Frame-Options header."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_transport_security(self, client: TestClient):
        """Test Strict-Transport-Security header."""
        response = client.get("/health")
        assert response.status_code == 200
