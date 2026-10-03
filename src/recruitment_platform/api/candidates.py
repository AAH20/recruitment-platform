"""
Candidates API endpoints for the recruitment platform.

Provides:
  GET  /candidates  — list candidates with pagination, filtering, sorting
  POST /candidates  — create a new candidate with validation
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, EmailStr, Field, field_validator

router = APIRouter(prefix="/candidates", tags=["candidates"])


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class CandidateStatus(str, Enum):
    NEW = "new"
    SCREENING = "screening"
    INTERVIEW = "interview"
    OFFER = "offer"
    HIRED = "hired"
    REJECTED = "rejected"


class ExperienceLevel(str, Enum):
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    PRINCIPAL = "principal"


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class CandidateCreate(BaseModel):
    """Payload for creating a new candidate."""

    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    phone: str | None = Field(None, max_length=20)
    role_applied: str = Field(..., min_length=1, max_length=120)
    years_experience: int = Field(..., ge=0, le=60)
    experience_level: ExperienceLevel
    skills: list[str] = Field(default_factory=list, max_length=30)
    expected_salary: int | None = Field(None, ge=0)
    currency: str = Field(default="USD", pattern="^[A-Z]{3}$")
    location: str | None = Field(None, max_length=120)
    remote_ok: bool = True
    linkedin_url: str | None = Field(None, max_length=255)
    notes: str | None = Field(None, max_length=2000)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        if v is None:
            return v
        digits = "".join(c for c in v if c.isdigit() or c == "+")
        if len(digits) < 7:
            raise ValueError("Phone number must contain at least 7 digits")
        return v

    @field_validator("skills")
    @classmethod
    def validate_skills(cls, v: list[str]) -> list[str]:
        return [s.strip().lower() for s in v if s.strip()]


class CandidateResponse(BaseModel):
    """Full candidate representation returned by the API."""

    id: str
    first_name: str
    last_name: str
    email: str
    phone: str | None
    role_applied: str
    years_experience: int
    experience_level: ExperienceLevel
    skills: list[str]
    expected_salary: int | None
    currency: str
    location: str | None
    remote_ok: bool
    linkedin_url: str | None
    notes: str | None
    status: CandidateStatus
    created_at: str
    updated_at: str


class PaginatedCandidates(BaseModel):
    """Paginated list response."""

    data: list[CandidateResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ---------------------------------------------------------------------------
# In-memory mock store (replace with real DB in production)
# ---------------------------------------------------------------------------


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


_MOCK_CANDIDATES: list[dict[str, Any]] = [
    {
        "id": str(uuid.uuid4()),
        "first_name": "Amara",
        "last_name": "Okafor",
        "email": "amara.okafor@example.com",
        "phone": "+1-415-555-0101",
        "role_applied": "Senior Backend Engineer",
        "years_experience": 7,
        "experience_level": "senior",
        "skills": ["python", "fastapi", "postgresql", "redis", "docker"],
        "expected_salary": 165000,
        "currency": "USD",
        "location": "San Francisco, CA",
        "remote_ok": True,
        "linkedin_url": "https://linkedin.com/in/amaraokafor",
        "notes": "Strong distributed-systems background.",
        "status": "interview",
        "created_at": "2026-09-15T10:22:00+00:00",
        "updated_at": "2026-09-28T14:05:00+00:00",
    },
    {
        "id": str(uuid.uuid4()),
        "first_name": "Liam",
        "last_name": "Chen",
        "email": "liam.chen@example.com",
        "phone": "+1-206-555-0142",
        "role_applied": "Frontend Engineer",
        "years_experience": 4,
        "experience_level": "mid",
        "skills": ["react", "typescript", "tailwindcss", "next.js"],
        "expected_salary": 130000,
        "currency": "USD",
        "location": "Seattle, WA",
        "remote_ok": True,
        "linkedin_url": "https://linkedin.com/in/liamchen",
        "notes": "Portfolio includes several open-source contributions.",
        "status": "screening",
        "created_at": "2026-09-20T08:11:00+00:00",
        "updated_at": "2026-09-25T16:40:00+00:00",
    },
    {
        "id": str(uuid.uuid4()),
        "first_name": "Sofia",
        "last_name": "Ramírez",
        "email": "sofia.ramirez@example.com",
        "phone": "+34-612-555-0199",
        "role_applied": "Data Scientist",
        "years_experience": 5,
        "experience_level": "mid",
        "skills": ["python", "pandas", "scikit-learn", "sql", "tensorflow"],
        "expected_salary": 120000,
        "currency": "EUR",
        "location": "Madrid, Spain",
        "remote_ok": True,
        "linkedin_url": "https://linkedin.com/in/sofia-ramirez",
        "notes": "Published two papers on NLP.",
        "status": "new",
        "created_at": "2026-10-01T09:00:00+00:00",
        "updated_at": "2026-10-01T09:00:00+00:00",
    },
    {
        "id": str(uuid.uuid4()),
        "first_name": "Noah",
        "last_name": "Patel",
        "email": "noah.patel@example.com",
        "phone": "+44-20-7946-0958",
        "role_applied": "DevOps Engineer",
        "years_experience": 6,
        "experience_level": "senior",
        "skills": ["kubernetes", "terraform", "aws", "ci/cd", "golang"],
        "expected_salary": 145000,
        "currency": "GBP",
        "location": "London, UK",
        "remote_ok": False,
        "linkedin_url": "https://linkedin.com/in/noahpatel",
        "notes": "Led migration to multi-region K8s clusters.",
        "status": "offer",
        "created_at": "2026-08-10T13:30:00+00:00",
        "updated_at": "2026-09-30T11:15:00+00:00",
    },
    {
        "id": str(uuid.uuid4()),
        "first_name": "Yuki",
        "last_name": "Tanaka",
        "email": "yuki.tanaka@example.com",
        "phone": "+81-3-5555-0123",
        "role_applied": "Machine Learning Engineer",
        "years_experience": 8,
        "experience_level": "senior",
        "skills": ["pytorch", "mlops", "python", "kubernetes", "ray"],
        "expected_salary": 180000,
        "currency": "USD",
        "location": "Tokyo, Japan",
        "remote_ok": True,
        "linkedin_url": "https://linkedin.com/in/yukitanaka",
        "notes": "Built real-time recommendation systems at scale.",
        "status": "interview",
        "created_at": "2026-09-05T02:45:00+00:00",
        "updated_at": "2026-09-27T09:20:00+00:00",
    },
    {
        "id": str(uuid.uuid4()),
        "first_name": "Elena",
        "last_name": "Kowalski",
        "email": "elena.kowalski@example.com",
        "phone": "+48-512-555-0177",
        "role_applied": "Product Designer",
        "years_experience": 3,
        "experience_level": "mid",
        "skills": ["figma", "user research", "prototyping", "design systems"],
        "expected_salary": 95000,
        "currency": "EUR",
        "location": "Warsaw, Poland",
        "remote_ok": True,
        "linkedin_url": "https://linkedin.com/in/elenakowalski",
        "notes": "Transitioned from graphic design; strong visual eye.",
        "status": "screening",
        "created_at": "2026-09-22T15:00:00+00:00",
        "updated_at": "2026-09-26T10:30:00+00:00",
    },
    {
        "id": str(uuid.uuid4()),
        "first_name": "Marcus",
        "last_name": "Johnson",
        "email": "marcus.johnson@example.com",
        "phone": "+1-312-555-0166",
        "role_applied": "Full-Stack Engineer",
        "years_experience": 10,
        "experience_level": "lead",
        "skills": ["typescript", "node.js", "react", "postgresql", "graphql"],
        "expected_salary": 195000,
        "currency": "USD",
        "location": "Chicago, IL",
        "remote_ok": True,
        "linkedin_url": "https://linkedin.com/in/marcusjohnson",
        "notes": "Previously engineering lead at a Series-C startup.",
        "status": "hired",
        "created_at": "2026-07-15T09:00:00+00:00",
        "updated_at": "2026-09-20T17:00:00+00:00",
    },
    {
        "id": str(uuid.uuid4()),
        "first_name": "Priya",
        "last_name": "Sharma",
        "email": "priya.sharma@example.com",
        "phone": "+91-98765-43210",
        "role_applied": "Backend Engineer",
        "years_experience": 2,
        "experience_level": "junior",
        "skills": ["python", "django", "sql", "git"],
        "expected_salary": 45000,
        "currency": "USD",
        "location": "Bangalore, India",
        "remote_ok": True,
        "linkedin_url": "https://linkedin.com/in/priyasharma",
        "notes": "Bootcamp graduate with strong fundamentals.",
        "status": "new",
        "created_at": "2026-10-02T07:30:00+00:00",
        "updated_at": "2026-10-02T07:30:00+00:00",
    },
    {
        "id": str(uuid.uuid4()),
        "first_name": "Diego",
        "last_name": "Fernández",
        "email": "diego.fernandez@example.com",
        "phone": "+54-11-5555-0144",
        "role_applied": "Site Reliability Engineer",
        "years_experience": 9,
        "experience_level": "senior",
        "skills": ["linux", "prometheus", "grafana", "ansible", "python"],
        "expected_salary": 155000,
        "currency": "USD",
        "location": "Buenos Aires, Argentina",
        "remote_ok": True,
        "linkedin_url": "https://linkedin.com/in/diegof",
        "notes": "Reduced MTTR by 60% at previous role.",
        "status": "rejected",
        "created_at": "2026-08-28T12:00:00+00:00",
        "updated_at": "2026-09-18T14:00:00+00:00",
    },
    {
        "id": str(uuid.uuid4()),
        "first_name": "Aisha",
        "last_name": "Bello",
        "email": "aisha.bello@example.com",
        "phone": "+234-801-555-0188",
        "role_applied": "Data Engineer",
        "years_experience": 4,
        "experience_level": "mid",
        "skills": ["python", "spark", "airflow", "dbt", "snowflake"],
        "expected_salary": 110000,
        "currency": "USD",
        "location": "Lagos, Nigeria",
        "remote_ok": True,
        "linkedin_url": "https://linkedin.com/in/aishabello",
        "notes": "Built pipelines processing 10M+ events/day.",
        "status": "interview",
        "created_at": "2026-09-12T11:00:00+00:00",
        "updated_at": "2026-09-29T08:45:00+00:00",
    },
]


# ---------------------------------------------------------------------------
# GET /candidates — list with pagination, filtering, sorting
# ---------------------------------------------------------------------------


@router.get(
    "",
    response_model=PaginatedCandidates,
    summary="List candidates",
    description="Retrieve a paginated list of candidates with optional filtering and sorting.",
)
async def list_candidates(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    status: CandidateStatus | None = Query(None, description="Filter by status"),
    experience_level: ExperienceLevel | None = Query(
        None, description="Filter by experience level"
    ),
    role: str | None = Query(
        None, description="Filter by role applied (partial match)"
    ),
    location: str | None = Query(
        None, description="Filter by location (partial match)"
    ),
    remote_ok: bool | None = Query(None, description="Filter by remote availability"),
    min_years: int | None = Query(
        None, ge=0, description="Minimum years of experience"
    ),
    max_years: int | None = Query(
        None, ge=0, description="Maximum years of experience"
    ),
    skills: str | None = Query(None, description="Comma-separated skills to filter by"),
    search: str | None = Query(
        None, description="Full-text search across name, email, role"
    ),
    sort_by: str = Query(
        "created_at",
        pattern="^(created_at|updated_at|last_name|years_experience|expected_salary)$",
        description="Field to sort by",
    ),
    sort_order: str = Query(
        "desc", pattern="^(asc|desc)$", description="Sort direction"
    ),
) -> PaginatedCandidates:
    """
    Return a paginated, filtered, and sorted list of candidates.
    """
    filtered = _MOCK_CANDIDATES.copy()

    # --- Filtering ---
    if status is not None:
        filtered = [c for c in filtered if c["status"] == status.value]

    if experience_level is not None:
        filtered = [
            c for c in filtered if c["experience_level"] == experience_level.value
        ]

    if role:
        role_lower = role.lower()
        filtered = [c for c in filtered if role_lower in c["role_applied"].lower()]

    if location:
        loc_lower = location.lower()
        filtered = [
            c for c in filtered if c["location"] and loc_lower in c["location"].lower()
        ]

    if remote_ok is not None:
        filtered = [c for c in filtered if c["remote_ok"] == remote_ok]

    if min_years is not None:
        filtered = [c for c in filtered if c["years_experience"] >= min_years]

    if max_years is not None:
        filtered = [c for c in filtered if c["years_experience"] <= max_years]

    if skills:
        skill_set = {s.strip().lower() for s in skills.split(",") if s.strip()}
        filtered = [c for c in filtered if skill_set.issubset(set(c["skills"]))]

    if search:
        q = search.lower()
        filtered = [
            c
            for c in filtered
            if q in c["first_name"].lower()
            or q in c["last_name"].lower()
            or q in c["email"].lower()
            or q in c["role_applied"].lower()
        ]

    # --- Sorting ---
    reverse = sort_order == "desc"
    filtered.sort(key=lambda c: c.get(sort_by, ""), reverse=reverse)

    # --- Pagination ---
    total = len(filtered)
    total_pages = max(1, (total + page_size - 1) // page_size)
    start = (page - 1) * page_size
    end = start + page_size
    page_items = filtered[start:end]

    return PaginatedCandidates(
        data=[CandidateResponse(**c) for c in page_items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


# ---------------------------------------------------------------------------
# POST /candidates — create with validation
# ---------------------------------------------------------------------------


@router.post(
    "",
    response_model=CandidateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new candidate",
    description="Create a new candidate record with full validation.",
)
async def create_candidate(payload: CandidateCreate) -> CandidateResponse:
    """
    Create a new candidate from the provided payload.
    Returns the created candidate with generated id and timestamps.
    """
    # Check for duplicate email
    email_lower = payload.email.lower()
    for existing in _MOCK_CANDIDATES:
        if existing["email"].lower() == email_lower:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A candidate with email '{payload.email}' already exists.",
            )

    now = _now_iso()
    new_candidate: dict[str, Any] = {
        "id": str(uuid.uuid4()),
        "first_name": payload.first_name,
        "last_name": payload.last_name,
        "email": payload.email,
        "phone": payload.phone,
        "role_applied": payload.role_applied,
        "years_experience": payload.years_experience,
        "experience_level": payload.experience_level.value,
        "skills": payload.skills,
        "expected_salary": payload.expected_salary,
        "currency": payload.currency,
        "location": payload.location,
        "remote_ok": payload.remote_ok,
        "linkedin_url": payload.linkedin_url,
        "notes": payload.notes,
        "status": CandidateStatus.NEW.value,
        "created_at": now,
        "updated_at": now,
    }

    _MOCK_CANDIDATES.append(new_candidate)

    return CandidateResponse(**new_candidate)


# ---------------------------------------------------------------------------
# GET /candidates/{candidate_id} — retrieve a single candidate
# ---------------------------------------------------------------------------


@router.get(
    "/{candidate_id}",
    response_model=CandidateResponse,
    summary="Get candidate by ID",
    description="Retrieve a single candidate by their unique identifier.",
)
async def get_candidate(candidate_id: str) -> CandidateResponse:
    """Return a single candidate by ID or raise 404."""
    for candidate in _MOCK_CANDIDATES:
        if candidate["id"] == candidate_id:
            return CandidateResponse(**candidate)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Candidate with id '{candidate_id}' not found.",
    )


# ---------------------------------------------------------------------------
# PUT /candidates/{candidate_id} — update a candidate
# ---------------------------------------------------------------------------


class CandidateUpdate(BaseModel):
    """Payload for updating an existing candidate — all fields optional."""

    first_name: str | None = Field(None, min_length=1, max_length=50)
    last_name: str | None = Field(None, min_length=1, max_length=50)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=20)
    role_applied: str | None = Field(None, min_length=1, max_length=120)
    years_experience: int | None = Field(None, ge=0, le=60)
    experience_level: ExperienceLevel | None = None
    skills: list[str] | None = Field(None, max_length=30)
    expected_salary: int | None = Field(None, ge=0)
    currency: str | None = Field(None, pattern="^[A-Z]{3}$")
    location: str | None = Field(None, max_length=120)
    remote_ok: bool | None = None
    linkedin_url: str | None = Field(None, max_length=255)
    notes: str | None = Field(None, max_length=2000)
    status: CandidateStatus | None = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        if v is None:
            return v
        digits = "".join(c for c in v if c.isdigit() or c == "+")
        if len(digits) < 7:
            raise ValueError("Phone number must contain at least 7 digits")
        return v

    @field_validator("skills")
    @classmethod
    def validate_skills(cls, v: list[str] | None) -> list[str] | None:
        if v is None:
            return v
        return [s.strip().lower() for s in v if s.strip()]


@router.put(
    "/{candidate_id}",
    response_model=CandidateResponse,
    summary="Update candidate",
    description="Update an existing candidate. Only provided fields are modified.",
)
async def update_candidate(
    candidate_id: str, payload: CandidateUpdate
) -> CandidateResponse:
    """Update a candidate by ID. Only fields present in the payload are changed."""
    for i, candidate in enumerate(_MOCK_CANDIDATES):
        if candidate["id"] == candidate_id:
            update_data = payload.model_dump(exclude_unset=True)
            # Convert enum values to their string representation
            if (
                "experience_level" in update_data
                and update_data["experience_level"] is not None
            ):
                update_data["experience_level"] = update_data["experience_level"].value
            if "status" in update_data and update_data["status"] is not None:
                update_data["status"] = update_data["status"].value
            candidate.update(update_data)
            _MOCK_CANDIDATES[i]["updated_at"] = _now_iso()
            return CandidateResponse(**candidate)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Candidate with id '{candidate_id}' not found.",
    )


# ---------------------------------------------------------------------------
# DELETE /candidates/{candidate_id} — delete a candidate
# ---------------------------------------------------------------------------


@router.delete(
    "/{candidate_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete candidate",
    description="Permanently delete a candidate by their unique identifier.",
)
async def delete_candidate(candidate_id: str) -> None:
    """Delete a candidate by ID or raise 404."""
    for i, candidate in enumerate(_MOCK_CANDIDATES):
        if candidate["id"] == candidate_id:
            _MOCK_CANDIDATES.pop(i)
            return
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Candidate with id '{candidate_id}' not found.",
    )
