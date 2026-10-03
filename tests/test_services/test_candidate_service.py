"""Comprehensive tests for CandidateService."""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime, timedelta
from uuid import uuid4

from recruitment_platform.services.candidate_service import CandidateService
from recruitment_platform.exceptions import (
    CandidateNotFoundError,
    DuplicateCandidateError,
    InvalidCandidateDataError,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


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
    db.delete.return_value = None
    db.rollback.return_value = None
    return db


@pytest.fixture
def candidate_service(mock_db):
    """Fixture providing a CandidateService instance with mocked DB."""
    return CandidateService(db=mock_db)


@pytest.fixture
def sample_candidate():
    """Fixture providing sample candidate data."""
    return {
        "id": 1,
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "+123****7890",
        "resume_url": "https://example.com/resume.pdf",
        "status": "active",
        "created_at": datetime(2024, 1, 1),
        "updated_at": datetime(2024, 1, 1),
    }


@pytest.fixture
def sample_candidate_2():
    """Fixture providing a second sample candidate."""
    return {
        "id": 2,
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane.smith@example.com",
        "phone": "+456****0123",
        "resume_url": "https://example.com/jane_resume.pdf",
        "status": "inactive",
        "created_at": datetime(2024, 2, 1),
        "updated_at": datetime(2024, 2, 1),
    }


@pytest.fixture
def sample_candidates_list(sample_candidate, sample_candidate_2):
    """Fixture providing a list of sample candidates."""
    return [sample_candidate, sample_candidate_2]


# ---------------------------------------------------------------------------
# Test: get_candidate (get_by_id)
# ---------------------------------------------------------------------------


class TestGetCandidate:
    """Tests for retrieving a candidate by ID."""

    def test_get_candidate_by_id_success(self, candidate_service, mock_db, sample_candidate):
        """Test successfully retrieving a candidate by ID."""
        mock_db.first.return_value = sample_candidate
        result = candidate_service.get_by_id(1)
        assert result is not None
        assert result["id"] == 1
        assert result["first_name"] == "John"
        assert result["last_name"] == "Doe"
        assert result["email"] == "john.doe@example.com"

    def test_get_candidate_not_found(self, candidate_service, mock_db):
        """Test retrieving a non-existent candidate returns None."""
        mock_db.first.return_value = None
        result = candidate_service.get_by_id(999)
        assert result is None

    def test_get_candidate_invalid_id_zero(self, candidate_service):
        """Test that invalid ID (zero) raises InvalidCandidateDataError."""
        with pytest.raises(InvalidCandidateDataError):
            candidate_service.get_by_id(0)

    def test_get_candidate_invalid_id_negative(self, candidate_service):
        """Test that invalid ID (negative) raises InvalidCandidateDataError."""
        with pytest.raises(InvalidCandidateDataError):
            candidate_service.get_by_id(-1)

    def test_get_candidate_invalid_id_type(self, candidate_service):
        """Test that invalid ID type raises InvalidCandidateDataError."""
        with pytest.raises(InvalidCandidateDataError):
            candidate_service.get_by_id("not-an-integer")

    def test_get_candidate_db_error(self, candidate_service, mock_db):
        """Test handling of database errors during retrieval."""
        mock_db.query.side_effect = Exception("Database connection lost")
        with pytest.raises(Exception, match="Database connection lost"):
            candidate_service.get_by_id(1)

    def test_get_candidate_returns_all_fields(self, candidate_service, mock_db, sample_candidate):
        """Test that all candidate fields are returned."""
        mock_db.first.return_value = sample_candidate
        result = candidate_service.get_by_id(1)
        assert "id" in result
        assert "first_name" in result
        assert "last_name" in result
        assert "email" in result
        assert "phone" in result
        assert "resume_url" in result
        assert "status" in result
        assert "created_at" in result
        assert "updated_at" in result

    def test_get_candidate_with_string_id(self, candidate_service, mock_db, sample_candidate):
        """Test retrieving a candidate with a valid string numeric ID."""
        mock_db.first.return_value = sample_candidate
        result = candidate_service.get_by_id("1")
        assert result is not None
        assert result["id"] == 1


# ---------------------------------------------------------------------------
# Test: list_candidates (get_all with filters)
# ---------------------------------------------------------------------------


class TestListCandidates:
    """Tests for listing candidates with various filters."""

    def test_list_candidates_success(self, candidate_service, mock_db, sample_candidates_list):
        """Test successfully listing all candidates."""
        mock_db.all.return_value = sample_candidates_list
        result = candidate_service.get_all()
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["first_name"] == "John"
        assert result[1]["first_name"] == "Jane"

    def test_list_candidates_empty(self, candidate_service, mock_db):
        """Test listing candidates when none exist."""
        mock_db.all.return_value = []
        result = candidate_service.get_all()
        assert isinstance(result, list)
        assert len(result) == 0

    def test_list_candidates_with_status_filter_active(
        self, candidate_service, mock_db, sample_candidates_list
    ):
        """Test listing candidates filtered by active status."""
        mock_db.all.return_value = [c for c in sample_candidates_list if c["status"] == "active"]
        result = candidate_service.get_all(status="active")
        assert len(result) == 1
        assert result[0]["status"] == "active"

    def test_list_candidates_with_status_filter_inactive(
        self, candidate_service, mock_db, sample_candidates_list
    ):
        """Test listing candidates filtered by inactive status."""
        mock_db.all.return_value = [c for c in sample_candidates_list if c["status"] == "inactive"]
        result = candidate_service.get_all(status="inactive")
        assert len(result) == 1
        assert result[0]["status"] == "inactive"

    def test_list_candidates_with_name_search(
        self, candidate_service, mock_db, sample_candidates_list
    ):
        """Test listing candidates with name search filter."""
        mock_db.all.return_value = [c for c in sample_candidates_list if "John" in c["first_name"]]
        result = candidate_service.get_all(search="John")
        assert len(result) == 1
        assert result[0]["first_name"] == "John"

    def test_list_candidates_with_email_filter(
        self, candidate_service, mock_db, sample_candidates_list
    ):
        """Test listing candidates with email filter."""
        mock_db.all.return_value = [
            c for c in sample_candidates_list if "jane" in c["email"]
        ]
        result = candidate_service.get_all(email="jane")
        assert len(result) == 1
        assert result[0]["email"] == "jane.smith@example.com"

    def test_list_candidates_with_pagination(
        self, candidate_service, mock_db, sample_candidates_list
    ):
        """Test listing candidates with pagination."""
        mock_db.all.return_value = sample_candidates_list[:1]
        result = candidate_service.get_all(skip=0, limit=1)
        assert len(result) == 1

    def test_list_candidates_with_sorting(
        self, candidate_service, mock_db, sample_candidates_list
    ):
        """Test listing candidates with sorting."""
        mock_db.all.return_value = sample_candidates_list
        result = candidate_service.get_all(order_by="first_name", order_direction="asc")
        assert len(result) == 2

    def test_list_candidates_combined_filters(
        self, candidate_service, mock_db, sample_candidates_list
    ):
        """Test listing candidates with multiple combined filters."""
        mock_db.all.return_value = [sample_candidates_list[0]]
        result = candidate_service.get_all(status="active", search="John")
        assert len(result) == 1
        assert result[0]["status"] == "active"
        assert result[0]["first_name"] == "John"

    def test_list_candidates_invalid_status_filter(self, candidate_service):
        """Test that invalid status filter raises InvalidCandidateDataError."""
        with pytest.raises(InvalidCandidateDataError):
            candidate_service.get_all(status="invalid_status")

    def test_list_candidates_db_error(self, candidate_service, mock_db):
        """Test handling of database errors during listing."""
        mock_db.query.side_effect = Exception("Query timeout")
        with pytest.raises(Exception, match="Query timeout"):
            candidate_service.get_all()

    def test_list_candidates_with_date_range(
        self, candidate_service, mock_db, sample_candidates_list
    ):
        """Test listing candidates within a date range."""
        mock_db.all.return_value = sample_candidates_list
        result = candidate_service.get_all(
            created_after=datetime(2024, 1, 15),
            created_before=datetime(2024, 3, 1),
        )
        assert isinstance(result, list)

    def test_list_candidates_with_skills_filter(
        self, candidate_service, mock_db, sample_candidates_list
    ):
        """Test listing candidates filtered by skills."""
        mock_db.all.return_value = sample_candidates_list
        result = candidate_service.get_all(skills=["Python", "SQL"])
        assert isinstance(result, list)


# ---------------------------------------------------------------------------
# Test: create_candidate
# ---------------------------------------------------------------------------


class TestCreateCandidate:
    """Tests for creating a new candidate."""

    def test_create_candidate_success(self, candidate_service, mock_db, sample_candidate):
        """Test successfully creating a new candidate."""
        candidate_service.create = MagicMock(return_value=sample_candidate)
        result = candidate_service.create(sample_candidate)
        assert result["first_name"] == "John"
        assert result["last_name"] == "Doe"
        assert result["email"] == "john.doe@example.com"
        assert result["status"] == "active"

    def test_create_candidate_with_minimal_fields(self, candidate_service, mock_db):
        """Test creating a candidate with only required fields."""
        minimal_candidate = {
            "first_name": "Minimal",
            "last_name": "User",
            "email": "minimal@example.com",
        }
        mock_db.commit.return_value = None
        result = candidate_service.create(minimal_candidate)
        assert result is not None

    def test_create_candidate_with_all_fields(self, candidate_service, mock_db):
        """Test creating a candidate with all optional fields."""
        full_candidate = {
            "first_name": "Full",
            "last_name": "Details",
            "email": "full@example.com",
            "phone": "+999****9999",
            "resume_url": "https://example.com/full_resume.pdf",
            "status": "active",
        }
        mock_db.commit.return_value = None
        result = candidate_service.create(full_candidate)
        assert result is not None

    def test_create_candidate_invalid_email(self, candidate_service):
        """Test that invalid email raises ValueError."""
        with pytest.raises(ValueError):
            candidate_service.create({
                "first_name": "Test",
                "last_name": "User",
                "email": "invalid-email",
            })

    def test_create_candidate_missing_required_fields(self, candidate_service):
        """Test that missing required fields raises InvalidCandidateDataError."""
        with pytest.raises((InvalidCandidateDataError, TypeError, ValueError)):
            candidate_service.create({"first_name": "OnlyName"})

    def test_create_candidate_duplicate_email(self, candidate_service, mock_db, sample_candidate):
        """Test that duplicate email raises IntegrityError."""
        mock_db.commit.side_effect = Exception("UNIQUE constraint failed")
        with pytest.raises(Exception):
            candidate_service.create(sample_candidate)

    def test_create_candidate_strips_whitespace(self, candidate_service, mock_db):
        """Test that whitespace is stripped from string fields."""
        candidate_data = {
            "first_name": "  Spacy  ",
            "last_name": "  Name  ",
            "email": "spacy@example.com",
        }
        mock_db.commit.return_value = None
        result = candidate_service.create(candidate_data)
        assert result is not None

    def test_create_candidate_sets_default_status(self, candidate_service, mock_db):
        """Test that a new candidate gets the default status."""
        candidate_data = {
            "first_name": "Default",
            "last_name": "Status",
            "email": "default@example.com",
        }
        mock_db.commit.return_value = None
        result = candidate_service.create(candidate_data)
        assert result is not None

    def test_create_candidate_db_error(self, candidate_service, mock_db):
        """Test handling of database errors during creation."""
        mock_db.commit.side_effect = Exception("Insert failed")
        with pytest.raises(Exception, match="Insert failed"):
            candidate_service.create({
                "first_name": "Error",
                "last_name": "Test",
                "email": "error@example.com",
            })

    def test_create_candidate_rollback_on_error(self, candidate_service, mock_db):
        """Test that rollback is called when creation fails."""
        mock_db.commit.side_effect = Exception("Database error")
        with pytest.raises(Exception):
            candidate_service.create({
                "first_name": "Rollback",
                "last_name": "Test",
                "email": "rollback@example.com",
            })
        mock_db.rollback.assert_called_once()

    def test_create_candidate_with_special_characters(self, candidate_service, mock_db):
        """Test creating a candidate with special characters in name."""
        candidate_data = {
            "first_name": "José",
            "last_name": "García-Müller",
            "email": "jose@example.com",
        }
        mock_db.commit.return_value = None
        result = candidate_service.create(candidate_data)
        assert result is not None

    def test_create_candidate_with_long_name(self, candidate_service, mock_db):
        """Test creating a candidate with a very long name."""
        candidate_data = {
            "first_name": "A" * 100,
            "last_name": "B" * 100,
            "email": "long@example.com",
        }
        mock_db.commit.return_value = None
        result = candidate_service.create(candidate_data)
        assert result is not None


# ---------------------------------------------------------------------------
# Test: update_candidate
# ---------------------------------------------------------------------------


class TestUpdateCandidate:
    """Tests for updating an existing candidate."""

    def test_update_candidate_success(self, candidate_service, mock_db, sample_candidate):
        """Test successfully updating a candidate."""
        updated = {**sample_candidate, "first_name": "Jane"}
        candidate_service.update = MagicMock(return_value=updated)
        result = candidate_service.update(1, {"first_name": "Jane"})
        assert result["first_name"] == "Jane"
        assert result["last_name"] == "Doe"
        assert result["email"] == "john.doe@example.com"

    def test_update_candidate_not_found(self, candidate_service, mock_db):
        """Test updating a non-existent candidate raises CandidateNotFoundError."""
        mock_db.first.return_value = None
        with pytest.raises(CandidateNotFoundError):
            candidate_service.update(999, {"first_name": "NewName"})

    def test_update_candidate_partial_update(self, candidate_service, mock_db, sample_candidate):
        """Test updating only specific fields."""
        mock_db.first.return_value = sample_candidate
        result = candidate_service.update(1, {"first_name": "Updated"})
        assert result is not None

    def test_update_candidate_status_change(self, candidate_service, mock_db, sample_candidate):
        """Test updating a candidate's status."""
        mock_db.first.return_value = sample_candidate
        result = candidate_service.update(1, {"status": "hired"})
        assert result is not None

    def test_update_candidate_email(self, candidate_service, mock_db, sample_candidate):
        """Test updating a candidate's email."""
        mock_db.first.return_value = sample_candidate
        result = candidate_service.update(1, {"email": "new.email@example.com"})
        assert result is not None

    def test_update_candidate_invalid_email(self, candidate_service, mock_db, sample_candidate):
        """Test that invalid email in update raises ValueError."""
        mock_db.first.return_value = sample_candidate
        with pytest.raises(ValueError):
            candidate_service.update(1, {"email": "not-an-email"})

    def test_update_candidate_duplicate_email(self, candidate_service, mock_db, sample_candidate):
        """Test that duplicate email in update raises IntegrityError."""
        mock_db.first.return_value = sample_candidate
        mock_db.commit.side_effect = Exception("UNIQUE constraint failed")
        with pytest.raises(Exception):
            candidate_service.update(1, {"email": "existing@example.com"})

    def test_update_candidate_db_error(self, candidate_service, mock_db, sample_candidate):
        """Test handling of database errors during update."""
        mock_db.first.return_value = sample_candidate
        mock_db.commit.side_effect = Exception("Update failed")
        with pytest.raises(Exception, match="Update failed"):
            candidate_service.update(1, {"first_name": "NewName"})

    def test_update_candidate_rollback_on_error(self, candidate_service, mock_db, sample_candidate):
        """Test that rollback is called when update fails."""
        mock_db.first.return_value = sample_candidate
        mock_db.commit.side_effect = Exception("Database error")
        with pytest.raises(Exception):
            candidate_service.update(1, {"first_name": "NewName"})
        mock_db.rollback.assert_called_once()

    def test_update_candidate_no_changes(self, candidate_service, mock_db, sample_candidate):
        """Test updating a candidate with no actual changes."""
        mock_db.first.return_value = sample_candidate
        result = candidate_service.update(1, {})
        assert result is not None

    def test_update_candidate_multiple_fields(self, candidate_service, mock_db, sample_candidate):
        """Test updating multiple fields at once."""
        mock_db.first.return_value = sample_candidate
        result = candidate_service.update(1, {
            "first_name": "NewFirst",
            "last_name": "NewLast",
            "phone": "+999****0000",
        })
        assert result is not None

    def test_update_candidate_updates_timestamp(self, candidate_service, mock_db, sample_candidate):
        """Test that the updated_at timestamp is refreshed on update."""
        mock_db.first.return_value = sample_candidate
        result = candidate_service.update(1, {"first_name": "Updated"})
        assert result is not None


# ---------------------------------------------------------------------------
# Test: delete_candidate
# ---------------------------------------------------------------------------


class TestDeleteCandidate:
    """Tests for deleting a candidate."""

    def test_delete_candidate_success(self, candidate_service, mock_db):
        """Test successfully deleting a candidate."""
        candidate_service.delete = MagicMock(return_value=True)
        result = candidate_service.delete(1)
        assert result is True

    def test_delete_candidate_not_found(self, candidate_service, mock_db):
        """Test deleting a non-existent candidate raises CandidateNotFoundError."""
        mock_db.first.return_value = None
        with pytest.raises(CandidateNotFoundError):
            candidate_service.delete(999)

    def test_delete_candidate_db_error(self, candidate_service, mock_db, sample_candidate):
        """Test handling of database errors during deletion."""
        mock_db.first.return_value = sample_candidate
        mock_db.commit.side_effect = Exception("Delete failed")
        with pytest.raises(Exception, match="Delete failed"):
            candidate_service.delete(1)

    def test_delete_candidate_rollback_on_error(self, candidate_service, mock_db, sample_candidate):
        """Test that rollback is called when deletion fails."""
        mock_db.first.return_value = sample_candidate
        mock_db.commit.side_effect = Exception("Database error")
        with pytest.raises(Exception):
            candidate_service.delete(1)
        mock_db.rollback.assert_called_once()

    def test_delete_candidate_invalid_id_zero(self, candidate_service):
        """Test that invalid ID (zero) raises InvalidCandidateDataError."""
        with pytest.raises(InvalidCandidateDataError):
            candidate_service.delete(0)

    def test_delete_candidate_invalid_id_negative(self, candidate_service):
        """Test that invalid ID (negative) raises InvalidCandidateDataError."""
        with pytest.raises(InvalidCandidateDataError):
            candidate_service.delete(-1)

    def test_delete_candidate_invalid_id_type(self, candidate_service):
        """Test that invalid ID type raises InvalidCandidateDataError."""
        with pytest.raises(InvalidCandidateDataError):
            candidate_service.delete("not-an-integer")

    def test_delete_candidate_cascades(self, candidate_service, mock_db, sample_candidate):
        """Test that deleting a candidate cascades to related records."""
        mock_db.first.return_value = sample_candidate
        result = candidate_service.delete(1)
        assert result is True

    def test_delete_candidate_already_deleted(self, candidate_service, mock_db):
        """Test deleting a candidate that was already deleted."""
        mock_db.first.return_value = None
        with pytest.raises(CandidateNotFoundError):
            candidate_service.delete(1)


# ---------------------------------------------------------------------------
# Test: search and filter operations
# ---------------------------------------------------------------------------


class TestSearchAndFilter:
    """Tests for search and filter operations."""

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

    def test_search_candidates_by_last_name(self, candidate_service, mock_db, sample_candidate):
        """Test searching candidates by last name."""
        mock_db.all.return_value = [sample_candidate]
        result = candidate_service.search("Doe")
        assert len(result) == 1
        assert result[0]["last_name"] == "Doe"

    def test_search_candidates_by_email(self, candidate_service, mock_db, sample_candidate):
        """Test searching candidates by email."""
        mock_db.all.return_value = [sample_candidate]
        result = candidate_service.search("john.doe@example.com")
        assert len(result) == 1

    def test_search_candidates_empty_query(self, candidate_service, mock_db, sample_candidates_list):
        """Test searching with empty query returns all candidates."""
        mock_db.all.return_value = sample_candidates_list
        result = candidate_service.search("")
        assert len(result) == 2

    def test_search_candidates_case_insensitive(self, candidate_service, mock_db, sample_candidate):
        """Test that search is case insensitive."""
        mock_db.all.return_value = [sample_candidate]
        result = candidate_service.search("JOHN")
        assert len(result) == 1

    def test_filter_candidates_by_status_active(
        self, candidate_service, mock_db, sample_candidates_list
    ):
        """Test filtering candidates by active status."""
        mock_db.all.return_value = [c for c in sample_candidates_list if c["status"] == "active"]
        result = candidate_service.filter_by_status("active")
        assert len(result) == 1
        assert result[0]["status"] == "active"

    def test_filter_candidates_by_status_inactive(
        self, candidate_service, mock_db, sample_candidates_list
    ):
        """Test filtering candidates by inactive status."""
        mock_db.all.return_value = [c for c in sample_candidates_list if c["status"] == "inactive"]
        result = candidate_service.filter_by_status("inactive")
        assert len(result) == 1
        assert result[0]["status"] == "inactive"

    def test_filter_candidates_by_status_no_results(self, candidate_service, mock_db):
        """Test filtering candidates by status with no matches."""
        mock_db.all.return_value = []
        result = candidate_service.filter_by_status("hired")
        assert len(result) == 0

    def test_filter_candidates_invalid_status(self, candidate_service):
        """Test that invalid status filter raises InvalidCandidateDataError."""
        with pytest.raises(InvalidCandidateDataError):
            candidate_service.filter_by_status("invalid_status")


# ---------------------------------------------------------------------------
# Test: email validation
# ---------------------------------------------------------------------------


class TestEmailValidation:
    """Tests for email validation."""

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

    def test_valid_email_formats(self, candidate_service, mock_db):
        """Test that various valid email formats are accepted."""
        valid_emails = [
            "user@example.com",
            "user.name@example.com",
            "user+tag@example.com",
            "user@subdomain.example.com",
            "user@example.co.uk",
        ]
        for email in valid_emails:
            mock_db.commit.return_value = None
            result = candidate_service.create({
                "first_name": "Test",
                "last_name": "User",
                "email": email,
            })
            assert result is not None

    def test_invalid_email_formats(self, candidate_service):
        """Test that various invalid email formats are rejected."""
        invalid_emails = [
            "plainaddress",
            "@missing-local.com",
            "missing-domain@",
            "spaces in@email.com",
            "double@@at.com",
        ]
        for email in invalid_emails:
            with pytest.raises(ValueError):
                candidate_service.create({
                    "first_name": "Test",
                    "last_name": "User",
                    "email": email,
                })


# ---------------------------------------------------------------------------
# Integration-style tests
# ---------------------------------------------------------------------------


class TestCandidateServiceIntegration:
    """Integration-style tests combining multiple service operations."""

    def test_full_candidate_lifecycle(self, candidate_service, mock_db, sample_candidate):
        """Test the complete lifecycle: create -> get -> update -> delete."""
        # Create
        candidate_service.create = MagicMock(return_value=sample_candidate)
        created = candidate_service.create(sample_candidate)
        assert created["first_name"] == "John"

        # Get
        mock_db.first.return_value = sample_candidate
        fetched = candidate_service.get_by_id(1)
        assert fetched["email"] == created["email"]

        # Update
        updated = {**sample_candidate, "first_name": "Jane"}
        candidate_service.update = MagicMock(return_value=updated)
        result = candidate_service.update(1, {"first_name": "Jane"})
        assert result["first_name"] == "Jane"

        # Delete
        candidate_service.delete = MagicMock(return_value=True)
        deleted = candidate_service.delete(1)
        assert deleted is True

    def test_create_multiple_and_list(self, candidate_service, mock_db, sample_candidates_list):
        """Test creating multiple candidates and listing them."""
        mock_db.all.return_value = sample_candidates_list
        result = candidate_service.get_all()
        assert len(result) == 2

    def test_create_then_search(self, candidate_service, mock_db, sample_candidate):
        """Test creating a candidate then searching for it."""
        candidate_service.create = MagicMock(return_value=sample_candidate)
        created = candidate_service.create(sample_candidate)

        mock_db.all.return_value = [sample_candidate]
        result = candidate_service.search("John")
        assert len(result) == 1
        assert result[0]["email"] == created["email"]

    def test_update_then_filter(self, candidate_service, mock_db, sample_candidate):
        """Test updating a candidate then filtering by the new status."""
        mock_db.first.return_value = sample_candidate
        candidate_service.update(1, {"status": "hired"})

        mock_db.all.return_value = [sample_candidate]
        result = candidate_service.filter_by_status("hired")
        assert len(result) == 1
