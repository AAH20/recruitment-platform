"""Pydantic schemas for the recruitment platform."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


class BaseSchema(BaseModel):
    """Base configuration for all schemas."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# ---------------------------------------------------------------------------
# Candidate
# ---------------------------------------------------------------------------


class CandidateCreate(BaseSchema):
    """Schema for creating a candidate."""

    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: str | None = Field(None, max_length=20)
    resume_url: str | None = Field(None, max_length=500)
    linkedin_url: str | None = Field(None, max_length=500)
    skills: list[str] = Field(default_factory=list)
    experience_years: float | None = Field(None, ge=0, le=60)
    current_company: str | None = Field(None, max_length=200)
    current_title: str | None = Field(None, max_length=200)
    education: str | None = Field(None, max_length=500)
    notes: str | None = Field(None, max_length=2000)


class CandidateUpdate(BaseSchema):
    """Schema for updating a candidate — all fields optional."""

    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=20)
    resume_url: str | None = Field(None, max_length=500)
    linkedin_url: str | None = Field(None, max_length=500)
    skills: list[str] | None = None
    experience_years: float | None = Field(None, ge=0, le=60)
    current_company: str | None = Field(None, max_length=200)
    current_title: str | None = Field(None, max_length=200)
    education: str | None = Field(None, max_length=500)
    notes: str | None = Field(None, max_length=2000)


class CandidateResponse(BaseSchema):
    """Schema for candidate response."""

    id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone: str | None = None
    resume_url: str | None = None
    linkedin_url: str | None = None
    skills: list[str] = Field(default_factory=list)
    experience_years: float | None = None
    current_company: str | None = None
    current_title: str | None = None
    education: str | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Job
# ---------------------------------------------------------------------------


class JobStatus(Enum):
    """Job posting status."""

    DRAFT = "draft"
    OPEN = "open"
    CLOSED = "closed"
    ARCHIVED = "archived"


class JobCreate(BaseSchema):
    """Schema for creating a job posting."""

    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=10000)
    department: str = Field(..., min_length=1, max_length=100)
    location: str = Field(..., min_length=1, max_length=200)
    employment_type: str = Field(..., min_length=1, max_length=50)
    salary_min: float | None = Field(None, ge=0)
    salary_max: float | None = Field(None, ge=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    requirements: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    hiring_manager_id: int | None = None
    recruiter_id: int | None = None
    status: JobStatus = JobStatus.DRAFT


class JobUpdate(BaseSchema):
    """Schema for updating a job posting — all fields optional."""

    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, min_length=1, max_length=10000)
    department: str | None = Field(None, min_length=1, max_length=100)
    location: str | None = Field(None, min_length=1, max_length=200)
    employment_type: str | None = Field(None, min_length=1, max_length=50)
    salary_min: float | None = Field(None, ge=0)
    salary_max: float | None = Field(None, ge=0)
    currency: str | None = Field(None, min_length=3, max_length=3)
    requirements: list[str] | None = None
    responsibilities: list[str] | None = None
    hiring_manager_id: int | None = None
    recruiter_id: int | None = None
    status: JobStatus | None = None


class JobResponse(BaseSchema):
    """Schema for job response."""

    id: int
    title: str
    description: str
    department: str
    location: str
    employment_type: str
    salary_min: float | None = None
    salary_max: float | None = None
    currency: str
    requirements: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    hiring_manager_id: int | None = None
    recruiter_id: int | None = None
    status: JobStatus
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------


class ApplicationStatus(Enum):
    """Application status."""

    NEW = "new"
    SCREENING = "screening"
    INTERVIEW = "interview"
    OFFER = "offer"
    HIRED = "hired"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class ApplicationCreate(BaseSchema):
    """Schema for creating a job application."""

    candidate_id: int = Field(..., gt=0)
    job_id: int = Field(..., gt=0)
    cover_letter: str | None = Field(None, max_length=5000)
    source: str | None = Field(None, max_length=100)
    referral: str | None = Field(None, max_length=200)


