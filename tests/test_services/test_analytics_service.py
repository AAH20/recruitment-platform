"""Tests for AnalyticsService."""
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from recruitment_platform.services.analytics_service import (
    get_recruitment_metrics,
    get_pipeline_funnel,
    get_source_effectiveness,
    get_time_to_hire,
    _parse_time_range,
    _format_response,
    VALID_TIME_RANGES,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def valid_time_ranges():
    """Return all valid time range strings."""
    return ["7d", "30d", "90d", "180d", "365d", "all"]


@pytest.fixture
def sample_metrics_response():
    """Return a sample recruitment metrics response."""
    return {
        "success": True,
        "data": {
            "time_range": "30d",
            "period_start": "2024-01-01T00:00:00",
            "period_end": "2024-01-31T00:00:00",
            "total_applications": 150,
            "total_hires": 12,
            "open_positions": 8,
            "offer_acceptance_rate": 0.75,
            "applications_per_opening": 18.75,
            "active_candidates": 45,
            "rejected_candidates": 93,
            "withdrawn_candidates": 10,
        },
        "generated_at": "2024-01-31T00:00:00",
    }


@pytest.fixture
def sample_funnel_response():
    """Return a sample pipeline funnel response."""
    return {
        "success": True,
        "data": {
            "time_range": "30d",
            "period_start": "2024-01-01T00:00:00",
            "period_end": "2024-01-31T00:00:00",
            "stages": [
                {"stage": "applied", "count": 200},
                {"stage": "screened", "count": 150, "conversion_rate": 0.75},
                {"stage": "interviewed", "count": 80, "conversion_rate": 0.5333},
                {"stage": "offered", "count": 30, "conversion_rate": 0.375},
                {"stage": "hired", "count": 12, "conversion_rate": 0.4},
            ],
            "overall_conversion_rate": 0.06,
        },
        "generated_at": "2024-01-31T00:00:00",
    }


@pytest.fixture
def sample_source_effectiveness_response():
    """Return a sample source effectiveness response."""
    return {
        "success": True,
        "data": {
            "time_range": "30d",
            "period_start": "2024-01-01T00:00:00",
            "period_end": "2024-01-31T00:00:00",
            "sources": [
                {
                    "source": "linkedin",
                    "applications": 80,
                    "hires": 6,
                    "cost_per_hire": 250.0,
                    "quality_score": 0.82,
                    "conversion_rate": 0.075,
                },
                {
                    "source": "referral",
                    "applications": 40,
                    "hires": 4,
                    "cost_per_hire": 100.0,
                    "quality_score": 0.91,
                    "conversion_rate": 0.1,
                },
            ],
            "total_sources": 2,
            "most_effective_source": "referral",
        },
        "generated_at": "2024-01-31T00:00:00",
    }


@pytest.fixture
def sample_time_to_hire_response():
    """Return a sample time-to-hire response."""
    return {
        "success": True,
        "data": {
            "time_range": "30d",
            "period_start": "2024-01-01T00:00:00",
            "period_end": "2024-01-31T00:00:00",
            "overall": {
                "average_days": 28.5,
                "median_days": 26.0,
                "p25_days": 18.0,
                "p75_days": 38.0,
                "min_days": 7,
                "max_days": 65,
            },
            "by_department": [
                {"department": "engineering", "average_days": 30.2},
                {"department": "sales", "average_days": 22.1},
            ],
            "by_seniority": [
                {"seniority": "junior", "average_days": 20.0},
                {"seniority": "senior", "average_days": 35.0},
            ],
            "sample_size": 42,
        },
        "generated_at": "2024-01-31T00:00:00",
    }


# ---------------------------------------------------------------------------
# Tests for _parse_time_range helper
# ---------------------------------------------------------------------------


class TestParseTimeRange:
    """Test suite for _parse_time_range helper function."""

    def test_valid_time_ranges(self, valid_time_ranges):
        """Test that all valid time ranges are accepted."""
        for tr in valid_time_ranges:
            start, end = _parse_time_range(tr)
            assert isinstance(end, datetime)
            if tr == "all":
                assert start is None
            else:
                assert isinstance(start, datetime)
                assert start < end

    def test_7d_range(self):
        """Test 7-day time range calculation."""
        start, end = _parse_time_range("7d")
        delta = end - start
        assert delta.days == 7

    def test_30d_range(self):
        """Test 30-day time range calculation."""
        start, end = _parse_time_range("30d")
        delta = end - start
        assert delta.days == 30

    def test_90d_range(self):
        """Test 90-day time range calculation."""
        start, end = _parse_time_range("90d")
        delta = end - start
        assert delta.days == 90

    def test_180d_range(self):
        """Test 180-day time range calculation."""
        start, end = _parse_time_range("180d")
        delta = end - start
        assert delta.days == 180

    def test_365d_range(self):
        """Test 365-day time range calculation."""
        start, end = _parse_time_range("365d")
        delta = end - start
        assert delta.days == 365

    def test_all_range_returns_none_start(self):
        """Test that 'all' returns None for start datetime."""
        start, end = _parse_time_range("all")
        assert start is None
        assert isinstance(end, datetime)

    def test_invalid_time_range_raises_value_error(self):
        """Test that an invalid time range raises ValueError."""
        with pytest.raises(ValueError, match="Invalid time_range"):
            _parse_time_range("invalid")

    def test_empty_string_raises_value_error(self):
        """Test that an empty string raises ValueError."""
        with pytest.raises(ValueError, match="Invalid time_range"):
            _parse_time_range("")

    def test_case_sensitive(self):
        """Test that time range is case-sensitive."""
        with pytest.raises(ValueError):
            _parse_time_range("30D")

    def test_numeric_only_raises_value_error(self):
        """Test that a numeric-only string raises ValueError."""
        with pytest.raises(ValueError):
            _parse_time_range("30")


# ---------------------------------------------------------------------------
# Tests for _format_response helper
# ---------------------------------------------------------------------------


class TestFormatResponse:
    """Test suite for _format_response helper function."""

    def test_format_response_structure(self):
        """Test that _format_response wraps data correctly."""
        data = {"key": "value"}
        result = _format_response(data)
        assert result["success"] is True
        assert result["data"] == data
        assert "generated_at" in result

    def test_format_response_preserves_data(self):
        """Test that original data is preserved in the response."""
        data = {"nested": {"a": 1, "b": [1, 2, 3]}}
        result = _format_response(data)
        assert result["data"]["nested"]["a"] == 1
        assert result["data"]["nested"]["b"] == [1, 2, 3]

    def test_format_response_generated_at_is_isoformat(self):
        """Test that generated_at is an ISO format string."""
        result = _format_response({})
        # Should be parseable as ISO format
        parsed = datetime.fromisoformat(result["generated_at"])
        assert isinstance(parsed, datetime)

    def test_format_response_with_empty_data(self):
        """Test formatting with empty data dict."""
        result = _format_response({})
        assert result["success"] is True
        assert result["data"] == {}
        assert "generated_at" in result


# ---------------------------------------------------------------------------
# Tests for get_recruitment_metrics
# ---------------------------------------------------------------------------


class TestGetRecruitmentMetrics:
    """Test suite for get_recruitment_metrics function."""

    def test_returns_dict(self):
        """Test that get_recruitment_metrics returns a dict."""
        result = get_recruitment_metrics("30d")
        assert isinstance(result, dict)

    def test_response_has_success_key(self):
        """Test that response contains 'success' key set to True."""
        result = get_recruitment_metrics("30d")
        assert result["success"] is True

    def test_response_has_data_key(self):
        """Test that response contains 'data' key."""
        result = get_recruitment_metrics("30d")
        assert "data" in result

    def test_response_has_generated_at(self):
        """Test that response contains 'generated_at' timestamp."""
        result = get_recruitment_metrics("30d")
        assert "generated_at" in result
        # Verify it's a valid ISO format string
        datetime.fromisoformat(result["generated_at"])

    def test_data_contains_time_range(self):
        """Test that data contains the requested time range."""
        result = get_recruitment_metrics("30d")
        assert result["data"]["time_range"] == "30d"

    def test_data_contains_period_start(self):
        """Test that data contains period_start."""
        result = get_recruitment_metrics("30d")
        assert "period_start" in result["data"]

    def test_data_contains_period_end(self):
        """Test that data contains period_end."""
        result = get_recruitment_metrics("30d")
        assert "period_end" in result["data"]

    def test_period_start_is_isoformat(self):
        """Test that period_start is an ISO format string."""
        result = get_recruitment_metrics("30d")
        period_start = result["data"]["period_start"]
        if period_start is not None:
            datetime.fromisoformat(period_start)

    def test_period_end_is_isoformat(self):
        """Test that period_end is an ISO format string."""
        result = get_recruitment_metrics("30d")
        period_end = result["data"]["period_end"]
        datetime.fromisoformat(period_end)

    def test_all_time_range_period_start_is_none(self):
        """Test that 'all' time range has None period_start."""
        result = get_recruitment_metrics("all")
        assert result["data"]["period_start"] is None

    def test_data_contains_total_applications(self):
        """Test that data contains total_applications field."""
        result = get_recruitment_metrics("30d")
        assert "total_applications" in result["data"]
        assert isinstance(result["data"]["total_applications"], int)

    def test_data_contains_total_hires(self):
        """Test that data contains total_hires field."""
        result = get_recruitment_metrics("30d")
        assert "total_hires" in result["data"]
        assert isinstance(result["data"]["total_hires"], int)

    def test_data_contains_open_positions(self):
        """Test that data contains open_positions field."""
        result = get_recruitment_metrics("30d")
        assert "open_positions" in result["data"]
        assert isinstance(result["data"]["open_positions"], int)

    def test_data_contains_offer_acceptance_rate(self):
        """Test that data contains offer_acceptance_rate field."""
        result = get_recruitment_metrics("30d")
        assert "offer_acceptance_rate" in result["data"]
        assert isinstance(result["data"]["offer_acceptance_rate"], (int, float))

    def test_data_contains_applications_per_opening(self):
        """Test that data contains applications_per_opening field."""
        result = get_recruitment_metrics("30d")
        assert "applications_per_opening" in result["data"]
        assert isinstance(result["data"]["applications_per_opening"], (int, float))

    def test_data_contains_active_candidates(self):
        """Test that data contains active_candidates field."""
        result = get_recruitment_metrics("30d")
        assert "active_candidates" in result["data"]
        assert isinstance(result["data"]["active_candidates"], int)

    def test_data_contains_rejected_candidates(self):
        """Test that data contains rejected_candidates field."""
        result = get_recruitment_metrics("30d")
        assert "rejected_candidates" in result["data"]
        assert isinstance(result["data"]["rejected_candidates"], int)

    def test_data_contains_withdrawn_candidates(self):
        """Test that data contains withdrawn_candidates field."""
        result = get_recruitment_metrics("30d")
        assert "withdrawn_candidates" in result["data"]
        assert isinstance(result["data"]["withdrawn_candidates"], int)

    def test_all_valid_time_ranges(self, valid_time_ranges):
        """Test that all valid time ranges produce valid responses."""
        for tr in valid_time_ranges:
            result = get_recruitment_metrics(tr)
            assert result["success"] is True
            assert result["data"]["time_range"] == tr

    def test_invalid_time_range_raises_value_error(self):
        """Test that invalid time range raises ValueError."""
        with pytest.raises(ValueError, match="Invalid time_range"):
            get_recruitment_metrics("invalid")

    def test_invalid_time_range_raises_value_error_empty(self):
        """Test that empty string raises ValueError."""
        with pytest.raises(ValueError):
            get_recruitment_metrics("")

    def test_invalid_time_range_raises_value_error_numeric(self):
        """Test that numeric-only string raises ValueError."""
        with pytest.raises(ValueError):
            get_recruitment_metrics("45")

    def test_metrics_values_are_zero_by_default(self):
        """Test that default metrics values are zero (no DB)."""
        result = get_recruitment_metrics("30d")
        data = result["data"]
        assert data["total_applications"] == 0
        assert data["total_hires"] == 0
        assert data["open_positions"] == 0
        assert data["offer_acceptance_rate"] == 0.0
        assert data["applications_per_opening"] == 0.0
        assert data["active_candidates"] == 0
        assert data["rejected_candidates"] == 0
        assert data["withdrawn_candidates"] == 0

    @patch("recruitment_platform.services.analytics_service._parse_time_range")
    def test_runtime_error_when_parse_fails(self, mock_parse):
        """Test that RuntimeError is raised when parsing fails."""
        mock_parse.side_effect = Exception("parse error")
        with pytest.raises(RuntimeError, match="Failed to retrieve recruitment metrics"):
            get_recruitment_metrics("30d")

    @patch("recruitment_platform.services.analytics_service.logger")
    def test_logging_on_success(self, mock_logger):
        """Test that info is logged on successful retrieval."""
        get_recruitment_metrics("30d")
        mock_logger.info.assert_called_once()

    @patch("recruitment_platform.services.analytics_service.logger")
    def test_logging_on_error(self, mock_logger):
        """Test that error is logged on failure."""
        with patch(
            "recruitment_platform.services.analytics_service._parse_time_range"
        ) as mock_parse:
            mock_parse.side_effect = Exception("unexpected")
            with pytest.raises(RuntimeError):
                get_recruitment_metrics("30d")
            mock_logger.error.assert_called_once()


# ---------------------------------------------------------------------------
# Tests for get_pipeline_funnel
# ---------------------------------------------------------------------------


class TestGetPipelineFunnel:
    """Test suite for get_pipeline_funnel function."""

    def test_returns_dict(self):
        """Test that get_pipeline_funnel returns a dict."""
        result = get_pipeline_funnel("30d")
        assert isinstance(result, dict)

    def test_response_has_success_key(self):
        """Test that response contains 'success' key set to True."""
        result = get_pipeline_funnel("30d")
        assert result["success"] is True

    def test_response_has_data_key(self):
        """Test that response contains 'data' key."""
        result = get_pipeline_funnel("30d")
        assert "data" in result

    def test_response_has_generated_at(self):
        """Test that response contains 'generated_at' timestamp."""
        result = get_pipeline_funnel("30d")
        assert "generated_at" in result
        datetime.fromisoformat(result["generated_at"])

    def test_data_contains_time_range(self):
        """Test that data contains the requested time range."""
        result = get_pipeline_funnel("30d")
        assert result["data"]["time_range"] == "30d"

    def test_data_contains_period_start(self):
        """Test that data contains period_start."""
        result = get_pipeline_funnel("30d")
        assert "period_start" in result["data"]

    def test_data_contains_period_end(self):
        """Test that data contains period_end."""
        result = get_pipeline_funnel("30d")
        assert "period_end" in result["data"]

    def test_all_time_range_period_start_is_none(self):
        """Test that 'all' time range has None period_start."""
        result = get_pipeline_funnel("all")
        assert result["data"]["period_start"] is None

    def test_data_contains_stages(self):
        """Test that data contains stages list."""
        result = get_pipeline_funnel("30d")
        assert "stages" in result["data"]
        assert isinstance(result["data"]["stages"], list)

    def test_stages_has_five_stages(self):
        """Test that there are exactly 5 pipeline stages."""
        result = get_pipeline_funnel("30d")
        assert len(result["data"]["stages"]) == 5

    def test_stage_names_are_correct(self):
        """Test that stage names match expected pipeline stages."""
        result = get_pipeline_funnel("30d")
        stage_names = [s["stage"] for s in result["data"]["stages"]]
        assert stage_names == ["applied", "screened", "interviewed", "offered", "hired"]

    def test_each_stage_has_count(self):
        """Test that each stage has a count field."""
        result = get_pipeline_funnel("30d")
        for stage in result["data"]["stages"]:
            assert "count" in stage
            assert isinstance(stage["count"], int)

    def test_first_stage_has_no_conversion_rate(self):
        """Test that the first stage (applied) has no conversion_rate."""
        result = get_pipeline_funnel("30d")
        first_stage = result["data"]["stages"][0]
        assert "conversion_rate" not in first_stage

    def test_subsequent_stages_have_conversion_rate(self):
        """Test that stages after the first have conversion_rate."""
        result = get_pipeline_funnel("30d")
        for stage in result["data"]["stages"][1:]:
            assert "conversion_rate" in stage
            assert isinstance(stage["conversion_rate"], (int, float))

    def test_conversion_rates_are_zero_when_no_data(self):
        """Test that conversion rates are 0.0 when counts are zero."""
        result = get_pipeline_funnel("30d")
        for stage in result["data"]["stages"][1:]:
            assert stage["conversion_rate"] == 0.0

    def test_data_contains_overall_conversion_rate(self):
        """Test that data contains overall_conversion_rate."""
        result = get_pipeline_funnel("30d")
        assert "overall_conversion_rate" in result["data"]
        assert isinstance(result["data"]["overall_conversion_rate"], (int, float))

    def test_overall_conversion_rate_is_zero_by_default(self):
        """Test that overall_conversion_rate is 0.0 with no data."""
        result = get_pipeline_funnel("30d")
        assert result["data"]["overall_conversion_rate"] == 0.0

    def test_all_valid_time_ranges(self, valid_time_ranges):
        """Test that all valid time ranges produce valid responses."""
        for tr in valid_time_ranges:
            result = get_pipeline_funnel(tr)
            assert result["success"] is True
            assert result["data"]["time_range"] == tr

    def test_invalid_time_range_raises_value_error(self):
        """Test that invalid time range raises ValueError."""
        with pytest.raises(ValueError, match="Invalid time_range"):
            get_pipeline_funnel("invalid")

    def test_invalid_time_range_raises_value_error_empty(self):
        """Test that empty string raises ValueError."""
        with pytest.raises(ValueError):
            get_pipeline_funnel("")

    @patch("recruitment_platform.services.analytics_service._parse_time_range")
    def test_runtime_error_when_parse_fails(self, mock_parse):
        """Test that RuntimeError is raised when parsing fails."""
        mock_parse.side_effect = Exception("parse error")
        with pytest.raises(RuntimeError, match="Failed to retrieve pipeline funnel"):
            get_pipeline_funnel("30d")

    @patch("recruitment_platform.services.analytics_service.logger")
    def test_logging_on_success(self, mock_logger):
        """Test that info is logged on successful retrieval."""
        get_pipeline_funnel("30d")
        mock_logger.info.assert_called_once()

    @patch("recruitment_platform.services.analytics_service.logger")
    def test_logging_on_error(self, mock_logger):
        """Test that error is logged on failure."""
        with patch(
            "recruitment_platform.services.analytics_service._parse_time_range"
        ) as mock_parse:
            mock_parse.side_effect = Exception("unexpected")
            with pytest.raises(RuntimeError):
                get_pipeline_funnel("30d")
            mock_logger.error.assert_called_once()


# ---------------------------------------------------------------------------
# Tests for get_source_effectiveness
# ---------------------------------------------------------------------------


class TestGetSourceEffectiveness:
    """Test suite for get_source_effectiveness function."""

    def test_returns_dict(self):
        """Test that get_source_effectiveness returns a dict."""
        result = get_source_effectiveness("30d")
        assert isinstance(result, dict)

    def test_response_has_success_key(self):
        """Test that response contains 'success' key set to True."""
        result = get_source_effectiveness("30d")
        assert result["success"] is True

    def test_response_has_data_key(self):
        """Test that response contains 'data' key."""
        result = get_source_effectiveness("30d")
        assert "data" in result

    def test_response_has_generated_at(self):
        """Test that response contains 'generated_at' timestamp."""
        result = get_source_effectiveness("30d")
        assert "generated_at" in result
        datetime.fromisoformat(result["generated_at"])

    def test_data_contains_time_range(self):
        """Test that data contains the requested time range."""
        result = get_source_effectiveness("30d")
        assert result["data"]["time_range"] == "30d"

    def test_data_contains_period_start(self):
        """Test that data contains period_start."""
        result = get_source_effectiveness("30d")
        assert "period_start" in result["data"]

    def test_data_contains_period_end(self):
        """Test that data contains period_end."""
        result = get_source_effectiveness("30d")
        assert "period_end" in result["data"]

    def test_all_time_range_period_start_is_none(self):
        """Test that 'all' time range has None period_start."""
        result = get_source_effectiveness("all")
        assert result["data"]["period_start"] is None

    def test_data_contains_sources(self):
        """Test that data contains sources list."""
        result = get_source_effectiveness("30d")
        assert "sources" in result["data"]
        assert isinstance(result["data"]["sources"], list)

    def test_sources_is_not_empty(self):
        """Test that sources list is not empty."""
        result = get_source_effectiveness("30d")
        assert len(result["data"]["sources"]) > 0

    def test_expected_sources_present(self):
        """Test that expected recruitment sources are present."""
        result = get_source_effectiveness("30d")
        source_names = [s["source"] for s in result["data"]["sources"]]
        assert "linkedin" in source_names
        assert "referral" in source_names
        assert "indeed" in source_names
        assert "company_careers_page" in source_names

    def test_each_source_has_required_fields(self):
        """Test that each source has all required fields."""
        result = get_source_effectiveness("30d")
        required_fields = [
            "source",
            "applications",
            "hires",
            "cost_per_hire",
            "quality_score",
            "conversion_rate",
        ]
        for source in result["data"]["sources"]:
            for field in required_fields:
                assert field in source, f"Missing field '{field}' in source {source.get('source', 'unknown')}"

    def test_source_applications_is_int(self):
        """Test that applications is an integer."""
        result = get_source_effectiveness("30d")
        for source in result["data"]["sources"]:
            assert isinstance(source["applications"], int)

    def test_source_hires_is_int(self):
        """Test that hires is an integer."""
        result = get_source_effectiveness("30d")
        for source in result["data"]["sources"]:
            assert isinstance(source["hires"], int)

    def test_source_cost_per_hire_is_numeric(self):
        """Test that cost_per_hire is numeric."""
        result = get_source_effectiveness("30d")
        for source in result["data"]["sources"]:
            assert isinstance(source["cost_per_hire"], (int, float))

    def test_source_quality_score_is_numeric(self):
        """Test that quality_score is numeric."""
        result = get_source_effectiveness("30d")
        for source in result["data"]["sources"]:
            assert isinstance(source["quality_score"], (int, float))

    def test_source_conversion_rate_is_numeric(self):
        """Test that conversion_rate is numeric."""
        result = get_source_effectiveness("30d")
        for source in result["data"]["sources"]:
            assert isinstance(source["conversion_rate"], (int, float))

    def test_data_contains_total_sources(self):
        """Test that data contains total_sources count."""
        result = get_source_effectiveness("30d")
        assert "total_sources" in result["data"]
        assert isinstance(result["data"]["total_sources"], int)

    def test_total_sources_matches_list_length(self):
        """Test that total_sources matches the length of sources list."""
        result = get_source_effectiveness("30d")
        assert result["data"]["total_sources"] == len(result["data"]["sources"])

    def test_data_contains_most_effective_source(self):
        """Test that data contains most_effective_source field."""
        result = get_source_effectiveness("30d")
        assert "most_effective_source" in result["data"]

    def test_most_effective_source_is_none_by_default(self):
        """Test that most_effective_source is None when no data."""
        result = get_source_effectiveness("30d")
        assert result["data"]["most_effective_source"] is None

    def test_all_source_values_zero_by_default(self):
        """Test that all source metrics are zero with no data."""
        result = get_source_effectiveness("30d")
        for source in result["data"]["sources"]:
            assert source["applications"] == 0
            assert source["hires"] == 0
            assert source["cost_per_hire"] == 0.0
            assert source["quality_score"] == 0.0
            assert source["conversion_rate"] == 0.0

    def test_all_valid_time_ranges(self, valid_time_ranges):
        """Test that all valid time ranges produce valid responses."""
        for tr in valid_time_ranges:
            result = get_source_effectiveness(tr)
            assert result["success"] is True
            assert result["data"]["time_range"] == tr

    def test_invalid_time_range_raises_value_error(self):
        """Test that invalid time range raises ValueError."""
        with pytest.raises(ValueError, match="Invalid time_range"):
            get_source_effectiveness("invalid")

    def test_invalid_time_range_raises_value_error_empty(self):
        """Test that empty string raises ValueError."""
        with pytest.raises(ValueError):
            get_source_effectiveness("")

    @patch("recruitment_platform.services.analytics_service._parse_time_range")
    def test_runtime_error_when_parse_fails(self, mock_parse):
        """Test that RuntimeError is raised when parsing fails."""
        mock_parse.side_effect = Exception("parse error")
        with pytest.raises(RuntimeError, match="Failed to retrieve source effectiveness"):
            get_source_effectiveness("30d")

    @patch("recruitment_platform.services.analytics_service.logger")
    def test_logging_on_success(self, mock_logger):
        """Test that info is logged on successful retrieval."""
        get_source_effectiveness("30d")
        mock_logger.info.assert_called_once()

    @patch("recruitment_platform.services.analytics_service.logger")
    def test_logging_on_error(self, mock_logger):
        """Test that error is logged on failure."""
        with patch(
            "recruitment_platform.services.analytics_service._parse_time_range"
        ) as mock_parse:
            mock_parse.side_effect = Exception("unexpected")
            with pytest.raises(RuntimeError):
                get_source_effectiveness("30d")
            mock_logger.error.assert_called_once()


# ---------------------------------------------------------------------------
# Tests for get_time_to_hire
# ---------------------------------------------------------------------------


class TestGetTimeToHire:
    """Test suite for get_time_to_hire function."""

    def test_returns_dict(self):
        """Test that get_time_to_hire returns a dict."""
        result = get_time_to_hire("30d")
        assert isinstance(result, dict)

    def test_response_has_success_key(self):
        """Test that response contains 'success' key set to True."""
        result = get_time_to_hire("30d")
        assert result["success"] is True

    def test_response_has_data_key(self):
        """Test that response contains 'data' key."""
        result = get_time_to_hire("30d")
        assert "data" in result

    def test_response_has_generated_at(self):
        """Test that response contains 'generated_at' timestamp."""
        result = get_time_to_hire("30d")
        assert "generated_at" in result
        datetime.fromisoformat(result["generated_at"])

    def test_data_contains_time_range(self):
        """Test that data contains the requested time range."""
        result = get_time_to_hire("30d")
        assert result["data"]["time_range"] == "30d"

    def test_data_contains_period_start(self):
        """Test that data contains period_start."""
        result = get_time_to_hire("30d")
        assert "period_start" in result["data"]

    def test_data_contains_period_end(self):
        """Test that data contains period_end."""
        result = get_time_to_hire("30d")
        assert "period_end" in result["data"]

    def test_all_time_range_period_start_is_none(self):
        """Test that 'all' time range has None period_start."""
        result = get_time_to_hire("all")
        assert result["data"]["period_start"] is None

    def test_data_contains_overall(self):
        """Test that data contains overall statistics."""
        result = get_time_to_hire("30d")
        assert "overall" in result["data"]
        assert isinstance(result["data"]["overall"], dict)

    def test_overall_contains_average_days(self):
        """Test that overall contains average_days."""
        result = get_time_to_hire("30d")
        assert "average_days" in result["data"]["overall"]
        assert isinstance(result["data"]["overall"]["average_days"], (int, float))

    def test_overall_contains_median_days(self):
        """Test that overall contains median_days."""
        result = get_time_to_hire("30d")
        assert "median_days" in result["data"]["overall"]
        assert isinstance(result["data"]["overall"]["median_days"], (int, float))

    def test_overall_contains_p25_days(self):
        """Test that overall contains p25_days."""
        result = get_time_to_hire("30d")
        assert "p25_days" in result["data"]["overall"]
        assert isinstance(result["data"]["overall"]["p25_days"], (int, float))

    def test_overall_contains_p75_days(self):
        """Test that overall contains p75_days."""
        result = get_time_to_hire("30d")
        assert "p75_days" in result["data"]["overall"]
        assert isinstance(result["data"]["overall"]["p75_days"], (int, float))

    def test_overall_contains_min_days(self):
        """Test that overall contains min_days."""
        result = get_time_to_hire("30d")
        assert "min_days" in result["data"]["overall"]
        assert isinstance(result["data"]["overall"]["min_days"], int)

    def test_overall_contains_max_days(self):
        """Test that overall contains max_days."""
        result = get_time_to_hire("30d")
        assert "max_days" in result["data"]["overall"]
        assert isinstance(result["data"]["overall"]["max_days"], int)

    def test_overall_values_zero_by_default(self):
        """Test that overall stats are zero with no data."""
        result = get_time_to_hire("30d")
        overall = result["data"]["overall"]
        assert overall["average_days"] == 0.0
        assert overall["median_days"] == 0.0
        assert overall["p25_days"] == 0.0
        assert overall["p75_days"] == 0.0
        assert overall["min_days"] == 0
        assert overall["max_days"] == 0

    def test_data_contains_by_department(self):
        """Test that data contains by_department list."""
        result = get_time_to_hire("30d")
        assert "by_department" in result["data"]
        assert isinstance(result["data"]["by_department"], list)

    def test_data_contains_by_seniority(self):
        """Test that data contains by_seniority list."""
        result = get_time_to_hire("30d")
        assert "by_seniority" in result["data"]
        assert isinstance(result["data"]["by_seniority"], list)

    def test_data_contains_sample_size(self):
        """Test that data contains sample_size."""
        result = get_time_to_hire("30d")
        assert "sample_size" in result["data"]
        assert isinstance(result["data"]["sample_size"], int)

    def test_sample_size_is_zero_by_default(self):
        """Test that sample_size is 0 with no data."""
        result = get_time_to_hire("30d")
        assert result["data"]["sample_size"] == 0

    def test_by_department_is_empty_by_default(self):
        """Test that by_department is empty with no data."""
        result = get_time_to_hire("30d")
        assert result["data"]["by_department"] == []

    def test_by_seniority_is_empty_by_default(self):
        """Test that by_seniority is empty with no data."""
        result = get_time_to_hire("30d")
        assert result["data"]["by_seniority"] == []

    def test_all_valid_time_ranges(self, valid_time_ranges):
        """Test that all valid time ranges produce valid responses."""
        for tr in valid_time_ranges:
            result = get_time_to_hire(tr)
            assert result["success"] is True
            assert result["data"]["time_range"] == tr

    def test_invalid_time_range_raises_value_error(self):
        """Test that invalid time range raises ValueError."""
        with pytest.raises(ValueError, match="Invalid time_range"):
            get_time_to_hire("invalid")

    def test_invalid_time_range_raises_value_error_empty(self):
        """Test that empty string raises ValueError."""
        with pytest.raises(ValueError):
            get_time_to_hire("")

    @patch("recruitment_platform.services.analytics_service._parse_time_range")
    def test_runtime_error_when_parse_fails(self, mock_parse):
        """Test that RuntimeError is raised when parsing fails."""
        mock_parse.side_effect = Exception("parse error")
        with pytest.raises(RuntimeError, match="Failed to retrieve time-to-hire metrics"):
            get_time_to_hire("30d")

    @patch("recruitment_platform.services.analytics_service.logger")
    def test_logging_on_success(self, mock_logger):
        """Test that info is logged on successful retrieval."""
        get_time_to_hire("30d")
        mock_logger.info.assert_called_once()

    @patch("recruitment_platform.services.analytics_service.logger")
    def test_logging_on_error(self, mock_logger):
        """Test that error is logged on failure."""
        with patch(
            "recruitment_platform.services.analytics_service._parse_time_range"
        ) as mock_parse:
            mock_parse.side_effect = Exception("unexpected")
            with pytest.raises(RuntimeError):
                get_time_to_hire("30d")
            mock_logger.error.assert_called_once()


# ---------------------------------------------------------------------------
# Cross-cutting tests
# ---------------------------------------------------------------------------


class TestAnalyticsServiceConsistency:
    """Cross-cutting tests for consistency across all analytics functions."""

    def test_all_functions_return_success_true(self):
        """Test that all analytics functions return success=True."""
        for func in [get_recruitment_metrics, get_pipeline_funnel, get_source_effectiveness, get_time_to_hire]:
            result = func("30d")
            assert result["success"] is True, f"{func.__name__} did not return success=True"

    def test_all_functions_have_generated_at(self):
        """Test that all analytics functions include generated_at."""
        for func in [get_recruitment_metrics, get_pipeline_funnel, get_source_effectiveness, get_time_to_hire]:
            result = func("30d")
            assert "generated_at" in result, f"{func.__name__} missing generated_at"

    def test_all_functions_accept_all_time_ranges(self, valid_time_ranges):
        """Test that all functions accept all valid time ranges."""
        funcs = [get_recruitment_metrics, get_pipeline_funnel, get_source_effectiveness, get_time_to_hire]
        for func in funcs:
            for tr in valid_time_ranges:
                result = func(tr)
                assert result["success"] is True, f"{func.__name__} failed for time_range={tr}"

    def test_all_functions_reject_invalid_time_range(self):
        """Test that all functions reject invalid time ranges."""
        funcs = [get_recruitment_metrics, get_pipeline_funnel, get_source_effectiveness, get_time_to_hire]
        for func in funcs:
            with pytest.raises(ValueError, match="Invalid time_range"):
                func("invalid")

    def test_all_functions_reject_empty_time_range(self):
        """Test that all functions reject empty time ranges."""
        funcs = [get_recruitment_metrics, get_pipeline_funnel, get_source_effectiveness, get_time_to_hire]
        for func in funcs:
            with pytest.raises(ValueError):
                func("")

    def test_all_functions_include_time_range_in_data(self):
        """Test that all functions echo the time_range in their data."""
        funcs = [get_recruitment_metrics, get_pipeline_funnel, get_source_effectiveness, get_time_to_hire]
        for func in funcs:
            result = func("90d")
            assert result["data"]["time_range"] == "90d", f"{func.__name__} did not echo time_range"

    def test_all_functions_include_period_in_data(self):
        """Test that all functions include period_start and period_end."""
        funcs = [get_recruitment_metrics, get_pipeline_funnel, get_source_effectiveness, get_time_to_hire]
        for func in funcs:
            result = func("30d")
            assert "period_start" in result["data"], f"{func.__name__} missing period_start"
            assert "period_end" in result["data"], f"{func.__name__} missing period_end"
