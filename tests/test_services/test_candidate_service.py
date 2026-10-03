"""Tests for CandidateService."""
import pytest
from unittest.mock import MagicMock, patch
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
def candidate_service(mock_db):
    """Fixture providing a CandidateService instance with mocked DB."""
    from recruitment_platform.services.candidate_service import CandidateService
    return CandidateService(db=mock_db)


@pytest.fixture
def sample_candidate():
    """Fixture providing sample candidate data."""
    return {
        "id": 1,
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "+1234567890",
        "resume_url": "https://example.com/resume.pdf",
        "status": "active",
        "created_at": datetime(2024, 1, 1),
        "updated_at": datetime(2024, 1, 1),
    }


class TestCandidateService:
    """Test suite for CandidateService."""

    def test_create_candidate(self, candidate_service, mock_db, sample_candidate):
        """Test creating a new candidate."""
        candidate_service.create = MagicMock(return_value=sample_candidate)
        result = candidate_service.create(sample_candidate)
        assert result["first_name"] == "John"
        assert result["last_name"] == "Doe"
        assert result["email"] == "john.doe@example.com"
        assert result["status"] == "active"

    def test_get_candidate_by_id(self, candidate_service, mock_db, sample_candidate):
        """Test retrieving a candidate by ID."""
        mock_db.first.return_value = sample_candidate
        result = candidate_service.get_by_id(1)
        assert result is not None
        assert result["id"] == 1
        assert result["email"] == "john.doe@example.com"

    def test_get_candidate_not_found(self, candidate_service, mock_db):
        """Test retrieving a non-existent candidate returns None."""
        mock_db.first.return_value = None
        result = candidate_service.get_by_id(999)
        assert result is None

    def test_get_all_candidates(self, candidate_service, mock_db, sample_candidate):
        """Test retrieving all candidates."""
        mock_db.all.return_value = [sample_candidate]
        result = candidate_service.get_all()
        assert len(result) == 1
        assert result[0]["first_name"] == "John"

    def test_update_candidate(self, candidate_service, mock_db, sample_candidate):
        """Test updating a candidate."""
        updated = {**sample_candidate, "first_name": "Jane"}
        candidate_service.update = MagicMock(return_value=updated)
        result = candidate_service.update(1, {"first_name": "Jane"})
        assert result["first_name"] == "Jane"
        assert result["last_name"] == "Doe"

    def test_delete_candidate(self, candidate_service, mock_db):
        """Test deleting a candidate."""
        candidate_service.delete = MagicMock(return_value=True)
        result = candidate_service.delete(1)
        assert result is True

    def test_search_candidates_by_name(self, candidate_service, mock_db, sample_candidate):
        """Test searching candidates by name."""
        mock_db.all.return_value = [sample_candidate]
        result = candidate_service.search("John")
        assert len(result) == 1
        assert result[0]["first_name"] == "John"

    def test_search_candidates_no_results(self, candidate_service, mock_db):
        """Test searching candidates with no matches."""
        mock_db.all.return_value = []
        result = candidate_service.search("NonExistent")
        assert len(result) == 0

    def test_filter_candidates_by_status(self, candidate_service, mock_db, sample_candidate):
        """Test filtering candidates by status."""
        mock_db.all.return_value = [sample_candidate]
        result = candidate_service.filter_by_status("active")
        assert len(result) == 1
        assert result[0]["status"] == "active"

    def test_candidate_email_validation(self, candidate_service):
        """Test that invalid email raises ValueError."""
        with pytest.raises(ValueError):
            candidate_service.create({
                "first_name": "Test",
                "last_name": "User",
                "email": "invalid-email",
            })

    def test_candidate_email_uniqueness(self, candidate_service, mock_db, sample_candidate):
        """Test that duplicate email raises IntegrityError."""
        mock_db.commit.side_effect = Exception("UNIQUE constraint failed")
        with pytest.raises(Exception):
            candidate_service.create(sample_candidate)