class ApplicationUpdate(BaseSchema):
    """Schema for updating an application — all fields optional."""

    status: ApplicationStatus | None = None
    cover_letter: str | None = Field(None, max_length=5000)
    source: str | None = Field(None, max_length=100)
    referral: str | None = Field(None, max_length=200)
    notes: str | None = Field(None, max_length=2000)


class ApplicationResponse(BaseSchema):
    """Schema for application response."""

    id: int
    candidate_id: int
    job_id: int
    status: ApplicationStatus
    cover_letter: str | None = None
    source: str | None = None
    referral: str | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Interview
# ---------------------------------------------------------------------------


class InterviewType(Enum):
    """Interview type."""

    PHONE = "phone"
    VIDEO = "video"
    ONSITE = "onsite"
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    PANEL = "panel"


class InterviewStatus(Enum):
    """Interview status."""

    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class InterviewCreate(BaseSchema):
    """Schema for creating an interview."""

    application_id: int = Field(..., gt=0)
    interviewer_id: int = Field(..., gt=0)
    interview_type: InterviewType
    scheduled_at: datetime
    duration_minutes: int = Field(..., ge=15, le=480)
    location: str | None = Field(None, max_length=500)
    meeting_link: str | None = Field(None, max_length=500)
    notes: str | None = Field(None, max_length=2000)


class InterviewUpdate(BaseSchema):
    """Schema for updating an interview — all fields optional."""

    interviewer_id: int | None = Field(None, gt=0)
    interview_type: InterviewType | None = None
    scheduled_at: datetime | None = None
    duration_minutes: int | None = Field(None, ge=15, le=480)
    location: str | None = Field(None, max_length=500)
    meeting_link: str | None = Field(None, max_length=500)
    status: InterviewStatus | None = None
    notes: str | None = Field(None, max_length=2000)
    feedback: str | None = Field(None, max_length=5000)


class InterviewResponse(BaseSchema):
    """Schema for interview response."""

    id: int
    application_id: int
    interviewer_id: int
    interview_type: InterviewType
    scheduled_at: datetime
    duration_minutes: int
    location: str | None = None
    meeting_link: str | None = None
    status: InterviewStatus
    notes: str | None = None
    feedback: str | None = None
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Assessment
# ---------------------------------------------------------------------------


class AssessmentType(Enum):
    """Assessment type."""

    TECHNICAL = "technical"
    COGNITIVE = "cognitive"
    PERSONALITY = "personality"
    CODING = "coding"
    CASE_STUDY = "case_study"


class AssessmentStatus(Enum):
    """Assessment status."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    EVALUATED = "evaluated"


class AssessmentCreate(BaseSchema):
    """Schema for creating an assessment."""

    application_id: int = Field(..., gt=0)
    assessment_type: AssessmentType
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=5000)
    duration_minutes: int | None = Field(None, ge=15, le=480)
    max_score: float | None = Field(None, gt=0)
    passing_score: float | None = Field(None, ge=0)
    due_date: datetime | None = None
    external_url: str | None = Field(None, max_length=500)


class AssessmentUpdate(BaseSchema):
    """Schema for updating an assessment — all fields optional."""

    assessment_type: AssessmentType | None = None
    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=5000)
    duration_minutes: int | None = Field(None, ge=15, le=480)
    max_score: float | None = Field(None, gt=0)
    passing_score: float | None = Field(None, ge=0)
    status: AssessmentStatus | None = None
    score: float | None = Field(None, ge=0)
    due_date: datetime | None = None
    external_url: str | None = Field(None, max_length=500)
    feedback: str | None = Field(None, max_length=5000)


class AssessmentResponse(BaseSchema):
    """Schema for assessment response."""

    id: int
    application_id: int
    assessment_type: AssessmentType
    title: str
    description: str | None = None
    duration_minutes: int | None = None
    max_score: float | None = None
    passing_score: float | None = None
    status: AssessmentStatus
    score: float | None = None
    due_date: datetime | None = None
    external_url: str | None = None
    feedback: str | None = None
    created_at: datetime
    updated_at: datetime
