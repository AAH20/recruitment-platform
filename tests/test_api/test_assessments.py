"""API-level tests for ``/api/assessments`` (mock-backed CRUD).

This resource previously had no HTTP-level coverage.  The tests pin the
documented behaviours (pagination envelope, create/201, get/404, partial
update, delete/404) and one real defect: the id generator
(``_generate_id`` -> ``assess_{len(MOCK) + 1}``) can reissue an id that already
exists once any record has been deleted.
"""

from __future__ import annotations

import copy

import pytest
from fastapi.testclient import TestClient

from recruitment_platform.api import assessments as assessments_module

VALID_PAYLOAD = {
    "title": "Test Assessment",
    "description": "A brand new assessment",
    "assessment_type": "technical",
    "duration_minutes": 30,
}


@pytest.fixture(autouse=True)
def _restore_mock_store():
    """The mock store is module-global; restore it after each test."""
    snapshot = copy.deepcopy(assessments_module.MOCK_ASSESSMENTS)
    yield
    assessments_module.MOCK_ASSESSMENTS[:] = snapshot


class TestAssessmentEndpoints:
    """Exercise assessment CRUD end to end through the ASGI app."""

    def test_list_assessments_returns_paginated_envelope(
        self, client: TestClient, auth_headers
    ):
        resp = client.get("/api/assessments/", headers=auth_headers)
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert set(body) == {"items", "total", "page", "page_size", "total_pages"}
        assert body["total"] == len(assessments_module.MOCK_ASSESSMENTS)

    def test_list_assessments_filters_by_type(
        self, client: TestClient, auth_headers
    ):
        resp = client.get(
            "/api/assessments/",
            params={"assessment_type": "behavioral"},
            headers=auth_headers,
        )
        assert resp.status_code == 200, resp.text
        items = resp.json()["items"]
        assert items, "expected at least one seeded 'behavioral' assessment"
        assert all(i["assessment_type"] == "behavioral" for i in items)

    def test_list_assessments_rejects_invalid_type(
        self, client: TestClient, auth_headers
    ):
        resp = client.get(
            "/api/assessments/",
            params={"assessment_type": "nonsense"},
            headers=auth_headers,
        )
        assert resp.status_code == 422, resp.text

    def test_create_assessment_returns_201_and_is_retrievable(
        self, client: TestClient, auth_headers
    ):
        resp = client.post(
            "/api/assessments/", json=VALID_PAYLOAD, headers=auth_headers
        )
        assert resp.status_code == 201, resp.text
        body = resp.json()
        assert body["title"] == VALID_PAYLOAD["title"]
        assert body["question_count"] == 0
        assert body["is_active"] is True

        got = client.get(f"/api/assessments/{body['id']}", headers=auth_headers)
        assert got.status_code == 200, got.text
        assert got.json()["id"] == body["id"]

    def test_create_assessment_rejects_bad_duration(
        self, client: TestClient, auth_headers
    ):
        bad = dict(VALID_PAYLOAD, duration_minutes=1)  # below ge=5
        resp = client.post("/api/assessments/", json=bad, headers=auth_headers)
        assert resp.status_code == 422, resp.text

    def test_get_missing_assessment_returns_404(
        self, client: TestClient, auth_headers
    ):
        resp = client.get("/api/assessments/assess_999", headers=auth_headers)
        assert resp.status_code == 404, resp.text

    def test_update_assessment_partial(self, client: TestClient, auth_headers):
        created = client.post(
            "/api/assessments/", json=VALID_PAYLOAD, headers=auth_headers
        )
        assess_id = created.json()["id"]
        resp = client.put(
            f"/api/assessments/{assess_id}",
            json={"title": "Renamed", "is_active": False},
            headers=auth_headers,
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["title"] == "Renamed"
        assert body["is_active"] is False
        # untouched fields survive a partial update
        assert body["duration_minutes"] == VALID_PAYLOAD["duration_minutes"]

    def test_delete_assessment_then_get_returns_404(
        self, client: TestClient, auth_headers
    ):
        created = client.post(
            "/api/assessments/", json=VALID_PAYLOAD, headers=auth_headers
        )
        assess_id = created.json()["id"]
        resp = client.delete(f"/api/assessments/{assess_id}", headers=auth_headers)
        assert resp.status_code == 204, resp.text
        assert (
            client.get(f"/api/assessments/{assess_id}", headers=auth_headers).status_code
            == 404
        )

    def test_delete_missing_assessment_returns_404(
        self, client: TestClient, auth_headers
    ):
        resp = client.delete("/api/assessments/assess_999", headers=auth_headers)
        assert resp.status_code == 404, resp.text

    def test_create_id_does_not_collide_after_delete(
        self, client: TestClient, auth_headers
    ):
        """Regression: deleting a row then creating must not reuse a live id."""
        seeded = client.get(
            "/api/assessments/", params={"page_size": 100}, headers=auth_headers
        ).json()["items"]
        victim = seeded[0]["id"]
        assert (
            client.delete(f"/api/assessments/{victim}", headers=auth_headers).status_code
            == 204
        )

        created = client.post(
            "/api/assessments/", json=VALID_PAYLOAD, headers=auth_headers
        )
        assert created.status_code == 201, created.text
        new_id = created.json()["id"]

        live_ids = [a["id"] for a in assessments_module.MOCK_ASSESSMENTS]
        assert live_ids.count(new_id) == 1, f"duplicate id {new_id} in store"
