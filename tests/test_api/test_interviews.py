"""Comprehensive API tests for /api/v1/interviews endpoints."""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta, timezone


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    """Return a TestClient for the app."""
from recruitment_platform.main import app
return TestClient(app)


@pytest.fixture
def auth_headers():
    """Return headers with a valid auth token."""
return {"Authorization": "Bearer test-token"}


@pytest.fixture
def sample_interview_payload():
    """Return a valid payload for creating an interview."""
future = datetime.now(timezone.utc) + timedelta(days=7)
return {
"candidate_id": "cand-001",
"job_id": "job-001",
"interviewer_id": "user-001",
"scheduled_at": future.isoformat(),
"duration_minutes": 60,
"interview_type": "technical",
"location": "https://meet.example.com/abc123",
"notes": "Initial technical screening",
}


@pytest.fixture
def created_interview(client, auth_headers, sample_interview_payload):
    """Create an interview and return the response JSON."""
resp = client.post(
"/api/v1/interviews",
json=sample_interview_payload,
headers=auth_headers,
)
assert resp.status_code == 201
return resp.json()


# ---------------------------------------------------------------------------
# 1. GET /api/v1/interviews — list with pagination
# ---------------------------------------------------------------------------

class TestListInterviews:
    """Tests for GET /api/v1/interviews."""

    def test_list_interviews_success(self, client, auth_headers):
        """GET /api/v1/interviews returns 200 with a list."""
resp = client.get("/api/v1/interviews", headers=auth_headers)
assert resp.status_code == 200
data = resp.json()
assert isinstance(data, list)

    def test_list_interviews_pagination_default(self, client, auth_headers):
        """Default pagination returns a reasonable page size."""
resp = client.get("/api/v1/interviews", headers=auth_headers)
assert resp.status_code == 200
data = resp.json()
assert len(data) <= 100

    def test_list_interviews_pagination_custom_page(self, client, auth_headers):
        """Custom page parameter is respected."""
resp = client.get("/api/v1/interviews?page=2&page_size=5", headers=auth_headers)
assert resp.status_code == 200
data = resp.json()
assert isinstance(data, list)
assert len(data) <= 5

    def test_list_interviews_pagination_page_size(self, client, auth_headers):
        """page_size parameter limits results."""
resp = client.get("/api/v1/interviews?page_size=3", headers=auth_headers)
assert resp.status_code == 200
data = resp.json()
assert len(data) <= 3

    def test_list_interviews_pagination_zero_page_size(self, client, auth_headers):
        """page_size=0 should return empty list or 422."""
resp = client.get("/api/v1/interviews?page_size=0", headers=auth_headers)
assert resp.status_code in (200, 422)
if resp.status_code == 200:
            assert resp.json() == []

    def test_list_interviews_pagination_negative_page(self, client, auth_headers):
        """Negative page should return 422 or empty."""
resp = client.get("/api/v1/interviews?page=-1", headers=auth_headers)
assert resp.status_code in (200, 422)

    def test_list_interviews_unauthenticated(self, client):
        """GET /api/v1/interviews without auth returns 401."""
resp = client.get("/api/v1/interviews")
assert resp.status_code == 401

    def test_list_interviews_response_fields(self, client, auth_headers, created_interview):
        """Each interview in the list has required fields."""
resp = client.get("/api/v1/interviews", headers=auth_headers)
assert resp.status_code == 200
data = resp.json()
if data:
            item = data[0]
for field in ("id", "candidate_id", "job_id", "scheduled_at", "status"):
                assert field in item, f"Missing field: {field}"

    def test_list_interviews_filter_by_status(self, client, auth_headers):
        """Filter interviews by status."""
resp = client.get("/api/v1/interviews?status=scheduled", headers=auth_headers)
assert resp.status_code == 200
data = resp.json()
for item in data:
            assert item.get("status") == "scheduled"

    def test_list_interviews_filter_by_candidate(self, client, auth_headers):
        """Filter interviews by candidate_id."""
