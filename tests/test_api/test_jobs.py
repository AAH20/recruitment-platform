"""Tests for job API endpoints.

Every request carries a real bearer token from the ``auth_headers`` fixture, so
these tests exercise the production AuthMiddleware path.
"""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient


def _job_payload(**overrides) -> dict:
    """Build a valid JobCreate payload."""
    payload = {
        "title": "Senior Software Engineer",
        "description": "We are looking for a senior software engineer",
        "location": "San Francisco, CA",
        "salary_min": 120000,
        "salary_max": 180000,
        "employer_id": 1,
    }
    payload.update(overrides)
    return payload


class TestJobEndpoints:
    """Test job CRUD operations (authenticated)."""

    def test_create_job(self, client: TestClient, auth_headers):
        """Test creating a new job."""
        response = client.post(
            "/api/jobs", json=_job_payload(), headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["title"] == "Senior Software Engineer"

    def test_get_job(self, client: TestClient, auth_headers):
        """Test getting a job by ID."""
        create_response = client.post(
            "/api/jobs", json=_job_payload(), headers=auth_headers
        )
        job_id = create_response.json()["id"]

        response = client.get(f"/api/jobs/{job_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["id"] == job_id

    def test_list_jobs(self, client: TestClient, auth_headers):
        """Test listing jobs returns the documented paginated envelope."""
        client.post("/api/jobs", json=_job_payload(), headers=auth_headers)

        response = client.get("/api/jobs", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["items"], list)
        assert data["total"] >= 1
        assert data["page"] == 1

    def test_update_job(self, client: TestClient, auth_headers):
        """Test updating a job."""
        create_response = client.post(
            "/api/jobs", json=_job_payload(), headers=auth_headers
        )
        job_id = create_response.json()["id"]

        response = client.put(
            f"/api/jobs/{job_id}",
            json={"title": "Updated Job Title"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Updated Job Title"

    def test_delete_job(self, client: TestClient, auth_headers):
        """Test deleting a job returns 204 and the record disappears."""
        create_response = client.post(
            "/api/jobs", json=_job_payload(), headers=auth_headers
        )
        job_id = create_response.json()["id"]

        response = client.delete(f"/api/jobs/{job_id}", headers=auth_headers)
        assert response.status_code == 204

        follow_up = client.get(f"/api/jobs/{job_id}", headers=auth_headers)
        assert follow_up.status_code == 404

    def test_create_job_validation(self, client: TestClient, auth_headers):
        """Test job creation rejects a missing required field."""
        response = client.post("/api/jobs", json={}, headers=auth_headers)
        assert response.status_code == 422

    def test_create_job_negative_salary(self, client: TestClient, auth_headers):
        """Test negative salary is rejected."""
        response = client.post(
            "/api/jobs", json=_job_payload(salary_min=-1), headers=auth_headers
        )
        assert response.status_code == 422

    def test_get_nonexistent_job(self, client: TestClient, auth_headers):
        """Test getting a non-existent job returns 404."""
        response = client.get("/api/jobs/999999", headers=auth_headers)
        assert response.status_code == 404

    def test_list_jobs_paginates(self, client: TestClient, auth_headers):
        """Test list_jobs honours page/page_size.

        Note: list_jobs exposes no filters (no location/search params), so this
        asserts pagination rather than a filter that does not exist.
        """
        for _ in range(3):
            client.post("/api/jobs", json=_job_payload(), headers=auth_headers)

        page1 = client.get("/api/jobs?page=1&page_size=2", headers=auth_headers).json()
        assert page1["page"] == 1
        assert page1["page_size"] == 2
        assert len(page1["items"]) <= 2
        assert page1["total"] >= 3

    def test_list_jobs_rejects_invalid_pagination(
        self, client: TestClient, auth_headers
    ):
        """Test page_size above the documented maximum is rejected."""
        response = client.get("/api/jobs?page_size=101", headers=auth_headers)
        assert response.status_code == 422

    def test_list_jobs_requires_auth(self, client: TestClient):
        """Test listing jobs without a token is rejected."""
        assert client.get("/api/jobs").status_code == 401

    def test_create_job_requires_auth(self, client: TestClient):
        """Test creating a job without a token is rejected."""
        response = client.post("/api/jobs", json=_job_payload())
        assert response.status_code == 401