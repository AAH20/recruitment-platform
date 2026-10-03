"""
Integration tests for the report workflow.

Covers:
- Full report lifecycle: generate → get → download
- Report analytics retrieval
- Report export
"""

import pytest
from datetime import datetime, timedelta
from typing import Any, Dict, Generator

from recruitment_platform.main import create_app
from recruitment_platform.extensions import db


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def app() -> Generator[Any, None, None]:
    """Create application configured for testing."""
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "SECRET_KEY": "test-secret-key",
        }
    )

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app: Any) -> Generator[Any, None, None]:
    """Provide a test client."""
    return app.test_client()


@pytest.fixture
def auth_headers(client: Any) -> Dict[str, str]:
    """Register a user and return authenticated headers."""
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "SecurePass123!",
            "name": "Test User",
        },
    )
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "SecurePass123!"},
    )
    token = resp.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_job(client: Any, auth_headers: Dict[str, str]) -> Dict[str, Any]:
    """Create a sample job posting for report generation."""
    resp = client.post(
        "/api/v1/jobs",
        headers=auth_headers,
        json={
            "title": "Senior Software Engineer",
            "description": "Build scalable backend services",
            "department": "Engineering",
            "location": "Remote",
            "status": "open",
        },
    )
    return resp.get_json()


@pytest.fixture
def sample_candidates(client: Any, auth_headers: Dict[str, str], sample_job: Dict[str, Any]) -> list:
    """Create sample candidates for the job."""
    candidates = []
    for i in range(5):
        resp = client.post(
            "/api/v1/candidates",
            headers=auth_headers,
            json={
                "name": f"Candidate {i}",
                "email": f"candidate{i}@example.com",
                "job_id": sample_job["id"],
                "status": "applied" if i < 3 else "screening",
            },
        )
        candidates.append(resp.get_json())
    return candidates


@pytest.fixture
def generated_report(client: Any, auth_headers: Dict[str, str], sample_job: Dict[str, Any], sample_candidates: list) -> Dict[str, Any]:
    """Generate a report and return the response data."""
    resp = client.post(
        "/api/v1/reports/generate",
        headers=auth_headers,
        json={
            "job_id": sample_job["id"],
            "report_type": "candidate_pipeline",
            "date_range": {
                "start": (datetime.utcnow() - timedelta(days=30)).isoformat(),
                "end": datetime.utcnow().isoformat(),
            },
        },
    )
    return resp.get_json()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestFullReportLifecycle:
    """Test the complete report lifecycle: generate → get → download."""

    def test_full_report_lifecycle(
        self,
        client: Any,
        auth_headers: Dict[str, str],
        sample_job: Dict[str, Any],
        sample_candidates: list,
    ) -> None:
        """Generate a report, retrieve it, and download it."""
        # Step 1: Generate report
        gen_resp = client.post(
            "/api/v1/reports/generate",
            headers=auth_headers,
            json={
                "job_id": sample_job["id"],
                "report_type": "candidate_pipeline",
                "date_range": {
                    "start": (datetime.utcnow() - timedelta(days=30)).isoformat(),
                    "end": datetime.utcnow().isoformat(),
                },
            },
        )
        assert gen_resp.status_code == 201, f"Generate failed: {gen_resp.get_json()}"
        gen_data = gen_resp.get_json()
        assert "report_id" in gen_data
        assert gen_data["status"] in ("pending", "processing", "completed")
        report_id = gen_data["report_id"]

        # Step 2: Get report
        get_resp = client.get(
            f"/api/v1/reports/{report_id}",
            headers=auth_headers,
        )
        assert get_resp.status_code == 200, f"Get failed: {get_resp.get_json()}"
        report_data = get_resp.get_json()
        assert report_data["id"] == report_id
        assert report_data["job_id"] == sample_job["id"]
        assert report_data["report_type"] == "candidate_pipeline"
        assert "status" in report_data
        assert "created_at" in report_data

        # Step 3: Download report
        download_resp = client.get(
            f"/api/v1/reports/{report_id}/download",
            headers=auth_headers,
        )
        assert download_resp.status_code == 200, "Download failed"
        assert download_resp.content_type in (
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "text/csv",
            "application/octet-stream",
        )
        assert len(download_resp.data) > 0, "Downloaded report is empty"


class TestReportAnalytics:
    """Test report analytics retrieval."""

    def test_report_analytics(
        self,
        client: Any,
        auth_headers: Dict[str, str],
        generated_report: Dict[str, Any],
    ) -> None:
        """Generate a report and retrieve its analytics."""
        report_id = generated_report["report_id"]

        resp = client.get(
            f"/api/v1/reports/{report_id}/analytics",
            headers=auth_headers,
        )
        assert resp.status_code == 200, f"Analytics failed: {resp.get_json()}"
        analytics = resp.get_json()

        # Verify analytics structure
        assert "report_id" in analytics
        assert analytics["report_id"] == report_id
        assert "metrics" in analytics
        assert isinstance(analytics["metrics"], dict)

        # Verify expected metric keys
        metrics = analytics["metrics"]
        expected_keys = ["total_candidates", "conversion_rate", "time_to_hire"]
        for key in expected_keys:
            assert key in metrics, f"Missing metric: {key}"

        # Verify metric values are numeric
        for key, value in metrics.items():
            assert isinstance(value, (int, float)), f"Metric {key} is not numeric: {type(value)}"


class TestReportExport:
    """Test report export functionality."""

    def test_report_export(
        self,
        client: Any,
        auth_headers: Dict[str, str],
        generated_report: Dict[str, Any],
    ) -> None:
        """Generate a report and export it."""
        report_id = generated_report["report_id"]

        # Test CSV export
        resp = client.get(
            f"/api/v1/reports/{report_id}/export?format=csv",
            headers=auth_headers,
        )
        assert resp.status_code == 200, f"Export failed: {resp.get_json()}"
        assert resp.content_type in ("text/csv", "application/octet-stream")
        assert len(resp.data) > 0, "Exported file is empty"

        # Verify CSV content has headers
        content = resp.data.decode("utf-8")
        assert len(content) > 0
        lines = content.strip().split("\n")
        assert len(lines) >= 1, "CSV should have at least a header row"
