"""Tests for candidate API endpoints.

These tests exercise the real AuthMiddleware: every request carries a valid
bearer token obtained from the /api/auth/login endpoint via the ``auth_headers``
fixture. No middleware is stubbed.
"""

from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient


class TestCandidateEndpoints:
    """Test candidate CRUD operations (authenticated)."""

    def test_create_candidate(self, client: TestClient, auth_headers, sample_candidate):
        """Test creating a new candidate."""
        response = client.post(
            "/api/candidates", json=sample_candidate, headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["first_name"] == sample_candidate["first_name"]

    def test_get_candidate(self, client: TestClient, auth_headers, sample_candidate):
        """Test getting a candidate by ID."""
        create_response = client.post(
            "/api/candidates", json=sample_candidate, headers=auth_headers
        )
        candidate_id = create_response.json()["id"]

        response = client.get(f"/api/candidates/{candidate_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == candidate_id

    def test_list_candidates(self, client: TestClient, auth_headers, sample_candidate):
        """Test listing candidates returns a paginated envelope."""
        client.post("/api/candidates", json=sample_candidate, headers=auth_headers)

        response = client.get("/api/candidates", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["data"], list)
        assert data["total"] >= 1
        assert data["page"] == 1

    def test_update_candidate(self, client: TestClient, auth_headers, sample_candidate):
        """Test updating a candidate."""
        create_response = client.post(
            "/api/candidates", json=sample_candidate, headers=auth_headers
        )
        candidate_id = create_response.json()["id"]

        response = client.put(
            f"/api/candidates/{candidate_id}",
            json={"first_name": "Jane"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["first_name"] == "Jane"

    def test_delete_candidate(self, client: TestClient, auth_headers, sample_candidate):
        """Test deleting a candidate returns 204 and the record disappears."""
        create_response = client.post(
            "/api/candidates", json=sample_candidate, headers=auth_headers
        )
        candidate_id = create_response.json()["id"]

        response = client.delete(f"/api/candidates/{candidate_id}", headers=auth_headers)
        assert response.status_code == 204

        follow_up = client.get(f"/api/candidates/{candidate_id}", headers=auth_headers)
        assert follow_up.status_code == 404

    def test_create_candidate_validation(self, client: TestClient, auth_headers):
        """Test candidate creation rejects a missing required field."""
        response = client.post("/api/candidates", json={}, headers=auth_headers)
        assert response.status_code == 422

    def test_create_candidate_invalid_email(
        self, client: TestClient, auth_headers, sample_candidate
    ):
        """Test candidate creation rejects an invalid email."""
        response = client.post(
            "/api/candidates",
            json={**sample_candidate, "email": "not-an-email"},
            headers=auth_headers,
        )
        assert response.status_code == 422

    def test_create_candidate_duplicate_email(
        self, client: TestClient, auth_headers, sample_candidate
    ):
        """Test duplicate candidate email is rejected with 409."""
        first = client.post(
            "/api/candidates", json=sample_candidate, headers=auth_headers
        )
        assert first.status_code == 201

        second = client.post(
            "/api/candidates", json=sample_candidate, headers=auth_headers
        )
        assert second.status_code == 409

    def test_get_nonexistent_candidate(self, client: TestClient, auth_headers):
        """Test getting a non-existent candidate returns 404."""
        response = client.get(
            f"/api/candidates/{uuid.uuid4()}", headers=auth_headers
        )
        assert response.status_code == 404

    def test_filter_candidates_by_experience_level(
        self, client: TestClient, auth_headers
    ):
        """Test filtering candidates by experience level."""
        response = client.get(
            "/api/candidates?experience_level=senior", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert all(c["experience_level"] == "senior" for c in data["data"])

    def test_list_candidates_requires_auth(self, client: TestClient):
        """Test listing candidates without a token is rejected."""
        response = client.get("/api/candidates")
        assert response.status_code == 401

    def test_create_candidate_requires_auth(self, client: TestClient, sample_candidate):
        """Test creating a candidate without a token is rejected."""
        response = client.post("/api/candidates", json=sample_candidate)
        assert response.status_code == 401

    @pytest.mark.parametrize("path", ["/api/candidates", "/api/candidates/abc"])
    def test_all_candidate_routes_require_auth(self, client: TestClient, path: str):
        """Test every candidate route enforces authentication."""
        assert client.get(path).status_code == 401