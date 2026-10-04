"""Service layer for managing job applications."""

from __future__ import annotations

import logging
from datetime import datetime

from recruitment_platform.models import Application

logger = logging.getLogger(__name__)

VALID_STATUSES = {
    "pending",
    "reviewing",
    "interview",
    "offered",
    "rejected",
    "withdrawn",
    "accepted",
}


class ApplicationNotFoundError(Exception):
    """Raised when an application is not found."""


class ApplicationValidationError(Exception):
    """Raised when application data is invalid."""


def get_application(db_session, application_id: int) -> Application:
    """Get an application by its ID."""
    application = db_session.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise ApplicationNotFoundError(f"Application {application_id} not found")
    return application


def list_applications(db_session) -> list[Application]:
    """List all applications."""
    return db_session.query(Application).all()


def create_application(db_session, data: dict) -> Application:
    """Create a new application."""
    application = Application(
        job_id=data["job_id"],
        candidate_id=data["candidate_id"],
        status=data.get("status", "pending"),
    )
    db_session.add(application)
    db_session.commit()
    db_session.refresh(application)
    return application


def update_application_status(db_session, application_id: int, status: str) -> Application:
    """Update the status of an application."""
    application = get_application(db_session, application_id)
    application.status = status
    db_session.commit()
    db_session.refresh(application)
    return application


def delete_application(db_session, application_id: int) -> bool:
    """Delete an application."""
    application = get_application(db_session, application_id)
    db_session.delete(application)
    db_session.commit()
    return True
