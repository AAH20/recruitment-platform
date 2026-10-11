"""API-level tests for the search endpoints.

Regression guard for the same mount-prefix duplication bug fixed for export:
the router is mounted with ``prefix="/search"`` but the decorators also
hard-coded ``/search/...``, exposing ``/api/search/search/jobs`` and leaving
``/api/search/jobs`` unregistered.
"""

from __future__ import annotations

from fastapi.testclient import TestClient


class TestSearchRoutes:
    """Exercise the search endpoints at their intended paths."""

    def test_search_jobs(self, client: TestClient, auth_headers):
        resp = client.get(
            "/api/search/jobs", params={"q": "engineer"}, headers=auth_headers
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["query"] == "engineer"
        assert body["results"] == []

    def test_search_candidates(self, client: TestClient, auth_headers):
        resp = client.get(
            "/api/search/candidates", params={"q": "python"}, headers=auth_headers
        )
        assert resp.status_code == 200, resp.text
        assert resp.json()["query"] == "python"

    def test_search_skills_returns_list(self, client: TestClient, auth_headers):
        resp = client.get(
            "/api/search/skills", params={"q": "py"}, headers=auth_headers
        )
        assert resp.status_code == 200, resp.text
        assert isinstance(resp.json(), list)

    def test_autocomplete_returns_list(self, client: TestClient, auth_headers):
        resp = client.get(
            "/api/search/autocomplete",
            params={"q": "eng", "entity_type": "job"},
            headers=auth_headers,
        )
        assert resp.status_code == 200, resp.text
        assert isinstance(resp.json(), list)

    def test_search_requires_query_param(self, client: TestClient, auth_headers):
        """``q`` is mandatory; omitting it is a 422, not a 500."""
        resp = client.get("/api/search/jobs", headers=auth_headers)
        assert resp.status_code == 422, resp.text

    def test_limit_out_of_range_is_rejected(self, client: TestClient, auth_headers):
        resp = client.get(
            "/api/search/jobs",
            params={"q": "x", "limit": 1000},
            headers=auth_headers,
        )
        assert resp.status_code == 422, resp.text

    def test_doubled_prefix_path_is_not_registered(
        self, client: TestClient, auth_headers
    ):
        resp = client.get(
            "/api/search/search/jobs", params={"q": "x"}, headers=auth_headers
        )
        assert resp.status_code == 404, resp.text
