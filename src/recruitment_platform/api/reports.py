"""Reports API endpoints for the recruitment platform."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class ReportBase(BaseModel):
    """Shared report attributes."""

    name: str = Field(..., min_length=1, max_length=255, description="Report name")
    report_type: str = Field(
        ...,
        description="Type of report (e.g. 'pipeline', 'hiring', 'diversity')",
    )
    parameters: dict[str, Any] | None = Field(
        default=None, description="Optional report generation parameters"
    )


class ReportCreate(ReportBase):
    """Payload for generating a new report."""


class ReportSummary(BaseModel):
    """Lightweight report representation for list views."""

    id: str = Field(..., description="Unique report identifier")
    name: str
    report_type: str
    status: str = Field(..., description="Report status: pending, ready, failed")
    created_at: datetime
    file_size: int | None = Field(
        default=None, description="File size in bytes (when ready)"
    )


class ReportDetail(ReportSummary):
    """Full report representation."""

    parameters: dict[str, Any] | None = None
    generated_at: datetime | None = None
    error_message: str | None = None


class ReportListResponse(BaseModel):
    """Paginated list of reports."""

    items: list[ReportSummary]
    total: int = Field(..., description="Total number of reports available")
    page: int = Field(..., description="Current page number (1-indexed)")
    page_size: int = Field(..., description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")


class ReportDownloadResponse(BaseModel):
    """Metadata returned when a download is initiated."""

    report_id: str
    filename: str
    content_type: str
    file_size: int


# ---------------------------------------------------------------------------
# In-memory store (replace with real persistence layer)
# ---------------------------------------------------------------------------

_REPORTS: dict[str, dict[str, Any]] = {}


def _generate_report_id() -> str:
    return str(uuid.uuid4())


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get("", response_model=ReportListResponse, summary="List reports")
async def list_reports(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    report_type: str | None = Query(None, description="Filter by report type"),
) -> ReportListResponse:
    """Return a paginated list of reports.

    Args:
        page: 1-indexed page number.
        page_size: Maximum number of items per page (1-100).
        report_type: Optional filter by report type.

    Returns:
        Paginated list of report summaries.

    Raises:
        HTTPException: 400 if pagination parameters are invalid.
    """
    all_reports: list[dict[str, Any]] = list(_REPORTS.values())

    if report_type:
        all_reports = [r for r in all_reports if r["report_type"] == report_type]

    total = len(all_reports)
    pages = (total + page_size - 1) // page_size if total else 1

    if page > pages and total > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Page {page} exceeds total pages ({pages})",
        )

    start = (page - 1) * page_size
    end = start + page_size
    items = all_reports[start:end]

    return ReportListResponse(
        items=[ReportSummary(**r) for r in items],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.post(
    "",
    response_model=ReportDetail,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a new report",
)
async def create_report(payload: ReportCreate) -> ReportDetail:
    """Generate a new report.

    Args:
        payload: Report creation payload.

    Returns:
        The newly created report (status: pending).

    Raises:
        HTTPException: 422 if the payload fails validation (handled by FastAPI).
    """
    report_id = _generate_report_id()
    now = datetime.utcnow()

    report: dict[str, Any] = {
        "id": report_id,
        "name": payload.name,
        "report_type": payload.report_type,
        "parameters": payload.parameters,
        "status": "pending",
        "created_at": now,
        "generated_at": None,
        "file_size": None,
        "error_message": None,
    }

    _REPORTS[report_id] = report

    return ReportDetail(**report)


@router.get("/{report_id}", response_model=ReportDetail, summary="Get report by ID")
async def get_report(report_id: str) -> ReportDetail:
    """Retrieve a single report by its ID.

    Args:
        report_id: The unique report identifier.

    Returns:
        The full report detail.

    Raises:
        HTTPException: 404 if the report is not found.
    """
    report = _REPORTS.get(report_id)
    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report '{report_id}' not found",
        )

    return ReportDetail(**report)


@router.get(
    "/{report_id}/download",
    summary="Download report file",
)
async def download_report(report_id: str) -> StreamingResponse:
    """Download the generated report file.

    Args:
        report_id: The unique report identifier.

    Returns:
        A streaming response with the report file content.

    Raises:
        HTTPException: 404 if the report is not found.
        HTTPException: 409 if the report is not ready for download.
    """
    report = _REPORTS.get(report_id)
    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report '{report_id}' not found",
        )

    if report["status"] != "ready":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Report '{report_id}' is not ready for download (status: {report['status']})",
        )

    filename = f"{report['name'].replace(' ', '_')}_{report_id}.csv"
    file_content = b"id,name,status\n"  # placeholder — replace with real file data

    return StreamingResponse(
        iter([file_content]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(file_content)),
        },
    )
