"""Employer service for recruitment platform."""

from __future__ import annotations

import logging

from recruitment_platform.models.employer import Employer

logger = logging.getLogger(__name__)


class EmployerNotFoundError(Exception):
    """Raised when an employer is not found."""


class EmployerServiceError(Exception):
    """Raised when an employer service operation fails."""


def get_employer(db_session, employer_id: int) -> Employer:
    """Get employer by ID."""
    employer = db_session.query(Employer).filter(Employer.id == employer_id).first()
    if not employer:
        raise EmployerNotFoundError(f"Employer {employer_id} not found")
    return employer


def list_employers(db_session) -> list[Employer]:
    """List all employers."""
    return db_session.query(Employer).all()


def create_employer(db_session, data: dict) -> Employer:
    """Create a new employer."""
    employer = Employer(
        name=data["name"],
        industry=data.get("industry"),
        size=data.get("size"),
        location=data.get("location"),
        website=data.get("website"),
        description=data.get("description"),
    )
    db_session.add(employer)
    db_session.commit()
    db_session.refresh(employer)
    return employer


def update_employer(db_session, employer_id: int, data: dict) -> Employer:
    """Update an existing employer."""
    employer = get_employer(db_session, employer_id)
    for key, value in data.items():
        setattr(employer, key, value)
    db_session.commit()
    db_session.refresh(employer)
    return employer


def delete_employer(db_session, employer_id: int) -> bool:
    """Delete an employer."""
    employer = get_employer(db_session, employer_id)
    db_session.delete(employer)
    db_session.commit()
    return True
