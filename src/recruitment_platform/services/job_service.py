"""Job service for recruitment platform."""

from __future__ import annotations

import json
import logging

from recruitment_platform.models import Job

logger = logging.getLogger(__name__)


class JobNotFoundError(Exception):
    """Raised when a job is not found."""


class JobServiceError(Exception):
    """Raised when a job service operation fails."""


def get_job(db_session, job_id: int) -> Job:
    """Get job by ID."""
    job = db_session.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise JobNotFoundError(f"Job {job_id} not found")
    return job


def list_jobs(db_session) -> list[Job]:
    """List all jobs."""
    return db_session.query(Job).all()


def create_job(db_session, data: dict) -> Job:
    """Create a new job."""
    requirements = json.dumps(data.get("requirements", [])) if data.get("requirements") else None

    job = Job(
        title=data["title"],
        description=data.get("description"),
        requirements=requirements,
        employer_id=data.get("employer_id", 0),
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)
    return job


def update_job(db_session, job_id: int, data: dict) -> Job:
    """Update an existing job."""
    job = get_job(db_session, job_id)
    for key, value in data.items():
        if key == "requirements" and isinstance(value, list):
            value = json.dumps(value)
        setattr(job, key, value)
    db_session.commit()
    db_session.refresh(job)
    return job


def delete_job(db_session, job_id: int) -> bool:
    """Delete a job."""
    job = get_job(db_session, job_id)
    db_session.delete(job)
    db_session.commit()
    return True


def filter_jobs(db_session, **filters) -> list[Job]:
    """Filter jobs by criteria."""
    query = db_session.query(Job)
    if "location" in filters:
        query = query.filter(Job.title.ilike(f"%{filters['location']}%"))
    return query.all()
