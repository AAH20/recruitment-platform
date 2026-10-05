"""Tests for employer API endpoints.

Every request carries a real bearer token from the ``auth_headers`` fixture, so
these tests exercise the production AuthMiddleware path.
"""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient


def _employer_payload(**overrides) -> dict:
    """Build a valid EmployerCreate payload with a unique slug/email."""
    unique = uuid.uuid4().hex[:8]
    payload = {
        "name": "Test Company",
        "slug": f"test-company-{unique}",
        "industry": "Technology",
        "contact_email": f"hr-{unique}@testcompany.com",
        "website": "https://testcompany.com",
        "company_size": "51-200",
        "description": "A test company for testing",
    }
    payload.update(overrides)
    return payload


class TestEmployerEndpoints:
    """Test employer CRUD operations (authenticated)."""

    def test_create_employer(self, client: TestClient, auth_headers):
        """Test creating a new employer."""
        response = client.post(
            "/api/employers", json=_employer_payload(), headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["name"] == "Test Company"

    def test_get_employer(self, client: TestClient, auth_headers):
        """Test getting an employer by ID."""
        create_response = client.post(
            "/api/employers", json=_employer_payload(), headers=auth_headers
        )
        employer_id = create_response.json()["id"]

        response = client.get(f"/api/employers/{employer_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["id"] == employer_id

    def test_list_employers(self, client: TestClient, auth_headers):
        """Test listing employers returns a paginated envelope."""
        client.post("/api/employers", json=_employer_payload(), headers=auth_headers)

        response = client.get("/api/employers", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["data"], list)
        assert data["total"] >= 1

    def test_update_employer(self, client: TestClient, auth_headers):
        """Test updating an employer."""
        create_response = client.post(
            "/api/employers", json=_employer_payload(), headers=auth_headers
        )
        employer_id = create_response.json()["id"]

        response = client.put(
            f"/api/employers/{employer_id}",
            json={"description": "Updated description"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["description"] == "Updated description"

    def test_delete_employer(self, client: TestClient, auth_headers):
        """Test deleting an employer returns 204 and the record disappears."""
        create_response = client.post(
            "/api/employers", json=_employer_payload(), headers=auth_headers
        )
        employer_id = create_response.json()["id"]

        response = client.delete(f"/api/employers/{employer_id}", headers=auth_headers)
        assert response.status_code == 204

        follow_up = client.get(f"/api/employers/{employer_id}", headers=auth_headers)
        assert follow_up.status_code == 404

    def test_create_employer_validation(self, client: TestClient, auth_headers):
        """Test employer creation rejects a missing required field."""
        response = client.post("/api/employers", json={}, headers=auth_headers)
        assert response.status_code == 422

    def test_create_employer_invalid_slug(self, client: TestClient, auth_headers):
        """Test slug pattern is enforced."""
        response = client.post(
            "/api/employers",
            json=_employer_payload(slug="Not A Slug"),
            headers=auth_headers,
        )
        assert response.status_code == 422

    def test_create_employer_duplicate_slug(self, client: TestClient, auth_headers):
        """Test duplicate slug is rejected with 409."""
        payload = _employer_payload()
        assert (
            client.post("/api/employers", json=payload, headers=auth_headers).status_code
            == 201
        )
        assert (
            client.post("/api/employers", json=payload, headers=auth_headers).status_code
            == 409
        )

    def test_create_employer_duplicate_email(self, client: TestClient, auth_headers):
        """Test duplicate contact email is rejected with 409."""
        unique = uuid.uuid4().hex[:8]
        payload = _employer_payload(
            slug=f"slug-a-{unique}", contact_email=f"dup-{unique}@testcompany.com"
        )
        assert (
            client.post("/api/employers", json=payload, headers=auth_headers).status_code
            == 201
        )

        clash = _employer_payload(
            slug=f"slug-b-{unique}", contact_email=f"dup-{unique}@testcompany.com"
        )
        assert (
            client.post("/api/employers", json=clash, headers=auth_headers).status_code
            == 409
        )

    def test_get_nonexistent_employer(self, client: TestClient, auth_headers):
        """Test getting a non-existent employer returns 404."""
        response = client.get(f"/api/employers/{uuid.uuid4()}", headers=auth_headers)
        assert response.status_code == 404

    def test_filter_employers_by_industry(self, client: TestClient, auth_headers):
        """Test filtering employers by industry."""
        unique = uuid.uuid4().hex[:8]
        client.post(
            "/api/employers",
            json=_employer_payload(slug=f"fin-{unique}", industry="Finance"),
            headers=auth_headers,
        )

        response = client.get("/api/employers?industry=Finance", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert all(e["industry"] == "Finance" for e in data["data"])

    def test_list_employers_requires_auth(self, client: TestClient):
        """Test listing employers without a token is rejected."""
        assert client.get("/api/employers").status_code == 401

    def test_create_employer_requires_auth(self, client: TestClient):
        """Test creating an employer without a token is rejected."""
        response = client.post("/api/employers", json=_employer_payload())
        assert response.status_code == 401