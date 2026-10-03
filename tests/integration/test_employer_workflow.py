"""
Integration tests for the employer workflow.

Covers:
- Full employer lifecycle (create → update → delete)
- Employer job flow (create employer → create job → get analytics)
- Employer branding (create employer → analyze brand → suggest improvements)
"""

import pytest
import requests
from typing import Any, Dict, Generator

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

BASE_URL = "http://localhost:8000/api/v1"


@pytest.fixture
def employer_payload() -> Dict[str, Any]:
    """Return a valid employer creation payload."""
    return {
        "name": "Test Employer Inc.",
        "industry": "Technology",
        "size": "50-200",
        "website": "https://test-employer.example.com",
        "description": "A test employer for integration testing.",
        "location": "San Francisco, CA",
        "contact_email": "hr@test-employer.example.com",
    }


@pytest.fixture
def created_employer(employer_payload: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
    """Create an employer and yield the response data; clean up after the test."""
    response = requests.post(f"{BASE_URL}/employers", json=employer_payload)
    assert response.status_code == 201, f"Failed to create employer: {response.text}"
    employer = response.json()
    yield employer

    # Cleanup: delete the employer if it still exists
    employer_id = employer.get("id") or employer.get("employer_id")
    if employer_id:
        requests.delete(f"{BASE_URL}/employers/{employer_id}")


@pytest.fixture
def job_payload() -> Dict[str, Any]:
    """Return a valid job creation payload."""
    return {
        "title": "Senior Software Engineer",
        "description": "Build and maintain scalable backend services.",
        "requirements": ["Python", "FastAPI", "PostgreSQL", "Docker"],
        "location": "Remote",
        "salary_min": 120000,
        "salary_max": 180000,
        "employment_type": "full-time",
        "department": "Engineering",
    }


@pytest.fixture
def branding_payload() -> Dict[str, Any]:
    """Return a valid branding analysis payload."""
    return {
        "company_values": ["innovation", "transparency", "work-life balance"],
        "target_audience": "senior software engineers",
        "brand_voice": "professional yet approachable",
        "current_messaging": "We are a fast-growing tech company.",
    }


# ---------------------------------------------------------------------------
# 1. Full Employer Lifecycle
# ---------------------------------------------------------------------------

class TestFullEmployerLifecycle:
    """Test the complete employer lifecycle: create → update → delete."""

    def test_create_employer(self, employer_payload: Dict[str, Any]) -> None:
        """Verify that an employer can be created successfully."""
        response = requests.post(f"{BASE_URL}/employers", json=employer_payload)

        assert response.status_code == 201
        data = response.json()
        assert "id" in data or "employer_id" in data
        assert data["name"] == employer_payload["name"]
        assert data["industry"] == employer_payload["industry"]
        assert data["website"] == employer_payload["website"]

    def test_update_employer(self, created_employer: Dict[str, Any]) -> None:
        """Verify that an existing employer can be updated."""
        employer_id = created_employer.get("id") or created_employer.get("employer_id")
        update_data = {
            "name": "Updated Test Employer Inc.",
            "size": "200-500",
            "description": "An updated description for the test employer.",
        }

        response = requests.patch(
            f"{BASE_URL}/employers/{employer_id}", json=update_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["size"] == update_data["size"]
        assert data["description"] == update_data["description"]

    def test_delete_employer(self, created_employer: Dict[str, Any]) -> None:
        """Verify that an employer can be deleted."""
        employer_id = created_employer.get("id") or created_employer.get("employer_id")

        response = requests.delete(f"{BASE_URL}/employers/{employer_id}")
        assert response.status_code in (200, 204)

        # Verify the employer no longer exists
        get_response = requests.get(f"{BASE_URL}/employers/{employer_id}")
        assert get_response.status_code == 404

    def test_full_lifecycle(self, employer_payload: Dict[str, Any]) -> None:
        """End-to-end: create → update → delete in a single flow."""
        # Create
        create_resp = requests.post(f"{BASE_URL}/employers", json=employer_payload)
        assert create_resp.status_code == 201
        employer = create_resp.json()
        employer_id = employer.get("id") or employer.get("employer_id")
        assert employer_id is not None

        # Update
        update_resp = requests.patch(
            f"{BASE_URL}/employers/{employer_id}",
            json={"name": "Lifecycle Test Employer"},
        )
        assert update_resp.status_code == 200
        assert update_resp.json()["name"] == "Lifecycle Test Employer"

        # Delete
        delete_resp = requests.delete(f"{BASE_URL}/employers/{employer_id}")
        assert delete_resp.status_code in (200, 204)

        # Confirm deletion
        get_resp = requests.get(f"{BASE_URL}/employers/{employer_id}")
        assert get_resp.status_code == 404


# ---------------------------------------------------------------------------
# 2. Employer Job Flow
# ---------------------------------------------------------------------------

class TestEmployerJobFlow:
    """Test the employer job flow: create employer → create job → get analytics."""

    def test_create_job_for_employer(
        self, created_employer: Dict[str, Any], job_payload: Dict[str, Any]
    ) -> None:
        """Verify that a job can be created for an existing employer."""
        employer_id = created_employer.get("id") or created_employer.get("employer_id")
        job_payload_with_employer = {**job_payload, "employer_id": employer_id}

        response = requests.post(f"{BASE_URL}/jobs", json=job_payload_with_employer)

        assert response.status_code == 201
        data = response.json()
        assert "id" in data or "job_id" in data
        assert data["title"] == job_payload["title"]
        assert data["employer_id"] == employer_id

    def test_get_employer_analytics(
        self, created_employer: Dict[str, Any], job_payload: Dict[str, Any]
    ) -> None:
        """Verify that analytics can be retrieved for an employer with jobs."""
        employer_id = created_employer.get("id") or created_employer.get("employer_id")

        # Create a job first so analytics has data
        job_payload_with_employer = {**job_payload, "employer_id": employer_id}
        job_resp = requests.post(f"{BASE_URL}/jobs", json=job_payload_with_employer)
        assert job_resp.status_code == 201

        # Fetch analytics
        response = requests.get(f"{BASE_URL}/employers/{employer_id}/analytics")

        assert response.status_code == 200
        data = response.json()
        assert "total_jobs" in data or "job_count" in data
        assert "employer_id" in data or "employer" in data

    def test_full_job_flow(
        self, employer_payload: Dict[str, Any], job_payload: Dict[str, Any]
    ) -> None:
        """End-to-end: create employer → create job → get analytics."""
        # Step 1: Create employer
        emp_resp = requests.post(f"{BASE_URL}/employers", json=employer_payload)
        assert emp_resp.status_code == 201
        employer = emp_resp.json()
        employer_id = employer.get("id") or employer.get("employer_id")

        # Step 2: Create job
        job_resp = requests.post(
            f"{BASE_URL}/jobs",
            json={**job_payload, "employer_id": employer_id},
        )
        assert job_resp.status_code == 201
        job = job_resp.json()
        assert job["employer_id"] == employer_id

        # Step 3: Get analytics
        analytics_resp = requests.get(f"{BASE_URL}/employers/{employer_id}/analytics")
        assert analytics_resp.status_code == 200
        analytics = analytics_resp.json()
        assert analytics is not None

        # Cleanup
        requests.delete(f"{BASE_URL}/employers/{employer_id}")


# ---------------------------------------------------------------------------
# 3. Employer Branding
# ---------------------------------------------------------------------------

class TestEmployerBranding:
    """Test employer branding: create employer → analyze brand → suggest improvements."""

    def test_analyze_employer_brand(
        self, created_employer: Dict[str, Any], branding_payload: Dict[str, Any]
    ) -> None:
        """Verify that brand analysis can be performed for an employer."""
        employer_id = created_employer.get("id") or created_employer.get("employer_id")

        response = requests.post(
            f"{BASE_URL}/employers/{employer_id}/branding/analyze",
            json=branding_payload,
        )

        assert response.status_code == 200
        data = response.json()
        assert "score" in data or "rating" in data or "analysis" in data

    def test_suggest_brand_improvements(
        self, created_employer: Dict[str, Any], branding_payload: Dict[str, Any]
    ) -> None:
        """Verify that brand improvement suggestions can be retrieved."""
        employer_id = created_employer.get("id") or created_employer.get("employer_id")

        # First analyze the brand
        analyze_resp = requests.post(
            f"{BASE_URL}/employers/{employer_id}/branding/analyze",
            json=branding_payload,
        )
        assert analyze_resp.status_code == 200

        # Then get suggestions
        response = requests.get(
            f"{BASE_URL}/employers/{employer_id}/branding/suggestions"
        )

        assert response.status_code == 200
        data = response.json()
        assert "suggestions" in data or "improvements" in data or "recommendations" in data

    def test_full_branding_flow(
        self, employer_payload: Dict[str, Any], branding_payload: Dict[str, Any]
    ) -> None:
        """End-to-end: create employer → analyze brand → suggest improvements."""
        # Step 1: Create employer
        emp_resp = requests.post(f"{BASE_URL}/employers", json=employer_payload)
        assert emp_resp.status_code == 201
        employer = emp_resp.json()
        employer_id = employer.get("id") or employer.get("employer_id")

        # Step 2: Analyze brand
        analyze_resp = requests.post(
            f"{BASE_URL}/employers/{employer_id}/branding/analyze",
            json=branding_payload,
        )
        assert analyze_resp.status_code == 200
        analysis = analyze_resp.json()
        assert analysis is not None

        # Step 3: Get improvement suggestions
        suggestions_resp = requests.get(
            f"{BASE_URL}/employers/{employer_id}/branding/suggestions"
        )
        assert suggestions_resp.status_code == 200
        suggestions = suggestions_resp.json()
        assert suggestions is not None

        # Cleanup
        requests.delete(f"{BASE_URL}/employers/{employer_id}")
