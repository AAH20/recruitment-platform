"""Comprehensive API tests for the /api/v1/jobs endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from recruitment_platform.main import app, get_db
from recruitment_platform.database import Base


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh in-memory SQLite database for each test."""
engine = create_engine(
"sqlite:///:memory:",
connect_args={"check_same_thread": False},
poolclass=StaticPool,
)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
try:
        yield db
finally:
        db.close()
Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Return a TestClient wired to the test database."""
def override_get_db():
        try:
            yield db_session
finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
with TestClient(app) as test_client:
        yield test_client
app.dependency_overrides.clear()


@pytest.fixture
def sample_job_payload():
    """Return a valid payload for creating a job."""
return {
"title": "Senior Backend Engineer",
"description": "Build and maintain scalable APIs.",
"company": "Acme Corp",
"location": "Remote",
"salary_min": 120000,
"salary_max": 180000,
"employment_type": "full-time",
"status": "open",
}


@pytest.fixture
def created_job(client, sample_job_payload):
    """Create a job via the API and return the response JSON."""
response = client.post("/api/v1/jobs", json=sample_job_payload)
assert response.status_code == 201
return response.json()


# ---------------------------------------------------------------------------
# 1. GET /api/v1/jobs — list with pagination
# ---------------------------------------------------------------------------

class TestListJobs:
    """Tests for GET /api/v1/jobs."""

    def test_list_jobs_empty(self, client):
        """GET /api/v1/jobs returns an empty list when no jobs exist."""
response = client.get("/api/v1/jobs")
assert response.status_code == 200
data = response.json()
assert data["items"] == []
assert data["total"] == 0
assert data["page"] == 1
assert data["page_size"] == 20

    def test_list_jobs_returns_created_jobs(self, client, sample_job_payload):
        """GET /api/v1/jobs returns previously created jobs."""
client.post("/api/v1/jobs", json=sample_job_payload)
response = client.get("/api/v1/jobs")
assert response.status_code == 200
data = response.json()
assert data["total"] == 1
assert len(data["items"]) == 1
assert data["items"][0]["title"] == sample_job_payload["title"]

    def test_list_jobs_pagination_first_page(self, client, sample_job_payload):
        """GET /api/v1/jobs returns the correct first page of results."""
for i in range(5):
            payload = {**sample_job_payload, "title": f"Job {i}"}
client.post("/api/v1/jobs", json=payload)

        response = client.get("/api/v1/jobs?page=1&page_size=2")
assert response.status_code == 200
data = response.json()
assert data["total"] == 5
assert data["page"] == 1
assert data["page_size"] == 2
assert len(data["items"]) == 2

    def test_list_jobs_pagination_second_page(self, client, sample_job_payload):
        """GET /api/v1/jobs returns the correct second page of results."""
for i in range(5):
            payload = {**sample_job_payload, "title": f"Job {i}"}
client.post("/api/v1/jobs", json=payload)

        response = client.get("/api/v1/jobs?page=2&page_size=2")
assert response.status_code == 200
data = response.json()
assert data["total"] == 5
assert data["page"] == 2
assert data["page_size"] == 2
assert len(data["items"]) == 2

    def test_list_jobs_pagination_last_partial_page(self, client, sample_job_payload):
        """GET /api/v1/jobs returns a partial last page correctly."""
for i in range(5):
            payload = {**sample_job_payload, "title": f"Job {i}"}
client.post("/api/v1/jobs", json=payload)

        response = client.get("/api/v1/jobs?page=3&page_size=2")
assert response.status_code == 200
data = response.json()
assert data["total"] == 5
assert data["page"] == 3
assert len(data["items"]) == 1

    def test_list_jobs_pagination_out_of_range(self, client, sample_job_payload):
        """GET /api/v1/jobs returns empty items when page exceeds total pages."""
client.post("/api/v1/jobs", json=sample_job_payload)
response = client.get("/api/v1/jobs?page=10&page_size=20")
assert response.status_code == 200
data = response.json()
assert data["items"] == []
assert data["total"] == 1

    def test_list_jobs_default_page_size(self, client, sample_job_payload):
        """GET /api/v1/jobs uses default page_size of 20."""
response = client.get("/api/v1/jobs")
assert response.status_code == 200
data = response.json()
assert data["page_size"] == 20


# ---------------------------------------------------------------------------
# 2. POST /api/v1/jobs — create
# ---------------------------------------------------------------------------

class TestCreateJob:
    """Tests for POST /api/v1/jobs."""

    def test_create_job_success(self, client, sample_job_payload):
        """POST /api/v1/jobs creates a job and returns 201 with the job data."""
response = client.post("/api/v1/jobs", json=sample_job_payload)
assert response.status_code == 201
data = response.json()
assert data["id"] is not None
assert data["title"] == sample_job_payload["title"]
assert data["description"] == sample_job_payload["description"]
assert data["company"] == sample_job_payload["company"]
assert data["location"] == sample_job_payload["location"]
assert data["salary_min"] == sample_job_payload["salary_min"]
assert data["salary_max"] == sample_job_payload["salary_max"]
assert data["employment_type"] == sample_job_payload["employment_type"]
assert data["status"] == sample_job_payload["status"]
assert "created_at" in data
assert "updated_at" in data

    def test_create_job_missing_required_fields(self, client):
        """POST /api/v1/jobs returns 422 when required fields are missing."""
response = client.post("/api/v1/jobs", json={})
assert response.status_code == 422

    def test_create_job_missing_title(self, client, sample_job_payload):
        """POST /api/v1/jobs returns 422 when title is missing."""
payload = {k: v for k, v in sample_job_payload.items() if k != "title"}
response = client.post("/api/v1/jobs", json=payload)
assert response.status_code == 422

    def test_create_job_invalid_salary_range(self, client, sample_job_payload):
        """POST /api/v1/jobs returns 422 when salary_min > salary_max."""
payload = {**sample_job_payload, "salary_min": 200000, "salary_max": 100000}
response = client.post("/api/v1/jobs", json=payload)
assert response.status_code == 422

    def test_create_job_invalid_employment_type(self, client, sample_job_payload):
        """POST /api/v1/jobs returns 422 for an invalid employment_type."""
payload = {**sample_job_payload, "employment_type": "internship-fulltime-hybrid"}
response = client.post("/api/v1/jobs", json=payload)
assert response.status_code == 422

    def test_create_job_auto_generates_id(self, client, sample_job_payload):
        """POST /api/v1/jobs auto-generates a unique id for each job."""
resp1 = client.post("/api/v1/jobs", json=sample_job_payload)
resp2 = client.post("/api/v1/jobs", json=sample_job_payload)
assert resp1.status_code == 201
assert resp2.status_code == 201
assert resp1.json()["id"] != resp2.json()["id"]


# ---------------------------------------------------------------------------
# 3. GET /api/v1/jobs/{id} — retrieve single job
# ---------------------------------------------------------------------------

class TestGetJob:
    """Tests for GET /api/v1/jobs/{id}."""

    def test_get_job_success(self, client, created_job, sample_job_payload):
        """GET /api/v1/jobs/{id} returns the correct job."""
job_id = created_job["id"]
response = client.get(f"/api/v1/jobs/{job_id}")
assert response.status_code == 200
data = response.json()
assert data["id"] == job_id
assert data["title"] == sample_job_payload["title"]
assert data["company"] == sample_job_payload["company"]

    def test_get_job_not_found(self, client):
        """GET /api/v1/jobs/{id} returns 404 for a non-existent job."""
response = client.get("/api/v1/jobs/99999")
assert response.status_code == 404
assert "detail" in response.json()

    def test_get_job_invalid_id_format(self, client):
        """GET /api/v1/jobs/{id} returns 422 for a non-integer id."""
response = client.get("/api/v1/jobs/not-a-number")
assert response.status_code == 422


# ---------------------------------------------------------------------------
# 4. PUT /api/v1/jobs/{id} — update
# ---------------------------------------------------------------------------

class TestUpdateJob:
    """Tests for PUT /api/v1/jobs/{id}."""

    def test_update_job_success(self, client, created_job):
        """PUT /api/v1/jobs/{id} updates and returns the modified job."""
job_id = created_job["id"]
update_payload = {"title": "Staff Engineer", "salary_max": 220000}
response = client.put(f"/api/v1/jobs/{job_id}", json=update_payload)
assert response.status_code == 200
data = response.json()
assert data["id"] == job_id
assert data["title"] == "Staff Engineer"
assert data["salary_max"] == 220000
# Unchanged fields remain intact
        assert data["company"] == created_job["company"]
assert data["location"] == created_job["location"]

    def test_update_job_not_found(self, client):
        """PUT /api/v1/jobs/{id} returns 404 for a non-existent job."""
response = client.put("/api/v1/jobs/99999", json={"title": "New Title"})
assert response.status_code == 404

    def test_update_job_partial(self, client, created_job):
        """PUT /api/v1/jobs/{id} supports partial updates."""
job_id = created_job["id"]
response = client.put(f"/api/v1/jobs/{job_id}", json={"status": "closed"})
assert response.status_code == 200
data = response.json()
assert data["status"] == "closed"
assert data["title"] == created_job["title"]

    def test_update_job_invalid_id_format(self, client):
        """PUT /api/v1/jobs/{id} returns 422 for a non-integer id."""
response = client.put("/api/v1/jobs/abc", json={"title": "X"})
assert response.status_code == 422

    def test_update_job_empty_body(self, client, created_job):
        """PUT /api/v1/jobs/{id} with empty body returns the job unchanged."""
job_id = created_job["id"]
response = client.put(f"/api/v1/jobs/{job_id}", json={})
assert response.status_code == 200
data = response.json()
assert data["title"] == created_job["title"]


# ---------------------------------------------------------------------------
# 5. DELETE /api/v1/jobs/{id} — delete
# ---------------------------------------------------------------------------

class TestDeleteJob:
    """Tests for DELETE /api/v1/jobs/{id}."""

    def test_delete_job_success(self, client, created_job):
        """DELETE /api/v1/jobs/{id} removes the job and returns 204."""
job_id = created_job["id"]
response = client.delete(f"/api/v1/jobs/{job_id}")
assert response.status_code == 204

        # Verify the job is gone
        get_response = client.get(f"/api/v1/jobs/{job_id}")
assert get_response.status_code == 404

    def test_delete_job_not_found(self, client):
        """DELETE /api/v1/jobs/{id} returns 404 for a non-existent job."""
response = client.delete("/api/v1/jobs/99999")
assert response.status_code == 404

    def test_delete_job_invalid_id_format(self, client):
        """DELETE /api/v1/jobs/{id} returns 422 for a non-integer id."""
response = client.delete("/api/v1/jobs/not-a-number")
assert response.status_code == 422

    def test_delete_job_idempotent_behaviour(self, client, created_job):
        """DELETE /api/v1/jobs/{id} on an already-deleted job returns 404."""
job_id = created_job["id"]
client.delete(f"/api/v1/jobs/{job_id}")
response = client.delete(f"/api/v1/jobs/{job_id}")
assert response.status_code == 404
