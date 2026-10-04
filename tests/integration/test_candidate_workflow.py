"""Integration tests for candidate workflow: lifecycle, job matching, and application flow."""

import pytest
from datetime import datetime, timedelta


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def candidate_payload():
    """Return a valid candidate creation payload."""
return {
"first_name": "Jane",
"last_name": "Doe",
"email": "jane.doe@example.com",
"phone": "+1-555-0100",
"skills": ["Python", "FastAPI", "PostgreSQL"],
"experience_years": 5,
"resume_url": "https://example.com/resumes/jane-doe.pdf",
}


@pytest.fixture
def job_payload():
    """Return a valid job creation payload."""
return {
"title": "Senior Backend Engineer",
"description": "Build and maintain scalable backend services.",
"department": "Engineering",
"location": "Remote",
"required_skills": ["Python", "FastAPI"],
"min_experience_years": 3,
"status": "open",
}


@pytest.fixture
def created_candidate(client, candidate_payload):
    """Create a candidate and return the response JSON."""
response = client.post("/api/v1/candidates", json=candidate_payload)
assert response.status_code == 201
return response.json()


@pytest.fixture
def created_job(client, job_payload):
    """Create a job and return the response JSON."""
response = client.post("/api/v1/jobs", json=job_payload)
assert response.status_code == 201
return response.json()


# ---------------------------------------------------------------------------
# Test 1: Full candidate lifecycle — create → update → delete
# ---------------------------------------------------------------------------


class TestFullCandidateLifecycle:
    """Test the complete lifecycle of a candidate record."""

    def test_create_candidate(self, client, candidate_payload):
        """Verify a candidate can be created successfully."""
response = client.post("/api/v1/candidates", json=candidate_payload)

        assert response.status_code == 201
data = response.json()
assert data["id"] is not None
assert data["first_name"] == candidate_payload["first_name"]
assert data["last_name"] == candidate_payload["last_name"]
assert data["email"] == candidate_payload["email"]
assert data["skills"] == candidate_payload["skills"]
assert data["experience_years"] == candidate_payload["experience_years"]
assert "created_at" in data
assert "updated_at" in data

    def test_get_candidate(self, client, created_candidate):
        """Verify a candidate can be retrieved by ID."""
candidate_id = created_candidate["id"]
response = client.get(f"/api/v1/candidates/{candidate_id}")

        assert response.status_code == 200
data = response.json()
assert data["id"] == candidate_id
assert data["email"] == created_candidate["email"]

    def test_update_candidate(self, client, created_candidate):
        """Verify a candidate can be updated."""
candidate_id = created_candidate["id"]
update_payload = {
"first_name": "Janet",
"skills": ["Python", "FastAPI", "PostgreSQL", "Redis"],
"experience_years": 6,
}
response = client.put(
f"/api/v1/candidates/{candidate_id}", json=update_payload
)

        assert response.status_code == 200
data = response.json()
assert data["id"] == candidate_id
assert data["first_name"] == "Janet"
assert data["last_name"] == created_candidate["last_name"]
assert data["skills"] == update_payload["skills"]
assert data["experience_years"] == 6
assert data["updated_at"] >= data["created_at"]

    def test_delete_candidate(self, client, created_candidate):
        """Verify a candidate can be deleted."""
candidate_id = created_candidate["id"]

        # Delete the candidate
        delete_response = client.delete(f"/api/v1/candidates/{candidate_id}")
assert delete_response.status_code == 204

        # Confirm the candidate no longer exists
        get_response = client.get(f"/api/v1/candidates/{candidate_id}")
assert get_response.status_code == 404

    def test_full_lifecycle(self, client, candidate_payload):
        """End-to-end: create → read → update → delete."""
# CREATE
        create_response = client.post("/api/v1/candidates", json=candidate_payload)
assert create_response.status_code == 201
candidate = create_response.json()
candidate_id = candidate["id"]
assert candidate["email"] == candidate_payload["email"]

        # READ
        get_response = client.get(f"/api/v1/candidates/{candidate_id}")
assert get_response.status_code == 200
assert get_response.json()["id"] == candidate_id

        # UPDATE
        update_payload = {"first_name": "Updated", "experience_years": 10}
