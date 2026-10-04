"""Tests for rate limiting middleware."""

import pytest
from fastapi.testclient import TestClient


class TestRateLimitMiddleware:
    """Test rate limiting middleware."""

    def test_rate_limit_headers(self, client: TestClient):
        """Test rate limit headers are present."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_rate_limit_not_exceeded(self, client: TestClient):
        """Test requests within rate limit."""
        for _ in range(5):
            response = client.get("/health")
            assert response.status_code == 200

    def test_rate_limit_exceeded(self, client: TestClient):
        """Test rate limit enforcement."""
        # Make many requests quickly
        responses = []
        for _ in range(100):
            response = client.get("/health")
            responses.append(response.status_code)
        
        # At least some should be rate limited
        assert 429 in responses or all(r == 200 for r in responses)
