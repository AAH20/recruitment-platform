"""Job service for recruitment platform."""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class JobServiceError(Exception):
    """Base exception for job service errors."""


class JobNotFoundError(JobServiceError):
    """Raised when a job is not found."""


class JobValidationError(JobServiceError):
    """Raised when job data fails validation."""


@dataclass
class Job:
    """Represents a job posting."""

    id: str
    title: str
    description: str
    company: str
    location: str
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    employment_type: str = "full-time"
    status: str = "open"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


# In-memory store for demonstration
_jobs: Dict[str, Job] = {}


def _validate_job_data(data: Dict[str, Any]) -> None:
    """Validate job data before creation or update.

    Args:
        data: Dictionary containing job fields.

    Raises:
        JobValidationError: If required fields are missing or invalid.
    """
    required_fields = ["title", "description", "company", "location"]
    missing = [f for f in required_fields if not data.get(f)]
    if missing:
        raise JobValidationError(
            f"Missing required fields: {', '.join(missing)}"
        )

    if data.get("salary_min") is not None and data.get("salary_max") is not None:
        if data["salary_min"] > data["salary_max"]:
            raise JobValidationError("salary_min cannot exceed salary_max")

    valid_types = {"full-time", "part-time", "contract", "internship", "temporary"}
    if data.get("employment_type", "full-time") not in valid_types:
        raise JobValidationError(
            f"employment_type must be one of: {', '.join(valid_types)}"
        )


def _job_to_dict(job: Job) -> Dict[str, Any]:
    """Convert a Job instance to a dictionary.

    Args:
        job: The Job instance to convert.

    Returns:
        Dictionary representation of the job.
    """
    return asdict(job)


def get_job(job_id: str) -> Dict[str, Any]:
    """Get a job by its ID.

    Args:
        job_id: The unique identifier of the job.

    Returns:
        A dictionary containing the job data.

    Raises:
        JobNotFoundError: If no job exists with the given ID.
        JobServiceError: If the operation fails.
    """
    try:
        job = _jobs.get(job_id)
        if job is None:
            raise JobNotFoundError(f"Job with id '{job_id}' not found")
        return _job_to_dict(job)
    except JobNotFoundError:
        raise
    except Exception as e:
        logger.error("Failed to get job %s: %s", job_id, e)
        raise JobServiceError(f"Failed to get job: {e}") from e


def list_jobs(
    filters: Dict[str, Any], page: int, page_size: int
) -> List[Dict[str, Any]]:
    """List jobs with optional filters and pagination.

    Args:
        filters: Dictionary of filter criteria (company, location, status,
                 employment_type, tags).
        page: Page number (1-indexed).
        page_size: Number of jobs per page.

    Returns:
        A list of job dictionaries matching the filters.

    Raises:
        JobServiceError: If the operation fails.
        ValueError: If page or page_size is invalid.
    """
    if page < 1:
        raise ValueError("page must be >= 1")
    if page_size < 1:
        raise ValueError("page_size must be >= 1")

    try:
        results: List[Job] = list(_jobs.values())

        # Apply filters
        if filters.get("company"):
            results = [j for j in results if j.company.lower() == filters["company"].lower()]
        if filters.get("location"):
            results = [j for j in results if j.location.lower() == filters["location"].lower()]
        if filters.get("status"):
            results = [j for j in results if j.status == filters["status"]]
        if filters.get("employment_type"):
            results = [j for j in results if j.employment_type == filters["employment_type"]]
        if filters.get("tags"):
            tag_set = set(filters["tags"])
            results = [j for j in results if tag_set.issubset(set(j.tags))]

        # Apply pagination
        start = (page - 1) * page_size
        end = start + page_size
        paginated = results[start:end]

        return [_job_to_dict(j) for j in paginated]
    except (ValueError, JobServiceError):
        raise
    except Exception as e:
        logger.error("Failed to list jobs: %s", e)
        raise JobServiceError(f"Failed to list jobs: {e}") from e


def create_job(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new job posting.

    Args:
        data: Dictionary containing job fields (title, description, company,
              location, salary_min, salary_max, employment_type, tags, etc.).

    Returns:
        A dictionary containing the created job data with generated ID.

    Raises:
        JobValidationError: If required fields are missing or data is invalid.
        JobServiceError: If the creation fails.
    """
    if not data or not isinstance(data, dict):
        raise ValueError("data must be a non-empty dictionary")

    try:
        _validate_job_data(data)

        job_id = str(uuid.uuid4())
        now = datetime.utcnow()

        job = Job(
            id=job_id,
            title=data["title"],
            description=data["description"],
            company=data["company"],
            location=data["location"],
            salary_min=data.get("salary_min"),
            salary_max=data.get("salary_max"),
            employment_type=data.get("employment_type", "full-time"),
            status=data.get("status", "open"),
            created_at=now,
            updated_at=now,
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
        )

        _jobs[job_id] = job
        return _job_to_dict(job)
    except (JobValidationError, ValueError):
        raise
    except Exception as e:
        logger.error("Failed to create job: %s", e)
        raise JobServiceError(f"Failed to create job: {e}") from e


def update_job(job_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Update an existing job.

    Args:
        job_id: The unique identifier of the job to update.
        data: Dictionary containing fields to update.

    Returns:
        A dictionary containing the updated job data.

    Raises:
        JobNotFoundError: If no job exists with the given ID.
        JobValidationError: If the update data is invalid.
        JobServiceError: If the update operation fails.
    """
    if not data or not isinstance(data, dict):
        raise ValueError("data must be a non-empty dictionary")

    try:
        job = _jobs.get(job_id)
        if job is None:
            raise JobNotFoundError(f"Job with id '{job_id}' not found")

        # Merge existing data with updates for validation
        merged = _job_to_dict(job)
        merged.update(data)
        _validate_job_data(merged)

        # Apply updates
        for key, value in data.items():
            if hasattr(job, key):
                setattr(job, key, value)

        job.updated_at = datetime.utcnow()
        return _job_to_dict(job)
    except (JobNotFoundError, JobValidationError, ValueError):
        raise
    except Exception as e:
        logger.error("Failed to update job %s: %s", job_id, e)
        raise JobServiceError(f"Failed to update job: {e}") from e


def delete_job(job_id: str) -> bool:
    """Delete a job by its ID.

    Args:
        job_id: The unique identifier of the job to delete.

    Returns:
        True if the job was deleted successfully.

    Raises:
        JobNotFoundError: If no job exists with the given ID.
        JobServiceError: If the deletion operation fails.
    """
    try:
        if job_id not in _jobs:
            raise JobNotFoundError(f"Job with id '{job_id}' not found")
        del _jobs[job_id]
        return True
    except JobNotFoundError:
        raise
    except Exception as e:
        logger.error("Failed to delete job %s: %s", job_id, e)
        raise JobServiceError(f"Failed to delete job: {e}") from e