resp = client.get("/api/v1/interviews?candidate_id=cand-001", headers=auth_headers)
assert resp.status_code == 200
data = resp.json()
for item in data:
            assert item.get("candidate_id") == "cand-001"


# ---------------------------------------------------------------------------
# 2. POST /api/v1/interviews — schedule
# ---------------------------------------------------------------------------

class TestScheduleInterview:
    """Tests for POST /api/v1/interviews."""

    def test_schedule_interview_success(self, client, auth_headers, sample_interview_payload):
        """POST /api/v1/interviews creates an interview and returns 201."""
resp = client.post(
"/api/v1/interviews",
json=sample_interview_payload,
headers=auth_headers,
)
    assert resp.status_code == 201
data = resp.json()
assert "id" in data
assert data["candidate_id"] == sample_interview_payload["candidate_id"]
assert data["job_id"] == sample_interview_payload["job_id"]
assert data["status"] == "scheduled"

    def test_schedule_interview_minimal_payload(self, client, auth_headers):
        """POST with only required fields succeeds."""
future = datetime.now(timezone.utc) + timedelta(days=1)
payload = {
"candidate_id": "cand-002",
"job_id": "job-002",
"scheduled_at": future.isoformat(),
}
resp = client.post("/api/v1/interviews", json=payload, headers=auth_headers)
assert resp.status_code == 201
data = resp.json()
assert data["candidate_id"] == "cand-002"

    def test_schedule_interview_missing_required_fields(self, client, auth_headers):
        """POST without required fields returns 422."""
resp = client.post("/api/v1/interviews", json={}, headers=auth_headers)
assert resp.status_code == 422

    def test_schedule_interview_missing_candidate_id(self, client, auth_headers):
        """POST without candidate_id returns 422."""
future = datetime.now(timezone.utc) + timedelta(days=1)
payload = {"job_id": "job-001", "scheduled_at": future.isoformat()}
resp = client.post("/api/v1/interviews", json=payload, headers=auth_headers)
assert resp.status_code == 422

    def test_schedule_interview_missing_job_id(self, client, auth_headers):
        """POST without job_id returns 422."""
future = datetime.now(timezone.utc) + timedelta(days=1)
payload = {"candidate_id": "cand-001", "scheduled_at": future.isoformat()}
resp = client.post("/api/v1/interviews", json=payload, headers=auth_headers)
assert resp.status_code == 422

    def test_schedule_interview_missing_scheduled_at(self, client, auth_headers):
        """POST without scheduled_at returns 422."""
payload = {"candidate_id": "cand-001", "job_id": "job-001"}
resp = client.post("/api/v1/interviews", json=payload, headers=auth_headers)
assert resp.status_code == 422

    def test_schedule_interview_invalid_datetime(self, client, auth_headers):
        """POST with invalid datetime returns 422."""
payload = {
"candidate_id": "cand-001",
"job_id": "job-001",
"scheduled_at": "not-a-date",
}
resp = client.post("/api/v1/interviews", json=payload, headers=auth_headers)
assert resp.status_code == 422

    def test_schedule_interview_past_datetime(self, client, auth_headers):
        """POST with past datetime returns 422 or 400."""
past = datetime.now(timezone.utc) - timedelta(days=1)
payload = {
"candidate_id": "cand-001",
"job_id": "job-001",
"scheduled_at": past.isoformat(),
}
resp = client.post("/api/v1/interviews", json=payload, headers=auth_headers)
assert resp.status_code in (400, 422)

    def test_schedule_interview_unauthenticated(self, client, sample_interview_payload):
        """POST without auth returns 401."""
resp = client.post("/api/v1/interviews", json=sample_interview_payload)
assert resp.status_code == 401

    def test_schedule_interview_invalid_interview_type(self, client, auth_headers):
        """POST with invalid interview_type returns 422."""
