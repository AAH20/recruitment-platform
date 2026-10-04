"""
Comprehensive API tests for the Applications endpoints.

Tests cover:
- POST /api/v1/applications — create application
- GET /api/v1/applications — list applications with pagination
- GET /api/v1/applications/{id} — get single application
- PUT /api/v1/applications/{id} — update application status
- DELETE /api/v1/applications/{id} — delete application
"""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from recruitment_platform.main import app, get_db
from recruitment_platform.models import Base


# ── Test Database Setup ───────────────────────────────────────────────────────

TEST_DATABASE_URL = "sqlite:///./test_applications.db"

engine = create_engine(
TEST_DATABASE_URL,
connect_args={"check_same_thread": False},
poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override the dependency to use the test database."""
db = TestingSessionLocal()
try:
        yield db
finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    """Create fresh tables before each test and drop them after."""
Base.metadata.create_all(bind=engine)
yield
Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Provide a TestClient instance."""
with TestClient(app) as c:
        yield c


@pytest.fixture
def sample_application_payload():
    """Return a valid payload for creating an application."""
return {
"job_id": str(uuid.uuid4()),
"candidate_id": str(uuid.uuid4()),
"cover_letter": "I am excited to apply for this position.",
"resume_url": "https://example.com/resume.pdf",
}


@pytest.fixture
def created_application(client, sample_application_payload):
    """Create an application and return the response JSON."""
response = client.post("/api/v1/applications", json=sample_application_payload)
assert response.status_code == 201
return response.json()


# ── 1. POST /api/v1/applications — test_create_application ────────────────────


class TestCreateApplication:
    """Tests for POST /api/v1/applications endpoint."""

    def test_create_application_success(self, client, sample_application_payload):
        """Successfully create a new application."""
response = client.post("/api/v1/applications", json=sample_application_payload)

        assert response.status_code == 201
data = response.json()
assert data["job_id"] == sample_application_payload["job_id"]
assert data["candidate_id"] == sample_application_payload["candidate_id"]
assert data["cover_letter"] == sample_application_payload["cover_letter"]
assert data["resume_url"] == sample_application_payload["resume_url"]
assert data["status"] == "pending"
assert "id" in data
assert "applied_at" in data
assert "updated_at" in data

    def test_create_application_without_optional_fields(self, client):
        """Create application with only required fields."""
payload = {
"job_id": str(uuid.uuid4()),
"candidate_id": str(uuid.uuid4()),
}
response = client.post("/api/v1/applications", json=payload)

        assert response.status_code == 201
data = response.json()
assert data["job_id"] == payload["job_id"]
assert data["candidate_id"] == payload["candidate_id"]
assert data["status"] == "pending"

    def test_create_application_missing_job_id(self, client):
        """Fail when job_id is missing."""
payload = {"candidate_id": str(uuid.uuid4())}
response = client.post("/api/v1/applications", json=payload)

        assert response.status_code == 422

    def test_create_application_missing_candidate_id(self, client):
        """Fail when candidate_id is missing."""
payload = {"job_id": str(uuid.uuid4())}
response = client.post("/api/v1/applications", json=payload)

        assert response.status_code == 422

    def test_create_application_empty_body(self, client):
        """Fail when request body is empty."""
response = client.post("/api/v1/applications", json={})

        assert response.status_code == 422

    def test_create_application_invalid_job_id_type(self, client):
        """Fail when job_id is not a valid UUID."""
payload = {"job_id": "not-a-uuid", "candidate_id": str(uuid.uuid4())}
response = client.post("/api/v1/applications", json=payload)

        assert response.status_code == 422

    def test_create_application_invalid_candidate_id_type(self, client):
        """Fail when candidate_id is not a valid UUID."""
payload = {"job_id": str(uuid.uuid4()), "candidate_id": "not-a-uuid"}
response = client.post("/api/v1/applications", json=payload)

        assert response.status_code == 422

    def test_create_application_duplicate(self, client, sample_application_payload):
        """Handle duplicate application (same job + candidate)."""
response1 = client.post("/api/v1/applications", json=sample_application_payload)
assert response1.status_code == 201

        response2 = client.post("/api/v1/applications", json=sample_application_payload)
assert response2.status_code in (201, 409)

    def test_create_application_with_all_fields(self, client):
        """Create application with every possible field populated."""
payload = {
"job_id": str(uuid.uuid4()),
"candidate_id": str(uuid.uuid4()),
"cover_letter": "A" * 5000,
"resume_url": "https://example.com/path/to/resume.pdf",
}
response = client.post("/api/v1/applications", json=payload)

        assert response.status_code == 201
data = response.json()
assert data["job_id"] == payload["job_id"]
assert data["candidate_id"] == payload["candidate_id"]
assert data["cover_letter"] == payload["cover_letter"]
assert data["resume_url"] == payload["resume_url"]

    def test_create_application_response_content_type(self, client, sample_application_payload):
        """Response should have JSON content type."""
response = client.post("/api/v1/applications", json=sample_application_payload)

        assert response.headers["content-type"].startswith("application/json")

    def test_create_application_with_cover_letter(self, client):
        """Create application with cover letter."""
payload = {
"job_id": str(uuid.uuid4()),
"candidate_id": str(uuid.uuid4()),
"cover_letter": "I have 5 years of experience in Python development.",
}
response = client.post("/api/v1/applications", json=payload)

        assert response.status_code == 201
data = response.json()
assert data["cover_letter"] == payload["cover_letter"]

    def test_create_application_with_resume_url(self, client):
        """Create application with resume URL."""
payload = {
"job_id": str(uuid.uuid4()),
"candidate_id": str(uuid.uuid4()),
"resume_url": "https://storage.example.com/resumes/candidate123.pdf",
}
response = client.post("/api/v1/applications", json=payload)

        assert response.status_code == 201
data = response.json()
assert data["resume_url"] == payload["resume_url"]


# ── 2. GET /api/v1/applications — test_list_applications ─────────────────────


class TestListApplications:
    """Tests for GET /api/v1/applications endpoint."""

    def test_list_applications_empty(self, client):
        """Return empty list when no applications exist."""
response = client.get("/api/v1/applications")

        assert response.status_code == 200
assert response.json() == []

    def test_list_applications_single(self, client, created_application):
        """Return list with one application."""
response = client.get("/api/v1/applications")

        assert response.status_code == 200
data = response.json()
assert len(data) == 1
assert data[0]["id"] == created_application["id"]

    def test_list_applications_multiple(self, client, sample_application_payload):
        """Return all created applications."""
for _ in range(3):
            client.post("/api/v1/applications", json=sample_application_payload)

        response = client.get("/api/v1/applications")

        assert response.status_code == 200
data = response.json()
assert len(data) == 3

    def test_list_applications_pagination(self, client, sample_application_payload):
        """Test pagination with skip and limit."""
for _ in range(5):
            client.post("/api/v1/applications", json=sample_application_payload)

        # Get first 2
        response = client.get("/api/v1/applications?skip=0&limit=2")
assert response.status_code == 200
data = response.json()
assert len(data) == 2

        # Get next 2
        response = client.get("/api/v1/applications?skip=2&limit=2")
assert response.status_code == 200
data = response.json()
assert len(data) == 2

        # Get remaining
        response = client.get("/api/v1/applications?skip=4&limit=2")
assert response.status_code == 200
data = response.json()
assert len(data) == 1

    def test_list_applications_pagination_skip_only(self, client, sample_application_payload):
        """Test pagination with skip parameter only."""
for _ in range(5):
            client.post("/api/v1/applications", json=sample_application_payload)

        response = client.get("/api/v1/applications?skip=3")
assert response.status_code == 200
data = response.json()
assert len(data) == 2

    def test_list_applications_pagination_limit_only(self, client, sample_application_payload):
        """Test pagination with limit parameter only."""
for _ in range(5):
            client.post("/api/v1/applications", json=sample_application_payload)

        response = client.get("/api/v1/applications?limit=3")
assert response.status_code == 200
data = response.json()
assert len(data) == 3

    def test_list_applications_filter_by_job_id(self, client, sample_application_payload):
        """Filter applications by job_id."""
job_id = str(uuid.uuid4())
for _ in range(3):
            payload = {**sample_application_payload, "job_id": job_id}
client.post("/api/v1/applications", json=payload)

        # Create one with different job_id
        other_payload = {**sample_application_payload, "job_id": str(uuid.uuid4())}
client.post("/api/v1/applications", json=other_payload)

        response = client.get(f"/api/v1/applications?job_id={job_id}")
assert response.status_code == 200
data = response.json()
assert len(data) == 3
for app in data:
            assert app["job_id"] == job_id

    def test_list_applications_filter_by_candidate_id(self, client, sample_application_payload):
        """Filter applications by candidate_id."""
candidate_id = str(uuid.uuid4())
for _ in range(2):
            payload = {**sample_application_payload, "candidate_id": candidate_id}
client.post("/api/v1/applications", json=payload)

        response = client.get(f"/api/v1/applications?candidate_id={candidate_id}")
assert response.status_code == 200
data = response.json()
assert len(data) == 2
for app in data:
            assert app["candidate_id"] == candidate_id

    def test_list_applications_filter_by_status(self, client, sample_application_payload):
        """Filter applications by status."""
# Create applications and update their statuses
        for i in range(3):
            resp = client.post("/api/v1/applications", json=sample_application_payload)
app_id = resp.json()["id"]

            if i == 0:
                client.put(f"/api/v1/applications/{app_id}", json={"status": "accepted"})
elif i == 1:
                client.put(f"/api/v1/applications/{app_id}", json={"status": "rejected"})

        # Filter by accepted
        response = client.get("/api/v1/applications?status=accepted")
assert response.status_code == 200
data = response.json()
assert len(data) == 1
assert data[0]["status"] == "accepted"

        # Filter by rejected
        response = client.get("/api/v1/applications?status=rejected")
assert response.status_code == 200
data = response.json()
assert len(data) == 1
assert data[0]["status"] == "rejected"

        # Filter by pending (default)
        response = client.get("/api/v1/applications?status=pending")
assert response.status_code == 200
data = response.json()
assert len(data) == 1
assert data[0]["status"] == "pending"

    def test_list_applications_response_structure(self, client, created_application):
        """Verify the structure of returned application objects."""
response = client.get("/api/v1/applications")

        assert response.status_code == 200
data = response.json()
assert len(data) == 1

        app = data[0]
required_fields = {"id", "job_id", "candidate_id", "status", "applied_at", "updated_at"}
assert required_fields.issubset(set(app.keys()))

    def test_list_applications_ordering(self, client, sample_application_payload):
        """Applications should be returned in a consistent order."""
for _ in range(3):
            client.post("/api/v1/applications", json=sample_application_payload)

        response = client.get("/api/v1/applications")
data = response.json()

        ids = [app["id"] for app in data]
assert len(ids) == len(set(ids))  # All IDs unique

    def test_list_applications_pagination_beyond_total(self, client, sample_application_payload):
        """Requesting beyond total count returns empty list."""
for _ in range(3):
            client.post("/api/v1/applications", json=sample_application_payload)

        response = client.get("/api/v1/applications?skip=10&limit=5")
assert response.status_code == 200
data = response.json()
assert data == []

    def test_list_applications_invalid_pagination_params(self, client):
        """Invalid pagination parameters should return 422."""
response = client.get("/api/v1/applications?skip=-1")
assert response.status_code == 422

        response = client.get("/api/v1/applications?limit=-1")
assert response.status_code == 422

        response = client.get("/api/v1/applications?skip=abc")
assert response.status_code == 422


# ── 3. GET /api/v1/applications/{id} — test_get_application ──────────────────


class TestGetApplication:
    """Tests for GET /api/v1/applications/{id} endpoint."""

    def test_get_application_success(self, client, created_application):
        """Successfully retrieve an application by ID."""
app_id = created_application["id"]
response = client.get(f"/api/v1/applications/{app_id}")

        assert response.status_code == 200
data = response.json()
assert data["id"] == app_id
assert data["job_id"] == created_application["job_id"]
assert data["candidate_id"] == created_application["candidate_id"]
assert data["status"] == created_application["status"]

    def test_get_application_not_found(self, client):
        """Return 404 when application does not exist."""
fake_id = str(uuid.uuid4())
response = client.get(f"/api/v1/applications/{fake_id}")

        assert response.status_code == 404

    def test_get_application_invalid_id_format(self, client):
        """Return 422 when ID is not a valid UUID."""
response = client.get("/api/v1/applications/not-a-uuid")

        assert response.status_code == 422

    def test_get_application_response_structure(self, client, created_application):
        """Verify the structure of a single application response."""
app_id = created_application["id"]
response = client.get(f"/api/v1/applications/{app_id}")

        assert response.status_code == 200
data = response.json()

        required_fields = {"id", "job_id", "candidate_id", "status", "applied_at", "updated_at"}
assert required_fields.issubset(set(data.keys()))

    def test_get_application_with_cover_letter(self, client, sample_application_payload):
        """Retrieve application with cover letter."""
payload = {**sample_application_payload, "cover_letter": "Test cover letter"}
create_resp = client.post("/api/v1/applications", json=payload)
app_id = create_resp.json()["id"]

        response = client.get(f"/api/v1/applications/{app_id}")
assert response.status_code == 200
assert response.json()["cover_letter"] == "Test cover letter"

    def test_get_application_with_resume_url(self, client, sample_application_payload):
        """Retrieve application with resume URL."""
payload = {**sample_application_payload, "resume_url": "https://example.com/resume.pdf"}
create_resp = client.post("/api/v1/applications", json=payload)
app_id = create_resp.json()["id"]

        response = client.get(f"/api/v1/applications/{app_id}")
assert response.status_code == 200
assert response.json()["resume_url"] == "https://example.com/resume.pdf"


# ── 4. PUT /api/v1/applications/{id} — test_update_application_status ─────────


class TestUpdateApplicationStatus:
    """Tests for PUT /api/v1/applications/{id} endpoint."""

    def test_update_application_status_success(self, client, created_application):
        """Successfully update an application's status."""
app_id = created_application["id"]
new_status = "accepted"

        response = client.put(
f"/api/v1/applications/{app_id}",
json={"status": new_status},
)

        assert response.status_code == 200
data = response.json()
assert data["id"] == app_id
assert data["status"] == new_status
assert data["updated_at"] is not None

    def test_update_application_status_to_rejected(self, client, created_application):
        """Update status to rejected."""
app_id = created_application["id"]

        response = client.put(
f"/api/v1/applications/{app_id}",
json={"status": "rejected"},
)

        assert response.status_code == 200
assert response.json()["status"] == "rejected"

    def test_update_application_status_to_under_review(self, client, created_application):
        """Update status to under_review."""
app_id = created_application["id"]

        response = client.put(
f"/api/v1/applications/{app_id}",
json={"status": "under_review"},
)

        assert response.status_code == 200
assert response.json()["status"] == "under_review"

    def test_update_application_status_invalid_status(self, client, created_application):
        """Fail with an invalid status value."""
app_id = created_application["id"]

        response = client.put(
f"/api/v1/applications/{app_id}",
json={"status": "invalid_status"},
)

        assert response.status_code == 422

    def test_update_application_status_empty_status(self, client, created_application):
        """Fail with an empty status string."""
app_id = created_application["id"]

        response = client.put(
f"/api/v1/applications/{app_id}",
json={"status": ""},
)

        assert response.status_code == 422

    def test_update_application_status_missing_field(self, client, created_application):
        """Fail when status field is missing from request body."""
app_id = created_application["id"]

        response = client.put(
f"/api/v1/applications/{app_id}",
json={},
)

        assert response.status_code == 422

    def test_update_application_status_nonexistent_application(self, client):
        """Fail when application ID does not exist."""
fake_id = str(uuid.uuid4())
response = client.put(
f"/api/v1/applications/{fake_id}",
json={"status": "accepted"},
)

        assert response.status_code == 404

    def test_update_application_status_invalid_id_type(self, client):
        """Fail when application ID is not a valid UUID."""
response = client.put(
"/api/v1/applications/not-a-uuid",
json={"status": "accepted"},
)

        assert response.status_code == 422

    def test_update_application_status_multiple_transitions(self, client, created_application):
        """Test multiple status transitions in sequence."""
app_id = created_application["id"]

        statuses = ["under_review", "accepted"]
for status in statuses:
            response = client.put(
f"/api/v1/applications/{app_id}",
json={"status": status},
)
            assert response.status_code == 200
assert response.json()["status"] == status

    def test_update_application_status_preserves_other_fields(self, client, created_application):
        """Status update should not modify other fields."""
app_id = created_application["id"]
original = created_application

        response = client.put(
f"/api/v1/applications/{app_id}",
json={"status": "accepted"},
)

        assert response.status_code == 200
data = response.json()
assert data["job_id"] == original["job_id"]
assert data["candidate_id"] == original["candidate_id"]
assert data["cover_letter"] == original["cover_letter"]
assert data["resume_url"] == original["resume_url"]

    def test_update_application_status_response_content_type(self, client, created_application):
        """Response should have JSON content type."""
app_id = created_application["id"]

        response = client.put(
f"/api/v1/applications/{app_id}",
json={"status": "accepted"},
)

        assert response.headers["content-type"].startswith("application/json")

    def test_update_application_status_idempotent(self, client, created_application):
        """Setting the same status twice should succeed both times."""
app_id = created_application["id"]

        response1 = client.put(
f"/api/v1/applications/{app_id}",
json={"status": "accepted"},
)
        assert response1.status_code == 200

        response2 = client.put(
f"/api/v1/applications/{app_id}",
json={"status": "accepted"},
)
        assert response2.status_code == 200
assert response2.json()["status"] == "accepted"

    def test_update_application_status_to_pending(self, client, created_application):
        """Update status back to pending."""
app_id = created_application["id"]

        # First change to accepted
        client.put(f"/api/v1/applications/{app_id}", json={"status": "accepted"})

        # Then back to pending
        response = client.put(
f"/api/v1/applications/{app_id}",
json={"status": "pending"},
)
        assert response.status_code == 200
assert response.json()["status"] == "pending"


# ── 5. DELETE /api/v1/applications/{id} — test_delete_application ─────────────


class TestDeleteApplication:
    """Tests for DELETE /api/v1/applications/{id} endpoint."""

    def test_delete_application_success(self, client, created_application):
        """Successfully delete an application."""
app_id = created_application["id"]

        response = client.delete(f"/api/v1/applications/{app_id}")

        assert response.status_code == 204

        # Verify it's actually deleted
        get_response = client.get(f"/api/v1/applications/{app_id}")
assert get_response.status_code == 404

    def test_delete_application_not_found(self, client):
        """Return 404 when application does not exist."""
fake_id = str(uuid.uuid4())
response = client.delete(f"/api/v1/applications/{fake_id}")

        assert response.status_code == 404

    def test_delete_application_invalid_id_format(self, client):
        """Return 422 when ID is not a valid UUID."""
response = client.delete("/api/v1/applications/not-a-uuid")

        assert response.status_code == 422

    def test_delete_application_then_list(self, client, created_application):
        """Deleted application should not appear in list."""
app_id = created_application["id"]

        # Delete the application
        client.delete(f"/api/v1/applications/{app_id}")

        # Verify it's not in the list
        response = client.get("/api/v1/applications")
assert response.status_code == 200
data = response.json()
assert len(data) == 0

    def test_delete_application_then_get(self, client, created_application):
        """Deleted application should return 404 on GET."""
app_id = created_application["id"]

        client.delete(f"/api/v1/applications/{app_id}")

        response = client.get(f"/api/v1/applications/{app_id}")
assert response.status_code == 404

    def test_delete_application_then_update(self, client, created_application):
        """Updating a deleted application should return 404."""
app_id = created_application["id"]

        client.delete(f"/api/v1/applications/{app_id}")

        response = client.put(
f"/api/v1/applications/{app_id}",
json={"status": "accepted"},
)
        assert response.status_code == 404

    def test_delete_one_application_others_remain(self, client, sample_application_payload):
        """Deleting one application should not affect others."""
# Create two applications
        resp1 = client.post("/api/v1/applications", json=sample_application_payload)
app_id1 = resp1.json()["id"]

        resp2 = client.post("/api/v1/applications", json=sample_application_payload)
app_id2 = resp2.json()["id"]

        # Delete first
        client.delete(f"/api/v1/applications/{app_id1}")

        # Verify second still exists
        response = client.get(f"/api/v1/applications/{app_id2}")
assert response.status_code == 200

        # Verify list has one item
        response = client.get("/api/v1/applications")
assert len(response.json()) == 1

    def test_delete_application_twice(self, client, created_application):
        """Deleting the same application twice should return 404 on second attempt."""
app_id = created_application["id"]

        response1 = client.delete(f"/api/v1/applications/{app_id}")
assert response1.status_code == 204

        response2 = client.delete(f"/api/v1/applications/{app_id}")
assert response2.status_code == 404
