"""Regression tests for the ``/api/v1`` route wire-up.

The v1 routers declared their prefix as ``/api/v1/<resource>`` and are included
into the root ``api_router``, which ``main.create_app`` mounts at ``/api``.
The ``/api`` segment was therefore applied twice, exposing every v1 endpoint at
``/api/api/v1/...`` and leaving the documented, client-facing ``/api/v1/...``
path (see README and the SDK/frontend ``API_BASE_URL``) unregistered.
"""

from __future__ import annotations

from fastapi.testclient import TestClient


class TestV1ReportRoutes:
    def test_list_reports(self, client: TestClient, auth_headers):
        resp = client.get("/api/v1/reports", headers=auth_headers)
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert set(body) >= {"items", "total", "page", "page_size", "pages"}

    def test_create_then_get_report(self, client: TestClient, auth_headers):
        created = client.post(
            "/api/v1/reports",
            json={"name": "Q1 Pipeline", "report_type": "pipeline"},
            headers=auth_headers,
        )
        assert created.status_code == 201, created.text
        report_id = created.json()["id"]
        assert created.json()["status"] == "pending"

        got = client.get(f"/api/v1/reports/{report_id}", headers=auth_headers)
        assert got.status_code == 200, got.text
        assert got.json()["id"] == report_id

    def test_get_missing_report_returns_404(self, client: TestClient, auth_headers):
        resp = client.get("/api/v1/reports/does-not-exist", headers=auth_headers)
        assert resp.status_code == 404, resp.text

    def test_download_pending_report_returns_409(
        self, client: TestClient, auth_headers
    ):
        created = client.post(
            "/api/v1/reports",
            json={"name": "Pending", "report_type": "hiring"},
            headers=auth_headers,
        )
        report_id = created.json()["id"]
        resp = client.get(f"/api/v1/reports/{report_id}/download", headers=auth_headers)
        assert resp.status_code == 409, resp.text

    def test_doubled_path_not_registered(self, client: TestClient, auth_headers):
        resp = client.get("/api/api/v1/reports", headers=auth_headers)
        assert resp.status_code == 404, resp.text


class TestV1AnalyticsRoutes:
    def test_dashboard(self, client: TestClient, auth_headers):
        resp = client.get("/api/v1/analytics", headers=auth_headers)
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["total_active_jobs"] == 0

    def test_pipeline_metrics(self, client: TestClient, auth_headers):
        resp = client.get("/api/v1/analytics/pipeline", headers=auth_headers)
        assert resp.status_code == 200, resp.text
        assert resp.json()["stages"] == []

    def test_doubled_path_not_registered(self, client: TestClient, auth_headers):
        resp = client.get("/api/api/v1/analytics", headers=auth_headers)
        assert resp.status_code == 404, resp.text


class TestV1SkillsAndPools:
    def test_list_skills(self, client: TestClient, auth_headers):
        resp = client.get("/api/v1/skills", headers=auth_headers)
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert set(body) >= {"items", "total", "page", "page_size", "pages"}
        assert body["total"] >= 1

    def test_list_interviews(self, client: TestClient, auth_headers):
        resp = client.get("/api/v1/interviews", headers=auth_headers)
        assert resp.status_code == 200, resp.text
        assert resp.json()["items"] == []

    def test_list_talent_pools(self, client: TestClient, auth_headers):
        resp = client.get("/api/v1/talent-pools", headers=auth_headers)
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert set(body) >= {"items", "total", "page", "page_size", "total_pages"}
