"""SQL injection prevention tests for recruitment-platform."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from recruitment_platform.main import app


class TestSQLInjectionPrevention:
    """Test that SQL injection attacks are prevented."""

    SQL_INJECTION_PAYLOADS = [
        "' OR '1'='1",
        "' OR 1=1--",
        "'; DROP TABLE users;--",
        "1' UNION SELECT * FROM users--",
        "' OR '1'='1' /*",
        "admin'--",
        "' OR 1=1#",
        "1 AND 1=1",
        "'; EXEC xp_cmdshell('dir');--",
        "' OR ''='",
        "1; SELECT * FROM users",
        "' UNION SELECT null, null, null--",
        "1' AND (SELECT COUNT(*) FROM users) > 0--",
        "'; INSERT INTO users VALUES ('hacker', 'pass')--",
        "' OR 1=1 LIMIT 1--",
        "1' OR '1'='1",
        "'; UPDATE users SET password='hacked'--",
        "' OR 'x'='x",
        "1 AND 1=2",
        "'; DELETE FROM users WHERE '1'='1",
    ]

    @pytest.fixture
    def client(self):
        with TestClient(app) as c:
            yield c

    def test_login_sql_injection_email(self, client):
        """Test that SQL injection in login email field is prevented."""
        for payload in self.SQL_INJECTION_PAYLOADS:
            resp = client.post(
                "/api/v1/auth/login",
                json={"email": payload, "password": "test123"}
            )
            # Should return 401 (invalid credentials) or 422 (validation error)
            # Should NOT return 200 (successful login)
            assert resp.status_code != 200, (
                f"SQL injection succeeded with payload: {payload}"
            )

    def test_login_sql_injection_password(self, client):
        """Test that SQL injection in login password field is prevented."""
        for payload in self.SQL_INJECTION_PAYLOADS:
            resp = client.post(
                "/api/v1/auth/login",
                json={"email": "test@example.com", "password": payload}
            )
            assert resp.status_code != 200, (
                f"SQL injection succeeded with payload: {payload}"
            )

    def test_register_sql_injection_name(self, client):
        """Test that SQL injection in register name field is prevented."""
        for payload in self.SQL_INJECTION_PAYLOADS:
            resp = client.post(
                "/api/v1/auth/register",
                json={
                    "name": payload,
                    "email": f"test_{hash(payload)}@example.com",
                    "password": "test123"
                }
            )
            # Should not create a user with SQL injection payload
            if resp.status_code == 200:
                # If created, the name should be sanitized
                data = resp.json()
                assert "OR" not in data.get("user", {}).get("name", ""), (
                    f"SQL injection in name not sanitized: {payload}"
                )

    def test_search_sql_injection(self, client):
        """Test that SQL injection in search queries is prevented."""
        for payload in self.SQL_INJECTION_PAYLOADS:
            resp = client.get(
                "/api/v1/search/jobs",
                params={"q": payload}
            )
            # Should not cause server error or return all results
            assert resp.status_code != 500, (
                f"SQL injection caused server error with payload: {payload}"
            )

    def test_search_candidates_sql_injection(self, client):
        """Test SQL injection in candidate search."""
        for payload in self.SQL_INJECTION_PAYLOADS:
            resp = client.get(
                "/api/v1/search/candidates",
                params={"q": payload}
            )
            assert resp.status_code != 500, (
                f"SQL injection caused server error with payload: {payload}"
            )
