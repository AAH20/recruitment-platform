"""Job listing API endpoints."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field

router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class JobBase(BaseModel):
    """Shared fields for a job posting."""

    model_config = ConfigDict(from_attributes=True)

    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    location: str | None = Field(default=None, max_length=255)
    salary_min: float | None = Field(default=None, ge=0)
    salary_max: float | None = Field(default=None, ge=0)
    is_active: bool = True


class JobCreate(JobBase):
    """Payload for creating a new job."""

    employer_id: int = Field(..., gt=0)


class JobUpdate(BaseModel):
    """Payload for updating an existing job — all fields optional."""

    model_config = ConfigDict(from_attributes=True)

    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, min_length=1)
    location: str | None = Field(default=None, max_length=255)
    salary_min: float | None = Field(default=None, ge=0)
    salary_max: float | None = Field(default=None, ge=0)
    is_active: bool | None = None


class JobResponse(JobBase):
    """Response model for a single job."""

    id: int
    employer_id: int


class JobListResponse(BaseModel):
    """Paginated list of jobs."""

    items: list[JobResponse]
    total: int
    page: int
    page_size: int
    pages: int


# ---------------------------------------------------------------------------
# In-memory store (replace with real DB in production)
# ---------------------------------------------------------------------------

_jobs: dict[int, dict[str, Any]] = {}
_next_id: int = 1


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_job_or_404(job_id: int) -> dict[str, Any]:
    """Return the job dict or raise a 404."""
    if job_id not in _jobs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found",
        )
    return _jobs[job_id]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.get("", response_model=JobListResponse)
async def list_jobs(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> JobListResponse:
    """Return a paginated list of all jobs."""
    all_jobs = list(_jobs.values())
    total = len(all_jobs)
    pages = (total + page_size - 1) // page_size if total else 0
    start = (page - 1) * page_size
    end = start + page_size
    items = [JobResponse(**j) for j in all_jobs[start:end]]
    return JobListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(payload: JobCreate) -> JobResponse:
    """Create a new job posting."""
    global _next_id
    job = payload.model_dump()
    job["id"] = _next_id
    _jobs[_next_id] = job
    _next_id += 1
    return JobResponse(**job)


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: int) -> JobResponse:
    """Return a single job by its ID."""
    job = _get_job_or_404(job_id)
    return JobResponse(**job)


@router.put("/{job_id}", response_model=JobResponse)
async def update_job(job_id: int, payload: JobUpdate) -> JobResponse:
    """Update an existing job. Only provided fields are changed."""
    job = _get_job_or_404(job_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        job[field] = value
    return JobResponse(**job)


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(job_id: int) -> None:
    """Delete a job by its ID."""
    _get_job_or_404(job_id)
    del _jobs[job_id]
