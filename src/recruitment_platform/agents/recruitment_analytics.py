"""Recruitment analytics agent for computing recruitment metrics."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)

VALID_TIME_RANGES = {"7d", "30d", "90d", "180d", "365d"}


def _parse_time_range(time_range: str) -> tuple[datetime, datetime]:
    """Parse a time range string into start and end datetimes.

    Args:
        time_range: One of '7d', '30d', '90d', '180d', '365d'.

    Returns:
        A tuple of (start_datetime, end_datetime).

    Raises:
        ValueError: If the time range is not recognised.
    """
    if time_range not in VALID_TIME_RANGES:
        raise ValueError(
            f"Invalid time_range '{time_range}'. "
            f"Must be one of: {', '.join(sorted(VALID_TIME_RANGES))}"
        )
    days = int(time_range[:-1])
    end = datetime.utcnow()
    start = end - timedelta(days=days)
    return start, end


def get_recruitment_metrics(time_range: str) -> dict[str, Any]:
    """Get recruitment metrics for the given time range.

    Args:
        time_range: The time window for metrics aggregation.
            Supported values: '7d', '30d', '90d', '180d', '365d'.

    Returns:
        A dictionary containing recruitment metrics with keys:
            - total_applications: Total number of applications received.
            - total_hires: Total number of hires made.
            - average_time_to_hire_days: Average days from application to hire.
            - offer_acceptance_rate: Percentage of offers accepted.
            - applications_per_hire: Average applications needed per hire.
            - time_range: The requested time range.
            - start_date: ISO format start date of the range.
            - end_date: ISO format end date of the range.

    Raises:
        ValueError: If the time_range is invalid.
        RuntimeError: If metrics computation fails.
    """
    try:
        start, end = _parse_time_range(time_range)
    except ValueError:
        raise

    try:
        # Placeholder: replace with actual data source queries
        total_applications = 0
        total_hires = 0
        average_time_to_hire_days = 0.0
        offer_acceptance_rate = 0.0
        applications_per_hire = 0.0

        return {
            "total_applications": total_applications,
            "total_hires": total_hires,
            "average_time_to_hire_days": average_time_to_hire_days,
            "offer_acceptance_rate": offer_acceptance_rate,
            "applications_per_hire": applications_per_hire,
            "time_range": time_range,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
        }
    except Exception as exc:
        logger.error("Failed to compute recruitment metrics: %s", exc)
        raise RuntimeError(f"Failed to compute recruitment metrics: {exc}") from exc


def get_pipeline_funnel(time_range: str) -> dict[str, Any]:
    """Get pipeline funnel data for the given time range.

    Args:
        time_range: The time window for funnel analysis.
            Supported values: '7d', '30d', '90d', '180d', '365d'.

    Returns:
        A dictionary containing pipeline funnel data with keys:
            - stages: List of dicts with 'stage_name', 'count', and
              'conversion_rate' for each pipeline stage.
            - overall_conversion_rate: Percentage from first to last stage.
            - time_range: The requested time range.
            - start_date: ISO format start date of the range.
            - end_date: ISO format end date of the range.

    Raises:
        ValueError: If the time_range is invalid.
        RuntimeError: If funnel computation fails.
    """
    try:
        start, end = _parse_time_range(time_range)
    except ValueError:
        raise

    try:
        # Placeholder: replace with actual pipeline stage queries
        stages: list[dict[str, Any]] = []
        overall_conversion_rate = 0.0

        return {
            "stages": stages,
            "overall_conversion_rate": overall_conversion_rate,
            "time_range": time_range,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
        }
    except Exception as exc:
        logger.error("Failed to compute pipeline funnel: %s", exc)
        raise RuntimeError(f"Failed to compute pipeline funnel: {exc}") from exc


def get_source_effectiveness(time_range: str) -> dict[str, Any]:
    """Get source effectiveness data for the given time range.

    Args:
        time_range: The time window for source analysis.
            Supported values: '7d', '30d', '90d', '180d', '365d'.

    Returns:
        A dictionary containing source effectiveness data with keys:
            - sources: List of dicts with 'source_name', 'applications',
              'hires', 'cost_per_hire', and 'roi_score' for each source.
            - top_source: The name of the most effective source.
            - time_range: The requested time range.
            - start_date: ISO format start date of the range.
            - end_date: ISO format end date of the range.

    Raises:
        ValueError: If the time_range is invalid.
        RuntimeError: If source effectiveness computation fails.
    """
    try:
        start, end = _parse_time_range(time_range)
    except ValueError:
        raise

    try:
        # Placeholder: replace with actual source effectiveness queries
        sources: list[dict[str, Any]] = []
        top_source = ""

        return {
            "sources": sources,
            "top_source": top_source,
            "time_range": time_range,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
        }
    except Exception as exc:
        logger.error("Failed to compute source effectiveness: %s", exc)
        raise RuntimeError(
            f"Failed to compute source effectiveness: {exc}"
        ) from exc
