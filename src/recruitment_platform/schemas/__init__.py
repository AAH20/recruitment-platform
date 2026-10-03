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
    phone: Optional[str] = Field(None, max_length=20)
    resume_url: Optional[str] = Field(None, max_length=500)
    linkedin_url: Optional[str] = Field(None, max_length=500)
    skills: list[str] = Field(default_factory=list)
    experience_years: Optional[float] = Field(None, ge=0, le=60)
    current_company: Optional[str] = Field(None, max_length=200)
    current_title: Optional[str] = Field(None, max_length=200)
    education: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=2000)


class CandidateUpdate(BaseSchema):
    """Schema for updating a candidate — all fields optional."""

    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    resume_url: Optional[str] = Field(None, max_length=500)
    linkedin_url: Optional[str] = Field(None, max_length=500)
    skills: Optional[list[str]] = None
    experience_years: Optional[float] = Field(None, ge=0, le=60)
    current_company: Optional[str] = Field(None, max_length=200)
    current_title: Optional[str] = Field(None, max_length=200)
    education: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=2000)


class CandidateResponse(BaseSchema):
    """Schema for candidate response."""

    id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    resume_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    skills: list[str] = Field(default_factory=list)
    experience_years: Optional[float] = None
    current_company: Optional[str] = None
    current_title: Optional[str] = None
    education: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Job
# ---------------------------------------------------------------------------

class JobStatus(str, Enum):
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
    salary_min: Optional[float] = Field(None, ge=0)
    salary_max: Optional[float] = Field(None, ge=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    requirements: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    hiring_manager_id: Optional[int] = None
    recruiter_id: Optional[int] = None
    status: JobStatus = JobStatus.DRAFT


class JobUpdate(BaseSchema):
    """Schema for updating a job posting — all fields optional."""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=10000)
    department: Optional[str] = Field(None, min_length=1, max_length=100)
    location: Optional[str] = Field(None, min_length=1, max_length=200)
    employment_type: Optional[str] = Field(None, min_length=1, max_length=50)
    salary_min: Optional[float] = Field(None, ge=0)
    salary_max: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    requirements: Optional[list[str]] = None
    responsibilities: Optional[list[str]] = None
    hiring_manager_id: Optional[int] = None
    recruiter_id: Optional[int] = None
    status: Optional[JobStatus] = None


class JobResponse(BaseSchema):
    """Schema for job response."""

    id: int
    title: str
    description: str
    department: str
    location: str
    employment_type: str
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    currency: str
    requirements: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    hiring_manager_id: Optional[int] = None
    recruiter_id: Optional[int] = None
    status: JobStatus
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

class ApplicationStatus(str, Enum):
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
    cover_letter: Optional[str] = Field(None, max_length=5000)
    source: Optional[str] = Field(None, max_length=100)
    referral: Optional[str] = Field(None, max_length=200)


class ApplicationUpdate(BaseSchema):
    """Schema for updating an application — all fields optional."""

    status: Optional[ApplicationStatus] = None
    cover_letter: Optional[str] = Field(None, max_length=5000)
    source: Optional[str] = Field(None, max_length=100)
    referral: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = Field(None, max_length=2000)


class ApplicationResponse(BaseSchema):
    """Schema for application response."""

    id: int
    candidate_id: int
    job_id: int
    status: ApplicationStatus
    cover_letter: Optional[str] = None
    source: Optional[str] = None
    referral: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Interview
# ---------------------------------------------------------------------------

class InterviewType(str, Enum):
    """Interview type."""

    PHONE = "phone"
    VIDEO = "video"
    ONSITE = "onsite"
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    PANEL = "panel"


class InterviewStatus(str, Enum):
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
    location: Optional[str] = Field(None, max_length=500)
    meeting_link: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=2000)


class InterviewUpdate(BaseSchema):
    """Schema for updating an interview — all fields optional."""

    interviewer_id: Optional[int] = Field(None, gt=0)
    interview_type: Optional[InterviewType] = None
    scheduled_at: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=15, le=480)
    location: Optional[str] = Field(None, max_length=500)
    meeting_link: Optional[str] = Field(None, max_length=500)
    status: Optional[InterviewStatus] = None
    notes: Optional[str] = Field(None, max_length=2000)
    feedback: Optional[str] = Field(None, max_length=5000)


class InterviewResponse(BaseSchema):
    """Schema for interview response."""

    id: int
    application_id: int
    interviewer_id: int
    interview_type: InterviewType
    scheduled_at: datetime
    duration_minutes: int
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    status: InterviewStatus
    notes: Optional[str] = None
    feedback: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Assessment
# ---------------------------------------------------------------------------

class AssessmentType(str, Enum):
    """Assessment type."""

    TECHNICAL = "technical"
    COGNITIVE = "cognitive"
    PERSONALITY = "personality"
    CODING = "coding"
    CASE_STUDY = "case_study"


class AssessmentStatus(str, Enum):
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
    description: Optional[str] = Field(None, max_length=5000)
    duration_minutes: Optional[int] = Field(None, ge=15, le=480)
    max_score: Optional[float] = Field(None, gt=0)
    passing_score: Optional[float] = Field(None, ge=0)
    due_date: Optional[datetime] = None
    external_url: Optional[str] = Field(None, max_length=500)


class AssessmentUpdate(BaseSchema):
    """Schema for updating an assessment — all fields optional."""

    assessment_type: Optional[AssessmentType] = None
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    duration_minutes: Optional[int] = Field(None, ge=15, le=480)
    max_score: Optional[float] = Field(None, gt=0)
    passing_score: Optional[float] = Field(None, ge=0)
    status: Optional[AssessmentStatus] = None
    score: Optional[float] = Field(None, ge=0)
    due_date: Optional[datetime] = None
    external_url: Optional[str] = Field(None, max_length=500)
    feedback: Optional[str] = Field(None, max_length=5000)


class AssessmentResponse(BaseSchema):
    """Schema for assessment response."""

    id: int
    application_id: int
    assessment_type: AssessmentType
    title: str
    description: Optional[str] = None
    duration_minutes: Optional[int] = None
    max_score: Optional[float] = None
    passing_score: Optional[float] = None
    status: AssessmentStatus
    score: Optional[float] = None
    due_date: Optional[datetime] = None
    external_url: Optional[str] = None
    feedback: Optional[str] = None
    created_at: datetime
    updated_at: datetime
