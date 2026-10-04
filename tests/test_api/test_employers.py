"""Tests for employer API endpoints."""

import pytest
from fastapi.testclient import TestClient


class TestEmployerEndpoints:
    """Test employer CRUD operations."""

    def test_create_employer(self, client: TestClient, sample_employer):
        """Test creating a new employer."""
        response = client.post("/api/employers", json=sample_employer)
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["name"] == sample_employer["name"]

    def test_get_employer(self, client: TestClient, sample_employer):
        """Test getting an employer by ID."""
        # Create employer first
        create_response = client.post("/api/employers", json=sample_employer)
        employer_id = create_response.json()["id"]

        # Get employer
        response = client.get(f"/api/employers/{employer_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == employer_id
        assert data["name"] == sample_employer["name"]

    def test_list_employers(self, client: TestClient, sample_employer):
        """Test listing all employers."""
        # Create employer
        client.post("/api/employers", json=sample_employer)

        # List employers
        response = client.get("/api/employers")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_update_employer(self, client: TestClient, sample_employer):
        """Test updating an employer."""
        # Create employer
        create_response = client.post("/api/employers", json=sample_employer)
        employer_id = create_response.json()["id"]

        # Update employer
        update_data = {"name": "Updated Company Name"}
        response = client.put(f"/api/employers/{employer_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Company Name"

    def test_delete_employer(self, client: TestClient, sample_employer):
        """Test deleting an employer."""
        # Create employer
        create_response = client.post("/api/employers", json=sample_employer)
        employer_id = create_response.json()["id"]

        # Delete employer
        response = client.delete(f"/api/employers/{employer_id}")
        assert response.status_code == 204

        # Verify deletion
        get_response = client.get(f"/api/employers/{employer_id}")
        assert get_response.status_code == 404

    def test_create_employer_validation(self, client: TestClient):
        """Test employer creation validation."""
        # Missing required fields
        response = client.post("/api/employers", json={})
        assert response.status_code == 422

    def test_get_nonexistent_employer(self, client: TestClient):
        """Test getting a non-existent employer."""
        response = client.get("/api/employers/99999")
        assert response.status_code == 404
