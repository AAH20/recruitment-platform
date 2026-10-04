"""
Integration tests for the recruitment analytics workflow.

Tests cover:
- Recruitment metrics retrieval
- Pipeline funnel analysis
- Source effectiveness reporting
- Time-to-hire metrics
"""

import pytest
from datetime import datetime, timedelta
from typing import Any, Dict, List


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def api_client():
    """Return a configured API client for the recruitment platform."""
    from recruitment_platform.recruitment_platform.client import RecruitmentAPIClient

    return RecruitmentAPIClient(base_url="http://localhost:8000", api_key="test-key")


@pytest.fixture
def analytics_service(api_client):
    """Return an analytics service bound to the API client."""
    from recruitment_platform.recruitment_platform.services.analytics import AnalyticsService

    return AnalyticsService(client=api_client)


@pytest.fixture
def sample_date_range():
    """Return a standard date range for analytics queries."""
    end_date = datetime(2024, 12, 31)
    start_date = end_date - timedelta(days=90)
    return {"start_date": start_date.isoformat(), "end_date": end_date.isoformat()}


@pytest.fixture
def sample_recruitment_metrics() -> Dict[str, Any]:
    """Return a representative recruitment metrics payload."""
    return {
        "total_applications": 1250,
        "total_hires": 85,
        "total_rejections": 920,
        "total_withdrawals": 180,
        "open_positions": 42,
        "filled_positions": 38,
        "conversion_rate": 0.068,
        "period": {"start": "2024-10-01", "end": "2024-12-31"},
    }


@pytest.fixture
def sample_pipeline_funnel() -> Dict[str, Any]:
    """Return a representative pipeline funnel payload."""
    return {
        "stages": [
            {"name": "applied", "count": 1250, "percentage": 100.0},
            {"name": "screening", "count": 875, "percentage": 70.0},
            {"name": "interview", "count": 420, "percentage": 33.6},
            {"name": "offer", "count": 120, "percentage": 9.6},
            {"name": "hired", "count": 85, "percentage": 6.8},
        ],
        "total_candidates": 1250,
        "period": {"start": "2024-10-01", "end": "2024-12-31"},
    }


@pytest.fixture
def sample_source_effectiveness() -> Dict[str, Any]:
    """Return a representative source effectiveness payload."""
    return {
        "sources": [
            {
                "source": "linkedin",
                "applications": 450,
                "hires": 32,
                "cost_per_hire": 120.50,
                "quality_score": 8.2,
            },
            {
                "source": "indeed",
                "applications": 380,
                "hires": 25,
                "cost_per_hire": 95.00,
                "quality_score": 7.5,
            },
            {
                "source": "referral",
                "applications": 120,
                "hires": 18,
                "cost_per_hire": 50.00,
                "quality_score": 9.1,
            },
            {
                "source": "career_page",
                "applications": 300,
                "hires": 10,
                "cost_per_hire": 30.00,
                "quality_score": 6.8,
            },
        ],
        "total_sources": 4,
        "period": {"start": "2024-10-01", "end": "2024-12-31"},
    }


@pytest.fixture
def sample_time_to_hire() -> Dict[str, Any]:
    """Return a representative time-to-hire metrics payload."""
    return {
        "average_days_to_hire": 32.5,
        "median_days_to_hire": 28,
        "min_days_to_hire": 7,
        "max_days_to_hire": 95,
        "by_department": [
            {"department": "engineering", "average_days": 38.2, "hires": 22},
            {"department": "sales", "average_days": 25.0, "hires": 30},
            {"department": "marketing", "average_days": 29.5, "hires": 18},
            {"department": "operations", "average_days": 35.0, "hires": 15},
        ],
        "period": {"start": "2024-10-01", "end": "2024-12-31"},
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestRecruitmentMetrics:
    """Tests for the recruitment metrics endpoint."""

    def test_recruitment_metrics(
        self, analytics_service, sample_date_range, sample_recruitment_metrics, mocker
    ):
        """Verify recruitment metrics are retrieved and contain expected fields."""
        # Arrange
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_recruitment_metrics
        mocker.patch.object(
            analytics_service.client, "get", return_value=mock_response
        )

        # Act
        result = analytics_service.get_recruitment_metrics(**sample_date_range)

        # Assert
        assert result is not None
        assert result["total_applications"] == 1250
        assert result["total_hires"] == 85
        assert result["total_rejections"] == 920
        assert result["total_withdrawals"] == 180
        assert result["open_positions"] == 42
        assert result["filled_positions"] == 38
        assert result["conversion_rate"] == pytest.approx(0.068)
        assert "period" in result
        assert result["period"]["start"] == "2024-10-01"
        assert result["period"]["end"] == "2024-12-31"

    def test_recruitment_metrics_empty_period(
        self, analytics_service, mocker
    ):
        """Verify metrics handle periods with no data gracefully."""
        # Arrange
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "total_applications": 0,
            "total_hires": 0,
            "total_rejections": 0,
            "total_withdrawals": 0,
            "open_positions": 0,
            "filled_positions": 0,
            "conversion_rate": 0.0,
            "period": {"start": "2024-10-01", "end": "2024-12-31"},
        }
        mocker.patch.object(
            analytics_service.client, "get", return_value=mock_response
        )

        # Act
        result = analytics_service.get_recruitment_metrics(
            start_date="2024-10-01T00:00:00", end_date="2024-12-31T00:00:00"
        )

        # Assert
        assert result["total_applications"] == 0
        assert result["conversion_rate"] == 0.0


