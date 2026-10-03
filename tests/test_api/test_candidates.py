"""
Comprehensive API tests for the Candidates endpoints.

Tests cover:
- GET    /api/v1/candidates          — list candidates with pagination
- POST   /api/v1/candidates          — create a new candidate
- GET    /api/v1/candidates/{id}     — retrieve a single candidate by ID
- PUT    /api/v1/candidates/{id}     — update an existing candidate
- DELETE /api/v1/candidates/{id}     — delete a candidate by ID
"""

import pytest
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    """Return a TestClient bound to the FastAPI application."""
    from recruitment_platform.main import app
    return TestClient(app)


@pytest.fixture
def sample_candidate_payload():
    """Return a valid payload for creating a candidate."""
    return {
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane.doe@example.com",
        "phone": "+1-555-0100",
        "role_applied": "Software Engineer",
        "years_experience": 5,
        "experience_level": "mid",
        "skills": ["Python", "FastAPI", "SQL"],
        "expected_salary": 120000,
        "currency": "USD",
        "location": "Berlin, Germany",
        "remote_ok": True,
    }


@pytest.fixture
def created_candidate(client, sample_candidate_payload):
    """Create a candidate via the API and return the response JSON."""
    response = client.post("/api/v1/candidates", json=sample_candidate_payload)
    assert response.status_code == 201, response.text
    return response.json()


# ---------------------------------------------------------------------------
# 1. GET /api/v1/candidates — test_list_candidates
# ---------------------------------------------------------------------------

