"""Tests for interview service."""

import pytest
from unittest.mock import MagicMock, patch


class TestInterviewService:
    """Test interview service functionality."""

    def test_schedule_interview(self, db_session):
        """Test scheduling an interview."""
        from recruitment_platform.services.interview_service import schedule_interview
        
        interview_data = {
            "application_id": 1,
            "interviewer_id": 1,
            "scheduled_at": "2024-01-01T10:00:00",
        }
        
        result = schedule_interview(db_session, interview_data)
        assert result is not None

    def test_get_interview(self, db_session):
        """Test getting an interview."""
        from recruitment_platform.services.interview_service import get_interview
        
        result = get_interview(db_session, 1)
        assert result is not None

    def test_list_interviews(self, db_session):
        """Test listing interviews."""
        from recruitment_platform.services.interview_service import list_interviews
        
        result = list_interviews(db_session)
        assert isinstance(result, list)

    def test_update_interview(self, db_session):
        """Test updating an interview."""
        from recruitment_platform.services.interview_service import update_interview
        
        update_data = {"status": "completed"}
        result = update_interview(db_session, 1, update_data)
        assert result is not None

    def test_cancel_interview(self, db_session):
        """Test canceling an interview."""
        from recruitment_platform.services.interview_service import cancel_interview
        
        result = cancel_interview(db_session, 1)
        assert result is True
