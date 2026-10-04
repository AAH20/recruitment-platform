"""Tests for job API endpoints."""

import pytest
from fastapi.testclient import TestClient


class TestJobEndpoints:
    """Test job CRUD operations."""

    def test_create_job(self, client: TestClient, sample_job):
        """Test creating a new job."""
        response = client.post("/api/jobs", json=sample_job)
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["title"] == sample_job["title"]

    def test_get_job(self, client: TestClient, sample_job):
        """Test getting a job by ID."""
        create_response = client.post("/api/jobs", json=sample_job)
        job_id = create_response.json()["id"]

        response = client.get(f"/api/jobs/{job_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == job_id

    def test_list_jobs(self, client: TestClient, sample_job):
        """Test listing all jobs."""
        client.post("/api/jobs", json=sample_job)

        response = client.get("/api/jobs")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_update_job(self, client: TestClient, sample_job):
        """Test updating a job."""
        create_response = client.post("/api/jobs", json=sample_job)
        job_id = create_response.json()["id"]

        update_data = {"title": "Updated Job Title"}
        response = client.put(f"/api/jobs/{job_id}", json=update_data)
        assert response.status_code == 200

    def test_delete_job(self, client: TestClient, sample_job):
        """Test deleting a job."""
        create_response = client.post("/api/jobs", json=sample_job)
        job_id = create_response.json()["id"]

        response = client.delete(f"/api/jobs/{job_id}")
        assert response.status_code == 204

    def test_create_job_validation(self, client: TestClient):
        """Test job creation validation."""
        response = client.post("/api/jobs", json={})
        assert response.status_code == 422

    def test_get_nonexistent_job(self, client: TestClient):
        """Test getting a non-existent job."""
        response = client.get("/api/jobs/99999")
        assert response.status_code == 404

    def test_filter_jobs_by_location(self, client: TestClient, sample_job):
        """Test filtering jobs by location."""
        client.post("/api/jobs", json=sample_job)

        response = client.get("/api/jobs?location=San Francisco")
        assert response.status_code == 200