class TestPipelineFunnel:
    """Tests for the pipeline funnel endpoint."""

    def test_pipeline_funnel(
        self, analytics_service, sample_date_range, sample_pipeline_funnel, mocker
    ):
        """Verify pipeline funnel data is retrieved with correct stage ordering."""
        # Arrange
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_pipeline_funnel
        mocker.patch.object(
            analytics_service.client, "get", return_value=mock_response
        )

        # Act
        result = analytics_service.get_pipeline_funnel(**sample_date_range)

        # Assert
        assert result is not None
        assert "stages" in result
        assert len(result["stages"]) == 5

        stage_names = [s["name"] for s in result["stages"]]
        assert stage_names == ["applied", "screening", "interview", "offer", "hired"]

        # Verify counts decrease monotonically
        counts = [s["count"] for s in result["stages"]]
        assert counts == sorted(counts, reverse=True)

        # Verify percentages are consistent
        for stage in result["stages"]:
            expected_pct = (stage["count"] / result["total_candidates"]) * 100
            assert stage["percentage"] == pytest.approx(expected_pct, rel=0.01)

    def test_pipeline_funnel_stage_percentages_sum(
        self, analytics_service, sample_date_range, sample_pipeline_funnel, mocker
    ):
        """Verify funnel stage percentages are internally consistent."""
        # Arrange
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_pipeline_funnel
        mocker.patch.object(
            analytics_service.client, "get", return_value=mock_response
        )

        # Act
        result = analytics_service.get_pipeline_funnel(**sample_date_range)

        # Assert
        first_stage = result["stages"][0]
        assert first_stage["percentage"] == pytest.approx(100.0)

        last_stage = result["stages"][-1]
        assert last_stage["name"] == "hired"
        assert last_stage["count"] == 85


class TestSourceEffectiveness:
    """Tests for the source effectiveness endpoint."""

    def test_source_effectiveness(
        self, analytics_service, sample_date_range, sample_source_effectiveness, mocker
    ):
        """Verify source effectiveness data is retrieved and well-formed."""
        # Arrange
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_source_effectiveness
        mocker.patch.object(
            analytics_service.client, "get", return_value=mock_response
        )

        # Act
        result = analytics_service.get_source_effectiveness(**sample_date_range)

        # Assert
        assert result is not None
        assert "sources" in result
        assert len(result["sources"]) == 4

        for source in result["sources"]:
            assert "source" in source
            assert "applications" in source
            assert "hires" in source
            assert "cost_per_hire" in source
            assert "quality_score" in source
            assert source["applications"] >= source["hires"]
            assert source["cost_per_hire"] > 0
            assert 0 <= source["quality_score"] <= 10

    def test_source_effectiveness_sorted_by_quality(
        self, analytics_service, sample_date_range, sample_source_effectiveness, mocker
    ):
        """Verify sources can be ranked by quality score."""
        # Arrange
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_source_effectiveness
        mocker.patch.object(
            analytics_service.client, "get", return_value=mock_response
        )

        # Act
        result = analytics_service.get_source_effectiveness(**sample_date_range)

        # Assert
        sources_by_quality = sorted(
            result["sources"], key=lambda s: s["quality_score"], reverse=True
        )
        assert sources_by_quality[0]["source"] == "referral"
        assert sources_by_quality[0]["quality_score"] == 9.1

        sources_by_cost = sorted(
            result["sources"], key=lambda s: s["cost_per_hire"]
        )
        assert sources_by_cost[0]["source"] == "career_page"
        assert sources_by_cost[0]["cost_per_hire"] == 30.0


class TestTimeToHire:
    """Tests for the time-to-hire metrics endpoint."""

    def test_time_to_hire(
        self, analytics_service, sample_date_range, sample_time_to_hire, mocker
    ):
        """Verify time-to-hire metrics are retrieved with correct statistics."""
        # Arrange
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_time_to_hire
        mocker.patch.object(
            analytics_service.client, "get", return_value=mock_response
        )

        # Act
        result = analytics_service.get_time_to_hire(**sample_date_range)

        # Assert
        assert result is not None
        assert result["average_days_to_hire"] == pytest.approx(32.5)
        assert result["median_days_to_hire"] == 28
        assert result["min_days_to_hire"] == 7
        assert result["max_days_to_hire"] == 95
        assert result["min_days_to_hire"] <= result["median_days_to_hire"]
        assert result["median_days_to_hire"] <= result["average_days_to_hire"]
        assert result["average_days_to_hire"] <= result["max_days_to_hire"]

    def test_time_to_hire_by_department(
        self, analytics_service, sample_date_range, sample_time_to_hire, mocker
    ):
        """Verify department-level time-to-hire breakdown is present."""
        # Arrange
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_time_to_hire
        mocker.patch.object(
            analytics_service.client, "get", return_value=mock_response
        )

        # Act
        result = analytics_service.get_time_to_hire(**sample_date_range)

        # Assert
        assert "by_department" in result
        assert len(result["by_department"]) == 4

        departments = [d["department"] for d in result["by_department"]]
        assert "engineering" in departments
        assert "sales" in departments
        assert "marketing" in departments
        assert "operations" in departments

        for dept in result["by_department"]:
            assert dept["average_days"] > 0
            assert dept["hires"] > 0

    def test_time_to_hire_department_averages_weighted(
        self, analytics_service, sample_date_range, sample_time_to_hire, mocker
    ):
        """Verify overall average is consistent with department breakdown."""
        # Arrange
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_time_to_hire
        mocker.patch.object(
            analytics_service.client, "get", return_value=mock_response
        )

        # Act
        result = analytics_service.get_time_to_hire(**sample_date_range)

        # Assert
        total_hires = sum(d["hires"] for d in result["by_department"])
        weighted_avg = sum(
            d["average_days"] * d["hires"] for d in result["by_department"]
        ) / total_hires

        assert weighted_avg == pytest.approx(result["average_days_to_hire"], rel=0.05)
