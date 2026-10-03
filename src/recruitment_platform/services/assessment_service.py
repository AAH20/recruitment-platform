"""Assessment service for managing candidate assessments."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class AssessmentNotFoundError(Exception):
    """Raised when an assessment cannot be found."""


class AssessmentServiceError(Exception):
    """Raised for general assessment service errors."""


class AssessmentService:
    """Service for managing candidate assessments."""

    def __init__(self, db: Any | None = None) -> None:
        """Initialize the assessment service.

        Args:
            db: Optional database connection or repository.
        """
        self._db = db
        self._assessments: dict[str, dict[str, Any]] = {}

    def get_assessment(self, assessment_id: str) -> dict:
        """Get assessment by ID.

        Args:
            assessment_id: The unique identifier of the assessment.

        Returns:
            The assessment data as a dictionary.

        Raises:
            AssessmentNotFoundError: If the assessment does not exist.
            AssessmentServiceError: If an error occurs while fetching.
        """
        try:
            if not assessment_id:
                raise ValueError("assessment_id is required")

            if self._db is not None:
                result = self._db.get_assessment(assessment_id)
                if result is None:
                    raise AssessmentNotFoundError(
                        f"Assessment '{assessment_id}' not found"
                    )
                return result

            if assessment_id not in self._assessments:
                raise AssessmentNotFoundError(
                    f"Assessment '{assessment_id}' not found"
                )
            return self._assessments[assessment_id]
        except AssessmentNotFoundError:
            raise
        except Exception as exc:
            logger.error("Error fetching assessment %s: %s", assessment_id, exc)
            raise AssessmentServiceError(
                f"Failed to fetch assessment '{assessment_id}'"
            ) from exc

    def list_assessments(
        self, filters: dict, page: int, page_size: int
    ) -> list[dict]:
        """List assessments with optional filters and pagination.

        Args:
            filters: Dictionary of filter criteria (e.g., status, type).
            page: Page number (1-indexed).
            page_size: Number of items per page.

        Returns:
            List of assessment dictionaries matching the filters.

        Raises:
            AssessmentServiceError: If an error occurs while listing.
        """
        try:
            if page < 1:
                raise ValueError("page must be >= 1")
            if page_size < 1:
                raise ValueError("page_size must be >= 1")

            if self._db is not None:
                return self._db.list_assessments(filters, page, page_size)

            results = list(self._assessments.values())

            for key, value in (filters or {}).items():
                results = [a for a in results if a.get(key) == value]

            start = (page - 1) * page_size
            end = start + page_size
            return results[start:end]
        except Exception as exc:
            logger.error("Error listing assessments: %s", exc)
            raise AssessmentServiceError("Failed to list assessments") from exc

    def create_assessment(self, data: dict) -> dict:
        """Create a new assessment.

        Args:
            data: Dictionary containing assessment data (title, questions, etc.).

        Returns:
            The created assessment data with generated ID.

        Raises:
            AssessmentServiceError: If creation fails or data is invalid.
        """
        try:
            if not data:
                raise ValueError("Assessment data is required")

            assessment_id = data.get("id") or self._generate_id()
            assessment = {
                "id": assessment_id,
                "title": data.get("title", ""),
                "description": data.get("description", ""),
                "questions": data.get("questions", []),
                "status": data.get("status", "draft"),
                "created_at": data.get("created_at"),
                "updated_at": data.get("updated_at"),
            }

            if self._db is not None:
                return self._db.create_assessment(assessment)

            self._assessments[assessment_id] = assessment
            return assessment
        except Exception as exc:
            logger.error("Error creating assessment: %s", exc)
            raise AssessmentServiceError("Failed to create assessment") from exc

    def score_assessment(self, assessment_id: str, answers: dict) -> dict:
        """Score an assessment given candidate answers.

        Args:
            assessment_id: The unique identifier of the assessment.
            answers: Dictionary mapping question IDs to candidate answers.

        Returns:
            Scoring result with score, max_score, percentage, and details.

        Raises:
            AssessmentNotFoundError: If the assessment does not exist.
            AssessmentServiceError: If scoring fails.
        """
        try:
            if not assessment_id:
                raise ValueError("assessment_id is required")
            if not answers:
                raise ValueError("answers are required")

            assessment = self.get_assessment(assessment_id)
            questions = assessment.get("questions", [])

            total_score = 0
            max_score = 0
            details: list[dict[str, Any]] = []

            for question in questions:
                q_id = question.get("id")
                q_score = question.get("score", 1)
                max_score += q_score

                candidate_answer = answers.get(q_id)
                correct_answer = question.get("correct_answer")
                is_correct = candidate_answer == correct_answer
                earned = q_score if is_correct else 0
                total_score += earned

                details.append({
                    "question_id": q_id,
                    "correct": is_correct,
                    "earned": earned,
                    "max": q_score,
                })

            percentage = (total_score / max_score * 100) if max_score > 0 else 0.0

            return {
                "assessment_id": assessment_id,
                "score": total_score,
                "max_score": max_score,
                "percentage": round(percentage, 2),
                "details": details,
            }
        except AssessmentNotFoundError:
            raise
        except Exception as exc:
            logger.error("Error scoring assessment %s: %s", assessment_id, exc)
            raise AssessmentServiceError(
                f"Failed to score assessment '{assessment_id}'"
            ) from exc

    def delete_assessment(self, assessment_id: str) -> bool:
        """Delete an assessment by ID.

        Args:
            assessment_id: The unique identifier of the assessment.

        Returns:
            True if the assessment was deleted, False otherwise.

        Raises:
            AssessmentNotFoundError: If the assessment does not exist.
            AssessmentServiceError: If deletion fails.
        """
        try:
            if not assessment_id:
                raise ValueError("assessment_id is required")

            if self._db is not None:
                result = self._db.delete_assessment(assessment_id)
                if not result:
                    raise AssessmentNotFoundError(
                        f"Assessment '{assessment_id}' not found"
                    )
                return True

            if assessment_id not in self._assessments:
                raise AssessmentNotFoundError(
                    f"Assessment '{assessment_id}' not found"
                )
            del self._assessments[assessment_id]
            return True
        except AssessmentNotFoundError:
            raise
        except Exception as exc:
            logger.error("Error deleting assessment %s: %s", assessment_id, exc)
            raise AssessmentServiceError(
                f"Failed to delete assessment '{assessment_id}'"
            ) from exc

    @staticmethod
    def _generate_id() -> str:
        """Generate a unique assessment ID.

        Returns:
            A unique identifier string.
        """
        import uuid

        return str(uuid.uuid4())
