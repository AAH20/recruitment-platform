"""Tests for application service."""

import pytest
from unittest.mock import MagicMock, patch


class TestApplicationService:
    """Test application service functionality."""

    def test_create_application(self, db_session):
        """Test creating an application."""
        from recruitment_platform.services.application_service import create_application
        
        app_data = {
            "job_id": 1,
            "candidate_id": 1,
            "cover_letter": "I am interested",
        }
        
        result = create_application(db_session, app_data)
        assert result is not None

    def test_get_application(self, db_session):
        """Test getting an application."""
        from recruitment_platform.services.application_service import get_application
        
        result = get_application(db_session, 1)
        assert result is not None

    def test_list_applications(self, db_session):
        """Test listing applications."""
        from recruitment_platform.services.application_service import list_applications
        
        result = list_applications(db_session)
        assert isinstance(result, list)

    def test_update_application_status(self, db_session):
        """Test updating application status."""
        from recruitment_platform.services.application_service import update_application_status
        
        result = update_application_status(db_session, 1, "accepted")
        assert result is not None

    def test_delete_application(self, db_session):
        """Test deleting an application."""
        from recruitment_platform.services.application_service import delete_application
        
        result = delete_application(db_session, 1)
        assert result is True
