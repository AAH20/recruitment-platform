"""Interview service for managing interviews in the recruitment platform."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class InterviewNotFoundError(Exception):
    """Raised when an interview is not found."""


class InterviewServiceError(Exception):
    """Raised when an interview service operation fails."""


class InterviewService:
    """Service for managing interviews."""

    def __init__(self, db: Any) -> None:
        """Initialize the interview service.

        Args:
            db: Database session or repository instance.
        """
        self._db = db

    def get_interview(self, interview_id: str) -> dict:
        """Get an interview by its ID.

        Args:
            interview_id: The unique identifier of the interview.

        Returns:
            A dictionary containing the interview data.

        Raises:
            InterviewNotFoundError: If no interview exists with the given ID.
            InterviewServiceError: If the database query fails.
        """
        try:
            interview = self._db.get_interview(interview_id)
            if interview is None:
                raise InterviewNotFoundError(
                    f"Interview with ID '{interview_id}' not found."
                )
            return interview
        except InterviewNotFoundError:
            raise
        except Exception as exc:
            logger.error("Failed to get interview %s: %s", interview_id, exc)
            raise InterviewServiceError(
                f"Failed to retrieve interview '{interview_id}'."
            ) from exc

    def list_interviews(
        self, filters: dict, page: int, page_size: int
    ) -> list[dict]:
        """List interviews with optional filters and pagination.

        Args:
            filters: A dictionary of filter criteria (e.g., status, candidate_id).
            page: The page number (1-indexed).
            page_size: The number of interviews per page.

        Returns:
            A list of interview dictionaries matching the filters.

        Raises:
            InterviewServiceError: If the database query fails.
            ValueError: If page or page_size is less than 1.
        """
        if page < 1:
            raise ValueError("page must be >= 1")
        if page_size < 1:
            raise ValueError("page_size must be >= 1")

        try:
            offset = (page - 1) * page_size
            interviews = self._db.list_interviews(
                filters=filters, offset=offset, limit=page_size
            )
            return interviews
        except Exception as exc:
            logger.error("Failed to list interviews: %s", exc)
            raise InterviewServiceError("Failed to list interviews.") from exc

    def schedule_interview(self, data: dict) -> dict:
        """Schedule a new interview.

        Args:
            data: A dictionary containing interview details (candidate_id,
                interviewer_id, scheduled_at, etc.).

        Returns:
            A dictionary containing the created interview data.

        Raises:
            InterviewServiceError: If scheduling fails.
            ValueError: If required fields are missing.
        """
        required_fields = {"candidate_id", "interviewer_id", "scheduled_at"}
        missing = required_fields - data.keys()
        if missing:
            raise ValueError(f"Missing required fields: {missing}")

        try:
            interview = self._db.create_interview(data)
            return interview
        except Exception as exc:
            logger.error("Failed to schedule interview: %s", exc)
            raise InterviewServiceError("Failed to schedule interview.") from exc

    def update_interview(self, interview_id: str, data: dict) -> dict:
        """Update an existing interview.

        Args:
            interview_id: The unique identifier of the interview to update.
            data: A dictionary containing the fields to update.

        Returns:
            A dictionary containing the updated interview data.

        Raises:
            InterviewNotFoundError: If no interview exists with the given ID.
            InterviewServiceError: If the update fails.
        """
        try:
            existing = self._db.get_interview(interview_id)
            if existing is None:
                raise InterviewNotFoundError(
                    f"Interview with ID '{interview_id}' not found."
                )
            updated = self._db.update_interview(interview_id, data)
            return updated
        except InterviewNotFoundError:
            raise
        except Exception as exc:
            logger.error("Failed to update interview %s: %s", interview_id, exc)
            raise InterviewServiceError(
                f"Failed to update interview '{interview_id}'."
            ) from exc

    def cancel_interview(self, interview_id: str) -> bool:
        """Cancel an existing interview.

        Args:
            interview_id: The unique identifier of the interview to cancel.

        Returns:
            True if the interview was successfully cancelled.

        Raises:
            InterviewNotFoundError: If no interview exists with the given ID.
            InterviewServiceError: If the cancellation fails.
        """
        try:
            existing = self._db.get_interview(interview_id)
            if existing is None:
                raise InterviewNotFoundError(
                    f"Interview with ID '{interview_id}' not found."
                )
            self._db.update_interview(interview_id, {"status": "cancelled"})
            return True
        except InterviewNotFoundError:
            raise
        except Exception as exc:
            logger.error("Failed to cancel interview %s: %s", interview_id, exc)
            raise InterviewServiceError(
                f"Failed to cancel interview '{interview_id}'."
            ) from exc
