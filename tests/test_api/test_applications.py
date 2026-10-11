"""API-level tests for ``/api/applications`` (mock-backed CRUD).

This resource previously had no HTTP-level coverage at all: only the sibling
resources (candidates / employers / jobs) had ``tests/test_api`` files.  The
tests below pin the documented behaviours (pagination envelope, create/409 on
duplicate, get/404, status update/422, delete/404) and one real defect: the
generated application id was derived from ``len(MOCK_APPLICATIONS) + 1``, so
deleting any record and then creating a new one could mint an id that already
existed, corrupting the store.
"""

from __future__ import annotations

import copy

import pytest
from fastapi.testclient import TestClient

from recruitment_platform.api import applications as applications_module

VALID_PAYLOAD = {
    "candidate_name": "Test Applicant",
    "candidate_email": "test.applicant@example.com",
    "position_id": "pos_xyz",
    "position_title": "Test Engineer",
    "years_experience": 3,
    "skills": ["Python", "SQL"],
    "source": "referral",
}


@pytest.fixture(autouse=True)
def _restore_mock_store():
    """The mock store is module-global; restore it after each test."""
    snapshot = copy.deepcopy(applications_module.MOCK_APPLICATIONS)
    yield
    applications_module.MOCK_APPLICATIONS[:] = snapshot


class TestApplicationEndpoints:
    """Exercise application CRUD end to end through the ASGI app."""

    def test_list_applications_returns_paginated_envelope(
        self, client: TestClient, auth_headers
    ):
        resp = client.get("/api/applications/", headers=auth_headers)
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert set(body) == {"items", "total", "page", "page_size", "total_pages"}
        assert body["total"] == len(applications_module.MOCK_APPLICATIONS)
        assert body["page_size"] == 10
        assert len(body["items"]) <= 10

    def test_list_applications_filters_by_status(
        self, client: TestClient, auth_headers
    ):
        resp = client.get(
            "/api/applications/", params={"status": "hired"}, headers=auth_headers
        )
        assert resp.status_code == 200, resp.text
        items = resp.json()["items"]
        assert items, "expected at least one seeded 'hired' application"
        assert all(item["status"] == "hired" for item in items)

    def test_list_applications_search_matches_email(
        self, client: TestClient, auth_headers
    ):
        resp = client.get(
            "/api/applications/",
            params={"search": "alice.johnson"},
            headers=auth_headers,
        )
        assert resp.status_code == 200, resp.text
        items = resp.json()["items"]
        assert any("alice.johnson" in item["candidate_email"] for item in items)

    def test_create_application_returns_201_and_is_retrievable(
        self, client: TestClient, auth_headers
    ):
        resp = client.post(
            "/api/applications/", json=VALID_PAYLOAD, headers=auth_headers
        )
        assert resp.status_code == 201, resp.text
        body = resp.json()
        assert body["status"] == "applied"
        assert body["candidate_email"] == VALID_PAYLOAD["candidate_email"]

        got = client.get(f"/api/applications/{body['id']}", headers=auth_headers)
        assert got.status_code == 200, got.text
        assert got.json()["id"] == body["id"]

    def test_create_duplicate_application_returns_409(
        self, client: TestClient, auth_headers
    ):
        first = client.post(
            "/api/applications/", json=VALID_PAYLOAD, headers=auth_headers
        )
        assert first.status_code == 201, first.text
        second = client.post(
            "/api/applications/", json=VALID_PAYLOAD, headers=auth_headers
        )
        assert second.status_code == 409, second.text

    def test_get_missing_application_returns_404(
        self, client: TestClient, auth_headers
    ):
        resp = client.get("/api/applications/does-not-exist", headers=auth_headers)
        assert resp.status_code == 404, resp.text

    def test_update_application_status(self, client: TestClient, auth_headers):
        created = client.post(
            "/api/applications/", json=VALID_PAYLOAD, headers=auth_headers
        )
        app_id = created.json()["id"]
        resp = client.put(
            f"/api/applications/{app_id}",
            params={"status_update": "screening"},
            headers=auth_headers,
        )
        assert resp.status_code == 200, resp.text
        assert resp.json()["status"] == "screening"

    def test_update_invalid_status_returns_422(
        self, client: TestClient, auth_headers
    ):
        created = client.post(
            "/api/applications/", json=VALID_PAYLOAD, headers=auth_headers
        )
        app_id = created.json()["id"]
        resp = client.put(
            f"/api/applications/{app_id}",
            params={"status_update": "not-a-status"},
            headers=auth_headers,
        )
        assert resp.status_code == 422, resp.text

    def test_delete_application_then_get_returns_404(
        self, client: TestClient, auth_headers
    ):
        created = client.post(
            "/api/applications/", json=VALID_PAYLOAD, headers=auth_headers
        )
        app_id = created.json()["id"]
        resp = client.delete(f"/api/applications/{app_id}", headers=auth_headers)
        assert resp.status_code == 204, resp.text
        assert (
            client.get(f"/api/applications/{app_id}", headers=auth_headers).status_code
            == 404
        )

    def test_delete_missing_application_returns_404(
        self, client: TestClient, auth_headers
    ):
        resp = client.delete("/api/applications/missing", headers=auth_headers)
        assert resp.status_code == 404, resp.text

    def test_create_id_does_not_collide_after_delete(
        self, client: TestClient, auth_headers
    ):
        """Regression: deleting a row then creating must not reuse a live id.

        With the old ``len(store) + 1`` scheme, deleting ``app_001`` from the
        12 seeded rows makes the next generated id ``app_012`` - which already
        exists - so the store ends up with two records sharing one id and
        ``GET`` becomes ambiguous.
        """
        seeded = client.get(
            "/api/applications/", params={"page_size": 100}, headers=auth_headers
        ).json()["items"]
        victim = seeded[0]["id"]
        assert (
            client.delete(f"/api/applications/{victim}", headers=auth_headers).status_code
            == 204
        )

        created = client.post(
            "/api/applications/", json=VALID_PAYLOAD, headers=auth_headers
        )
        assert created.status_code == 201, created.text
        new_id = created.json()["id"]

        live_ids = [a["id"] for a in applications_module.MOCK_APPLICATIONS]
        assert live_ids.count(new_id) == 1, f"duplicate id {new_id} in store"