future = datetime.now(timezone.utc) + timedelta(days=1)
payload = {
"candidate_id": "cand-001",
"job_id": "job-001",
"scheduled_at": future.isoformat(),
"interview_type": "invalid_type",
}
resp = client.post("/api/v1/interviews", json=payload, headers=auth_headers)
assert resp.status_code == 422

    def test_schedule_interview_negative_duration(self, client, auth_headers):
        """POST with negative duration returns 422."""
future = datetime.now(timezone.utc) + timedelta(days=1)
payload = {
"candidate_id": "cand-001",
"job_id": "job-001",
"scheduled_at": future.isoformat(),
"duration_minutes": -30,
}
resp = client.post("/api/v1/interviews", json=payload, headers=auth_headers)
assert resp.status_code == 422

    def test_schedule_interview_response_contains_id(self, client, auth_headers, sample_interview_payload):
        """Response contains a unique id."""
resp = client.post(
"/api/v1/interviews",
json=sample_interview_payload,
headers=auth_headers,
)
    assert resp.status_code == 201
data = resp.json()
assert data["id"]
assert isinstance(data["id"], str)


# ---------------------------------------------------------------------------
# 3. GET /api/v1/interviews/{id} — retrieve
# ---------------------------------------------------------------------------

class TestGetInterview:
    """Tests for GET /api/v1/interviews/{id}."""

    def test_get_interview_success(self, client, auth_headers, created_interview):
        """GET /api/v1/interviews/{id} returns 200 with the interview."""
interview_id = created_interview["id"]
resp = client.get(f"/api/v1/interviews/{interview_id}", headers=auth_headers)
assert resp.status_code == 200
data = resp.json()
assert data["id"] == interview_id
assert data["candidate_id"] == created_interview["candidate_id"]

    def test_get_interview_not_found(self, client, auth_headers):
        """GET with non-existent id returns 404."""
resp = client.get("/api/v1/interviews/nonexistent-id", headers=auth_headers)
assert resp.status_code == 404

    def test_get_interview_unauthenticated(self, client, created_interview):
        """GET without auth returns 401."""
interview_id = created_interview["id"]
resp = client.get(f"/api/v1/interviews/{interview_id}")
assert resp.status_code == 401

    def test_get_interview_response_fields(self, client, auth_headers, created_interview):
        """Response contains all expected fields."""
interview_id = created_interview["id"]
resp = client.get(f"/api/v1/interviews/{interview_id}", headers=auth_headers)
assert resp.status_code == 200
data = resp.json()
for field in ("id", "candidate_id", "job_id", "interviewer_id", "scheduled_at", "status"):
            assert field in data, f"Missing field: {field}"

    def test_get_interview_invalid_id_format(self, client, auth_headers):
        """GET with invalid id format returns 422 or 404."""
resp = client.get("/api/v1/interviews/!!!invalid!!!", headers=auth_headers)
assert resp.status_code in (404, 422)


# ---------------------------------------------------------------------------
# 4. PUT /api/v1/interviews/{id} — update
# ---------------------------------------------------------------------------

class TestUpdateInterview:
    """Tests for PUT /api/v1/interviews/{id}."""

    def test_update_interview_success(self, client, auth_headers, created_interview):
        """PUT /api/v1/interviews/{id} updates and returns 200."""
interview_id = created_interview["id"]
update_payload = {
"duration_minutes": 90,
"notes": "Updated: extended interview",
}
resp = client.put(
f"/api/v1/interviews/{interview_id}",
json=update_payload,
headers=auth_headers,
)
    assert resp.status_code == 200
data = resp.json()
assert data["id"] == interview_id
assert data["duration_minutes"] == 90
assert data["notes"] == "Updated: extended interview"

    def test_update_interview_reschedule(self, client, auth_headers, created_interview):
        """PUT can reschedule the interview."""
interview_id = created_interview["id"]
new_time = datetime.now(timezone.utc) + timedelta(days=14)
update_payload = {"scheduled_at": new_time.isoformat()}
resp = client.put(
f"/api/v1/interviews/{interview_id}",
json=update_payload,
headers=auth_headers,
)
    assert resp.status_code == 200
