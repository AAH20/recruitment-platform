"""XSS prevention tests for recruitment-platform."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from recruitment_platform.main import app
from recruitment_platform.security.auth import sanitize_input


class TestXSSPrevention:
    """Test that XSS attacks are prevented."""

    XSS_PAYLOADS = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "<svg onload=alert('XSS')>",
        "javascript:alert('XSS')",
        "<body onload=alert('XSS')>",
        "<iframe src='javascript:alert(1)'>",
        "<input onfocus=alert('XSS') autofocus>",
        "<marquee onstart=alert('XSS')>",
        "<details open ontoggle=alert('XSS')>",
        "\"><script>alert('XSS')</script>",
        "'><script>alert('XSS')</script>",
        "<img src=\"javascript:alert('XSS')\">",
        "<a href=\"javascript:alert('XSS')\">click</a>",
        "<div style=\"background-image: url(javascript:alert('XSS'))\">",
        "<object data=\"javascript:alert('XSS')\">",
        "<embed src=\"javascript:alert('XSS')\">",
        "<form><button formaction=\"javascript:alert('XSS')\">",
        "<video><source onerror=\"alert('XSS')\">",
        "<audio src=x onerror=alert('XSS')>",
    ]

    @pytest.fixture
    def client(self):
        with TestClient(app) as c:
            yield c

    def test_sanitize_input_escapes_html(self):
        """Test that sanitize_input properly escapes HTML."""
        for payload in self.XSS_PAYLOADS:
            sanitized = sanitize_input(payload)
            # Should not contain unescaped script tags
            assert "<script>" not in sanitized.lower(), (
                f"XSS payload not sanitized: {payload} -> {sanitized}"
            )

    def test_sanitize_input_escapes_quotes(self):
        """Test that sanitize_input escapes quotes."""
        result = sanitize_input("test'quote")
        assert "&#x27;" in result or "&apos;" in result

    def test_sanitize_input_escapes_ampersand(self):
        """Test that sanitize_input escapes ampersands."""
        result = sanitize_input("test&value")
        assert "&amp;" in result

    def test_register_xss_in_name(self, client):
        """Test that XSS in registration name is sanitized."""
        for payload in self.XSS_PAYLOADS:
            resp = client.post(
                "/api/v1/auth/register",
                json={
                    "name": payload,
                    "email": f"xss_test_{hash(payload)}@example.com",
                    "password": "test123"
                }
            )
            if resp.status_code == 200:
                data = resp.json()
                name = data.get("user", {}).get("name", "")
                # The name should be sanitized (HTML escaped)
                assert "<script>" not in name.lower(), (
                    f"XSS payload stored unsanitized: {payload}"
                )

    def test_search_xss_reflection(self, client):
        """Test that XSS in search queries is not reflected."""
        for payload in self.XSS_PAYLOADS:
            resp = client.get(
                "/api/v1/search/jobs",
                params={"q": payload}
            )
            # The response should not contain unescaped script tags
            if resp.status_code == 200:
                response_text = resp.text
                # Check that script tags are not reflected unescaped
                assert "<script>alert" not in response_text.lower(), (
                    f"XSS reflected in search response: {payload}"
                )
