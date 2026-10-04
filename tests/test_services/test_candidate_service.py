"""Tests for candidate service."""

import pytest
from unittest.mock import MagicMock, patch


class TestCandidateService:
    """Test candidate service functionality."""

    def test_create_candidate(self, db_session):
        """Test creating a candidate."""
        from recruitment_platform.services.candidate_service import create_candidate
        
        candidate_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "skills": ["Python", "FastAPI"],
        }
        
        result = create_candidate(db_session, candidate_data)
        assert result is not None
        assert result.name == "John Doe"

    def test_get_candidate(self, db_session):
        """Test getting a candidate."""
        from recruitment_platform.services.candidate_service import get_candidate, create_candidate
        
        candidate_data = {"name": "Jane Doe", "email": "jane@example.com"}
        created = create_candidate(db_session, candidate_data)
        
        result = get_candidate(db_session, created.id)
        assert result is not None
        assert result.name == "Jane Doe"

    def test_list_candidates(self, db_session):
        """Test listing candidates."""
        from recruitment_platform.services.candidate_service import list_candidates
        
        result = list_candidates(db_session)
        assert isinstance(result, list)

    def test_update_candidate(self, db_session):
        """Test updating a candidate."""
        from recruitment_platform.services.candidate_service import update_candidate, create_candidate
        
        candidate_data = {"name": "Bob", "email": "bob@example.com"}
        created = create_candidate(db_session, candidate_data)
        
        update_data = {"name": "Bob Updated"}
        result = update_candidate(db_session, created.id, update_data)
        assert result is not None
        assert result.name == "Bob Updated"

    def test_delete_candidate(self, db_session):
        """Test deleting a candidate."""
        from recruitment_platform.services.candidate_service import delete_candidate, create_candidate
        
        candidate_data = {"name": "Delete Me", "email": "delete@example.com"}
        created = create_candidate(db_session, candidate_data)
        
        result = delete_candidate(db_session, created.id)
        assert result is True

    def test_search_candidates(self, db_session):
        """Test searching candidates."""
        from recruitment_platform.services.candidate_service import search_candidates
        
        result = search_candidates(db_session, "Python")
        assert isinstance(result, list)