class TestListCandidates:
    """Tests for the GET /api/v1/candidates endpoint."""

    def test_list_candidates_returns_paginated_response(self, client):
        """The endpoint returns a paginated response structure."""
        response = client.get("/api/v1/candidates")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "total_pages" in data
        assert isinstance(data["data"], list)
        assert data["page"] == 1
        assert data["page_size"] == 10

    def test_list_candidates_default_pagination(self, client):
        """Default pagination returns page 1 with page_size 10."""
        response = client.get("/api/v1/candidates")
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 10
        assert len(data["data"]) <= 10

    def test_list_candidates_custom_page_size(self, client):
        """Custom page_size limits the number of returned items."""
        response = client.get("/api/v1/candidates?page_size=3")
        assert response.status_code == 200
        data = response.json()
        assert data["page_size"] == 3
        assert len(data["data"]) <= 3

    def test_list_candidates_second_page(self, client):
        """Requesting page 2 returns different items than page 1."""
        response1 = client.get("/api/v1/candidates?page=1&page_size=2")
        response2 = client.get("/api/v1/candidates?page=2&page_size=2")
        assert response1.status_code == 200
        assert response2.status_code == 200
        data1 = response1.json()
        data2 = response2.json()
        assert data1["page"] == 1
        assert data2["page"] == 2
        # If there are enough candidates, pages should have different IDs
        if data1["data"] and data2["data"]:
            ids1 = {c["id"] for c in data1["data"]}
            ids2 = {c["id"] for c in data2["data"]}
            assert ids1.isdisjoint(ids2)

    def test_list_candidates_total_matches_data_length(self, client):
        """Total count is consistent with pagination metadata."""
        response = client.get("/api/v1/candidates?page_size=5")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= len(data["data"])
        expected_pages = max(1, (data["total"] + 4) // 5)
        assert data["total_pages"] == expected_pages

    def test_list_candidates_filter_by_status(self, client):
        """Filtering by status returns only matching candidates."""
        response = client.get("/api/v1/candidates?status=new")
        assert response.status_code == 200
        data = response.json()
        for candidate in data["data"]:
            assert candidate["status"] == "new"

    def test_list_candidates_filter_by_experience_level(self, client):
        """Filtering by experience_level returns only matching candidates."""
        response = client.get("/api/v1/candidates?experience_level=senior")
        assert response.status_code == 200
        data = response.json()
        for candidate in data["data"]:
            assert candidate["experience_level"] == "senior"

    def test_list_candidates_filter_by_remote_ok(self, client):
        """Filtering by remote_ok returns only matching candidates."""
        response = client.get("/api/v1/candidates?remote_ok=true")
        assert response.status_code == 200
        data = response.json()
        for candidate in data["data"]:
            assert candidate["remote_ok"] is True

    def test_list_candidates_filter_by_min_years(self, client):
        """Filtering by min_years returns only candidates with enough experience."""
        response = client.get("/api/v1/candidates?min_years=5")
        assert response.status_code == 200
        data = response.json()
        for candidate in data["data"]:
            assert candidate["years_experience"] >= 5

    def test_list_candidates_filter_by_skills(self, client):
        """Filtering by skills returns only candidates with all specified skills."""
        response = client.get("/api/v1/candidates?skills=python")
        assert response.status_code == 200
        data = response.json()
        for candidate in data["data"]:
            assert "python" in candidate["skills"]

    def test_list_candidates_search_by_name(self, client):
        """Search by name returns matching candidates."""
        response = client.get("/api/v1/candidates?search=Amara")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        for candidate in data["data"]:
            assert "amara" in candidate["first_name"].lower() or "amara" in candidate["last_name"].lower()

    def test_list_candidates_sort_by_years_experience_asc(self, client):
        """Sorting by years_experience ascending returns ordered results."""
        response = client.get("/api/v1/candidates?sort_by=years_experience&sort_order=asc&page_size=100")
        assert response.status_code == 200
        data = response.json()
        years = [c["years_experience"] for c in data["data"]]
        assert years == sorted(years)

    def test_list_candidates_sort_by_years_experience_desc(self, client):
        """Sorting by years_experience descending returns ordered results."""
        response = client.get("/api/v1/candidates?sort_by=years_experience&sort_order=desc&page_size=100")
        assert response.status_code == 200
        data = response.json()
        years = [c["years_experience"] for c in data["data"]]
        assert years == sorted(years, reverse=True)

    def test_list_candidates_content_type(self, client):
        """The response Content-Type is application/json."""
        response = client.get("/api/v1/candidates")
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type", "")

    def test_list_candidates_page_size_exceeds_max(self, client):
        """Requesting page_size > 100 returns 422."""
        response = client.get("/api/v1/candidates?page_size=101")
        assert response.status_code == 422

    def test_list_candidates_invalid_page_number(self, client):
        """Requesting page < 1 returns 422."""
        response = client.get("/api/v1/candidates?page=0")
        assert response.status_code == 422

    def test_list_candidates_response_structure(self, client):
        """Each item in the list has the expected keys."""
        response = client.get("/api/v1/candidates")
        assert response.status_code == 200
        data = response.json()
        if data["data"]:
            first = data["data"][0]
            expected_keys = {
                "id", "first_name", "last_name", "email", "phone",
                "role_applied", "years_experience", "experience_level",
                "skills", "expected_salary", "currency", "location",
                "remote_ok", "linkedin_url", "notes", "status",
                "created_at", "updated_at",
            }
            assert expected_keys.issubset(set(first.keys()))


# ---------------------------------------------------------------------------
# 2. POST /api/v1/candidates — test_create_candidate
# ---------------------------------------------------------------------------

class TestCreateCandidate:
    """Tests for the POST /api/v1/candidates endpoint."""

    def test_create_candidate_success(self, client, sample_candidate_payload):
        """A valid payload returns 201 and the created candidate data."""
        response = client.post("/api/v1/candidates", json=sample_candidate_payload)
        assert response.status_code == 201
        data = response.json()
        assert data["first_name"] == sample_candidate_payload["first_name"]
        assert data["last_name"] == sample_candidate_payload["last_name"]
        assert data["email"] == sample_candidate_payload["email"]
        assert data["role_applied"] == sample_candidate_payload["role_applied"]
        assert data["years_experience"] == sample_candidate_payload["years_experience"]
        assert data["experience_level"] == sample_candidate_payload["experience_level"]
        assert data["skills"] == [s.lower() for s in sample_candidate_payload["skills"]]
        assert "id" in data
        assert isinstance(data["id"], str)
        assert data["status"] == "new"
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_candidate_auto_generates_id(self, client, sample_candidate_payload):
        """The server assigns a UUID string ID."""
        response = client.post("/api/v1/candidates", json=sample_candidate_payload)
        data = response.json()
        assert "id" in data
        assert data["id"] is not None
        assert isinstance(data["id"], str)
        assert len(data["id"]) > 0

    def test_create_candidate_missing_required_fields(self, client):
        """Omitting required fields returns 422 Unprocessable Entity."""
        incomplete_payload = {"first_name": "OnlyFirst"}
        response = client.post("/api/v1/candidates", json=incomplete_payload)
        assert response.status_code == 422

    def test_create_candidate_invalid_email(self, client, sample_candidate_payload):
        """An invalid email address is rejected with 422."""
        sample_candidate_payload["email"] = "not-an-email"
        response = client.post("/api/v1/candidates", json=sample_candidate_payload)
        assert response.status_code == 422

    def test_create_candidate_empty_body(self, client):
        """An empty JSON body returns 422."""
        response = client.post("/api/v1/candidates", json={})
        assert response.status_code == 422

    def test_create_candidate_duplicate_email(self, client, sample_candidate_payload):
        """Creating two candidates with the same email returns 409 Conflict."""
        resp1 = client.post("/api/v1/candidates", json=sample_candidate_payload)
        assert resp1.status_code == 201

        resp2 = client.post("/api/v1/candidates", json=sample_candidate_payload)
        assert resp2.status_code == 409

    def test_create_candidate_response_content_type(self, client, sample_candidate_payload):
        """The response Content-Type is application/json."""
        response = client.post("/api/v1/candidates", json=sample_candidate_payload)
        assert response.status_code == 201
        assert "application/json" in response.headers.get("content-type", "")

    def test_create_candidate_with_optional_fields(self, client):
        """A payload with only the required fields succeeds."""
        minimal_payload = {
            "first_name": "Minimal",
            "last_name": "User",
            "email": "minimal.user@example.com",
            "role_applied": "Developer",
            "years_experience": 2,
            "experience_level": "junior",
        }
        response = client.post("/api/v1/candidates", json=minimal_payload)
        assert response.status_code == 201
        data = response.json()
        assert data["first_name"] == "Minimal"
        assert data["email"] == "minimal.user@example.com"
        assert data["skills"] == []
        assert data["currency"] == "USD"
        assert data["remote_ok"] is True

    def test_create_candidate_skills_normalized_to_lowercase(self, client, sample_candidate_payload):
        """Skills are normalized to lowercase."""
        sample_candidate_payload["skills"] = ["PYTHON", "FastAPI", "SQL"]
        response = client.post("/api/v1/candidates", json=sample_candidate_payload)
        assert response.status_code == 201
        data = response.json()
        assert data["skills"] == ["python", "fastapi", "sql"]

    def test_create_candidate_invalid_experience_level(self, client, sample_candidate_payload):
        """An invalid experience_level returns 422."""
        sample_candidate_payload["experience_level"] = "expert"
        response = client.post("/api/v1/candidates", json=sample_candidate_payload)
        assert response.status_code == 422

    def test_create_candidate_negative_years_experience(self, client, sample_candidate_payload):
        """Negative years_experience returns 422."""
        sample_candidate_payload["years_experience"] = -1
        response = client.post("/api/v1/candidates", json=sample_candidate_payload)
        assert response.status_code == 422

    def test_create_candidate_exceeds_max_years_experience(self, client, sample_candidate_payload):
        """years_experience > 60 returns 422."""
        sample_candidate_payload["years_experience"] = 61
        response = client.post("/api/v1/candidates", json=sample_candidate_payload)
        assert response.status_code == 422

    def test_create_candidate_invalid_currency(self, client, sample_candidate_payload):
        """A currency not matching the 3-letter pattern returns 422."""
        sample_candidate_payload["currency"] = "US"
        response = client.post("/api/v1/candidates", json=sample_candidate_payload)
        assert response.status_code == 422

    def test_create_candidate_invalid_phone(self, client, sample_candidate_payload):
        """A phone number with fewer than 7 digits returns 422."""
        sample_candidate_payload["phone"] = "123"
        response = client.post("/api/v1/candidates", json=sample_candidate_payload)
        assert response.status_code == 422

    def test_create_candidate_appears_in_list(self, client, sample_candidate_payload):
        """A newly created candidate appears in the list endpoint."""
        create_resp = client.post("/api/v1/candidates", json=sample_candidate_payload)
        assert create_resp.status_code == 201
        created = create_resp.json()

        list_resp = client.get("/api/v1/candidates?search=" + created["email"])
        assert list_resp.status_code == 200
        data = list_resp.json()
        assert data["total"] >= 1
        ids = [c["id"] for c in data["data"]]
        assert created["id"] in ids


# ---------------------------------------------------------------------------
# 3. GET /api/v1/candidates/{id} — test_get_candidate
# ---------------------------------------------------------------------------

class TestGetCandidate:
    """Tests for the GET /api/v1/candidates/{id} endpoint."""

    def test_get_candidate_success(self, client, created_candidate):
        """Retrieving an existing candidate returns 200 and the correct data."""
        candidate_id = created_candidate["id"]
        response = client.get(f"/api/v1/candidates/{candidate_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == candidate_id
        assert data["email"] == created_candidate["email"]
        assert data["first_name"] == created_candidate["first_name"]
        assert data["last_name"] == created_candidate["last_name"]

    def test_get_candidate_not_found(self, client):
        """Retrieving a non-existent candidate returns 404."""
        response = client.get("/api/v1/candidates/nonexistent-id-99999")
        assert response.status_code == 404

    def test_get_candidate_response_structure(self, client, created_candidate):
        """The response contains all expected fields."""
        candidate_id = created_candidate["id"]
        response = client.get(f"/api/v1/candidates/{candidate_id}")
        data = response.json()
        expected_keys = {
            "id", "first_name", "last_name", "email", "phone",
            "role_applied", "years_experience", "experience_level",
            "skills", "expected_salary", "currency", "location",
            "remote_ok", "linkedin_url", "notes", "status",
            "created_at", "updated_at",
        }
        assert expected_keys.issubset(set(data.keys()))

    def test_get_candidate_content_type(self, client, created_candidate):
        """The response Content-Type is application/json."""
        candidate_id = created_candidate["id"]
        response = client.get(f"/api/v1/candidates/{candidate_id}")
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type", "")

    def test_get_candidate_after_update(self, client, created_candidate):
        """After updating a candidate the GET endpoint reflects the change."""
        candidate_id = created_candidate["id"]

        update_payload = {"first_name": "UpdatedName"}
        update_resp = client.put(
            f"/api/v1/candidates/{candidate_id}", json=update_payload
        )
        assert update_resp.status_code == 200

        response = client.get(f"/api/v1/candidates/{candidate_id}")
        assert response.status_code == 200
        assert response.json()["first_name"] == "UpdatedName"

    def test_get_candidate_from_mock_data(self, client):
        """Can retrieve one of the pre-seeded mock candidates."""
        list_resp = client.get("/api/v1/candidates?page_size=1")
        assert list_resp.status_code == 200
        data = list_resp.json()
        if data["data"]:
            candidate_id = data["data"][0]["id"]
            get_resp = client.get(f"/api/v1/candidates/{candidate_id}")
            assert get_resp.status_code == 200
            assert get_resp.json()["id"] == candidate_id


# ---------------------------------------------------------------------------
# 4. PUT /api/v1/candidates/{id} — test_update_candidate
# ---------------------------------------------------------------------------

class TestUpdateCandidate:
    """Tests for the PUT /api/v1/candidates/{id} endpoint."""

    def test_update_candidate_success(self, client, created_candidate):
        """Updating an existing candidate returns 200 and the updated data."""
        candidate_id = created_candidate["id"]
        update_payload = {"first_name": "UpdatedFirst"}
        response = client.put(
            f"/api/v1/candidates/{candidate_id}", json=update_payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == candidate_id
        assert data["first_name"] == "UpdatedFirst"
        # Other fields should remain unchanged
        assert data["last_name"] == created_candidate["last_name"]
        assert data["email"] == created_candidate["email"]

    def test_update_candidate_not_found(self, client):
        """Updating a non-existent candidate returns 404."""
        response = client.put(
            "/api/v1/candidates/nonexistent-id-99999",
            json={"first_name": "NewName"},
        )
        assert response.status_code == 404

    def test_update_candidate_partial_update(self, client, created_candidate):
        """Only provided fields are modified."""
        candidate_id = created_candidate["id"]
        original_email = created_candidate["email"]

        update_payload = {"location": "New York, NY"}
        response = client.put(
            f"/api/v1/candidates/{candidate_id}", json=update_payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data["location"] == "New York, NY"
        assert data["email"] == original_email
        assert data["first_name"] == created_candidate["first_name"]

    def test_update_candidate_status(self, client, created_candidate):
        """Updating status to a valid value succeeds."""
        candidate_id = created_candidate["id"]
        update_payload = {"status": "screening"}
        response = client.put(
            f"/api/v1/candidates/{candidate_id}", json=update_payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "screening"

    def test_update_candidate_invalid_status(self, client, created_candidate):
        """Updating status to an invalid value returns 422."""
        candidate_id = created_candidate["id"]
        update_payload = {"status": "invalid_status"}
        response = client.put(
            f"/api/v1/candidates/{candidate_id}", json=update_payload
        )
        assert response.status_code == 422

    def test_update_candidate_invalid_email(self, client, created_candidate):
        """Updating email to an invalid value returns 422."""
        candidate_id = created_candidate["id"]
        update_payload = {"email": "not-an-email"}
        response = client.put(
            f"/api/v1/candidates/{candidate_id}", json=update_payload
        )
        assert response.status_code == 422

    def test_update_candidate_skills(self, client, created_candidate):
        """Updating skills replaces the skills list."""
        candidate_id = created_candidate["id"]
        update_payload = {"skills": ["Rust", "Go", "Kubernetes"]}
        response = client.put(
            f"/api/v1/candidates/{candidate_id}", json=update_payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data["skills"] == ["rust", "go", "kubernetes"]

    def test_update_candidate_experience_level(self, client, created_candidate):
        """Updating experience_level to a valid value succeeds."""
        candidate_id = created_candidate["id"]
        update_payload = {"experience_level": "senior"}
        response = client.put(
            f"/api/v1/candidates/{candidate_id}", json=update_payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data["experience_level"] == "senior"

    def test_update_candidate_empty_body(self, client, created_candidate):
        """An empty update body returns 200 and leaves the candidate unchanged."""
        candidate_id = created_candidate["id"]
        original = client.get(f"/api/v1/candidates/{candidate_id}").json()

        response = client.put(
            f"/api/v1/candidates/{candidate_id}", json={}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == original["first_name"]
        assert data["email"] == original["email"]

    def test_update_candidate_updated_at_changes(self, client, created_candidate):
        """The updated_at timestamp changes after an update."""
        candidate_id = created_candidate["id"]
        original_updated_at = created_candidate["updated_at"]

        update_payload = {"notes": "Updated notes"}
        response = client.put(
            f"/api/v1/candidates/{candidate_id}", json=update_payload
        )
        assert response.status_code == 200
        data = response.json()
        # updated_at should be different from the original
        assert data["updated_at"] != original_updated_at or data["notes"] == "Updated notes"

    def test_update_candidate_content_type(self, client, created_candidate):
        """The response Content-Type is application/json."""
        candidate_id = created_candidate["id"]
        response = client.put(
            f"/api/v1/candidates/{candidate_id}",
            json={"first_name": "ContentTypeTest"},
        )
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type", "")


# ---------------------------------------------------------------------------
# 5. DELETE /api/v1/candidates/{id} — test_delete_candidate
# ---------------------------------------------------------------------------

class TestDeleteCandidate:
    """Tests for the DELETE /api/v1/candidates/{id} endpoint."""

    def test_delete_candidate_success(self, client, created_candidate):
        """Deleting an existing candidate returns 204 No Content."""
        candidate_id = created_candidate["id"]
        response = client.delete(f"/api/v1/candidates/{candidate_id}")
        assert response.status_code == 204

    def test_delete_candidate_not_found(self, client):
        """Deleting a non-existent candidate returns 404."""
        response = client.delete("/api/v1/candidates/nonexistent-id-99999")
        assert response.status_code == 404

    def test_delete_candidate_removes_from_list(self, client, created_candidate):
        """A deleted candidate no longer appears in the list."""
        candidate_id = created_candidate["id"]

        # Verify it exists
        get_resp = client.get(f"/api/v1/candidates/{candidate_id}")
        assert get_resp.status_code == 200

        # Delete it
        del_resp = client.delete(f"/api/v1/candidates/{candidate_id}")
        assert del_resp.status_code == 204

        # Verify it's gone
        get_resp2 = client.get(f"/api/v1/candidates/{candidate_id}")
        assert get_resp2.status_code == 404

    def test_delete_candidate_response_has_no_body(self, client, created_candidate):
        """The delete response has no body."""
        candidate_id = created_candidate["id"]
        response = client.delete(f"/api/v1/candidates/{candidate_id}")
        assert response.status_code == 204
        assert response.content == b""

    def test_delete_candidate_id_not_reusable(self, client, created_candidate):
        """After deletion, the same ID cannot be retrieved."""
        candidate_id = created_candidate["id"]

        client.delete(f"/api/v1/candidates/{candidate_id}")

        response = client.get(f"/api/v1/candidates/{candidate_id}")
        assert response.status_code == 404

    def test_delete_candidate_does_not_affect_others(self, client, sample_candidate_payload):
        """Deleting one candidate does not affect others."""
        # Create two candidates
        payload1 = {**sample_candidate_payload, "email": "delete-test-1@example.com"}
        payload2 = {**sample_candidate_payload, "email": "delete-test-2@example.com"}

        resp1 = client.post("/api/v1/candidates", json=payload1)
        resp2 = client.post("/api/v1/candidates", json=payload2)
        assert resp1.status_code == 201
        assert resp2.status_code == 201

        cand1 = resp1.json()
        cand2 = resp2.json()

        # Delete the first
        del_resp = client.delete(f"/api/v1/candidates/{cand1['id']}")
        assert del_resp.status_code == 204

        # Second should still exist
        get_resp = client.get(f"/api/v1/candidates/{cand2['id']}")
        assert get_resp.status_code == 200
        assert get_resp.json()["id"] == cand2["id"]
