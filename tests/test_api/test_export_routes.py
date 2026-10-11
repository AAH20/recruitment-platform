"""API-level tests for the data export endpoints.

Regression guard for a mount-prefix duplication bug: ``api/router.py`` mounts
this router with ``prefix="/export"`` while the decorators also hard-coded
``/export/...``.  The result was a bogus double path
(``/api/export/export/csv``) and the intended ``/api/export/csv`` was never
registered, so every client using the documented path got a 404.
"""

from __future__ import annotations

import json

from fastapi.testclient import TestClient


class TestExportRoutes:
    """Exercise the export endpoints at their intended paths."""

    def test_export_csv(self, client: TestClient, auth_headers):
        data = json.dumps([{"name": "John", "age": 30}])
        resp = client.get(
            "/api/export/csv", params={"data": data}, headers=auth_headers
        )
        assert resp.status_code == 200, resp.text
        assert resp.headers["content-type"].startswith("text/csv")
        assert "name,age" in resp.text
        assert "John,30" in resp.text

    def test_export_json(self, client: TestClient, auth_headers):
        data = json.dumps([{"name": "John"}])
        resp = client.get(
            "/api/export/json", params={"data": data}, headers=auth_headers
        )
        assert resp.status_code == 200, resp.text
        assert resp.headers["content-type"].startswith("application/json")
        assert '"name": "John"' in resp.text

    def test_export_xml(self, client: TestClient, auth_headers):
        data = json.dumps([{"name": "John"}])
        resp = client.get(
            "/api/export/xml", params={"data": data}, headers=auth_headers
        )
        assert resp.status_code == 200, resp.text
        assert resp.headers["content-type"].startswith("application/xml")
        assert "<name>John</name>" in resp.text

    def test_export_csv_invalid_json_returns_400(
        self, client: TestClient, auth_headers
    ):
        """Malformed ``data`` is a client error, not a 500."""
        resp = client.get(
            "/api/export/csv", params={"data": "not-json"}, headers=auth_headers
        )
        assert resp.status_code == 400, resp.text

    def test_doubled_prefix_path_is_not_registered(
        self, client: TestClient, auth_headers
    ):
        """The accidental /api/export/export/... path must not exist."""
        data = json.dumps([{"name": "John"}])
        resp = client.get(
            "/api/export/export/csv", params={"data": data}, headers=auth_headers
        )
        assert resp.status_code == 404, resp.text
