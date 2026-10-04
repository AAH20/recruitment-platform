"""Candidate service for recruitment platform."""

from __future__ import annotations

import json
import logging

from recruitment_platform.models import Candidate

logger = logging.getLogger(__name__)


class CandidateNotFoundError(Exception):
    """Raised when a candidate is not found."""


class CandidateServiceError(Exception):
    """Raised when a candidate service operation fails."""


def get_candidate(db_session, candidate_id: int) -> Candidate:
    """Get candidate by ID."""
    candidate = db_session.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise CandidateNotFoundError(f"Candidate {candidate_id} not found")
    return candidate


def list_candidates(db_session) -> list[Candidate]:
    """List all candidates."""
    return db_session.query(Candidate).all()


def create_candidate(db_session, data: dict) -> Candidate:
    """Create a new candidate."""
    skills = json.dumps(data.get("skills", [])) if data.get("skills") else None
    experience = str(data.get("experience_years")) if data.get("experience_years") else None
    education = data.get("education")

    candidate = Candidate(
        name=data["name"],
        email=data["email"],
        phone=data.get("phone"),
        skills=skills,
        experience=experience,
        education=education,
    )
    db_session.add(candidate)
    db_session.commit()
    db_session.refresh(candidate)
    return candidate


def update_candidate(db_session, candidate_id: int, data: dict) -> Candidate:
    """Update an existing candidate."""
    candidate = get_candidate(db_session, candidate_id)
    for key, value in data.items():
        if key == "skills" and isinstance(value, list):
            value = json.dumps(value)
        setattr(candidate, key, value)
    db_session.commit()
    db_session.refresh(candidate)
    return candidate


def delete_candidate(db_session, candidate_id: int) -> bool:
    """Delete a candidate."""
    candidate = get_candidate(db_session, candidate_id)
    db_session.delete(candidate)
    db_session.commit()
    return True


def search_candidates(db_session, query: str) -> list[Candidate]:
    """Search candidates by name or email."""
    return db_session.query(Candidate).filter(
        Candidate.name.ilike(f"%{query}%") | Candidate.email.ilike(f"%{query}%")
    ).all()
