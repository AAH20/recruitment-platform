"""Integration tests for complete hiring workflow."""

import pytest
from fastapi.testclient import TestClient


class TestHiringWorkflow:
    """Test complete hiring workflow."""

    def test_complete_hiring_flow(self, client: TestClient):
        """Test complete hiring workflow from job posting to hire."""
        # 1. Create employer
        employer_response = client.post("/api/employers", json={
            "name": "Test Company",
            "industry": "Technology",
        })
        assert employer_response.status_code == 201
        employer_id = employer_response.json()["id"]

        # 2. Create job
        job_response = client.post("/api/jobs", json={
            "title": "Software Engineer",
            "description": "Great opportunity",
            "employer_id": employer_id,
        })
        assert job_response.status_code == 201
        job_id = job_response.json()["id"]

        # 3. Create candidate
        candidate_response = client.post("/api/candidates", json={
            "name": "John Doe",
            "email": "john@example.com",
        })
        assert candidate_response.status_code == 201
        candidate_id = candidate_response.json()["id"]

        # 4. Submit application
        application_response = client.post("/api/applications", json={
            "job_id": job_id,
            "candidate_id": candidate_id,
        })
        assert application_response.status_code == 201

        # 5. Schedule interview
        interview_response = client.post("/api/interviews", json={
            "application_id": application_response.json()["id"],
        })
        assert interview_response.status_code == 201

        # 6. Create assessment
        assessment_response = client.post("/api/assessments", json={
            "application_id": application_response.json()["id"],
        })
        assert assessment_response.status_code == 201

    def test_job_application_flow(self, client: TestClient):
        """Test job application workflow."""
        # Create job
        job_response = client.post("/api/jobs", json={
            "title": "DevOps Engineer",
            "description": "Cloud role",
        })
        assert job_response.status_code == 201
        job_id = job_response.json()["id"]

        # Create candidate
        candidate_response = client.post("/api/candidates", json={
            "name": "Jane Doe",
            "email": "jane@example.com",
        })
        assert candidate_response.status_code == 201
        candidate_id = candidate_response.json()["id"]

        # Apply
        application_response = client.post("/api/applications", json={
            "job_id": job_id,
            "candidate_id": candidate_id,
        })
        assert application_response.status_code == 201

        # Check application status
        status_response = client.get(f"/api/applications/{application_response.json()['id']}")
        assert status_response.status_code == 200

    def test_employer_job_posting_flow(self, client: TestClient):
        """Test employer job posting workflow."""
        # Create employer
        employer_response = client.post("/api/employers", json={
            "name": "New Company",
            "industry": "Finance",
        })
        assert employer_response.status_code == 201
        employer_id = employer_response.json()["id"]

        # Post multiple jobs
        for i in range(3):
            job_response = client.post("/api/jobs", json={
                "title": f"Role {i}",
                "description": f"Description {i}",
                "employer_id": employer_id,
            })
            assert job_response.status_code == 201

        # List jobs for employer
        jobs_response = client.get(f"/api/jobs?employer_id={employer_id}")
        assert jobs_response.status_code == 200
        assert len(jobs_response.json()) == 3
