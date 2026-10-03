"""Recruitment Analytics API Endpoints."""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

router = APIRouter()


class PipelineStageMetrics(BaseModel):
    """Metrics for a single pipeline stage."""

    stage: str = Field(..., description="Pipeline stage name")
    count: int = Field(..., ge=0, description="Number of candidates in this stage")
    conversion_rate: float = Field(..., ge=0, le=1, description="Conversion rate from previous stage")
    avg_days_in_stage: float = Field(..., ge=0, description="Average days spent in this stage")


class PipelineMetricsResponse(BaseModel):
    """Response model for pipeline metrics."""

    total_candidates: int = Field(..., ge=0, description="Total candidates in pipeline")
    stages: List[PipelineStageMetrics] = Field(..., description="Metrics per pipeline stage")
    overall_conversion_rate: float = Field(..., ge=0, le=1, description="Overall pipeline conversion rate")
    period_start: Optional[date] = Field(None, description="Start of reporting period")
    period_end: Optional[date] = Field(None, description="End of reporting period")


class TimeToHireMetrics(BaseModel):
    """Time-to-hire metrics for a role or department."""

    role: str = Field(..., description="Role or department name")
    avg_days_to_hire: float = Field(..., ge=0, description="Average days from application to hire")
    median_days_to_hire: float = Field(..., ge=0, description="Median days from application to hire")
    min_days_to_hire: int = Field(..., ge=0, description="Minimum days to hire")
    max_days_to_hire: int = Field(..., ge=0, description="Maximum days to hire")
    hires_count: int = Field(..., ge=0, description="Number of hires in period")


class TimeToHireResponse(BaseModel):
    """Response model for time-to-hire metrics."""

    overall_avg_days: float = Field(..., ge=0, description="Overall average days to hire")
    overall_median_days: float = Field(..., ge=0, description="Overall median days to hire")
    by_role: List[TimeToHireMetrics] = Field(..., description="Time-to-hire metrics grouped by role")
    period_start: Optional[date] = Field(None, description="Start of reporting period")
    period_end: Optional[date] = Field(None, description="End of reporting period")


class SourceEffectivenessMetrics(BaseModel):
    """Effectiveness metrics for a single recruitment source."""

    source: str = Field(..., description="Recruitment source name")
    candidates_sourced: int = Field(..., ge=0, description="Candidates sourced from this source")
    candidates_hired: int = Field(..., ge=0, description="Candidates hired from this source")
    hire_rate: float = Field(..., ge=0, le=1, description="Hire rate for this source")
    cost_per_hire: Optional[float] = Field(None, ge=0, description="Cost per hire for this source")
    quality_score: Optional[float] = Field(None, ge=0, le=1, description="Quality score (0-1)")


class SourceEffectivenessResponse(BaseModel):
    """Response model for source effectiveness metrics."""

    sources: List[SourceEffectivenessMetrics] = Field(..., description="Effectiveness metrics per source")
    total_sources: int = Field(..., ge=0, description="Total number of active sources")
    top_source: Optional[str] = Field(None, description="Highest performing source by hire rate")
    period_start: Optional[date] = Field(None, description="Start of reporting period")
    period_end: Optional[date] = Field(None, description="End of reporting period")


class AnalyticsDashboardResponse(BaseModel):
    """Response model for the recruitment analytics dashboard."""

    total_active_jobs: int = Field(..., ge=0, description="Total active job postings")
    total_candidates: int = Field(..., ge=0, description="Total candidates in system")
    total_hires_this_period: int = Field(..., ge=0, description="Total hires in current period")
    open_positions: int = Field(..., ge=0, description="Currently open positions")
    avg_time_to_hire: float = Field(..., ge=0, description="Average time to hire in days")
    offer_acceptance_rate: float = Field(..., ge=0, le=1, description="Offer acceptance rate")
    period_start: Optional[date] = Field(None, description="Start of reporting period")
    period_end: Optional[date] = Field(None, description="End of reporting period")


@router.get(
    "/api/v1/analytics",
    response_model=AnalyticsDashboardResponse,
    status_code=status.HTTP_200_OK,
    summary="Get recruitment analytics dashboard",
    description="Returns high-level recruitment analytics dashboard data including active jobs, candidates, hires, and key metrics.",
    responses={
        200: {"description": "Analytics dashboard data retrieved successfully"},
        500: {"description": "Internal server error"},
    },
)
async def get_analytics_dashboard() -> AnalyticsDashboardResponse:
    """Get recruitment analytics dashboard."""
    try:
        return AnalyticsDashboardResponse(
            total_active_jobs=0,
            total_candidates=0,
            total_hires_this_period=0,
            open_positions=0,
            avg_time_to_hire=0.0,
            offer_acceptance_rate=0.0,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve analytics dashboard: {str(exc)}",
        )


@router.get(
    "/api/v1/analytics/pipeline",
    response_model=PipelineMetricsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get pipeline metrics",
    description="Returns recruitment pipeline metrics including stage counts, conversion rates, and time in stage.",
    responses={
        200: {"description": "Pipeline metrics retrieved successfully"},
        500: {"description": "Internal server error"},
    },
)
async def get_pipeline_metrics() -> PipelineMetricsResponse:
    """Get pipeline metrics."""
    try:
        return PipelineMetricsResponse(
            total_candidates=0,
            stages=[],
            overall_conversion_rate=0.0,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve pipeline metrics: {str(exc)}",
        )


@router.get(
    "/api/v1/analytics/time-to-hire",
    response_model=TimeToHireResponse,
    status_code=status.HTTP_200_OK,
    summary="Get time-to-hire metrics",
    description="Returns time-to-hire metrics including average, median, min, and max days to hire, grouped by role.",
    responses={
        200: {"description": "Time-to-hire metrics retrieved successfully"},
        500: {"description": "Internal server error"},
    },
)
async def get_time_to_hire_metrics() -> TimeToHireResponse:
    """Get time-to-hire metrics."""
    try:
        return TimeToHireResponse(
            overall_avg_days=0.0,
            overall_median_days=0.0,
            by_role=[],
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve time-to-hire metrics: {str(exc)}",
        )


@router.get(
    "/api/v1/analytics/source-effectiveness",
    response_model=SourceEffectivenessResponse,
    status_code=status.HTTP_200_OK,
    summary="Get source effectiveness metrics",
    description="Returns recruitment source effectiveness metrics including candidates sourced, hired, hire rate, and cost per hire.",
    responses={
        200: {"description": "Source effectiveness metrics retrieved successfully"},
        500: {"description": "Internal server error"},
    },
)
async def get_source_effectiveness_metrics() -> SourceEffectivenessResponse:
    """Get source effectiveness metrics."""
    try:
        return SourceEffectivenessResponse(
            sources=[],
            total_sources=0,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve source effectiveness metrics: {str(exc)}",
        )
