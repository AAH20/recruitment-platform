"""Error handling tests.

Asserts the API returns structured JSON errors rather than HTML tracebacks, and
that errors never leak internal exception detail.
"""

from __future__ import annotations

from fastapi.testclient import TestClient


class TestStructuredErrors:
    """Errors must be JSON with a `detail` field, not HTML."""

    def test_404_returns_json(self, client: TestClient, auth_headers):
        """Test unknown routes return a JSON 404.

        AuthMiddleware runs before routing, so an unknown path is rejected as a
        401 unless a valid token is supplied.
        """
        response = client.get("/definitely-not-a-real-route", headers=auth_headers)
        assert response.status_code == 404
        assert "json" in response.headers["content-type"]

    def test_401_returns_json_detail(self, client: TestClient):
        """Test auth failures return a JSON body with detail."""
        response = client.get("/api/candidates")
        assert response.status_code == 401
        body = response.json()
        assert "detail" in body
        assert isinstance(body["detail"], str)

    def test_422_returns_validation_details(self, client: TestClient, auth_headers):
        """Test validation errors return a structured detail list."""
        response = client.post("/api/candidates", json={}, headers=auth_headers)
        assert response.status_code == 422
        body = response.json()
        assert isinstance(body["detail"], list)
        assert "loc" in body["detail"][0]

    def test_409_returns_json(self, client: TestClient, auth_headers, sample_candidate):
        """Test conflict errors return JSON."""
        client.post("/api/candidates", json=sample_candidate, headers=auth_headers)
        response = client.post(
            "/api/candidates", json=sample_candidate, headers=auth_headers
        )
        assert response.status_code == 409
        assert "detail" in response.json()

    def test_resource_404_returns_json(self, client: TestClient, auth_headers):
        """Test a missing resource returns a JSON 404 with detail."""
        response = client.get(
            "/api/candidates/00000000-0000-0000-0000-000000000000",
            headers=auth_headers,
        )
        assert response.status_code == 404
        assert "detail" in response.json()


class TestNoInternalLeakage:
    """Errors must not expose stack traces or internal state."""

    def test_401_does_not_leak_internals(self, client: TestClient):
        """Test the 401 body reveals nothing about the server internals."""
        body = client.get("/api/candidates").text.lower()
        for leak in ("traceback", "recruitment_platform", "traceback (most", "file \""):
            assert leak not in body, f"error response leaked '{leak}'"

    def test_500_never_returned_for_bad_token(self, client: TestClient):
        """Test malformed tokens produce 401, never a 500.

        Regression: the middleware used to raise HTTPException, which escaped
        Starlette's ExceptionMiddleware and surfaced as 500.
        """
        for token in ["garbage", "a.b.c", "Bearer x", "Bearer 12345"]:
            response = client.get(
                "/api/candidates", headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code != 500, (
                f"token {token!r} produced a 500 instead of a clean rejection"
            )