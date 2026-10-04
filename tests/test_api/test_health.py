"""Tests for health check endpoints."""

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoints:
    """Test health check and status endpoints."""

    def test_health_check(self, client: TestClient):
        """Test basic health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"

    def test_health_check_response_structure(self, client: TestClient):
        """Test health check returns expected structure."""
        response = client.get("/health")
        data = response.json()
        assert isinstance(data, dict)
        assert "status" in data

    def test_root_endpoint(self, client: TestClient):
        """Test root endpoint returns API info."""
        response = client.get("/")
        assert response.status_code == 200

    def test_docs_endpoint(self, client: TestClient):
        """Test Swagger docs are accessible."""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_openapi_endpoint(self, client: TestClient):
        """Test OpenAPI schema is accessible."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "paths" in data
