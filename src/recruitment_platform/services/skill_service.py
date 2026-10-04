"""Skill service for managing skills in the recruitment platform."""

from __future__ import annotations

import logging
import uuid
from typing import Any

logger = logging.getLogger(__name__)


class SkillNotFoundError(Exception):
    """Raised when a skill with the given ID does not exist."""


class SkillValidationError(Exception):
    """Raised when skill data fails validation."""


# In-memory store for skills
_skills: dict[int, dict[str, Any]] = {}
_next_skill_id: int = 1


def get_skill(db_session, skill_id: int) -> dict:
    """Get a skill by its ID."""
    skill = _skills.get(skill_id)
    if skill is None:
        raise SkillNotFoundError(f"Skill with id '{skill_id}' not found")
    return skill


def list_skills(db_session) -> list[dict]:
    """List all skills."""
    return list(_skills.values())


def create_skill(db_session, data: dict) -> dict:
    """Create a new skill."""
    global _next_skill_id
    skill = {"id": _next_skill_id, **data}
    _skills[_next_skill_id] = skill
    _next_skill_id += 1
    return skill


def update_skill(db_session, skill_id: int, data: dict) -> dict:
    """Update an existing skill."""
    skill = get_skill(db_session, skill_id)
    skill.update(data)
    return skill


def delete_skill(db_session, skill_id: int) -> bool:
    """Delete a skill."""
    if skill_id not in _skills:
        raise SkillNotFoundError(f"Skill with id '{skill_id}' not found")
    del _skills[skill_id]
    return True


class SkillService:
    """Service for CRUD operations on skills."""

    def __init__(self, db: Any = None) -> None:
        self._db = db

    def get_skill(self, skill_id: str) -> dict:
        if not skill_id or not isinstance(skill_id, str):
            raise SkillValidationError("skill_id must be a non-empty string")
        logger.info("Fetching skill with id=%s", skill_id)
        if self._db is not None:
            skill = self._db.get_skill(skill_id)
            if skill is None:
                raise SkillNotFoundError(f"Skill with id '{skill_id}' not found")
            return skill
        raise SkillNotFoundError(f"Skill with id '{skill_id}' not found")

    def list_skills(self, filters: dict | None = None, page: int = 1, page_size: int = 20) -> list[dict]:
        if page < 1:
            raise SkillValidationError("page must be >= 1")
        if page_size < 1:
            raise SkillValidationError("page_size must be >= 1")
        if self._db is not None:
            return self._db.list_skills(filters=filters, page=page, page_size=page_size)
        return []

    def create_skill(self, data: dict) -> dict:
        if not data or not isinstance(data, dict):
            raise SkillValidationError("data must be a non-empty dictionary")
        if "name" not in data or not data["name"]:
            raise SkillValidationError("skill 'name' is required")
        if self._db is not None:
            return self._db.create_skill(data)
        return {"id": "generated-id", **data}

    def update_skill(self, skill_id: str, data: dict) -> dict:
        if not skill_id or not isinstance(skill_id, str):
            raise SkillValidationError("skill_id must be a non-empty string")
        if not data or not isinstance(data, dict):
            raise SkillValidationError("data must be a non-empty dictionary")
        if self._db is not None:
            existing = self._db.get_skill(skill_id)
            if existing is None:
                raise SkillNotFoundError(f"Skill with id '{skill_id}' not found")
            return self._db.update_skill(skill_id, data)
        raise SkillNotFoundError(f"Skill with id '{skill_id}' not found")

    def delete_skill(self, skill_id: str) -> bool:
        if not skill_id or not isinstance(skill_id, str):
            raise SkillValidationError("skill_id must be a non-empty string")
        if self._db is not None:
            existing = self._db.get_skill(skill_id)
            if existing is None:
                raise SkillNotFoundError(f"Skill with id '{skill_id}' not found")
            self._db.delete_skill(skill_id)
            return True
        raise SkillNotFoundError(f"Skill with id '{skill_id}' not found")
