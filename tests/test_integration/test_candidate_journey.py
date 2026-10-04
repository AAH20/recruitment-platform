"""Integration tests for candidate journey."""

import pytest
from fastapi.testclient import TestClient


class TestCandidateJourney:
    """Test candidate journey from application to hire."""

    def test_candidate_application_journey(self, client: TestClient):
        """Test candidate application journey."""
        # Create candidate
        candidate_response = client.post("/api/candidates", json={
            "name": "Alice Smith",
            "email": "alice@example.com",
            "skills": ["Python", "FastAPI"],
        })
        assert candidate_response.status_code == 201
        candidate_id = candidate_response.json()["id"]

        # Create job
        job_response = client.post("/api/jobs", json={
            "title": "Backend Engineer",
            "description": "API development",
        })
        assert job_response.status_code == 201
        job_id = job_response.json()["id"]

        # Apply to job
        application_response = client.post("/api/applications", json={
            "job_id": job_id,
            "candidate_id": candidate_id,
        })
        assert application_response.status_code == 201

        # Check application status
        app_id = application_response.json()["id"]
        status_response = client.get(f"/api/applications/{app_id}")
        assert status_response.status_code == 200
        assert status_response.json()["status"] == "pending"

    def test_multiple_applications(self, client: TestClient):
        """Test candidate applying to multiple jobs."""
        # Create candidate
        candidate_response = client.post("/api/candidates", json={
            "name": "Bob Johnson",
            "email": "bob@example.com",
        })
        candidate_id = candidate_response.json()["id"]

        # Apply to multiple jobs
        for i in range(3):
            job_response = client.post("/api/jobs", json={
                "title": f"Position {i}",
                "description": f"Role {i}",
            })
            job_id = job_response.json()["id"]

            application_response = client.post("/api/applications", json={
                "job_id": job_id,
                "candidate_id": candidate_id,
            })
            assert application_response.status_code == 201
