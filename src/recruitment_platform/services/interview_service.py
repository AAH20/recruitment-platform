"""Interview service for managing interviews in the recruitment platform."""

from __future__ import annotations

import logging
from datetime import datetime

from recruitment_platform.models import Interview

logger = logging.getLogger(__name__)


class InterviewNotFoundError(Exception):
    """Raised when an interview is not found."""


class InterviewServiceError(Exception):
    """Raised when an interview service operation fails."""


def get_interview(db_session, interview_id: int) -> Interview:
    """Get an interview by its ID."""
    interview = db_session.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise InterviewNotFoundError(f"Interview {interview_id} not found")
    return interview


def list_interviews(db_session) -> list[Interview]:
    """List all interviews."""
    return db_session.query(Interview).all()


def schedule_interview(db_session, data: dict) -> Interview:
    """Schedule a new interview."""
    scheduled_at = data.get("scheduled_at")
    if isinstance(scheduled_at, str):
        scheduled_at = datetime.fromisoformat(scheduled_at.replace("Z", "+00:00"))

    interview = Interview(
        application_id=data["application_id"],
        interviewer_id=data.get("interviewer_id", 1),
        scheduled_at=scheduled_at or datetime.utcnow(),
    )
    db_session.add(interview)
    db_session.commit()
    db_session.refresh(interview)
    return interview


def update_interview(db_session, interview_id: int, data: dict) -> Interview:
    """Update an existing interview."""
    interview = get_interview(db_session, interview_id)
    for key, value in data.items():
        setattr(interview, key, value)
    db_session.commit()
    db_session.refresh(interview)
    return interview


def cancel_interview(db_session, interview_id: int) -> bool:
    """Cancel an existing interview."""
    interview = get_interview(db_session, interview_id)
    interview.status = "cancelled"
    db_session.commit()
    return True
