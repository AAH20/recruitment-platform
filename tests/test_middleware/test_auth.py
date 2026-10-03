"""
Authentication middleware tests for recruitment-platform.

Tests that the auth middleware correctly:
- Allows unauthenticated access to public endpoints
- Blocks unauthenticated access to protected endpoints
- Validates JWT tokens and rejects invalid/expired ones
- Handles missing or malformed Authorization headers
- Grants role-based access where applicable
"""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.testclient import TestClient
from jose import JWTError, jwt

# ---------------------------------------------------------------------------
# Test fixtures & helpers
# ---------------------------------------------------------------------------

SECRET_KEY = "test-secret-key-for-middleware-only"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer(auto_error=False)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token for testing."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode a JWT token, raising HTTPException on failure."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> dict:
    """Dependency that extracts and validates the current user from JWT."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    payload = decode_token(credentials.credentials)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    return {"id": user_id, "role": payload.get("role", "candidate")}


def require_role(required_role: str):
    """Factory for role-based access control dependency."""
    def role_checker(user: dict = Depends(get_current_user)) -> dict:
        if user["role"] != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role}' required",
            )
        return user
    return role_checker


@pytest.fixture
def app() -> FastAPI:
    """Create a FastAPI app with auth middleware dependencies wired in."""
    app = FastAPI(title="Recruitment Platform — Auth Test App")

    @app.get("/public")
    async def public_endpoint():
        return {"message": "public access granted"}

    @app.get("/protected")
    async def protected_endpoint(user: dict = Depends(get_current_user)):
        return {"message": "protected access granted", "user": user}

    @app.get("/admin-only")
    async def admin_endpoint(user: dict = Depends(require_role("admin"))):
        return {"message": "admin access granted", "user": user}

    @app.get("/recruiter-only")
    async def recruiter_endpoint(user: dict = Depends(require_role("recruiter"))):
        return {"message": "recruiter access granted", "user": user}

    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """Return a TestClient for the test app."""
    return TestClient(app)


# ---------------------------------------------------------------------------
# Tests — public endpoints (no auth required)
# ---------------------------------------------------------------------------

class TestPublicEndpoints:
    """Public endpoints must be accessible without authentication."""

    def test_public_endpoint_no_token(self, client: TestClient):
        response = client.get("/public")
        assert response.status_code == 200
        assert response.json() == {"message": "public access granted"}

    def test_public_endpoint_with_valid_token(self, client: TestClient):
        token = create_access_token({"sub": "user-1", "role": "candidate"})
        response = client.get("/public", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200

    def test_public_endpoint_with_invalid_token(self, client: TestClient):
        """Invalid tokens on public endpoints should still allow access."""
        response = client.get("/public", headers={"Authorization": "Bearer invalid-token"})
        assert response.status_code == 200


# ---------------------------------------------------------------------------
# Tests — protected endpoints (auth required)
# ---------------------------------------------------------------------------

class TestProtectedEndpoints:
    """Protected endpoints must reject unauthenticated requests."""

    def test_no_token_returns_401(self, client: TestClient):
        response = client.get("/protected")
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]

    def test_valid_token_grants_access(self, client: TestClient):
        token = create_access_token({"sub": "user-42", "role": "candidate"})
        response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        body = response.json()
        assert body["message"] == "protected access granted"
        assert body["user"]["id"] == "user-42"
        assert body["user"]["role"] == "candidate"

    def test_expired_token_returns_401(self, client: TestClient):
        expired_token = create_access_token(
            {"sub": "user-1"},
            expires_delta=timedelta(minutes=-1),
        )
        response = client.get("/protected", headers={"Authorization": f"Bearer {expired_token}"})
        assert response.status_code == 401
        assert "Invalid or expired token" in response.json()["detail"]

    def test_malformed_token_returns_401(self, client: TestClient):
        response = client.get("/protected", headers={"Authorization": "Bearer not.a.jwt"})
        assert response.status_code == 401

    def test_missing_sub_claim_returns_401(self, client: TestClient):
        token = jwt.encode({"role": "admin"}, SECRET_KEY, algorithm=ALGORITHM)
        response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 401
        assert "Invalid token payload" in response.json()["detail"]

    def test_wrong_scheme_returns_401(self, client: TestClient):
        token = create_access_token({"sub": "user-1"})
        response = client.get("/protected", headers={"Authorization": token})
        assert response.status_code == 401

    def test_empty_bearer_token_returns_401(self, client: TestClient):
        response = client.get("/protected", headers={"Authorization": "Bearer "})
        assert response.status_code == 401


# ---------------------------------------------------------------------------
# Tests — role-based access control
# ---------------------------------------------------------------------------

class TestRoleBasedAccess:
    """Role-based endpoints must enforce role requirements."""

    def test_admin_endpoint_with_admin_role(self, client: TestClient):
        token = create_access_token({"sub": "admin-1", "role": "admin"})
        response = client.get("/admin-only", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert response.json()["message"] == "admin access granted"

    def test_admin_endpoint_with_candidate_role_returns_403(self, client: TestClient):
        token = create_access_token({"sub": "user-1", "role": "candidate"})
        response = client.get("/admin-only", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 403
        assert "Role 'admin' required" in response.json()["detail"]

    def test_recruiter_endpoint_with_recruiter_role(self, client: TestClient):
        token = create_access_token({"sub": "rec-1", "role": "recruiter"})
        response = client.get("/recruiter-only", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200

    def test_recruiter_endpoint_with_admin_role_returns_403(self, client: TestClient):
        token = create_access_token({"sub": "admin-1", "role": "admin"})
        response = client.get("/recruiter-only", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 403

    def test_admin_endpoint_no_token_returns_401(self, client: TestClient):
        response = client.get("/admin-only")
        assert response.status_code == 401


# ---------------------------------------------------------------------------
# Tests — token edge cases
# ---------------------------------------------------------------------------

class TestTokenEdgeCases:
    """Edge cases in token handling."""

    def test_token_with_extra_claims(self, client: TestClient):
        token = create_access_token({
            "sub": "user-1",
            "role": "candidate",
            "email": "test@example.com",
            "iat": datetime.now(timezone.utc),
        })
        response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200

    def test_token_signed_with_wrong_secret(self, client: TestClient):
        wrong_token = jwt.encode(
            {"sub": "user-1"},
            "wrong-secret-key",
            algorithm=ALGORITHM,
        )
        response = client.get("/protected", headers={"Authorization": f"Bearer {wrong_token}"})
        assert response.status_code == 401

    def test_token_with_different_algorithm(self, client: TestClient):
        """A token signed with a different algorithm should be rejected."""
        # HS384 token — server only accepts HS256
        hs384_token = jwt.encode(
            {"sub": "user-1"},
            SECRET_KEY,
            algorithm="HS384",
        )
        response = client.get("/protected", headers={"Authorization": f"Bearer {hs384_token}"})
        assert response.status_code == 401

    def test_multiple_rapid_requests_with_same_token(self, client: TestClient):
        """Same valid token should work across multiple requests."""
        token = create_access_token({"sub": "user-1", "role": "candidate"})
        for _ in range(5):
            response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
            assert response.status_code == 200
