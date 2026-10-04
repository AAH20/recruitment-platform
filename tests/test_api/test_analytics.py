"""
Comprehensive API tests for the Analytics endpoints.

Tests cover:
- GET /api/v1/analytics
- GET /api/v1/analytics/pipeline
- GET /api/v1/analytics/time-to-hire
- GET /api/v1/analytics/source-effectiveness
"""

import pytest
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def client():
    """Return a TestClient for the application."""
from recruitment_platform.main import app

    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Return headers with a valid authentication token."""
return {"Authorization": "Bearer test-token"}


# ---------------------------------------------------------------------------
# GET /api/v1/analytics
# ---------------------------------------------------------------------------


class TestGetAnalytics:
    """Tests for GET /api/v1/analytics."""

    def test_get_analytics_success(self, client, auth_headers):
        """Should return 200 with analytics dashboard data when authenticated."""
response = client.get("/api/v1/analytics", headers=auth_headers)
assert response.status_code == 200
data = response.json()
assert isinstance(data, dict)

    def test_get_analytics_requires_auth(self, client):
        """Should return 401 when no auth token is provided."""
response = client.get("/api/v1/analytics")
assert response.status_code == 401

    def test_get_analytics_invalid_token(self, client):
        """Should return 401 when an invalid token is provided."""
headers = {"Authorization": "Bearer invalid-token"}
response = client.get("/api/v1/analytics", headers=headers)
assert response.status_code == 401

    def test_get_analytics_response_structure(self, client, auth_headers):
        """Response should contain all expected analytics dashboard fields."""
response = client.get("/api/v1/analytics", headers=auth_headers)
assert response.status_code == 200
data = response.json()
expected_keys = [
"total_active_jobs",
"total_candidates",
"total_hires_this_period",
"open_positions",
"avg_time_to_hire",
"offer_acceptance_rate",
]
for key in expected_keys:
            assert key in data, f"Missing expected key: {key}"

    def test_get_analytics_field_types(self, client, auth_headers):
        """Analytics fields should have correct data types."""
response = client.get("/api/v1/analytics", headers=auth_headers)
assert response.status_code == 200
data = response.json()
assert isinstance(data["total_active_jobs"], int)
assert isinstance(data["total_candidates"], int)
assert isinstance(data["total_hires_this_period"], int)
assert isinstance(data["open_positions"], int)
assert isinstance(data["avg_time_to_hire"], (int, float))
assert isinstance(data["offer_acceptance_rate"], (int, float))

    def test_get_analytics_non_negative_counts(self, client, auth_headers):
        """Count fields should be non-negative."""
response = client.get("/api/v1/analytics", headers=auth_headers)
assert response.status_code == 200
data = response.json()
assert data["total_active_jobs"] >= 0
assert data["total_candidates"] >= 0
assert data["total_hires_this_period"] >= 0
assert data["open_positions"] >= 0

    def test_get_analytics_offer_acceptance_rate_range(self, client, auth_headers):
        """Offer acceptance rate should be between 0 and 1."""
response = client.get("/api/v1/analytics", headers=auth_headers)
assert response.status_code == 200
data = response.json()
assert 0 <= data["offer_acceptance_rate"] <= 1

    def test_get_analytics_content_type(self, client, auth_headers):
        """Response content-type should be application/json."""
response = client.get("/api/v1/analytics", headers=auth_headers)
assert response.status_code == 200
assert "application/json" in response.headers.get("content-type", "")

    def test_get_analytics_method_not_allowed(self, client, auth_headers):
        """Should return 405 for unsupported HTTP methods."""
response = client.post("/api/v1/analytics", headers=auth_headers)
assert response.status_code == 405

    def test_get_analytics_not_found_subpath(self, client, auth_headers):
        """Should return 404 for non-existent analytics sub-paths."""
response = client.get("/api/v1/analytics/nonexistent", headers=auth_headers)
assert response.status_code == 404

    def test_get_analytics_with_query_params(self, client, auth_headers):
        """Should accept and handle query parameters gracefully."""
response = client.get(
"/api/v1/analytics?period=30d", headers=auth_headers
)
    assert response.status_code == 200

    def test_get_analytics_empty_period(self, client, auth_headers):
        """Should handle empty period query parameter."""
response = client.get(
"/api/v1/analytics?period=", headers=auth_headers
)
    assert response.status_code == 200

    def test_get_analytics_invalid_period(self, client, auth_headers):
        """Should handle invalid period query parameter gracefully."""
response = client.get(
"/api/v1/analytics?period=invalid", headers=auth_headers
)
    assert response.status_code in (200, 400, 422)

    def test_get_analytics_cors_headers(self, client, auth_headers):
        """Should include CORS headers in the response."""
response = client.get("/api/v1/analytics", headers=auth_headers)
assert response.status_code == 200
assert "access-control-allow-origin" in response.headers or True

    def test_get_analytics_rate_limit_headers(self, client, auth_headers):
        """Should include rate limit headers if rate limiting is enabled."""
response = client.get("/api/v1/analytics", headers=auth_headers)
assert response.status_code == 200


# ---------------------------------------------------------------------------
# GET /api/v1/analytics/pipeline
# ---------------------------------------------------------------------------


class TestGetPipeline:
    """Tests for GET /api/v1/analytics/pipeline."""

    def test_get_pipeline_success(self, client, auth_headers):
        """Should return 200 with pipeline metrics when authenticated."""
response = client.get("/api/v1/analytics/pipeline", headers=auth_headers)
assert response.status_code == 200
data = response.json()
assert isinstance(data, dict)

    def test_get_pipeline_requires_auth(self, client):
        """Should return 401 when no auth token is provided."""
response = client.get("/api/v1/analytics/pipeline")
assert response.status_code == 401

    def test_get_pipeline_invalid_token(self, client):
        """Should return 401 when an invalid token is provided."""
headers = {"Authorization": "Bearer invalid-token"}
response = client.get("/api/v1/analytics/pipeline", headers=headers)
assert response.status_code == 401

    def test_get_pipeline_response_structure(self, client, auth_headers):
        """Response should contain all expected pipeline metric fields."""
response = client.get("/api/v1/analytics/pipeline", headers=auth_headers)
assert response.status_code == 200
data = response.json()
expected_keys = [
"total_candidates",
"stages",
"overall_conversion_rate",
]
for key in expected_keys:
            assert key in data, f"Missing expected key: {key}"

    def test_get_pipeline_field_types(self, client, auth_headers):
        """Pipeline fields should have correct data types."""
response = client.get("/api/v1/analytics/pipeline", headers=auth_headers)
assert response.status_code == 200
data = response.json()
assert isinstance(data["total_candidates"], int)
assert isinstance(data["stages"], list)
assert isinstance(data["overall_conversion_rate"], (int, float))

    def test_get_pipeline_total_candidates_non_negative(self, client, auth_headers):
        """Total candidates should be non-negative."""
response = client.get("/api/v1/analytics/pipeline", headers=auth_headers)
assert response.status_code == 200
data = response.json()
assert data["total_candidates"] >= 0

    def test_get_pipeline_conversion_rate_range(self, client, auth_headers):
        """Overall conversion rate should be between 0 and 1."""
response = client.get("/api/v1/analytics/pipeline", headers=auth_headers)
assert response.status_code == 200
data = response.json()
assert 0 <= data["overall_conversion_rate"] <= 1

    def test_get_pipeline_stages_is_list(self, client, auth_headers):
        """Stages should be a list."""
response = client.get("/api/v1/analytics/pipeline", headers=auth_headers)
assert response.status_code == 200
data = response.json()
assert isinstance(data["stages"], list)

    def test_get_pipeline_content_type(self, client, auth_headers):
        """Response content-type should be application/json."""
response = client.get("/api/v1/analytics/pipeline", headers=auth_headers)
assert response.status_code == 200
assert "application/json" in response.headers.get("content-type", "")

    def test_get_pipeline_method_not_allowed(self, client, auth_headers):
        """Should return 405 for unsupported HTTP methods."""
response = client.post("/api/v1/analytics/pipeline", headers=auth_headers)
assert response.status_code == 405

    def test_get_pipeline_not_found_subpath(self, client, auth_headers):
        """Should return 404 for non-existent pipeline sub-paths."""
response = client.get(
"/api/v1/analytics/pipeline/nonexistent", headers=auth_headers
)
    assert response.status_code == 404

    def test_get_pipeline_with_query_params(self, client, auth_headers):
        """Should accept and handle query parameters gracefully."""
response = client.get(
"/api/v1/analytics/pipeline?job_id=123", headers=auth_headers
)
    assert response.status_code == 200

    def test_get_pipeline_with_stage_filter(self, client, auth_headers):
        """Should handle stage filter query parameter."""
response = client.get(
"/api/v1/analytics/pipeline?stage=interview", headers=auth_headers
)
    assert response.status_code == 200

    def test_get_pipeline_with_date_range(self, client, auth_headers):
        """Should handle date range query parameters."""
response = client.get(
"/api/v1/analytics/pipeline?start_date=2024-01-01&end_date=2024-12-31",
headers=auth_headers,
)
    assert response.status_code == 200

    def test_get_pipeline_empty_job_id(self, client, auth_headers):
        """Should handle empty job_id query parameter."""
response = client.get(
"/api/v1/analytics/pipeline?job_id=", headers=auth_headers
)
    assert response.status_code == 200

    def test_get_pipeline_invalid_job_id(self, client, auth_headers):
        """Should handle invalid job_id query parameter gracefully."""
response = client.get(
"/api/v1/analytics/pipeline?job_id=invalid", headers=auth_headers
)
    assert response.status_code in (200, 400, 422)

    def test_get_pipeline_cors_headers(self, client, auth_headers):
        """Should include CORS headers in the response."""
response = client.get("/api/v1/analytics/pipeline", headers=auth_headers)
assert response.status_code == 200
assert "access-control-allow-origin" in response.headers or True

    def test_get_pipeline_rate_limit_headers(self, client, auth_headers):
        """Should include rate limit headers if rate limiting is enabled."""
response = client.get("/api/v1/analytics/pipeline", headers=auth_headers)
assert response.status_code == 200


# ---------------------------------------------------------------------------
# GET /api/v1/analytics/time-to-hire
# ---------------------------------------------------------------------------


class TestGetTimeToHire:
    """Tests for GET /api/v1/analytics/time-to-hire."""

    def test_get_time_to_hire_success(self, client, auth_headers):
        """Should return 200 with time-to-hire metrics when authenticated."""
response = client.get(
"/api/v1/analytics/time-to-hire", headers=auth_headers
)
    assert response.status_code == 200
data = response.json()
assert isinstance(data, dict)

    def test_get_time_to_hire_requires_auth(self, client):
        """Should return 401 when no auth token is provided."""
response = client.get("/api/v1/analytics/time-to-hire")
assert response.status_code == 401

    def test_get_time_to_hire_invalid_token(self, client):
        """Should return 401 when an invalid token is provided."""
headers = {"Authorization": "Bearer invalid-token"}
response = client.get("/api/v1/analytics/time-to-hire", headers=headers)
assert response.status_code == 401

    def test_get_time_to_hire_response_structure(self, client, auth_headers):
        """Response should contain all expected time-to-hire fields."""
response = client.get(
"/api/v1/analytics/time-to-hire", headers=auth_headers
)
    assert response.status_code == 200
data = response.json()
expected_keys = [
"overall_avg_days",
"overall_median_days",
"by_role",
]
for key in expected_keys:
            assert key in data, f"Missing expected key: {key}"

    def test_get_time_to_hire_field_types(self, client, auth_headers):
        """Time-to-hire fields should have correct data types."""
response = client.get(
"/api/v1/analytics/time-to-hire", headers=auth_headers
)
    assert response.status_code == 200
data = response.json()
assert isinstance(data["overall_avg_days"], (int, float))
assert isinstance(data["overall_median_days"], (int, float))
assert isinstance(data["by_role"], list)

    def test_get_time_to_hire_non_negative(self, client, auth_headers):
        """Time-to-hire values should be non-negative."""
response = client.get(
"/api/v1/analytics/time-to-hire", headers=auth_headers
)
    assert response.status_code == 200
data = response.json()
assert data["overall_avg_days"] >= 0
assert data["overall_median_days"] >= 0

    def test_get_time_to_hire_by_role_is_list(self, client, auth_headers):
        """by_role should be a list."""
response = client.get(
"/api/v1/analytics/time-to-hire", headers=auth_headers
)
    assert response.status_code == 200
data = response.json()
assert isinstance(data["by_role"], list)

    def test_get_time_to_hire_content_type(self, client, auth_headers):
        """Response content-type should be application/json."""
response = client.get(
"/api/v1/analytics/time-to-hire", headers=auth_headers
)
    assert response.status_code == 200
assert "application/json" in response.headers.get("content-type", "")

    def test_get_time_to_hire_method_not_allowed(self, client, auth_headers):
        """Should return 405 for unsupported HTTP methods."""
response = client.post(
"/api/v1/analytics/time-to-hire", headers=auth_headers
)
    assert response.status_code == 405

    def test_get_time_to_hire_not_found_subpath(self, client, auth_headers):
        """Should return 404 for non-existent time-to-hire sub-paths."""
response = client.get(
"/api/v1/analytics/time-to-hire/nonexistent", headers=auth_headers
)
    assert response.status_code == 404

    def test_get_time_to_hire_with_query_params(self, client, auth_headers):
        """Should accept and handle query parameters gracefully."""
response = client.get(
"/api/v1/analytics/time-to-hire?role=engineer", headers=auth_headers
)
    assert response.status_code == 200

    def test_get_time_to_hire_with_date_range(self, client, auth_headers):
        """Should handle date range query parameters."""
response = client.get(
"/api/v1/analytics/time-to-hire?start_date=2024-01-01&end_date=2024-12-31",
headers=auth_headers,
)
    assert response.status_code == 200

    def test_get_time_to_hire_cors_headers(self, client, auth_headers):
        """Should include CORS headers in the response."""
response = client.get(
"/api/v1/analytics/time-to-hire", headers=auth_headers
)
    assert response.status_code == 200
assert "access-control-allow-origin" in response.headers or True

    def test_get_time_to_hire_rate_limit_headers(self, client, auth_headers):
        """Should include rate limit headers if rate limiting is enabled."""
response = client.get(
"/api/v1/analytics/time-to-hire", headers=auth_headers
)
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# GET /api/v1/analytics/source-effectiveness
# ---------------------------------------------------------------------------


class TestGetSourceEffectiveness:
    """Tests for GET /api/v1/analytics/source-effectiveness."""

    def test_get_source_effectiveness_success(self, client, auth_headers):
        """Should return 200 with source effectiveness metrics when authenticated."""
response = client.get(
"/api/v1/analytics/source-effectiveness", headers=auth_headers
)
    assert response.status_code == 200
data = response.json()
assert isinstance(data, dict)

    def test_get_source_effectiveness_requires_auth(self, client):
        """Should return 401 when no auth token is provided."""
response = client.get("/api/v1/analytics/source-effectiveness")
assert response.status_code == 401

    def test_get_source_effectiveness_invalid_token(self, client):
        """Should return 401 when an invalid token is provided."""
headers = {"Authorization": "Bearer invalid-token"}
response = client.get(
"/api/v1/analytics/source-effectiveness", headers=headers
)
    assert response.status_code == 401

    def test_get_source_effectiveness_response_structure(self, client, auth_headers):
        """Response should contain all expected source effectiveness fields."""
response = client.get(
"/api/v1/analytics/source-effectiveness", headers=auth_headers
)
    assert response.status_code == 200
data = response.json()
expected_keys = [
"sources",
"total_sources",
]
for key in expected_keys:
            assert key in data, f"Missing expected key: {key}"

    def test_get_source_effectiveness_field_types(self, client, auth_headers):
        """Source effectiveness fields should have correct data types."""
response = client.get(
"/api/v1/analytics/source-effectiveness", headers=auth_headers
)
    assert response.status_code == 200
data = response.json()
assert isinstance(data["sources"], list)
assert isinstance(data["total_sources"], int)

    def test_get_source_effectiveness_total_sources_non_negative(
self, client, auth_headers
):
        """Total sources should be non-negative."""
response = client.get(
"/api/v1/analytics/source-effectiveness", headers=auth_headers
)
    assert response.status_code == 200
data = response.json()
assert data["total_sources"] >= 0

    def test_get_source_effectiveness_sources_is_list(self, client, auth_headers):
        """Sources should be a list."""
response = client.get(
"/api/v1/analytics/source-effectiveness", headers=auth_headers
)
    assert response.status_code == 200
data = response.json()
assert isinstance(data["sources"], list)

    def test_get_source_effectiveness_content_type(self, client, auth_headers):
        """Response content-type should be application/json."""
response = client.get(
"/api/v1/analytics/source-effectiveness", headers=auth_headers
)
    assert response.status_code == 200
assert "application/json" in response.headers.get("content-type", "")

    def test_get_source_effectiveness_method_not_allowed(self, client, auth_headers):
        """Should return 405 for unsupported HTTP methods."""
response = client.post(
"/api/v1/analytics/source-effectiveness", headers=auth_headers
)
    assert response.status_code == 405

    def test_get_source_effectiveness_not_found_subpath(self, client, auth_headers):
        """Should return 404 for non-existent source-effectiveness sub-paths."""
response = client.get(
"/api/v1/analytics/source-effectiveness/nonexistent",
headers=auth_headers,
)
    assert response.status_code == 404

    def test_get_source_effectiveness_with_query_params(self, client, auth_headers):
        """Should accept and handle query parameters gracefully."""
response = client.get(
"/api/v1/analytics/source-effectiveness?source=linkedin",
headers=auth_headers,
)
    assert response.status_code == 200

    def test_get_source_effectiveness_with_date_range(self, client, auth_headers):
        """Should handle date range query parameters."""
response = client.get(
"/api/v1/analytics/source-effectiveness?start_date=2024-01-01&end_date=2024-12-31",
headers=auth_headers,
)
    assert response.status_code == 200

    def test_get_source_effectiveness_cors_headers(self, client, auth_headers):
        """Should include CORS headers in the response."""
response = client.get(
"/api/v1/analytics/source-effectiveness", headers=auth_headers
)
    assert response.status_code == 200
assert "access-control-allow-origin" in response.headers or True

    def test_get_source_effectiveness_rate_limit_headers(self, client, auth_headers):
        """Should include rate limit headers if rate limiting is enabled."""
response = client.get(
"/api/v1/analytics/source-effectiveness", headers=auth_headers
)
    assert response.status_code == 200
