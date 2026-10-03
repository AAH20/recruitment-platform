"""Tests for ApplicationService."""
import pytest
from unittest.mock import MagicMock
from datetime import datetime


@pytest.fixture
def mock_db():
    """Fixture providing a mock database session."""
    db = MagicMock()
    db.query.return_value = db
    db.filter.return_value = db
    db.first.return_value = None
    db.all.return_value = []
    db.add.return_value = None
    db.commit.return_value = None
    db.refresh.return_value = None
    return db


@pytest.fixture
def application_service(mock_db):
    """Fixture providing an ApplicationService instance with mocked DB."""
    from recruitment_platform.services.application_service import ApplicationService
    return ApplicationService(db=mock_db)


@pytest.fixture
def sample_application():
    """Fixture providing sample application data."""
    return {
        "id": 1,
        "candidate_id": 1,
        "job_id": 1,
        "status": "pending",
        "cover_letter": "I am interested in this position.",
        "resume_url": "https://example.com/resume.pdf",
        "created_at": datetime(2024, 1, 1),
        "updated_at": datetime(2024, 1, 1),
    }


class TestApplicationService:
    """Test suite for ApplicationService."""

    def test_create_application(self, application_service, mock_db, sample_application):
        """Test creating a new application."""
        application_service.create = MagicMock(return_value=sample_application)
        result = application_service.create(sample_application)
        assert result["candidate_id"] == 1
        assert result["job_id"] == 1
        assert result["status"] == "pending"

    def test_get_application_by_id(self, application_service, mock_db, sample_application):
        """Test retrieving an application by ID."""
        mock_db.first.return_value = sample_application
        result = application_service.get_by_id(1)
        assert result is not None
        assert result["id"] == 1
        assert result["status"] == "pending"

    def test_get_application_not_found(self, application_service, mock_db):
        """Test retrieving a non-existent application returns None."""
        mock_db.first.return_value = None
        result = application_service.get_by_id(999)
        assert result is None

    def test_get_all_applications(self, application_service, mock_db, sample_application):
        """Test retrieving all applications."""
        mock_db.all.return_value = [sample_application]
        result = application_service.get_all()
        assert len(result) == 1
        assert result[0]["status"] == "pending"

    def test_update_application_status(self, application_service, mock_db, sample_application):
        """Test updating application status."""
        updated = {**sample_application, "status": "reviewed"}
        application_service.update = MagicMock(return_value=updated)
        result = application_service.update(1, {"status": "reviewed"})
        assert result["status"] == "reviewed"

    def test_delete_application(self, application_service, mock_db):
        """Test deleting an application."""
        application_service.delete = MagicMock(return_value=True)
        result = application_service.delete(1)
        assert result is True

    def test_get_applications_by_candidate(self, application_service, mock_db, sample_application):
        """Test retrieving all applications for a candidate."""
        mock_db.all.return_value = [sample_application]
        result = application_service.get_by_candidate(1)
        assert len(result) == 1
        assert result[0]["candidate_id"] == 1

    def test_get_applications_by_job(self, application_service, mock_db, sample_application):
        """Test retrieving all applications for a job."""
        mock_db.all.return_value = [sample_application]
        result = application_service.get_by_job(1)
        assert len(result) == 1
        assert result[0]["job_id"] == 1

    def test_filter_applications_by_status(self, application_service, mock_db, sample_application):
        """Test filtering applications by status."""
        mock_db.all.return_value = [sample_application]
        result = application_service.filter_by_status("pending")
        assert len(result) == 1
        assert result[0]["status"] == "pending"

    def test_advance_application_stage(self, application_service, mock_db, sample_application):
        """Test advancing application to next stage."""
        advanced = {**sample_application, "status": "interview"}
        application_service.update = MagicMock(return_value=advanced)
        result = application_service.advance_stage(1)
        assert result["status"] == "interview"

    def test_reject_application(self, application_service, mock_db, sample_application):
        """Test rejecting an application."""
        rejected = {**sample_application, "status": "rejected"}
        application_service.update = MagicMock(return_value=rejected)
        result = application_service.reject(1)
        assert result["status"] == "rejected"

    def test_accept_application(self, application_service, mock_db, sample_application):
        """Test accepting an application."""
        accepted = {**sample_application, "status": "accepted"}
        application_service.update = MagicMock(return_value=accepted)
        result = application_service.accept(1)
        assert result["status"] == "accepted"

    def test_duplicate_application_prevention(self, application_service, mock_db, sample_application):
        """Test that duplicate application raises error."""
        mock_db.first.return_value = sample_application
        with pytest.raises(Exception):
            application_service.create(sample_application)

    def test_application_status_transitions(self, application_service, mock_db, sample_application):
        """Test valid status transitions."""
        valid_transitions = [
            ("pending", "reviewed"),
            ("reviewed", "interview"),
            ("interview", "accepted"),
            ("interview", "rejected"),
        ]
        for from_status, to_status in valid_transitions:
            updated = {**sample_application, "status": to_status}
            application_service.update = MagicMock(return_value=updated)
            result = application_service.update(1, {"status": to_status})
            assert result["status"] == to_status
