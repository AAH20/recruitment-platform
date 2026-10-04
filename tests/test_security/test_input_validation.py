"""Input validation tests for recruitment-platform."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from recruitment_platform.main import app


class TestInputValidation:
    """Test that input validation is properly enforced."""

    @pytest.fixture
    def client(self):
        with TestClient(app) as c:
            yield c

    def test_login_email_validation(self, client):
        """Test that login validates email format."""
        invalid_emails = [
            "not-an-email",
            "@example.com",
            "user@",
            "user@.com",
            "user@example",
            "user space@example.com",
            "user@exam ple.com",
        ]
        for email in invalid_emails:
            resp = client.post(
                "/api/v1/auth/login",
                json={"email": email, "password": "test123"}
            )
            # Should return 422 for invalid email or 401 for invalid credentials
            assert resp.status_code in (401, 422), (
                f"Invalid email '{email}' was accepted with status {resp.status_code}"
            )

    def test_login_password_minimum_length(self, client):
        """Test that password meets minimum length requirements."""
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": ""}
        )
        assert resp.status_code in (401, 422), (
            "Empty password was accepted"
        )

    def test_register_email_validation(self, client):
        """Test that registration validates email format."""
        invalid_emails = [
            "not-an-email",
            "@example.com",
            "user@",
        ]
        for email in invalid_emails:
            resp = client.post(
                "/api/v1/auth/register",
                json={
                    "name": "Test User",
                    "email": email,
                    "password": "test123"
                }
            )
            assert resp.status_code == 422, (
                f"Invalid email '{email}' was accepted in registration"
            )

    def test_register_password_validation(self, client):
        """Test that registration validates password strength."""
        weak_passwords = [
            "123",
            "abc",
            "short",
        ]
        for password in weak_passwords:
            resp = client.post(
                "/api/v1/auth/register",
                json={
                    "name": "Test User",
                    "email": f"test_{hash(password)}@example.com",
                    "password": password
                }
            )
            # Should reject weak passwords
            assert resp.status_code in (422, 400), (
                f"Weak password '{password}' was accepted"
            )

    def test_search_query_length_validation(self, client):
        """Test that search queries have length limits."""
        # Very long search query
        long_query = "a" * 10000
        resp = client.get(
            "/api/v1/search/jobs",
            params={"q": long_query}
        )
        # Should not cause server error
        assert resp.status_code != 500, (
            "Very long search query caused server error"
        )

    def test_search_limit_validation(self, client):
        """Test that search limit parameter is validated."""
        # Negative limit
        resp = client.get(
            "/api/v1/search/jobs",
            params={"q": "test", "limit": -1}
        )
        assert resp.status_code == 422, "Negative limit was accepted"

        # Zero limit
        resp = client.get(
            "/api/v1/search/jobs",
            params={"q": "test", "limit": 0}
        )
        assert resp.status_code == 422, "Zero limit was accepted"

        # Very large limit
        resp = client.get(
            "/api/v1/search/jobs",
            params={"q": "test", "limit": 10000}
        )
        assert resp.status_code == 422, "Very large limit was accepted"

    def test_search_offset_validation(self, client):
        """Test that search offset parameter is validated."""
        resp = client.get(
            "/api/v1/search/jobs",
            params={"q": "test", "offset": -1}
        )
        assert resp.status_code == 422, "Negative offset was accepted"

    def test_null_byte_in_input(self, client):
        """Test that null bytes in input are handled."""
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": "test\x00@example.com", "password": "test123"}
        )
        # Should not cause server error
        assert resp.status_code != 500

    def test_very_long_input(self, client):
        """Test that very long input is handled gracefully."""
        long_string = "a" * 100000
        resp = client.post(
            "/api/v1/auth/register",
            json={
                "name": long_string,
                "email": "test@example.com",
                "password": "test123"
            }
        )
        # Should not cause server error
        assert resp.status_code != 500

    def test_special_characters_in_input(self, client):
        """Test that special characters in input are handled."""
        special_chars = "!@#$%^&*()_+-=[]{}|;\":\",./<>?"
        resp = client.post(
            "/api/v1/auth/register",
            json={
                "name": f"Test{special_chars}User",
                "email": "test@example.com",
                "password": "test123"
            }
        )
        # Should not cause server error
        assert resp.status_code != 500
