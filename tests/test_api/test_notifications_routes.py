"""API-level tests for the notification endpoints.

Regression guard for the same mount-prefix duplication bug fixed for export:
the router is mounted with ``prefix="/notifications"`` but the decorators also
hard-coded ``/notifications/...``, exposing
``/api/notifications/notifications/email`` and leaving
``/api/notifications/email`` unregistered.
"""

from __future__ import annotations

from fastapi.testclient import TestClient


class TestNotificationRoutes:
    """Exercise the notification endpoints at their intended paths."""

    def test_send_email(self, client: TestClient, auth_headers):
        resp = client.post(
            "/api/notifications/email",
            params={"to": "alice@example.com", "subject": "Hi", "body": "Hello"},
            headers=auth_headers,
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["success"] is True
        assert body["channel"] == "email"

    def test_send_sms(self, client: TestClient, auth_headers):
        resp = client.post(
            "/api/notifications/sms",
            params={"to": "+15550123", "message": "ping"},
            headers=auth_headers,
        )
        assert resp.status_code == 200, resp.text
        assert resp.json()["channel"] == "sms"

    def test_send_push(self, client: TestClient, auth_headers):
        resp = client.post(
            "/api/notifications/push",
            params={"user_id": "u-1", "title": "T", "body": "B"},
            headers=auth_headers,
        )
        assert resp.status_code == 200, resp.text
        assert resp.json()["channel"] == "push"

    def test_doubled_prefix_path_is_not_registered(
        self, client: TestClient, auth_headers
    ):
        resp = client.post(
            "/api/notifications/notifications/email",
            params={"to": "a@example.com", "subject": "s", "body": "b"},
            headers=auth_headers,
        )
        assert resp.status_code == 404, resp.text
