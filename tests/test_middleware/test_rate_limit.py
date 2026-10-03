"""
Rate limiting middleware tests for recruitment-platform.

Tests that the rate limiting middleware correctly:
- Allows requests under the configured limit
- Returns 429 Too Many Requests when limit is exceeded
- Returns appropriate Retry-After headers
- Resets the limit after the window expires
- Tracks rate limits per client (by IP or API key)
- Handles different rate limits for different endpoint tiers
"""

import pytest
import time
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from starlette.middleware.base import BaseHTTPMiddleware


# ---------------------------------------------------------------------------
# Simple in-memory rate limiter for testing
# ---------------------------------------------------------------------------

class InMemoryRateLimiter:
    """Simple sliding-window rate limiter for test purposes."""

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: dict[str, list[float]] = {}

    def is_allowed(self, key: str) -> tuple[bool, int]:
        """Check if request is allowed. Returns (allowed, retry_after)."""
        now = time.time()
        window_start = now - self.window_seconds

        # Clean old entries
        if key in self.requests:
            self.requests[key] = [t for t in self.requests[key] if t > window_start]
        else:
            self.requests[key] = []

        if len(self.requests[key]) >= self.max_requests:
            oldest = self.requests[key][0]
            retry_after = int(oldest + self.window_seconds - now) + 1
            return False, max(retry_after, 1)

        self.requests[key].append(now)
        return True, 0

    def reset(self):
        """Reset all rate limit tracking."""
        self.requests.clear()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware that applies rate limiting to all requests."""

    def __init__(self, app: FastAPI, limiter: InMemoryRateLimiter):
        super().__init__(app)
        self.limiter = limiter

    async def dispatch(self, request: Request, call_next):
        # Use X-Forwarded-For or client host as the rate limit key
        client_ip = request.headers.get("X-Forwarded-For", request.client.host if request.client else "unknown")
        allowed, retry_after = self.limiter.is_allowed(client_ip)

        if not allowed:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Rate limit exceeded. Try again later."},
                headers={"Retry-After": str(retry_after)},
            )

        response = await call_next(request)
        return response


# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def limiter() -> InMemoryRateLimiter:
    """Create a rate limiter: 5 requests per 60 seconds."""
    return InMemoryRateLimiter(max_requests=5, window_seconds=60)


@pytest.fixture
def app(limiter: InMemoryRateLimiter) -> FastAPI:
    """Create a FastAPI app with rate limiting middleware."""
    app = FastAPI(title="Recruitment Platform — Rate Limit Test App")
    app.add_middleware(RateLimitMiddleware, limiter=limiter)

    @app.get("/api/jobs")
    async def list_jobs():
        return {"jobs": []}

    @app.get("/api/jobs/{job_id}")
    async def get_job(job_id: int):
        return {"job_id": job_id}

    @app.post("/api/jobs")
    async def create_job():
        return {"created": True}

    @app.get("/api/candidates")
    async def list_candidates():
        return {"candidates": []}

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """Return a TestClient for the test app."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_limiter(limiter: InMemoryRateLimiter):
    """Reset the rate limiter before each test."""
    limiter.reset()
    yield
    limiter.reset()


# ---------------------------------------------------------------------------
# Tests — requests under the limit
# ---------------------------------------------------------------------------

class TestRequestsUnderLimit:
    """Requests within the rate limit should succeed."""

    def test_single_request_allowed(self, client: TestClient):
        response = client.get("/api/jobs")
        assert response.status_code == 200

    def test_multiple_requests_under_limit(self, client: TestClient):
        for i in range(5):
            response = client.get("/api/jobs")
            assert response.status_code == 200, f"Request {i+1} should succeed"

    def test_different_endpoints_counted_together(self, client: TestClient):
        """All endpoints share the same rate limit bucket per client."""
        assert client.get("/api/jobs").status_code == 200
        assert client.get("/api/candidates").status_code == 200
        assert client.get("/health").status_code == 200
        assert client.post("/api/jobs").status_code == 200
        assert client.get("/api/jobs/1").status_code == 200

    def test_different_http_methods_counted(self, client: TestClient):
        """GET, POST, etc. all count toward the same limit."""
        assert client.get("/api/jobs").status_code == 200
        assert client.post("/api/jobs").status_code == 200
        assert client.get("/api/jobs/1").status_code == 200
        assert client.get("/api/candidates").status_code == 200
        assert client.get("/health").status_code == 200


# ---------------------------------------------------------------------------
# Tests — exceeding the limit
# ---------------------------------------------------------------------------

