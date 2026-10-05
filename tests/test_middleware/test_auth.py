"""Authentication middleware tests.

These assert that AuthMiddleware is genuinely enforced on the real app: a
missing or invalid token must produce a 401 (not a 500), and valid tokens must
be accepted. Nothing is monkeypatched - the tests would fail if the middleware
were disabled.
"""

from __future__ import annotations

from datetime import timedelta

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from recruitment_platform.security.auth import create_access_token
from recruitment_platform.security.middleware import AuthMiddleware

# A representative slice of protected routes across the API surface.
PROTECTED_ROUTES = [
    "/api/candidates",
    "/api/jobs",
    "/api/employers",
    "/api/applications",
    "/api/interviews",
    "/api/skills",
    "/api/talent-pools",
    "/api/reports",
    "/api/analytics",
    "/api/assessments",
]

PUBLIC_ROUTES = ["/", "/health", "/api/health", "/api/ready", "/docs", "/openapi.json"]


class TestAuthMiddlewareRejectsUnauthenticated:
    """Protected routes must reject requests without a valid token."""

    @pytest.mark.parametrize("path", PROTECTED_ROUTES)
    def test_protected_route_without_token(self, client: TestClient, path: str):
        """Test that protected endpoints reject unauthenticated requests."""
        response = client.get(path)
        assert response.status_code == 401, (
            f"{path} allowed unauthenticated access "
            f"(status {response.status_code}) - auth is not enforced!"
        )

    def test_401_not_500(self, client: TestClient):
        """Test auth failure returns 401, not an opaque 500.

        Regression: raising HTTPException from BaseHTTPMiddleware.dispatch
        escapes Starlette's ExceptionMiddleware and surfaced as a 500.
        """
        response = client.get("/api/candidates")
        assert response.status_code == 401
        assert response.status_code != 500
        assert response.json()["detail"] == "Authentication required"

    def test_401_has_www_authenticate_header(self, client: TestClient):
        """Test the 401 challenge advertises Bearer auth."""
        response = client.get("/api/candidates")
        assert response.headers.get("WWW-Authenticate") == "Bearer"


class TestAuthMiddlewareRejectsBadTokens:
    """Invalid, malformed or forged tokens must all be rejected."""

    @pytest.mark.parametrize(
        "auth_value",
        [
            "Bearer invalid_token",
            "Bearer not.a.jwt",
            "Bearer ",
            "NotBearer sometoken",
            "Basic dXNlcjpwYXNz",
            "Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIn0.bad",
        ],
    )
    def test_bad_token_rejected(self, client: TestClient, auth_value: str):
        """Test malformed/garbage tokens are rejected with 401."""
        response = client.get(
            "/api/candidates", headers={"Authorization": auth_value}
        )
        assert response.status_code == 401

    def test_missing_scheme_rejected(self, client: TestClient):
        """Test a bare token with no Bearer scheme is rejected."""
        response = client.get("/api/candidates", headers={"Authorization": "sometoken"})
        assert response.status_code == 401

    def test_expired_token_rejected(self, client: TestClient):
        """Test an expired token is rejected."""
        expired = create_access_token(
            {"sub": "user-1", "email": "u@example.com"},
            expires_delta=timedelta(minutes=-60),
        )
        response = client.get(
            "/api/candidates", headers={"Authorization": f"Bearer {expired}"}
        )
        assert response.status_code == 401


class TestAuthMiddlewareAllowsValidTokens:
    """Valid tokens must be accepted."""

    def test_valid_token_accepted(self, client: TestClient, auth_headers):
        """Test a real token from the register endpoint is accepted."""
        response = client.get("/api/candidates", headers=auth_headers)
        assert response.status_code == 200

    def test_handmade_token_accepted(self, client: TestClient, make_token):
        """Test a freshly minted token passes the middleware."""
        token = make_token(sub="user-123", email="u@example.com", roles=["recruiter"])
        response = client.get(
            "/api/candidates", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200

    def test_token_populates_request_state(self, client: TestClient, make_token):
        """Test the decoded user reaches the route via request.state.user."""
        token = make_token(sub="state-user", email="state@example.com", roles=["admin"])

        # Exercise the middleware against a minimal app so the request.state
        # mutation can be observed without depending on real route internals.
        probe_app = FastAPI()
        probe_app.add_middleware(AuthMiddleware)
        seen: dict = {}

        @probe_app.get("/probe")
        async def probe(request: Request) -> dict:
            seen.update(request.state.user)
            return {"ok": True}

        with TestClient(probe_app) as probe_client:
            resp = probe_client.get(
                "/probe", headers={"Authorization": f"Bearer {token}"}
            )
            assert resp.status_code == 200, (
                f"probe app returned {resp.status_code}: {resp.text}"
            )

        assert seen.get("id") == "state-user"
        assert seen.get("email") == "state@example.com"
        assert seen.get("roles") == ["admin"]


class TestPublicRoutesRemainPublic:
    """Health/docs must stay reachable without credentials."""

    @pytest.mark.parametrize("path", PUBLIC_ROUTES)
    def test_public_route_needs_no_token(self, client: TestClient, path: str):
        """Test public endpoints do not require authentication."""
        assert client.get(path).status_code == 200

    def test_auth_routes_are_public(self, client: TestClient):
        """Test login/register are reachable without a token.

        This is the fixture the rest of the suite authenticates through, so if
        auth itself demanded a token the entire suite would be unbootstrapped.
        """
        assert client.post("/api/auth/login", json={}).status_code == 422
        assert client.post("/api/auth/register", json={}).status_code == 422


class TestAuthFlow:
    """Register -> login -> access protected route with the issued token."""

    def test_full_auth_flow(self, client: TestClient, registered_user: dict):
        """Test a freshly registered user can log in and use the API."""
        reg = client.post("/api/auth/register", json=registered_user)
        assert reg.status_code == 200
        assert reg.json()["token"]

        login = client.post(
            "/api/auth/login",
            json={
                "email": registered_user["email"],
                "password": registered_user["password"],
            },
        )
        assert login.status_code == 200
        token = login.json()["token"]
        assert login.json()["user"]["email"] == registered_user["email"]

        protected = client.get(
            "/api/candidates", headers={"Authorization": f"Bearer {token}"}
        )
        assert protected.status_code == 200

    def test_login_wrong_password_rejected(self, client: TestClient, registered_user):
        """Test a wrong password does not yield a token."""
        client.post("/api/auth/register", json=registered_user)
        response = client.post(
            "/api/auth/login",
            json={
                "email": registered_user["email"],
                "password": "totally-wrong-password",
            },
        )
        assert response.status_code == 401

    def test_duplicate_registration_conflicts(self, client: TestClient, registered_user):
        """Test registering the same email twice returns 409."""
        assert client.post("/api/auth/register", json=registered_user).status_code == 200
        assert (
            client.post("/api/auth/register", json=registered_user).status_code == 409
        )