update_response = client.put(
f"/api/v1/candidates/{candidate_id}", json=update_payload
)
    assert update_response.status_code == 200
updated = update_response.json()
assert updated["first_name"] == "Updated"
assert updated["experience_years"] == 10
assert updated["email"] == candidate_payload["email"]

        # DELETE
        delete_response = client.delete(f"/api/v1/candidates/{candidate_id}")
assert delete_response.status_code == 204

        # VERIFY DELETION
        final_get = client.get(f"/api/v1/candidates/{candidate_id}")
assert final_get.status_code == 404


# ---------------------------------------------------------------------------
# Test 2: Candidate-job matching
# ---------------------------------------------------------------------------


class TestCandidateJobMatching:
    """Test matching candidates to jobs based on skills and experience."""

    def test_match_candidate_to_job(self, client, created_candidate, created_job):
        """Verify a candidate can be matched to a job."""
candidate_id = created_candidate["id"]
job_id = created_job["id"]

        response = client.post(
f"/api/v1/candidates/{candidate_id}/match",
json={"job_id": job_id},
)

        assert response.status_code == 200
data = response.json()
assert data["candidate_id"] == candidate_id
assert data["job_id"] == job_id
assert "match_score" in data
assert "matched_skills" in data
assert data["match_score"] > 0

    def test_match_returns_compatibility_details(
self, client, created_candidate, created_job
):
        """Verify match response includes skill overlap and score breakdown."""
candidate_id = created_candidate["id"]
job_id = created_job["id"]

        response = client.post(
f"/api/v1/candidates/{candidate_id}/match",
json={"job_id": job_id},
)

        assert response.status_code == 200
data = response.json()

        # Candidate has Python, FastAPI, PostgreSQL
        # Job requires Python, FastAPI
        assert "Python" in data["matched_skills"]
assert "FastAPI" in data["matched_skills"]
assert data["match_score"] >= 0.5

    def test_match_candidate_with_insufficient_experience(
self, client, candidate_payload, job_payload
):
        """Verify matching accounts for experience requirements."""
# Create a junior candidate
        candidate_payload["experience_years"] = 1
candidate_payload["email"] = "junior@example.com"
candidate_response = client.post("/api/v1/candidates", json=candidate_payload)
assert candidate_response.status_code == 201
junior_candidate = candidate_response.json()

        # Job requires 3+ years
        job_response = client.post("/api/v1/jobs", json=job_payload)
assert job_response.status_code == 201
job = job_response.json()

        response = client.post(
f"/api/v1/candidates/{junior_candidate['id']}/match",
json={"job_id": job["id"]},
)

        assert response.status_code == 200
data = response.json()
# Match should still work but with a lower score due to experience gap
        assert data["match_score"] < 1.0
assert "experience_gap" in data or "meets_experience" in data

    def test_get_candidate_matches(self, client, created_candidate, created_job):
        """Verify all matches for a candidate can be retrieved."""
candidate_id = created_candidate["id"]
job_id = created_job["id"]

        # Create a match first
        client.post(
f"/api/v1/candidates/{candidate_id}/match",
json={"job_id": job_id},
)

        # Retrieve matches
        response = client.get(f"/api/v1/candidates/{candidate_id}/matches")
assert response.status_code == 200
data = response.json()
assert isinstance(data, list)
assert len(data) >= 1
assert any(m["job_id"] == job_id for m in data)


# ---------------------------------------------------------------------------
# Test 3: Candidate application flow — apply → update status
# ---------------------------------------------------------------------------


class TestCandidateApplicationFlow:
    """Test the full application workflow from submission to status updates."""

    def test_apply_to_job(self, client, created_candidate, created_job):
        """Verify a candidate can apply to a job."""
candidate_id = created_candidate["id"]
job_id = created_job["id"]

        response = client.post(
f"/api/v1/candidates/{candidate_id}/apply",
json={"job_id": job_id, "cover_letter": "I am a great fit!"},
)

        assert response.status_code == 201
data = response.json()
assert data["candidate_id"] == candidate_id
assert data["job_id"] == job_id
assert data["status"] == "applied"
assert "applied_at" in data
assert "id" in data

    def test_get_application(self, client, created_candidate, created_job):
        """Verify an application can be retrieved by ID."""
