"""Integration tests for interview workflow."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from recruitment_platform.api.interviews import router as interviews_router
from recruitment_platform.api.applications import router as applications_router
from recruitment_platform.api.analytics import router as analytics_router
from fastapi import FastAPI


@pytest.fixture
def app():
    """Create a FastAPI app with all routers for integration testing."""
    application = FastAPI()
    application.include_router(interviews_router)
    application.include_router(applications_router)
    application.include_router(analytics_router)
    return application


@pytest.fixture
def client(app):
    """Create a TestClient for making HTTP requests."""
    return TestClient(app)


@pytest.fixture
def sample_interview_payload():
    """Return a valid payload for scheduling an interview."""
    return {
        "candidate_id": str(uuid4()),
        "job_id": str(uuid4()),
        "interviewer_id": str(uuid4()),
        "scheduled_at": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
        "duration_minutes": 60,
        "location": "Conference Room A",
        "meeting_link": "https://meet.example.com/interview-123",
        "notes": "Initial screening interview",
    }


@pytest.fixture
def sample_application_payload():
    """Return a valid payload for creating an application."""
    return {
        "candidate_name": "Test Candidate",
        "candidate_email": "test.candidate@example.com",
        "position_id": "pos_test_001",
        "position_title": "Test Engineer",
        "resume_url": "https://storage.example.com/resumes/test.pdf",
        "cover_letter": "I am excited to apply for this test role.",
        "source": "linkedin",
        "years_experience": 5,
        "skills": ["Python", "FastAPI", "PostgreSQL"],
    }


class TestFullInterviewLifecycle:
    """Test the complete lifecycle of an interview: schedule → update → cancel."""

    def test_full_interview_lifecycle(self, client, sample_interview_payload):
        """Schedule an interview, update it, then cancel it."""
        # Step 1: Schedule the interview
        response = client.post("/api/v1/interviews", json=sample_interview_payload)
        assert response.status_code == 201
        interview_data = response.json()
        interview_id = interview_data["id"]

        assert interview_data["status"] == "scheduled"
        assert interview_data["candidate_id"] == sample_interview_payload["candidate_id"]
        assert interview_data["job_id"] == sample_interview_payload["job_id"]
        assert interview_data["interviewer_id"] == sample_interview_payload["interviewer_id"]
        assert interview_data["duration_minutes"] == 60
        assert interview_data["location"] == "Conference Room A"
        assert interview_data["meeting_link"] == "https://meet.example.com/interview-123"
        assert interview_data["notes"] == "Initial screening interview"
        assert "created_at" in interview_data
        assert "updated_at" in interview_data

        # Step 2: Update the interview
        update_payload = {
            "duration_minutes": 90,
            "location": "Conference Room B",
            "notes": "Extended interview with technical assessment",
        }
        response = client.put(f"/api/v1/interviews/{interview_id}", json=update_payload)
        assert response.status_code == 200
        updated_data = response.json()

        assert updated_data["id"] == interview_id
        assert updated_data["duration_minutes"] == 90
        assert updated_data["location"] == "Conference Room B"
        assert updated_data["notes"] == "Extended interview with technical assessment"
        # Unchanged fields should remain
        assert updated_data["candidate_id"] == sample_interview_payload["candidate_id"]
        assert updated_data["job_id"] == sample_interview_payload["job_id"]
        assert updated_data["status"] == "scheduled"

        # Step 3: Verify the update by fetching the interview
        response = client.get(f"/api/v1/interviews/{interview_id}")
        assert response.status_code == 200
        fetched_data = response.json()
        assert fetched_data["duration_minutes"] == 90
        assert fetched_data["location"] == "Conference Room B"

        # Step 4: Cancel (delete) the interview
        response = client.delete(f"/api/v1/interviews/{interview_id}")
        assert response.status_code == 204

        # Step 5: Verify the interview is gone
        response = client.get(f"/api/v1/interviews/{interview_id}")
        assert response.status_code == 404


class TestInterviewApplicationFlow:
    """Test the flow from application creation through interview scheduling to status update."""

    def test_interview_application_flow(self, client, sample_application_payload, sample_interview_payload):
        """Create application → schedule interview → update application status."""
        # Step 1: Create a job application
        response = client.post("/applications", json=sample_application_payload)
        assert response.status_code == 201
        application_data = response.json()
        application_id = application_data["id"]

        assert application_data["candidate_name"] == "Test Candidate"
        assert application_data["candidate_email"] == "test.candidate@example.com"
        assert application_data["position_id"] == "pos_test_001"
        assert application_data["position_title"] == "Test Engineer"
        assert application_data["status"] == "applied"
        assert application_data["source"] == "linkedin"
        assert application_data["years_experience"] == 5
        assert "Python" in application_data["skills"]

        # Step 2: Schedule an interview for this application
        # Update the interview payload to reference the application's context
        interview_payload = sample_interview_payload.copy()
        interview_payload["notes"] = f"Interview for application {application_id}"

        response = client.post("/api/v1/interviews", json=interview_payload)
        assert response.status_code == 201
        interview_data = response.json()
        interview_id = interview_data["id"]

        assert interview_data["status"] == "scheduled"
        assert interview_data["notes"] == f"Interview for application {application_id}"

        # Step 3: Update application status to "interview"
        response = client.put(f"/applications/{application_id}", params={"status_update": "interview"})
        assert response.status_code == 200
        updated_application = response.json()

        assert updated_application["id"] == application_id
        assert updated_application["status"] == "interview"

        # Step 4: Update interview status to "completed"
        response = client.put(
            f"/api/v1/interviews/{interview_id}",
            json={"status": "completed"},
        )
        assert response.status_code == 200
        updated_interview = response.json()

        assert updated_interview["id"] == interview_id
        assert updated_interview["status"] == "completed"

        # Step 5: Update application status to "offer"
        response = client.put(f"/applications/{application_id}", params={"status_update": "offer"})
        assert response.status_code == 200
        final_application = response.json()

        assert final_application["id"] == application_id
        assert final_application["status"] == "offer"


class TestInterviewAnalytics:
    """Test analytics endpoints in the context of interview scheduling."""

    def test_interview_analytics(self, client, sample_interview_payload):
        """Schedule an interview and verify analytics endpoints return data."""
        # Step 1: Schedule an interview
        response = client.post("/api/v1/interviews", json=sample_interview_payload)
        assert response.status_code == 201
        interview_data = response.json()
        interview_id = interview_data["id"]

        assert interview_data["status"] == "scheduled"

        # Step 2: Get analytics dashboard
        response = client.get("/api/v1/analytics")
        assert response.status_code == 200
        dashboard = response.json()

        assert "total_active_jobs" in dashboard
        assert "total_candidates" in dashboard
        assert "total_hires_this_period" in dashboard
        assert "open_positions" in dashboard
        assert "avg_time_to_hire" in dashboard
        assert "offer_acceptance_rate" in dashboard

        # Step 3: Get pipeline metrics
        response = client.get("/api/v1/analytics/pipeline")
        assert response.status_code == 200
        pipeline = response.json()

        assert "total_candidates" in pipeline
        assert "stages" in pipeline
        assert "overall_conversion_rate" in pipeline
        assert isinstance(pipeline["stages"], list)

        # Step 4: Get time-to-hire metrics
        response = client.get("/api/v1/analytics/time-to-hire")
        assert response.status_code == 200
        time_to_hire = response.json()

        assert "overall_avg_days" in time_to_hire
        assert "overall_median_days" in time_to_hire
        assert "by_role" in time_to_hire
        assert isinstance(time_to_hire["by_role"], list)

        # Step 5: Get source effectiveness metrics
        response = client.get("/api/v1/analytics/source-effectiveness")
        assert response.status_code == 200
        source_effectiveness = response.json()

        assert "sources" in source_effectiveness
        assert "total_sources" in source_effectiveness
        assert isinstance(source_effectiveness["sources"], list)

        # Step 6: Verify the scheduled interview appears in the list
        response = client.get("/api/v1/interviews", params={"status": "scheduled"})
        assert response.status_code == 200
        interviews_list = response.json()

        assert "items" in interviews_list
        assert "total" in interviews_list
        interview_ids = [i["id"] for i in interviews_list["items"]]
        assert interview_id in interview_ids
