"""
Comprehensive agent tests for recruitment analytics functions.

Tests cover:
- get_recruitment_metrics
- get_pipeline_funnel
- get_source_effectiveness
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from typing import Any

from recruitment_platform.agents.recruitment_analytics import (
get_recruitment_metrics,
get_pipeline_funnel,
get_source_effectiveness,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_db_session():
    """Provide a mock database session."""
session = MagicMock()
session.query.return_value = session
session.filter.return_value = session
session.all.return_value = []
session.first.return_value = None
session.scalar.return_value = 0
return session


@pytest.fixture
def sample_recruitment_metrics():
    """Sample recruitment metrics data."""
return {
"total_candidates": 150,
"active_candidates": 89,
"hired_candidates": 12,
"rejected_candidates": 45,
"in_pipeline_candidates": 83,
"avg_time_to_hire_days": 28.5,
"offer_acceptance_rate": 0.75,
"interview_conversion_rate": 0.42,
}


@pytest.fixture
def sample_pipeline_funnel():
    """Sample pipeline funnel data."""
return {
"stages": [
{"stage": "applied", "count": 150, "conversion_rate": 1.0},
{"stage": "screening", "count": 120, "conversion_rate": 0.80},
{"stage": "interview", "count": 63, "conversion_rate": 0.525},
{"stage": "offer", "count": 25, "conversion_rate": 0.397},
{"stage": "hired", "count": 12, "conversion_rate": 0.48},
],
"overall_conversion_rate": 0.08,
"bottleneck_stage": "interview",
}


@pytest.fixture
def sample_source_effectiveness():
    """Sample source effectiveness data."""
return {
"sources": [
{
"source": "linkedin",
"candidates": 60,
"hired": 6,
"cost_per_hire": 1200.00,
"roi": 2.5,
"quality_score": 8.2,
},
{
"source": "indeed",
"candidates": 45,
"hired": 3,
"cost_per_hire": 1800.00,
"roi": 1.8,
"quality_score": 6.5,
},
{
"source": "referral",
"candidates": 25,
"hired": 2,
"cost_per_hire": 500.00,
"roi": 4.0,
"quality_score": 9.1,
},
{
"source": "career_site",
"candidates": 20,
"hired": 1,
"cost_per_hire": 2000.00,
"roi": 1.2,
"quality_score": 5.8,
},
],
"best_source": "referral",
"worst_source": "career_site",
"total_spend": 185000.00,
}


@pytest.fixture
def date_range():
    """Standard date range for tests."""
end_date = datetime(2024, 6, 30)
start_date = end_date - timedelta(days=90)
return start_date, end_date


# ---------------------------------------------------------------------------
# Tests for get_recruitment_metrics
# ---------------------------------------------------------------------------


class TestGetRecruitmentMetrics:
    """Tests for the get_recruitment_metrics function."""

    def test_get_recruitment_metrics_returns_dict(
self, mock_db_session, sample_recruitment_metrics
):
        """Test that get_recruitment_metrics returns a dictionary."""
with patch(
"src.recruitment_platform.agents.recruitment_analytics._fetch_metrics",
return_value=sample_recruitment_metrics,
):
            result = get_recruitment_metrics(mock_db_session)

        assert isinstance(result, dict)

    def test_get_recruitment_metrics_contains_expected_keys(
self, mock_db_session, sample_recruitment_metrics
):
        """Test that the result contains all expected metric keys."""
with patch(
"src.recruitment_platform.agents.recruitment_analytics._fetch_metrics",
return_value=sample_recruitment_metrics,
):
            result = get_recruitment_metrics(mock_db_session)

        expected_keys = {
"total_candidates",
"active_candidates",
"hired_candidates",
"rejected_candidates",
"in_pipeline_candidates",
"avg_time_to_hire_days",
"offer_acceptance_rate",
"interview_conversion_rate",
}
assert expected_keys.issubset(result.keys())

    def test_get_recruitment_metrics_values_match(
self, mock_db_session, sample_recruitment_metrics
):
        """Test that returned values match the expected data."""
with patch(
"src.recruitment_platform.agents.recruitment_analytics._fetch_metrics",
return_value=sample_recruitment_metrics,
):
            result = get_recruitment_metrics(mock_db_session)

        assert result["total_candidates"] == 150
assert result["active_candidates"] == 89
assert result["hired_candidates"] == 12
assert result["rejected_candidates"] == 45
assert result["in_pipeline_candidates"] == 83
assert result["avg_time_to_hire_days"] == 28.5
assert result["offer_acceptance_rate"] == 0.75
assert result["interview_conversion_rate"] == 0.42

    def test_get_recruitment_metrics_with_date_range(
self, mock_db_session, sample_recruitment_metrics, date_range
):
        """Test that date range parameters are passed through correctly."""
start_date, end_date = date_range
with patch(
"src.recruitment_platform.agents.recruitment_analytics._fetch_metrics",
return_value=sample_recruitment_metrics,
) as mock_fetch:
            get_recruitment_metrics(
mock_db_session, start_date=start_date, end_date=end_date
)

        mock_fetch.assert_called_once()
call_kwargs = mock_fetch.call_args
assert call_kwargs[1]["start_date"] == start_date
assert call_kwargs[1]["end_date"] == end_date

    def test_get_recruitment_metrics_empty_result(self, mock_db_session):
        """Test handling of empty metrics result."""
with patch(
"src.recruitment_platform.agents.recruitment_analytics._fetch_metrics",
return_value={},
):
            result = get_recruitment_metrics(mock_db_session)

        assert result == {}

    def test_get_recruitment_metrics_with_filters(
self, mock_db_session, sample_recruitment_metrics
):
        """Test that additional filters are passed through."""
with patch(
"src.recruitment_platform.agents.recruitment_analytics._fetch_metrics",
return_value=sample_recruitment_metrics,
) as mock_fetch:
            get_recruitment_metrics(
mock_db_session, department="engineering", role="senior"
)

        call_kwargs = mock_fetch.call_args[1]
assert call_kwargs["department"] == "engineering"
assert call_kwargs["role"] == "senior"

    def test_get_recruitment_metrics_numeric_types(
self, mock_db_session, sample_recruitment_metrics
):
        """Test that numeric fields have correct types."""
with patch(
"src.recruitment_platform.agents.recruitment_analytics._fetch_metrics",
return_value=sample_recruitment_metrics,
):
            result = get_recruitment_metrics(mock_db_session)

        assert isinstance(result["total_candidates"], int)
assert isinstance(result["active_candidates"], int)
assert isinstance(result["hired_candidates"], int)
assert isinstance(result["avg_time_to_hire_days"], (int, float))
assert isinstance(result["offer_acceptance_rate"], float)
assert isinstance(result["interview_conversion_rate"], float)

    def test_get_recruitment_metrics_rate_bounds(
self, mock_db_session, sample_recruitment_metrics
):
        """Test that rate values are within valid bounds [0, 1]."""
with patch(
"src.recruitment_platform.agents.recruitment_analytics._fetch_metrics",
return_value=sample_recruitment_metrics,
):
            result = get_recruitment_metrics(mock_db_session)

        assert 0 <= result["offer_acceptance_rate"] <= 1
assert 0 <= result["interview_conversion_rate"] <= 1

    def test_get_recruitment_metrics_consistency(
self, mock_db_session, sample_recruitment_metrics
):
        """Test that candidate counts are internally consistent."""
with patch(
"src.recruitment_platform.agents.recruitment_analytics._fetch_metrics",
return_value=sample_recruitment_metrics,
):
            result = get_recruitment_metrics(mock_db_session)

        total = result["total_candidates"]
hired = result["hired_candidates"]
rejected = result["rejected_candidates"]
in_pipeline = result["in_pipeline_candidates"]

        assert hired + rejected + in_pipeline <= total
assert hired <= total
assert rejected <= total


# ---------------------------------------------------------------------------
# Tests for get_pipeline_funnel
# ---------------------------------------------------------------------------


class TestGetPipelineFunnel:
    """Tests for the get_pipeline_funnel function."""

    def test_get_pipeline_funnel_returns_dict(
self, mock_db_session, sample_pipeline_funnel
):
        """Test that get_pipeline_funnel returns a dictionary."""
with patch(
"src.recruitment_platform.agents.recruitment_analytics._fetch_funnel",
return_value=sample_pipeline_funnel,
):
            result = get_pipeline_funnel(mock_db_session)

        assert isinstance(result, dict)

    def test_get_pipeline_funnel_contains_stages(
self, mock_db_session, sample_pipeline_funnel
):
        """Test that the result contains pipeline stages."""
with patch(
"src.recruitment_platform.agents.recruitment_analytics._fetch_funnel",
return_value=sample_pipeline_funnel,
):
            result = get_pipeline_funnel(mock_db_session)

        assert "stages" in result
assert len(result["stages"]) > 0

    def test_get_pipeline_funnel_stage_structure(
self, mock_db_session, sample_pipeline_funnel
):
        """Test that each stage has the required fields."""
with patch(
"src.recruitment_platform.agents.recruitment_analytics._fetch_funnel",
return_value=sample_pipeline_funnel,
):
            result = get_pipeline_funnel(mock_db_session)

        for stage in result["stages"]:
            assert "stage" in stage
assert "count" in stage
assert "conversion_rate" in stage

    def test_get_pipeline_funnel_stage_values(
self, mock_db_session, sample_pipeline_funnel
):
        """Test that stage values match expected data."""
with patch(
"src.recruitment_platform.agents.recruitment_analytics._fetch_funnel",
return_value=sample_pipeline_funnel,
):
            result = get_pipeline_funnel(mock_db_session)

        stages = {s["stage"]: s for s in result["stages"]}
assert stages["applied"]["count"] == 150
assert stages["screening"]["count"] == 120
assert stages["interview"]["count"] == 63
assert stages["offer"]["count"] == 25
assert stages["hired"]["count"] == 12

    def test_get_pipeline_funnel_monotonic_decrease(
self, mock_db_session, sample_pipeline_funnel
):
        """Test that candidate counts decrease monotonically through the funnel."""
with patch(
"src.recruitment_platform.agents.recruitment_analytics._fetch_funnel",
return_value=sample_pipeline_funnel,
):
            result = get_pipeline_funnel(mock_db_session)

        counts = [s["count"] for s in result["stages"]]
for i in range(1, len(counts)):
            assert counts[i] <= counts[i - 1]

    def test_get_pipeline_funnel_conversion_rates_valid(
self, mock_db_session, sample_pipeline_funnel
):
        """Test that conversion rates are within valid bounds."""
with patch(
"src.recruitment_platform.agents.recruitment_analytics._fetch_funnel",
return_value=sample_pipeline_funnel,
):
            result = get_pipeline_funnel(mock_db_session)

        for stage in result["stages"]:
            assert 0 <= stage["conversion_rate"] <= 1

    def test_get_pipeline_funnel_overall_conversion(
self, mock_db_session, sample_pipeline_funnel
):
        """Test that overall conversion rate is present and valid."""
with patch(
"src.recruitment_platform.agents.recruitment_analytics._fetch_funnel",
return_value=sample_pipeline_funnel,
):
            result = get_pipeline_funnel(mock_db_session)

        assert "overall_conversion_rate" in result
assert 0 <= result["overall_conversion_rate"] <= 1

    def test_get_pipeline_funnel_bottleneck_identified(
self, mock_db_session, sample_pipeline_funnel
):
        """Test that a bottleneck stage is identified."""
with patch(
"src.recruitment_platform.agents.recruitment_analytics._fetch_funnel",
return_value=sample_pipeline_funnel,
):
            result = get_pipeline_funnel(mock_db_session)

        assert "bottleneck_stage" in result
assert result["bottleneck_stage"] in [s["stage"] for s in result["stages"]]

    def test_get_pipeline_funnel_with_date_range(
self, mock_db_session, sample_pipeline_funnel, date_range
):
        """Test that date range parameters are passed through."""
start_date, end_date = date_range
with patch(
"src.recruitment_platform.agents.recruitment_analytics._fetch_funnel",
return_value=sample_pipeline_funnel,
) as mock_fetch:
            get_pipeline_funnel(
mock_db_session, start_date=start_date, end_date=end_date
)

        call_kwargs = mock_fetch.call_args[1]
assert call_kwargs["start_date"] == start_date
assert call_kwargs["end_date"] == end_date

    def test_get_pipeline_funnel_empty_stages(self, mock_db_session):
        """Test handling of empty funnel data."""
with patch(
"src.recruitment_platform.agents.recruitment_analytics._fetch_funnel",
return_value={"stages": [], "overall_conversion_rate": 0},
):
            result = get_pipeline_funnel(mock_db_session)

        assert result["stages"] == []
assert result["overall_conversion_rate"] == 0

    def test_get_pipeline_funnel_first_stage_full_conversion(
self, mock_db_session, sample_pipeline_funnel
):
        """Test that the first stage has 100% conversion rate."""
with patch(
"src.recruitment_platform.agents.recruitment_analytics._fetch_funnel",
return_value=sample_pipeline_funnel,
):
            result = get_pipeline_funnel(mock_db_session)

        first_stage = result["stages"][0]
assert first_stage["conversion_rate"] == 1.0


# ---------------------------------------------------------------------------
# Tests for get_source_effectiveness
# ---------------------------------------------------------------------------


class TestGetSourceEffectiveness:
    """Tests for the get_source_effectiveness function."""

    def test_get_source_effectiveness_returns_dict(
self, mock_db_session, sample_source_effectiveness
):
        """Test that get_source_effectiveness returns a dictionary."""
with patch(
"src.recruitment_platform.agents.recruitment_analytics._fetch_sources",
return_value=sample_source_effectiveness,
):
            result = get_source_effectiveness(mock_db_session)

        assert isinstance(result, dict)

    def test_get_source_effectiveness_contains_sources(
self, mock_db_session, sample_source_effectiveness
):
        """Test that the result contains source data."""
with patch(
"src.recruitment_platform.agents.recruitment_analytics._fetch_sources",
return_value=sample_source_effectiveness,
):
            result = get_source_effectiveness(mock_db_session)

        assert "sources" in result
assert len(result["sources"]) > 0

    def test_get_source_effectiveness_source_structure(
self, mock_db_session, sample_source_effectiveness
):
        """Test that each source has the required fields."""
with patch(
"src.recruitment_platform.agents.recruitment_analytics._fetch_sources",
return_value=sample_source_effectiveness,
):
            result = get_source_effectiveness(mock_db_session)

        for source in result["sources"]:
            assert "source" in source
assert "candidates" in source
assert "hired" in source
assert "cost_per_hire" in source
assert "roi" in source
assert "quality_score" in source

    def test_get_source_effectiveness_values_match(
self, mock_db_session, sample_source_effectiveness
):
        """Test that source values match expected data."""
with patch(
"src.recruitment_platform.agents.recruitment_analytics._fetch_sources",
return_value=sample_source_effectiveness,
):
            result = get_source_effectiveness(mock_db_session)

        sources = {s["source"]: s for s in result["sources"]}
assert sources["linkedin"]["candidates"] == 60
assert sources["linkedin"]["hired"] == 6
assert sources["referral"]["roi"] == 4.0
assert sources["referral"]["quality_score"] == 9.1

    def test_get_source_effectiveness_best_source(
self, mock_db_session, sample_source_effectiveness
):
        """Test that the best source is correctly identified."""
with patch(
"src.recruitment_platform.agents.recruitment_analytics._fetch_sources",
return_value=sample_source_effectiveness,
):
            result = get_source_effectiveness(mock_db_session)

        assert "best_source" in result
assert result["best_source"] == "referral"

    def test_get_source_effectiveness_worst_source(
self, mock_db_session, sample_source_effectiveness
):
        """Test that the worst source is correctly identified."""
with patch(
"src.recruitment_platform.agents.recruitment_analytics._fetch_sources",
return_value=sample_source_effectiveness,
):
            result = get_source_effectiveness(mock_db_session)

        assert "worst_source" in result
assert result["worst_source"] == "career_site"

    def test_get_source_effectiveness_total_spend(
self, mock_db_session, sample_source_effectiveness
):
        """Test that total spend is present and valid."""
with patch(
"src.recruitment_platform.agents.recruitment_analytics._fetch_sources",
return_value=sample_source_effectiveness,
):
            result = get_source_effectiveness(mock_db_session)

        assert "total_spend" in result
assert result["total_spend"] > 0

    def test_get_source_effectiveness_roi_positive(
self, mock_db_session, sample_source_effectiveness
):
        """Test that ROI values are positive."""
with patch(
"src.recruitment_platform.agents.recruitment_analytics._fetch_sources",
return_value=sample_source_effectiveness,
):
            result = get_source_effectiveness(mock_db_session)

        for source in result["sources"]:
            assert source["roi"] > 0

    def test_get_source_effectiveness_quality_score_range(
self, mock_db_session, sample_source_effectiveness
):
        """Test that quality scores are within expected range."""
with patch(
"src.recruitment_platform.agents.recruitment_analytics._fetch_sources",
return_value=sample_source_effectiveness,
):
            result = get_source_effectiveness(mock_db_session)

        for source in result["sources"]:
            assert 0 <= source["quality_score"] <= 10

    def test_get_source_effectiveness_hired_not_exceed_candidates(
self, mock_db_session, sample_source_effectiveness
):
        """Test that hired count does not exceed candidate count."""
with patch(
"src.recruitment_platform.agents.recruitment_analytics._fetch_sources",
return_value=sample_source_effectiveness,
):
            result = get_source_effectiveness(mock_db_session)

        for source in result["sources"]:
            assert source["hired"] <= source["candidates"]

    def test_get_source_effectiveness_with_date_range(
self, mock_db_session, sample_source_effectiveness, date_range
):
        """Test that date range parameters are passed through."""
start_date, end_date = date_range
with patch(
"src.recruitment_platform.agents.recruitment_analytics._fetch_sources",
return_value=sample_source_effectiveness,
) as mock_fetch:
            get_source_effectiveness(
mock_db_session, start_date=start_date, end_date=end_date
)

        call_kwargs = mock_fetch.call_args[1]
assert call_kwargs["start_date"] == start_date
assert call_kwargs["end_date"] == end_date

    def test_get_source_effectiveness_empty_sources(self, mock_db_session):
        """Test handling of empty sources data."""
with patch(
"src.recruitment_platform.agents.recruitment_analytics._fetch_sources",
return_value={
"sources": [],
"best_source": None,
"worst_source": None,
"total_spend": 0,
},
):
            result = get_source_effectiveness(mock_db_session)

        assert result["sources"] == []
assert result["best_source"] is None
assert result["worst_source"] is None

    def test_get_source_effectiveness_cost_per_hire_positive(
self, mock_db_session, sample_source_effectiveness
):
        """Test that cost per hire is positive for all sources."""
with patch(
"src.recruitment_platform.agents.recruitment_analytics._fetch_sources",
return_value=sample_source_effectiveness,
):
            result = get_source_effectiveness(mock_db_session)

        for source in result["sources"]:
            assert source["cost_per_hire"] > 0

    def test_get_source_effectiveness_sorted_by_roi(
self, mock_db_session, sample_source_effectiveness
):
        """Test that sources can be sorted by ROI for ranking."""
with patch(
"src.recruitment_platform.agents.recruitment_analytics._fetch_sources",
return_value=sample_source_effectiveness,
):
            result = get_source_effectiveness(mock_db_session)

        sources = result["sources"]
rois = [s["roi"] for s in sources]
# Verify we can sort and the best source has the highest ROI
        sorted_sources = sorted(sources, key=lambda x: x["roi"], reverse=True)
assert sorted_sources[0]["source"] == result["best_source"]


# ---------------------------------------------------------------------------
# Integration-style tests
# ---------------------------------------------------------------------------


class TestRecruitmentAnalyticsIntegration:
    """Integration-style tests combining multiple analytics functions."""

    def test_all_functions_accept_same_session(
self,
mock_db_session,
sample_recruitment_metrics,
sample_pipeline_funnel,
sample_source_effectiveness,
):
        """Test that all three functions accept the same session object."""
with patch(
"src.recruitment_platform.agents.recruitment_analytics._fetch_metrics",
return_value=sample_recruitment_metrics,
), patch(
        "src.recruitment_platform.agents.recruitment_analytics._fetch_funnel",
return_value=sample_pipeline_funnel,
), patch(
        "src.recruitment_platform.agents.recruitment_analytics._fetch_sources",
return_value=sample_source_effectiveness,
):
            metrics = get_recruitment_metrics(mock_db_session)
funnel = get_pipeline_funnel(mock_db_session)
sources = get_source_effectiveness(mock_db_session)

        assert isinstance(metrics, dict)
assert isinstance(funnel, dict)
assert isinstance(sources, dict)

    def test_all_functions_accept_date_range(
self,
mock_db_session,
sample_recruitment_metrics,
sample_pipeline_funnel,
sample_source_effectiveness,
date_range,
):
        """Test that all three functions accept date range parameters."""
start_date, end_date = date_range
with patch(
"src.recruitment_platform.agents.recruitment_analytics._fetch_metrics",
return_value=sample_recruitment_metrics,
), patch(
        "src.recruitment_platform.agents.recruitment_analytics._fetch_funnel",
return_value=sample_pipeline_funnel,
), patch(
        "src.recruitment_platform.agents.recruitment_analytics._fetch_sources",
return_value=sample_source_effectiveness,
):
            get_recruitment_metrics(
mock_db_session, start_date=start_date, end_date=end_date
)
        get_pipeline_funnel(
mock_db_session, start_date=start_date, end_date=end_date
)
        get_source_effectiveness(
mock_db_session, start_date=start_date, end_date=end_date
)

    def test_metrics_total_matches_funnel_first_stage(
self, mock_db_session, sample_recruitment_metrics, sample_pipeline_funnel
):
        """Test that total candidates in metrics matches first funnel stage."""
with patch(
"src.recruitment_platform.agents.recruitment_analytics._fetch_metrics",
return_value=sample_recruitment_metrics,
), patch(
        "src.recruitment_platform.agents.recruitment_analytics._fetch_funnel",
return_value=sample_pipeline_funnel,
):
            metrics = get_recruitment_metrics(mock_db_session)
funnel = get_pipeline_funnel(mock_db_session)

        assert metrics["total_candidates"] == funnel["stages"][0]["count"]

    def test_metrics_hired_matches_funnel_last_stage(
self, mock_db_session, sample_recruitment_metrics, sample_pipeline_funnel
):
        """Test that hired candidates in metrics matches last funnel stage."""
with patch(
"src.recruitment_platform.agents.recruitment_analytics._fetch_metrics",
return_value=sample_recruitment_metrics,
), patch(
        "src.recruitment_platform.agents.recruitment_analytics._fetch_funnel",
return_value=sample_pipeline_funnel,
):
            metrics = get_recruitment_metrics(mock_db_session)
funnel = get_pipeline_funnel(mock_db_session)

        assert metrics["hired_candidates"] == funnel["stages"][-1]["count"]

    def test_source_hired_sum_matches_metrics(
self, mock_db_session, sample_recruitment_metrics, sample_source_effectiveness
):
        """Test that sum of hired across sources matches metrics hired count."""
with patch(
"src.recruitment_platform.agents.recruitment_analytics._fetch_metrics",
return_value=sample_recruitment_metrics,
), patch(
        "src.recruitment_platform.agents.recruitment_analytics._fetch_sources",
return_value=sample_source_effectiveness,
):
            metrics = get_recruitment_metrics(mock_db_session)
sources = get_source_effectiveness(mock_db_session)

        total_hired_from_sources = sum(s["hired"] for s in sources["sources"])
assert total_hired_from_sources == metrics["hired_candidates"]
