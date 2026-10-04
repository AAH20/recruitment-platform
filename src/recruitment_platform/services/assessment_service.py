"""Assessment service for managing candidate assessments."""

from __future__ import annotations

import logging
from datetime import datetime

from recruitment_platform.models import Assessment

logger = logging.getLogger(__name__)


class AssessmentNotFoundError(Exception):
    """Raised when an assessment cannot be found."""


class AssessmentServiceError(Exception):
    """Raised for general assessment service errors."""


def get_assessment(db_session, assessment_id: int) -> Assessment:
    """Get assessment by ID."""
    assessment = db_session.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise AssessmentNotFoundError(f"Assessment {assessment_id} not found")
    return assessment


def list_assessments(db_session) -> list[Assessment]:
    """List all assessments."""
    return db_session.query(Assessment).all()


def create_assessment(db_session, data: dict) -> Assessment:
    """Create a new assessment."""
    assessment = Assessment(
        candidate_id=data.get("candidate_id", 1),
        skill=data.get("type", "general"),
        score=float(data.get("score", 0)),
        assessed_at=datetime.utcnow(),
    )
    db_session.add(assessment)
    db_session.commit()
    db_session.refresh(assessment)
    return assessment


def update_assessment(db_session, assessment_id: int, data: dict) -> Assessment:
    """Update an existing assessment."""
    assessment = get_assessment(db_session, assessment_id)
    for key, value in data.items():
        setattr(assessment, key, value)
    db_session.commit()
    db_session.refresh(assessment)
    return assessment


def delete_assessment(db_session, assessment_id: int) -> bool:
    """Delete an assessment."""
    assessment = get_assessment(db_session, assessment_id)
    db_session.delete(assessment)
    db_session.commit()
    return True
