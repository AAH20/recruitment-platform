"""Tests for candidate API endpoints."""

import pytest
from fastapi.testclient import TestClient


class TestCandidateEndpoints:
    """Test candidate CRUD operations."""

    def test_create_candidate(self, client: TestClient, sample_candidate):
        """Test creating a new candidate."""
        response = client.post("/api/candidates", json=sample_candidate)
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["name"] == sample_candidate["name"]

    def test_get_candidate(self, client: TestClient, sample_candidate):
        """Test getting a candidate by ID."""
        create_response = client.post("/api/candidates", json=sample_candidate)
        candidate_id = create_response.json()["id"]

        response = client.get(f"/api/candidates/{candidate_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == candidate_id

    def test_list_candidates(self, client: TestClient, sample_candidate):
        """Test listing all candidates."""
        client.post("/api/candidates", json=sample_candidate)

        response = client.get("/api/candidates")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_update_candidate(self, client: TestClient, sample_candidate):
        """Test updating a candidate."""
        create_response = client.post("/api/candidates", json=sample_candidate)
        candidate_id = create_response.json()["id"]

        update_data = {"name": "Jane Doe"}
        response = client.put(f"/api/candidates/{candidate_id}", json=update_data)
        assert response.status_code == 200

    def test_delete_candidate(self, client: TestClient, sample_candidate):
        """Test deleting a candidate."""
        create_response = client.post("/api/candidates", json=sample_candidate)
        candidate_id = create_response.json()["id"]

        response = client.delete(f"/api/candidates/{candidate_id}")
        assert response.status_code == 204

    def test_create_candidate_validation(self, client: TestClient):
        """Test candidate creation validation."""
        response = client.post("/api/candidates", json={})
        assert response.status_code == 422

    def test_get_nonexistent_candidate(self, client: TestClient):
        """Test getting a non-existent candidate."""
        response = client.get("/api/candidates/99999")
        assert response.status_code == 404

    def test_search_candidates(self, client: TestClient, sample_candidate):
        """Test searching candidates."""
        client.post("/api/candidates", json=sample_candidate)

        response = client.get("/api/candidates?search=John")
        assert response.status_code == 200
