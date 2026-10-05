"""Rate limiting middleware tests.

Asserts RateLimitMiddleware is genuinely enforced: exceeding the limit returns a
real 429 with a Retry-After header (not a 500).

Regression covered: raising HTTPException from BaseHTTPMiddleware.dispatch
escaped Starlette's ExceptionMiddleware, so limit breaches surfaced as 500.
"""

from __future__ import annotations

import asyncio

import pytest
from fastapi import FastAPI, HTTPException, Request
from fastapi.testclient import TestClient

from recruitment_platform.security.middleware import RateLimitMiddleware
from recruitment_platform.security.rate_limit import RateLimiter, rate_limiter


class TestRateLimitEnforcement:
    """Rate limiting must actually block traffic."""

    def test_burst_limit_returns_429(self, client: TestClient, auth_headers):
        """Test exceeding burst_size returns 429."""
        codes = [
            client.get("/api/candidates", headers=auth_headers).status_code
            for _ in range(30)
        ]
        assert 429 in codes, "rate limiting did not engage - it is not enforced!"
        assert 200 in codes, "every request was blocked; limiter is too strict"

    def test_429_not_500(self, client: TestClient, auth_headers):
        """Test the limit response is 429, not an opaque 500."""
        for _ in range(30):
            resp = client.get("/api/candidates", headers=auth_headers)
            if resp.status_code != 200:
                assert resp.status_code == 429, (
                    f"expected 429 on limit breach, got {resp.status_code}"
                )
                return
        pytest.fail("rate limit never engaged")

    def test_429_has_retry_after_header(self, client: TestClient, auth_headers):
        """Test the 429 response carries Retry-After."""
        for _ in range(30):
            resp = client.get("/api/candidates", headers=auth_headers)
            if resp.status_code == 429:
                assert resp.headers.get("Retry-After") == "60"
                return
        pytest.fail("rate limit never engaged")

    def test_requests_within_limit_succeed(self, client: TestClient, auth_headers):
        """Test requests under burst_size are not blocked."""
        for _ in range(5):
            assert (
                client.get("/api/candidates", headers=auth_headers).status_code == 200
            )


class TestRateLimitExemptions:
    """Health endpoints must bypass the limiter for k8s probes."""

    @pytest.mark.parametrize("path", ["/health", "/api/health", "/api/ready"])
    def test_health_paths_exempt(self, client: TestClient, path: str):
        """Test health checks are never rate limited."""
        for _ in range(40):
            assert client.get(path).status_code == 200, f"{path} got rate limited"


class TestRateLimiterUnit:
    """Direct unit tests of the RateLimiter algorithm."""

    def test_burst_size_enforced(self):
        """Test the limiter trips at burst_size."""
        limiter = RateLimiter(requests_per_minute=100, burst_size=3)

        class _Req:
            class client:  # noqa: N801
                host = "1.2.3.4"

        request = _Req()
        for _ in range(3):
            asyncio.run(limiter.check_rate_limit(request))

        with pytest.raises(HTTPException) as exc:
            asyncio.run(limiter.check_rate_limit(request))
        assert exc.value.status_code == 429

    def test_clients_are_isolated(self):
        """Test one noisy client does not throttle another."""
        limiter = RateLimiter(requests_per_minute=100, burst_size=2)

        class _Req:
            def __init__(self, host: str):
                self.client = type("c", (), {"host": host})()

        for _ in range(2):
            asyncio.run(limiter.check_rate_limit(_Req("10.0.0.1")))

        # Different IP must still be allowed.
        asyncio.run(limiter.check_rate_limit(_Req("10.0.0.2")))

    def test_window_expiry_recovers(self):
        """Test the limiter clears entries older than the window."""
        limiter = RateLimiter(requests_per_minute=100, burst_size=2)

        class _Req:
            class client:  # noqa: N801
                host = "5.5.5.5"

        request = _Req()
        for _ in range(2):
            asyncio.run(limiter.check_rate_limit(request))

        # Simulate the window having elapsed.
        limiter._requests["5.5.5.5"] = [0.0, 0.0]
        asyncio.run(limiter.check_rate_limit(request))


class TestRateLimitMiddlewareIsolated:
    """Verify the middleware is wired to the shared limiter."""

    def test_middleware_uses_shared_limiter(self):
        """Test RateLimitMiddleware delegates to the global rate_limiter."""
        import inspect

        from recruitment_platform.security import middleware as mw

        source = inspect.getsource(mw.RateLimitMiddleware.dispatch)
        assert "rate_limiter.check_rate_limit" in source