"""Analytics service for recruitment metrics and reporting."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)

VALID_TIME_RANGES = {"7d", "30d", "90d", "180d", "365d", "all"}


def _parse_time_range(time_range: str) -> tuple[datetime | None, datetime]:
    """Parse a time range string into start and end datetimes.

    Args:
        time_range: One of '7d', '30d', '90d', '180d', '365d', 'all'.

    Returns:
        A tuple of (start_datetime, end_datetime). For 'all', start is None.

    Raises:
        ValueError: If the time range is not recognised.
    """
    if time_range not in VALID_TIME_RANGES:
        raise ValueError(
            f"Invalid time_range '{time_range}'. "
            f"Must be one of: {', '.join(sorted(VALID_TIME_RANGES))}"
        )

    end = datetime.utcnow()
    if time_range == "all":
        return None, end

    days = int(time_range[:-1])
    start = end - timedelta(days=days)
    return start, end


def _format_response(data: dict[str, Any]) -> dict[str, Any]:
    """Wrap response data with metadata.

    Args:
        data: The raw metrics data.

    Returns:
        A dict containing the data and metadata.
    """
    return {
        "success": True,
        "data": data,
        "generated_at": datetime.utcnow().isoformat(),
    }


def get_recruitment_metrics(time_range: str) -> dict[str, Any]:
    """Get recruitment metrics for the given time range.

    Returns key recruitment KPIs including total applications, hires,
    open positions, and offer acceptance rate.

    Args:
        time_range: The time period to analyse. One of '7d', '30d',
            '90d', '180d', '365d', 'all'.

    Returns:
        A dict containing recruitment metrics wrapped with metadata.

    Raises:
        ValueError: If the time_range is invalid.
        RuntimeError: If metrics cannot be retrieved.
    """
    try:
        start, end = _parse_time_range(time_range)
    except ValueError:
        raise

    try:
        # TODO: Replace with actual database queries
        metrics: dict[str, Any] = {
            "time_range": time_range,
            "period_start": start.isoformat() if start else None,
            "period_end": end.isoformat(),
            "total_applications": 0,
            "total_hires": 0,
            "open_positions": 0,
            "offer_acceptance_rate": 0.0,
            "applications_per_opening": 0.0,
            "active_candidates": 0,
            "rejected_candidates": 0,
            "withdrawn_candidates": 0,
        }

        logger.info(
            "Retrieved recruitment metrics for period %s (%s to %s)",
            time_range,
            start,
            end,
        )
        return _format_response(metrics)

    except Exception as exc:
        logger.error("Failed to get recruitment metrics: %s", exc)
        raise RuntimeError(f"Failed to retrieve recruitment metrics: {exc}") from exc


def get_pipeline_funnel(time_range: str) -> dict[str, Any]:
    """Get pipeline funnel data for the given time range.

    Returns candidate counts at each stage of the recruitment pipeline:
    applied, screened, interviewed, offered, hired.

    Args:
        time_range: The time period to analyse. One of '7d', '30d',
            '90d', '180d', '365d', 'all'.

    Returns:
        A dict containing pipeline funnel data with stage counts and
        conversion rates.

    Raises:
        ValueError: If the time_range is invalid.
        RuntimeError: If funnel data cannot be retrieved.
    """
    try:
        start, end = _parse_time_range(time_range)
    except ValueError:
        raise

    try:
        # TODO: Replace with actual database queries
        stages = [
            {"stage": "applied", "count": 0},
            {"stage": "screened", "count": 0},
            {"stage": "interviewed", "count": 0},
            {"stage": "offered", "count": 0},
            {"stage": "hired", "count": 0},
        ]

        # Calculate conversion rates between stages
        for i in range(1, len(stages)):
            prev_count = stages[i - 1]["count"]
            curr_count = stages[i]["count"]
            stages[i]["conversion_rate"] = (
                round(curr_count / prev_count, 4) if prev_count > 0 else 0.0
            )

        funnel: dict[str, Any] = {
            "time_range": time_range,
            "period_start": start.isoformat() if start else None,
            "period_end": end.isoformat(),
            "stages": stages,
            "overall_conversion_rate": 0.0,
        }

        logger.info("Retrieved pipeline funnel for period %s", time_range)
        return _format_response(funnel)

    except Exception as exc:
        logger.error("Failed to get pipeline funnel: %s", exc)
        raise RuntimeError(f"Failed to retrieve pipeline funnel: {exc}") from exc


def get_source_effectiveness(time_range: str) -> dict[str, Any]:
    """Get source effectiveness data for the given time range.

    Returns metrics for each recruitment source (e.g., LinkedIn, referrals,
    job boards) including application count, hire count, cost per hire, and
    quality score.

    Args:
        time_range: The time period to analyse. One of '7d', '30d',
            '90d', '180d', '365d', 'all'.

    Returns:
        A dict containing per-source effectiveness metrics.

    Raises:
        ValueError: If the time_range is invalid.
        RuntimeError: If source effectiveness data cannot be retrieved.
    """
    try:
        start, end = _parse_time_range(time_range)
    except ValueError:
        raise

    try:
        # TODO: Replace with actual database queries
        sources: list[dict[str, Any]] = [
            {
                "source": "linkedin",
                "applications": 0,
                "hires": 0,
                "cost_per_hire": 0.0,
                "quality_score": 0.0,
                "conversion_rate": 0.0,
            },
            {
                "source": "referral",
                "applications": 0,
                "hires": 0,
                "cost_per_hire": 0.0,
                "quality_score": 0.0,
                "conversion_rate": 0.0,
            },
            {
                "source": "indeed",
                "applications": 0,
                "hires": 0,
                "cost_per_hire": 0.0,
                "quality_score": 0.0,
                "conversion_rate": 0.0,
            },
            {
                "source": "company_careers_page",
                "applications": 0,
                "hires": 0,
                "cost_per_hire": 0.0,
                "quality_score": 0.0,
                "conversion_rate": 0.0,
            },
        ]

        effectiveness: dict[str, Any] = {
            "time_range": time_range,
            "period_start": start.isoformat() if start else None,
            "period_end": end.isoformat(),
            "sources": sources,
            "total_sources": len(sources),
            "most_effective_source": None,
        }

        logger.info("Retrieved source effectiveness for period %s", time_range)
        return _format_response(effectiveness)

    except Exception as exc:
        logger.error("Failed to get source effectiveness: %s", exc)
        raise RuntimeError(f"Failed to retrieve source effectiveness: {exc}") from exc


def get_time_to_hire(time_range: str) -> dict[str, Any]:
    """Get time-to-hire metrics for the given time range.

    Returns average, median, and percentile breakdowns of the number of
    days between application and hire, segmented by department and role
    seniority.

    Args:
        time_range: The time period to analyse. One of '7d', '30d',
            '90d', '180d', '365d', 'all'.

    Returns:
        A dict containing time-to-hire statistics.

    Raises:
        ValueError: If the time_range is invalid.
        RuntimeError: If time-to-hire data cannot be retrieved.
    """
    try:
        start, end = _parse_time_range(time_range)
    except ValueError:
        raise

    try:
        # TODO: Replace with actual database queries
        time_to_hire: dict[str, Any] = {
            "time_range": time_range,
            "period_start": start.isoformat() if start else None,
            "period_end": end.isoformat(),
            "overall": {
                "average_days": 0.0,
                "median_days": 0.0,
                "p25_days": 0.0,
                "p75_days": 0.0,
                "min_days": 0,
                "max_days": 0,
            },
            "by_department": [],
            "by_seniority": [],
            "sample_size": 0,
        }

        logger.info("Retrieved time-to-hire metrics for period %s", time_range)
        return _format_response(time_to_hire)

    except Exception as exc:
        logger.error("Failed to get time-to-hire metrics: %s", exc)
        raise RuntimeError(f"Failed to retrieve time-to-hire metrics: {exc}") from exc
