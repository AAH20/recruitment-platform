"""Tests for error handling middleware."""

import pytest
from fastapi.testclient import TestClient


class TestErrorHandlerMiddleware:
    """Test error handling middleware."""

    def test_404_error(self, client: TestClient):
        """Test 404 error handling."""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_422_error(self, client: TestClient):
        """Test 422 validation error."""
        response = client.post("/api/employers", json={})
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_500_error(self, client: TestClient):
        """Test 500 error handling."""
        # This would need a route that raises an exception
        pass

    def test_error_response_structure(self, client: TestClient):
        """Test error response structure."""
        response = client.get("/api/nonexistent")
        data = response.json()
        assert isinstance(data, dict)
        assert "detail" in data