candidate_id = created_candidate["id"]
job_id = created_job["id"]

        # Create application
        apply_response = client.post(
f"/api/v1/candidates/{candidate_id}/apply",
json={"job_id": job_id},
)
    assert apply_response.status_code == 201
application = apply_response.json()

        # Retrieve it
        response = client.get(f"/api/v1/applications/{application['id']}")
assert response.status_code == 200
data = response.json()
assert data["id"] == application["id"]
assert data["candidate_id"] == candidate_id
assert data["job_id"] == job_id

    def test_update_application_status(self, client, created_candidate, created_job):
        """Verify application status can be updated through the pipeline."""
candidate_id = created_candidate["id"]
job_id = created_job["id"]

        # Apply
        apply_response = client.post(
f"/api/v1/candidates/{candidate_id}/apply",
json={"job_id": job_id},
)
    assert apply_response.status_code == 201
application = apply_response.json()
application_id = application["id"]
assert application["status"] == "applied"

        # Update to screening
        response = client.patch(
f"/api/v1/applications/{application_id}/status",
json={"status": "screening"},
)
    assert response.status_code == 200
data = response.json()
assert data["status"] == "screening"
assert data["id"] == application_id

        # Update to interview
        response = client.patch(
f"/api/v1/applications/{application_id}/status",
json={"status": "interview"},
)
    assert response.status_code == 200
data = response.json()
assert data["status"] == "interview"

        # Update to offer
        response = client.patch(
f"/api/v1/applications/{application_id}/status",
json={"status": "offer"},
)
    assert response.status_code == 200
data = response.json()
assert data["status"] == "offer"

    def test_full_application_flow(self, client, created_candidate, created_job):
        """End-to-end: apply → screening → interview → offer → accepted."""
candidate_id = created_candidate["id"]
job_id = created_job["id"]

        # APPLY
        apply_response = client.post(
f"/api/v1/candidates/{candidate_id}/apply",
json={
"job_id": job_id,
"cover_letter": "Excited about this opportunity!",
},
)
    assert apply_response.status_code == 201
application = apply_response.json()
application_id = application["id"]
assert application["status"] == "applied"

        # SCREENING
        response = client.patch(
f"/api/v1/applications/{application_id}/status",
json={"status": "screening"},
)
    assert response.status_code == 200
assert response.json()["status"] == "screening"

        # INTERVIEW
        response = client.patch(
f"/api/v1/applications/{application_id}/status",
json={"status": "interview"},
)
    assert response.status_code == 200
assert response.json()["status"] == "interview"

        # OFFER
        response = client.patch(
f"/api/v1/applications/{application_id}/status",
json={"status": "offer"},
)
    assert response.status_code == 200
assert response.json()["status"] == "offer"

        # ACCEPTED
        response = client.patch(
f"/api/v1/applications/{application_id}/status",
json={"status": "accepted"},
)
    assert response.status_code == 200
final_data = response.json()
assert final_data["status"] == "accepted"
assert final_data["id"] == application_id

        # Verify final state via GET
        get_response = client.get(f"/api/v1/applications/{application_id}")
assert get_response.status_code == 200
assert get_response.json()["status"] == "accepted"

    def test_list_candidate_applications(self, client, created_candidate, created_job):
        """Verify all applications for a candidate can be listed."""
candidate_id = created_candidate["id"]
job_id = created_job["id"]

        # Create application
        client.post(
f"/api/v1/candidates/{candidate_id}/apply",
json={"job_id": job_id},
)

        # List applications
        response = client.get(f"/api/v1/candidates/{candidate_id}/applications")
assert response.status_code == 200
data = response.json()
assert isinstance(data, list)
assert len(data) >= 1
assert any(app["job_id"] == job_id for app in data)

    def test_duplicate_application_rejected(self, client, created_candidate, created_job):
        """Verify a candidate cannot apply to the same job twice."""
candidate_id = created_candidate["id"]
job_id = created_job["id"]

        # First application
        response = client.post(
f"/api/v1/candidates/{candidate_id}/apply",
json={"job_id": job_id},
)
    assert response.status_code == 201

        # Duplicate application should fail
        response = client.post(
f"/api/v1/candidates/{candidate_id}/apply",
json={"job_id": job_id},
)
    assert response.status_code == 409
