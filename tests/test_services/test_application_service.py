"""Tests for application service."""
import pytest
from unittest.mock import MagicMock, patch

from recruitment_platform.models import Candidate, Job


class TestApplicationService:
    """Test application service functionality."""

    def _create_prerequisites(self, db_session):
        """Create candidate and job needed for application tests."""
        candidate = Candidate(name="Test Candidate", email="test@example.com")
        db_session.add(candidate)
        db_session.flush()
        job = Job(title="Test Job", employer_id=1)
        db_session.add(job)
        db_session.flush()
        return candidate, job

    def test_create_application(self, db_session):
        """Test creating an application."""
        from recruitment_platform.services.application_service import create_application

        candidate, job = self._create_prerequisites(db_session)

        app_data = {
            "job_id": job.id,
            "candidate_id": candidate.id,
            "cover_letter": "I am interested",
        }

        result = create_application(db_session, app_data)
        assert result is not None
        assert result.job_id == job.id
        assert result.candidate_id == candidate.id
        assert result.status == "pending"

    def test_get_application(self, db_session):
        """Test getting an application."""
        from recruitment_platform.services.application_service import (
            create_application,
            get_application,
        )

        candidate, job = self._create_prerequisites(db_session)
        app_data = {"job_id": job.id, "candidate_id": candidate.id}
        created = create_application(db_session, app_data)

        result = get_application(db_session, created.id)
        assert result is not None
        assert result.id == created.id

    def test_list_applications(self, db_session):
        """Test listing applications."""
        from recruitment_platform.services.application_service import list_applications

        result = list_applications(db_session)
        assert isinstance(result, list)

    def test_update_application_status(self, db_session):
        """Test updating application status."""
        from recruitment_platform.services.application_service import (
            create_application,
            update_application_status,
        )

        candidate, job = self._create_prerequisites(db_session)
        app_data = {"job_id": job.id, "candidate_id": candidate.id}
        created = create_application(db_session, app_data)

        result = update_application_status(db_session, created.id, "accepted")
        assert result is not None
        assert result.status == "accepted"

    def test_delete_application(self, db_session):
        """Test deleting an application."""
        from recruitment_platform.services.application_service import (
            create_application,
            delete_application,
        )

        candidate, job = self._create_prerequisites(db_session)
        app_data = {"job_id": job.id, "candidate_id": candidate.id}
        created = create_application(db_session, app_data)

        result = delete_application(db_session, created.id)
        assert result is True