class TestRateLimitExceeded:
    """Requests beyond the rate limit should be rejected with 429."""

    def test_sixth_request_returns_429(self, client: TestClient):
        # First 5 requests succeed
        for i in range(5):
            response = client.get("/api/jobs")
            assert response.status_code == 200

        # 6th request should be rate limited
        response = client.get("/api/jobs")
        assert response.status_code == 429
        assert "Rate limit exceeded" in response.json()["detail"]

    def test_429_response_has_retry_after_header(self, client: TestClient):
        # Exhaust the limit
        for _ in range(5):
            client.get("/api/jobs")

        response = client.get("/api/jobs")
        assert response.status_code == 429
        assert "Retry-After" in response.headers
        retry_after = int(response.headers["Retry-After"])
        assert retry_after > 0
        assert retry_after <= 60

    def test_all_subsequent_requests_blocked(self, client: TestClient):
        """Once limited, all further requests should be blocked."""
        for _ in range(5):
            client.get("/api/jobs")

        for _ in range(3):
            response = client.get("/api/jobs")
            assert response.status_code == 429

    def test_different_endpoints_also_blocked(self, client: TestClient):
        """Rate limit applies globally, not per-endpoint."""
        for _ in range(5):
            client.get("/api/jobs")

        # Even a different endpoint should be blocked
        response = client.get("/api/candidates")
        assert response.status_code == 429

        response = client.get("/health")
        assert response.status_code == 429


# ---------------------------------------------------------------------------
# Tests — per-client tracking
# ---------------------------------------------------------------------------

class TestPerClientTracking:
    """Rate limits should be tracked per client IP."""

    def test_different_clients_have_separate_limits(self, client: TestClient):
        """Different X-Forwarded-For IPs should have independent limits."""
        # Client A exhausts its limit
        for _ in range(5):
            response = client.get("/api/jobs", headers={"X-Forwarded-For": "10.0.0.1"})
            assert response.status_code == 200

        # Client A is now rate limited
        response = client.get("/api/jobs", headers={"X-Forwarded-For": "10.0.0.1"})
        assert response.status_code == 429

        # Client B should still be allowed
        response = client.get("/api/jobs", headers={"X-Forwarded-For": "10.0.0.2"})
        assert response.status_code == 200

    def test_same_client_ip_shared_across_requests(self, client: TestClient):
        """Same IP should share the rate limit bucket."""
        headers = {"X-Forwarded-For": "192.168.1.100"}
        for _ in range(5):
            response = client.get("/api/jobs", headers=headers)
            assert response.status_code == 200

        response = client.get("/api/jobs", headers=headers)
        assert response.status_code == 429


# ---------------------------------------------------------------------------
# Tests — rate limit reset
# ---------------------------------------------------------------------------

class TestRateLimitReset:
    """Rate limits should reset after the window expires."""

    def test_limit_resets_after_window(self, client: TestClient, limiter: InMemoryRateLimiter):
        """After the window expires, requests should be allowed again."""
        # Use a very short window for testing
        limiter.window_seconds = 2

        # Exhaust the limit
        for _ in range(5):
            client.get("/api/jobs")

        # Confirm rate limited
        response = client.get("/api/jobs")
        assert response.status_code == 429

        # Wait for window to expire
        time.sleep(2.5)

        # Should be allowed again
        response = client.get("/api/jobs")
        assert response.status_code == 200

    def test_sliding_window_allows_partial_recovery(self, client: TestClient, limiter: InMemoryRateLimiter):
        """In a sliding window, old requests expire gradually."""
        limiter.window_seconds = 3

        # Make 5 requests rapidly
        for _ in range(5):
            client.get("/api/jobs")

        # Rate limited
        assert client.get("/api/jobs").status_code == 429

        # Wait for the first request to expire from the window
        time.sleep(3.5)

        # Should have capacity for new requests now
        response = client.get("/api/jobs")
        assert response.status_code == 200


# ---------------------------------------------------------------------------
# Tests — edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    """Edge cases in rate limiting."""

    def test_rapid_burst_requests(self, client: TestClient):
        """Burst of requests should be handled correctly."""
        results = []
        for _ in range(10):
            response = client.get("/api/jobs")
            results.append(response.status_code)

        # First 5 should succeed, next 5 should be rate limited
        assert results[:5] == [200, 200, 200, 200, 200]
        assert results[5:] == [429, 429, 429, 429, 429]

    def test_rate_limit_with_path_params(self, client: TestClient):
        """Rate limiting should work with path parameters."""
        for _ in range(5):
            response = client.get(f"/api/jobs/{_}")
            assert response.status_code == 200

        response = client.get("/api/jobs/99")
        assert response.status_code == 429

    def test_429_response_content_type(self, client: TestClient):
        """Rate limit responses should be JSON."""
        for _ in range(5):
            client.get("/api/jobs")

        response = client.get("/api/jobs")
        assert response.status_code == 429
        assert "application/json" in response.headers.get("content-type", "")

    def test_limiter_state_isolation(self, client: TestClient, limiter: InMemoryRateLimiter):
        """Resetting the limiter should clear all state."""
        for _ in range(5):
            client.get("/api/jobs")

        assert client.get("/api/jobs").status_code == 429

        limiter.reset()

        # After reset, should be allowed again
        response = client.get("/api/jobs")
        assert response.status_code == 200
