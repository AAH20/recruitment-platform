"""Skill service for managing skills in the recruitment platform."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class SkillNotFoundError(Exception):
    """Raised when a skill with the given ID does not exist."""


class SkillValidationError(Exception):
    """Raised when skill data fails validation."""


class SkillService:
    """Service for CRUD operations on skills."""

    def __init__(self, db: Any = None) -> None:
        """Initialize the skill service.

        Args:
            db: Database session or repository instance.
        """
        self._db = db

    def get_skill(self, skill_id: str) -> dict:
        """Get a skill by its ID.

        Args:
            skill_id: The unique identifier of the skill.

        Returns:
            A dictionary containing the skill data.

        Raises:
            SkillNotFoundError: If no skill exists with the given ID.
            SkillValidationError: If skill_id is empty or invalid.
        """
        if not skill_id or not isinstance(skill_id, str):
            raise SkillValidationError("skill_id must be a non-empty string")

        logger.info("Fetching skill with id=%s", skill_id)

        if self._db is not None:
            skill = self._db.get_skill(skill_id)
            if skill is None:
                raise SkillNotFoundError(f"Skill with id '{skill_id}' not found")
            return skill

        raise SkillNotFoundError(f"Skill with id '{skill_id}' not found")

    def list_skills(
        self,
        filters: dict | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> list[dict]:
        """List skills with optional filtering and pagination.

        Args:
            filters: Optional dictionary of filter criteria.
            page: Page number (1-indexed).
            page_size: Number of items per page.

        Returns:
            A list of skill dictionaries matching the criteria.

        Raises:
            SkillValidationError: If page or page_size is invalid.
        """
        if page < 1:
            raise SkillValidationError("page must be >= 1")
        if page_size < 1:
            raise SkillValidationError("page_size must be >= 1")

        filters = filters or {}
        logger.info(
            "Listing skills with filters=%s, page=%d, page_size=%d",
            filters,
            page,
            page_size,
        )

        if self._db is not None:
            return self._db.list_skills(filters=filters, page=page, page_size=page_size)

        return []

    def create_skill(self, data: dict) -> dict:
        """Create a new skill.

        Args:
            data: Dictionary containing skill data (name, description, etc.).

        Returns:
            A dictionary containing the created skill data.

        Raises:
            SkillValidationError: If data is invalid or missing required fields.
        """
        if not data or not isinstance(data, dict):
            raise SkillValidationError("data must be a non-empty dictionary")

        if "name" not in data or not data["name"]:
            raise SkillValidationError("skill 'name' is required")

        logger.info("Creating skill with name=%s", data["name"])

        if self._db is not None:
            return self._db.create_skill(data)

        return {"id": "generated-id", **data}

    def update_skill(self, skill_id: str, data: dict) -> dict:
        """Update an existing skill.

        Args:
            skill_id: The unique identifier of the skill to update.
            data: Dictionary containing the fields to update.

        Returns:
            A dictionary containing the updated skill data.

        Raises:
            SkillNotFoundError: If no skill exists with the given ID.
            SkillValidationError: If skill_id or data is invalid.
        """
        if not skill_id or not isinstance(skill_id, str):
            raise SkillValidationError("skill_id must be a non-empty string")
        if not data or not isinstance(data, dict):
            raise SkillValidationError("data must be a non-empty dictionary")

        logger.info("Updating skill with id=%s", skill_id)

        if self._db is not None:
            existing = self._db.get_skill(skill_id)
            if existing is None:
                raise SkillNotFoundError(f"Skill with id '{skill_id}' not found")
            return self._db.update_skill(skill_id, data)

        raise SkillNotFoundError(f"Skill with id '{skill_id}' not found")

    def delete_skill(self, skill_id: str) -> bool:
        """Delete a skill by its ID.

        Args:
            skill_id: The unique identifier of the skill to delete.

        Returns:
            True if the skill was successfully deleted.

        Raises:
            SkillNotFoundError: If no skill exists with the given ID.
            SkillValidationError: If skill_id is empty or invalid.
        """
        if not skill_id or not isinstance(skill_id, str):
            raise SkillValidationError("skill_id must be a non-empty string")

        logger.info("Deleting skill with id=%s", skill_id)

        if self._db is not None:
            existing = self._db.get_skill(skill_id)
            if existing is None:
                raise SkillNotFoundError(f"Skill with id '{skill_id}' not found")
            self._db.delete_skill(skill_id)
            return True

        raise SkillNotFoundError(f"Skill with id '{skill_id}' not found")
