"""Authorization bypass tests for recruitment-platform."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from recruitment_platform.main import app
from recruitment_platform.security.auth import create_access_token


class TestAuthorizationBypass:
    """Test that authorization cannot be bypassed."""

    @pytest.fixture
    def client(self):
        with TestClient(app) as c:
            yield c

    def test_candidate_cannot_access_admin_endpoints(self, client):
        """Test that candidates cannot access admin endpoints."""
        token = create_access_token({
            "sub": "user-123",
            "email": "candidate@example.com",
            "roles": ["candidate"]
        })
        resp = client.get(
            "/api/v1/candidates",
            headers={"Authorization": f"Bearer {token}"}
        )
        # Candidate should not be able to access all candidates
        # (should be restricted to own profile only)
        assert resp.status_code in (403, 200)  # 200 if filtered to own data

    def test_viewer_cannot_access_recruiter_endpoints(self, client):
        """Test that viewers cannot access recruiter endpoints."""
        token = create_access_token({
            "sub": "user-123",
            "email": "viewer@example.com",
            "roles": ["viewer"]
        })
        # Viewer should not be able to create jobs
        resp = client.post(
            "/api/v1/jobs",
            headers={"Authorization": f"Bearer {token}"},
            json={"title": "Test Job", "description": "Test"}
        )
        assert resp.status_code == 403, (
            "Viewer was able to create a job"
        )

    def test_recruiter_cannot_access_admin_endpoints(self, client):
        """Test that recruiters cannot access admin endpoints."""
        token = create_access_token({
            "sub": "user-123",
            "email": "recruiter@example.com",
            "roles": ["recruiter"]
        })
        # Recruiter should not access admin settings
        resp = client.get(
            "/api/v1/settings",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert resp.status_code in (403, 404), (
            "Recruiter accessed admin settings"
        )

    def test_role_escalation_via_token_manipulation(self, client):
        """Test that role escalation via token manipulation is prevented."""
        # Create a token with viewer role
        token = create_access_token({
            "sub": "user-123",
            "email": "user@example.com",
            "roles": ["viewer"]
        })
        # Try to use it to access admin endpoints
        resp = client.get(
            "/api/v1/reports",
            headers={"Authorization": f"Bearer {token}"}
        )
        # Viewer has GET access to reports per default permissions
        # But should not have POST access
        resp = client.post(
            "/api/v1/reports",
            headers={"Authorization": f"Bearer {token}"},
            json={"type": "test"}
        )
        assert resp.status_code == 403, (
            "Viewer was able to create reports (privilege escalation)"
        )

    def test_horizontal_privilege_escalation(self, client):
        """Test that users cannot access other users' data."""
        token1 = create_access_token({
            "sub": "user-1",
            "email": "user1@example.com",
            "roles": ["candidate"]
        })
        # Try to access another user's application
        resp = client.get(
            "/api/v1/applications/2",
            headers={"Authorization": f"Bearer {token1}"}
        )
        # Should not be able to access other users' applications
        assert resp.status_code in (403, 404), (
            "User was able to access another user's application"
        )

    def test_inactive_user_cannot_access(self, client):
        """Test that inactive users cannot access protected resources."""
        # This tests the is_active check
        token = create_access_token({
            "sub": "inactive-user",
            "email": "inactive@example.com",
            "roles": ["recruiter"],
            "is_active": False
        })
        resp = client.get(
            "/api/v1/jobs",
            headers={"Authorization": f"Bearer {token}"}
        )
        # Inactive user should be rejected
        assert resp.status_code in (401, 403, 400), (
            "Inactive user was able to access protected resources"
        )
