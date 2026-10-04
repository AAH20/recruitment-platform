"""Tests for skill service."""

import pytest
from unittest.mock import MagicMock, patch


class TestSkillService:
    """Test skill service functionality."""

    def test_create_skill(self, db_session):
        """Test creating a skill."""
        from recruitment_platform.services.skill_service import create_skill
        
        skill_data = {"name": "Python", "category": "Programming"}
        
        result = create_skill(db_session, skill_data)
        assert result is not None
        assert result.name == "Python"

    def test_get_skill(self, db_session):
        """Test getting a skill."""
        from recruitment_platform.services.skill_service import get_skill
        
        result = get_skill(db_session, 1)
        assert result is not None

    def test_list_skills(self, db_session):
        """Test listing skills."""
        from recruitment_platform.services.skill_service import list_skills
        
        result = list_skills(db_session)
        assert isinstance(result, list)

    def test_update_skill(self, db_session):
        """Test updating a skill."""
        from recruitment_platform.services.skill_service import update_skill
        
        update_data = {"name": "Python 3"}
        result = update_skill(db_session, 1, update_data)
        assert result is not None

    def test_delete_skill(self, db_session):
        """Test deleting a skill."""
        from recruitment_platform.services.skill_service import delete_skill
        
        result = delete_skill(db_session, 1)
        assert result is True