data = resp.json()
assert data["id"] == interview_id

    def test_update_interview_not_found(self, client, auth_headers):
        """PUT with non-existent id returns 404."""
resp = client.put(
"/api/v1/interviews/nonexistent-id",
json={"notes": "test"},
headers=auth_headers,
)
    assert resp.status_code == 404

    def test_update_interview_unauthenticated(self, client, created_interview):
        """PUT without auth returns 401."""
interview_id = created_interview["id"]
resp = client.put(
f"/api/v1/interviews/{interview_id}",
json={"notes": "test"},
)
    assert resp.status_code == 401

    def test_update_interview_empty_body(self, client, auth_headers, created_interview):
        """PUT with empty body returns 422 or 200 (no-op)."""
interview_id = created_interview["id"]
resp = client.put(
f"/api/v1/interviews/{interview_id}",
json={},
headers=auth_headers,
)
    assert resp.status_code in (200, 422)

    def test_update_interview_invalid_datetime(self, client, auth_headers, created_interview):
        """PUT with invalid datetime returns 422."""
interview_id = created_interview["id"]
resp = client.put(
f"/api/v1/interviews/{interview_id}",
json={"scheduled_at": "invalid"},
headers=auth_headers,
)
    assert resp.status_code == 422

    def test_update_interview_change_type(self, client, auth_headers, created_interview):
        """PUT can change interview type."""
interview_id = created_interview["id"]
resp = client.put(
f"/api/v1/interviews/{interview_id}",
json={"interview_type": "behavioral"},
headers=auth_headers,
)
    assert resp.status_code == 200
data = resp.json()
assert data["interview_type"] == "behavioral"


# ---------------------------------------------------------------------------
# 5. DELETE /api/v1/interviews/{id} — cancel
# ---------------------------------------------------------------------------

class TestCancelInterview:
    """Tests for DELETE /api/v1/interviews/{id}."""

    def test_cancel_interview_success(self, client, auth_headers, created_interview):
        """DELETE /api/v1/interviews/{id} cancels and returns 200 or 204."""
interview_id = created_interview["id"]
resp = client.delete(f"/api/v1/interviews/{interview_id}", headers=auth_headers)
assert resp.status_code in (200, 204)

    def test_cancel_interview_status_changes(self, client, auth_headers, created_interview):
        """After cancellation, interview status is 'cancelled'."""
interview_id = created_interview["id"]
client.delete(f"/api/v1/interviews/{interview_id}", headers=auth_headers)
resp = client.get(f"/api/v1/interviews/{interview_id}", headers=auth_headers)
assert resp.status_code == 200
data = resp.json()
assert data["status"] == "cancelled"

    def test_cancel_interview_not_found(self, client, auth_headers):
        """DELETE with non-existent id returns 404."""
resp = client.delete("/api/v1/interviews/nonexistent-id", headers=auth_headers)
assert resp.status_code == 404

    def test_cancel_interview_unauthenticated(self, client, created_interview):
        """DELETE without auth returns 401."""
interview_id = created_interview["id"]
resp = client.delete(f"/api/v1/interviews/{interview_id}")
assert resp.status_code == 401

    def test_cancel_interview_idempotent_or_404(self, client, auth_headers, created_interview):
        """Cancelling twice returns 404 or 200/204 (idempotent)."""
interview_id = created_interview["id"]
resp1 = client.delete(f"/api/v1/interviews/{interview_id}", headers=auth_headers)
assert resp1.status_code in (200, 204)
resp2 = client.delete(f"/api/v1/interviews/{interview_id}", headers=auth_headers)
assert resp2.status_code in (200, 204, 404)

    def test_cancel_interview_invalid_id(self, client, auth_headers):
        """DELETE with invalid id returns 404 or 422."""
resp = client.delete("/api/v1/interviews/!!!invalid!!!", headers=auth_headers)
assert resp.status_code in (404, 422)
