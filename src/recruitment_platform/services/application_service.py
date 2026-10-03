"""Service layer for managing job applications."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

VALID_STATUSES = {
    "pending",
    "reviewing",
    "interview",
    "offered",
    "rejected",
    "withdrawn",
}


class ApplicationNotFoundError(Exception):
    """Raised when an application is not found."""


class ApplicationValidationError(Exception):
    """Raised when application data is invalid."""


def get_application(application_id: str) -> dict:
    """Get an application by its ID.

    Args:
        application_id: The unique identifier of the application.

    Returns:
        A dictionary containing the application data.

    Raises:
        ApplicationNotFoundError: If no application exists with the given ID.
        ApplicationValidationError: If the application_id is empty or invalid.
    """
    if not application_id or not isinstance(application_id, str):
        raise ApplicationValidationError("application_id must be a non-empty string")

    logger.info("Fetching application: %s", application_id)

    # TODO: Replace with actual database query
    application = None

    if application is None:
        raise ApplicationNotFoundError(
            f"Application with id '{application_id}' not found"
        )

    return application


def list_applications(
    filters: dict[str, Any] | None = None,
    page: int = 1,
    page_size: int = 20,
) -> list[dict]:
    """List applications with optional filtering and pagination.

    Args:
        filters: Optional dictionary of filter criteria (e.g., status, job_id).
        page: The page number (1-indexed).
        page_size: The number of results per page.

    Returns:
        A list of application dictionaries matching the criteria.

    Raises:
        ApplicationValidationError: If page or page_size is invalid.
    """
    if page < 1:
        raise ApplicationValidationError("page must be >= 1")
    if page_size < 1 or page_size > 100:
        raise ApplicationValidationError("page_size must be between 1 and 100")

    filters = filters or {}
    logger.info(
        "Listing applications with filters=%s, page=%d, page_size=%d",
        filters,
        page,
        page_size,
    )

    # TODO: Replace with actual database query
    applications: list[dict] = []

    return applications


def create_application(data: dict) -> dict:
    """Create a new application.

    Args:
        data: A dictionary containing the application data. Must include
            at least 'job_id' and 'candidate_id'.

    Returns:
        A dictionary containing the created application data, including
        the generated ID.

    Raises:
        ApplicationValidationError: If required fields are missing or data is invalid.
    """
    if not isinstance(data, dict):
        raise ApplicationValidationError("data must be a dictionary")

    required_fields = {"job_id", "candidate_id"}
    missing = required_fields - data.keys()
    if missing:
        raise ApplicationValidationError(
            f"Missing required fields: {', '.join(sorted(missing))}"
        )

    logger.info(
        "Creating application for job=%s, candidate=%s",
        data["job_id"],
        data["candidate_id"],
    )

    # TODO: Replace with actual database insert
    application: dict = {
        "id": "generated-id",
        "status": "pending",
        **data,
    }

    return application


def update_application_status(application_id: str, status: str) -> dict:
    """Update the status of an application.

    Args:
        application_id: The unique identifier of the application.
        status: The new status value. Must be one of: pending, reviewing,
            interview, offered, rejected, withdrawn.

    Returns:
        A dictionary containing the updated application data.

    Raises:
        ApplicationNotFoundError: If no application exists with the given ID.
        ApplicationValidationError: If the status is invalid or application_id is empty.
    """
    if not application_id or not isinstance(application_id, str):
        raise ApplicationValidationError("application_id must be a non-empty string")
    if status not in VALID_STATUSES:
        raise ApplicationValidationError(
            f"Invalid status '{status}'. Must be one of: {', '.join(sorted(VALID_STATUSES))}"
        )

    logger.info("Updating application %s status to %s", application_id, status)

    # TODO: Replace with actual database update
    application = None

    if application is None:
        raise ApplicationNotFoundError(
            f"Application with id '{application_id}' not found"
        )

    return application


def delete_application(application_id: str) -> bool:
    """Delete an application by its ID.

    Args:
        application_id: The unique identifier of the application to delete.

    Returns:
        True if the application was successfully deleted.

    Raises:
        ApplicationNotFoundError: If no application exists with the given ID.
        ApplicationValidationError: If the application_id is empty or invalid.
    """
    if not application_id or not isinstance(application_id, str):
        raise ApplicationValidationError("application_id must be a non-empty string")

    logger.info("Deleting application: %s", application_id)

    # TODO: Replace with actual database delete
    deleted = False

    if not deleted:
        raise ApplicationNotFoundError(
            f"Application with id '{application_id}' not found"
        )

    return True
