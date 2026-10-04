"""Pydantic schemas for the recruitment platform."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, TypeVar

if TYPE_CHECKING:
    from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

T = TypeVar("T")


class BaseSchema(BaseModel, Generic[T]):
    """Base schema with common configuration."""

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Core entity create schemas (used by tests)
# ---------------------------------------------------------------------------


class EmployerCreate(BaseSchema):
    """Schema for creating a new employer."""

    name: str = Field(..., min_length=1, max_length=255)
    industry: str | None = None
    size: str | None = None
    location: str | None = None
    website: str | None = None
    description: str | None = None


class CandidateCreate(BaseSchema):
    """Schema for creating a new candidate."""

    name: str = Field(..., min_length=1)
    email: EmailStr
    phone: str | None = None
    skills: list[str] = Field(default_factory=list)
    experience_years: int | None = None
    education: str | None = None


class JobCreate(BaseSchema):
    """Schema for creating a new job."""

    title: str = Field(..., min_length=1, max_length=500)
    description: str | None = None
    requirements: list[str] = Field(default_factory=list)
    salary_min: float | None = Field(default=None, ge=0)
    salary_max: float | None = Field(default=None, ge=0)
    location: str | None = None
    employer_id: int | None = None


class ApplicationCreate(BaseSchema):
    """Schema for creating a new application."""

    job_id: int
    candidate_id: int
    cover_letter: str | None = None
    status: str = Field(default="pending")


class HealthResponse(BaseSchema):
    """Health check response schema."""

    status: str
    service: str
    version: str | None = None
    timestamp: datetime | None = None


class AgentResponse(BaseSchema[T]):
    """Generic agent response wrapper."""

    success: bool = True
    data: T | None = None
    error: str | None = None
    metadata: dict[str, Any] | None = None


class ResumeParseRequest(BaseSchema):
    """Resume parsing request schema."""

    text: str = Field(..., description="Resume text content")
    extract_contact: bool = True
    extract_education: bool = True
    extract_experience: bool = True
    extract_skills: bool = True


class ResumeParseResponse(BaseSchema):
    """Resume parsing response schema."""

    contact: dict[str, str] = Field(default_factory=dict)
    education: list[dict[str, str]] = Field(default_factory=list)
    experience: list[dict[str, Any]] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)


class MatchRequest(BaseSchema):
    """Candidate matching request schema."""

    candidates: list[dict[str, Any]] = Field(
        ..., description="List of candidate profiles"
    )
    job_requirements: dict[str, Any] = Field(..., description="Job requirements")


class MatchResponse(BaseSchema):
    """Candidate matching response schema."""

    matches: list[dict[str, Any]] = Field(default_factory=list)
    total_candidates: int = 0
    processing_time_ms: float = 0.0


class InterviewSlotRequest(BaseSchema):
    """Interview slot optimization request schema."""

    participants: list[dict[str, Any]] = Field(
        ..., description="Participant availability data"
    )
    duration_minutes: int = Field(default=60, ge=15, le=480)
    preferred_days: list[str] = Field(default_factory=list)


class SkillsAssessmentRequest(BaseSchema):
    """Skills assessment request schema."""

    skill_assessments: dict[str, Any] = Field(..., description="Skill assessment data")
    target_level: str | None = None


class BiasAnalysisRequest(BaseSchema):
    """Bias analysis request schema."""

    text: str | None = None
    hiring_data: dict[str, Any] | None = None
    analysis_type: str = Field(default="language", description="Type of bias analysis")


class TalentPoolRequest(BaseSchema):
    """Talent pool request schema."""

    job_requirements: dict[str, Any] | None = None
    pool_criteria: dict[str, Any] | None = None
    action: str = Field(default="source", description="Action to perform")


class AnalyticsRequest(BaseSchema):
    """Analytics request schema."""

    analysis_type: str = Field(..., description="Type of analytics")
    date_range: dict[str, str] | None = None
    filters: dict[str, Any] | None = None


class OnboardingRequest(BaseSchema):
    """Onboarding request schema."""

    employee_id: str | None = None
    employee_data: dict[str, Any] | None = None
    action: str = Field(default="track_progress", description="Onboarding action")


class JobDescriptionRequest(BaseSchema):
    """Job description optimization request schema."""

    job_description: str = Field(..., description="Job description text")
    target_role: str | None = None
    brand_voice: str | None = None
    platform: str | None = None


class EmployerBrandingRequest(BaseSchema):
    """Employer branding request schema."""

    action: str = Field(..., description="Branding action to perform")
    company_data: dict[str, Any] | None = None
    content_type: str | None = None
    texts: list[str] | None = None
