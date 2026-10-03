"""Interview API endpoints for the recruitment platform."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/interviews", tags=["interviews"])


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class InterviewBase(BaseModel):
    """Shared fields for an interview."""

    candidate_id: UUID
    job_id: UUID
    interviewer_id: UUID
    scheduled_at: datetime
    duration_minutes: int = Field(default=60, ge=15, le=480)
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    notes: Optional[str] = None


class InterviewCreate(InterviewBase):
    """Payload for scheduling a new interview."""

    pass


class InterviewUpdate(BaseModel):
    """Payload for updating an existing interview (all fields optional)."""

    candidate_id: Optional[UUID] = None
    job_id: Optional[UUID] = None
    interviewer_id: Optional[UUID] = None
    scheduled_at: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(default=None, ge=15, le=480)
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = Field(default=None, pattern="^(scheduled|completed|cancelled|no_show)$")


class InterviewStatusUpdate(BaseModel):
    """Payload for changing only the interview status."""

    status: str = Field(pattern="^(scheduled|completed|cancelled|no_show)$")


class Interview(InterviewBase):
    """Full interview representation returned by the API."""

    id: UUID
    status: str = "scheduled"
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InterviewListResponse(BaseModel):
    """Paginated list of interviews."""

    items: list[Interview]
    total: int
    page: int
    page_size: int
    pages: int


# ---------------------------------------------------------------------------
# In-memory store (replace with real persistence layer)
# ---------------------------------------------------------------------------

_interviews: dict[UUID, Interview] = {}


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("", response_model=InterviewListResponse)
async def list_interviews(
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    status_filter: Optional[str] = Query(default=None, alias="status", pattern="^(scheduled|completed|cancelled|no_show)$"),
    candidate_id: Optional[UUID] = None,
    job_id: Optional[UUID] = None,
) -> InterviewListResponse:
    """List interviews with optional filtering and pagination."""
    items = list(_interviews.values())

    if status_filter:
        items = [i for i in items if i.status == status_filter]
    if candidate_id:
        items = [i for i in items if i.candidate_id == candidate_id]
    if job_id:
        items = [i for i in items if i.job_id == job_id]

    total = len(items)
    pages = (total + page_size - 1) // page_size if total else 1
    start = (page - 1) * page_size
    end = start + page_size

    return InterviewListResponse(
        items=items[start:end],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.post("", response_model=Interview, status_code=status.HTTP_201_CREATED)
async def schedule_interview(payload: InterviewCreate) -> Interview:
    """Schedule a new interview."""
    now = datetime.utcnow()
    interview = Interview(
        id=uuid4(),
        **payload.model_dump(),
        status="scheduled",
        created_at=now,
        updated_at=now,
    )
    _interviews[interview.id] = interview
    return interview


@router.get("/{interview_id}", response_model=Interview)
async def get_interview(interview_id: UUID) -> Interview:
    """Retrieve a single interview by its ID."""
    interview = _interviews.get(interview_id)
    if interview is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview {interview_id} not found",
        )
    return interview


@router.put("/{interview_id}", response_model=Interview)
async def update_interview(interview_id: UUID, payload: InterviewUpdate) -> Interview:
    """Update an existing interview."""
    interview = _interviews.get(interview_id)
    if interview is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview {interview_id} not found",
        )

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(interview, field, value)

    interview.updated_at = datetime.utcnow()
    _interviews[interview_id] = interview
    return interview


@router.delete("/{interview_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_interview(interview_id: UUID) -> None:
    """Cancel (delete) an interview."""
    interview = _interviews.get(interview_id)
    if interview is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview {interview_id} not found",
        )
    del _interviews[interview_id]
