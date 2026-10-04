"""Comprehensive tests for the application service module."""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from recruitment_platform.services.application_service import (
ApplicationService,
get_application,
list_applications,
create_application,
update_application_status,
delete_application,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_db():
    """Provide a mock database session."""
db = MagicMock()
db.commit = MagicMock()
db.rollback = MagicMock()
db.refresh = MagicMock()
db.query = MagicMock()
db.add = MagicMock()
db.delete = MagicMock()
return db


@pytest.fixture
def sample_application():
    """Return a sample application object."""
app = MagicMock()
app.id = 1
app.candidate_id = 101
app.job_id = 201
app.status = "pending"
app.cover_letter = "I am a great fit for this role."
app.resume_url = "https://example.com/resume.pdf"
app.created_at = datetime(2024, 1, 15, 10, 0, 0)
app.updated_at = datetime(2024, 1, 15, 10, 0, 0)
return app


@pytest.fixture
def sample_application_list():
    """Return a list of sample application objects."""
apps = []
for i in range(1, 4):
        app = MagicMock()
app.id = i
app.candidate_id = 100 + i
app.job_id = 200 + i
app.status = "pending" if i % 2 == 1 else "reviewed"
app.cover_letter = f"Cover letter {i}"
app.resume_url = f"https://example.com/resume{i}.pdf"
app.created_at = datetime(2024, 1, 15, 10, 0, 0) + timedelta(days=i)
app.updated_at = datetime(2024, 1, 15, 10, 0, 0) + timedelta(days=i)
apps.append(app)
return apps


@pytest.fixture
def service(mock_db):
    """Provide an ApplicationService instance with a mock db."""
return ApplicationService(db=mock_db)


# ---------------------------------------------------------------------------
# Tests for get_application
# ---------------------------------------------------------------------------


class TestGetApplication:
    """Tests for the get_application function."""

    def test_get_application_returns_application(self, mock_db, sample_application):
        """get_application should return the application when found."""
mock_query = MagicMock()
mock_query.filter.return_value.first.return_value = sample_application
mock_db.query.return_value = mock_query

        result = get_application(db=mock_db, application_id=1)

        assert result is not None
assert result.id == 1
assert result.candidate_id == 101
assert result.job_id == 201
assert result.status == "pending"

    def test_get_application_returns_none_when_not_found(self, mock_db):
        """get_application should return None when application does not exist."""
mock_query = MagicMock()
mock_query.filter.return_value.first.return_value = None
mock_db.query.return_value = mock_query

        result = get_application(db=mock_db, application_id=999)

        assert result is None

    def test_get_application_queries_correct_model(self, mock_db):
        """get_application should query the Application model."""
mock_query = MagicMock()
mock_query.filter.return_value.first.return_value = None
mock_db.query.return_value = mock_query

        get_application(db=mock_db, application_id=42)

        mock_db.query.assert_called_once()
args, _ = mock_db.query.call_args
assert args[0].__name__ == "Application"

    def test_get_application_with_service_instance(self, mock_db, sample_application):
        """get_application should work when called via service instance."""
mock_query = MagicMock()
mock_query.filter.return_value.first.return_value = sample_application
mock_db.query.return_value = mock_query

        service = ApplicationService(db=mock_db)
result = service.get_application(application_id=1)

        assert result is not None
assert result.id == 1

    def test_get_application_with_invalid_id(self, mock_db):
        """get_application should handle invalid IDs gracefully."""
mock_query = MagicMock()
mock_query.filter.return_value.first.return_value = None
mock_db.query.return_value = mock_query

        result = get_application(db=mock_db, application_id=-1)
assert result is None

        result = get_application(db=mock_db, application_id=0)
assert result is None


# ---------------------------------------------------------------------------
# Tests for list_applications
# ---------------------------------------------------------------------------


class TestListApplications:
    """Tests for the list_applications function."""

    def test_list_applications_returns_all(self, mock_db, sample_application_list):
        """list_applications should return all applications when no filters."""
mock_query = MagicMock()
mock_query.all.return_value = sample_application_list
mock_db.query.return_value = mock_query

        result = list_applications(db=mock_db)

        assert len(result) == 3
assert result[0].id == 1
assert result[2].id == 3

    def test_list_applications_empty_result(self, mock_db):
        """list_applications should return empty list when no applications exist."""
mock_query = MagicMock()
mock_query.all.return_value = []
mock_db.query.return_value = mock_query

        result = list_applications(db=mock_db)

        assert result == []

    def test_list_applications_filter_by_candidate_id(self, mock_db, sample_application_list):
        """list_applications should filter by candidate_id."""
filtered = [a for a in sample_application_list if a.candidate_id == 101]
mock_query = MagicMock()
mock_query.filter.return_value.all.return_value = filtered
mock_db.query.return_value = mock_query

        result = list_applications(db=mock_db, candidate_id=101)

        assert len(result) == 1
assert result[0].candidate_id == 101

    def test_list_applications_filter_by_job_id(self, mock_db, sample_application_list):
        """list_applications should filter by job_id."""
filtered = [a for a in sample_application_list if a.job_id == 202]
mock_query = MagicMock()
mock_query.filter.return_value.all.return_value = filtered
mock_db.query.return_value = mock_query

        result = list_applications(db=mock_db, job_id=202)

        assert len(result) == 1
assert result[0].job_id == 202

    def test_list_applications_filter_by_status(self, mock_db, sample_application_list):
        """list_applications should filter by status."""
filtered = [a for a in sample_application_list if a.status == "pending"]
mock_query = MagicMock()
mock_query.filter.return_value.all.return_value = filtered
mock_db.query.return_value = mock_query

        result = list_applications(db=mock_db, status="pending")

        assert len(result) == 2
assert all(a.status == "pending" for a in result)

    def test_list_applications_with_pagination(self, mock_db, sample_application_list):
        """list_applications should support skip and limit for pagination."""
mock_query = MagicMock()
mock_query.offset.return_value.limit.return_value.all.return_value = sample_application_list[1:]
mock_db.query.return_value = mock_query

        result = list_applications(db=mock_db, skip=1, limit=2)

        assert len(result) == 2
mock_query.offset.assert_called_once_with(1)
mock_query.offset.return_value.limit.assert_called_once_with(2)

    def test_list_applications_with_multiple_filters(self, mock_db, sample_application_list):
        """list_applications should combine multiple filters."""
filtered = [
a for a in sample_application_list
if a.candidate_id == 101 and a.status == "pending"
]
mock_query = MagicMock()
mock_query.filter.return_value.filter.return_value.all.return_value = filtered
mock_db.query.return_value = mock_query

        result = list_applications(db=mock_db, candidate_id=101, status="pending")

        assert len(result) == 1
assert result[0].candidate_id == 101
assert result[0].status == "pending"

    def test_list_applications_with_service_instance(self, mock_db, sample_application_list):
        """list_applications should work when called via service instance."""
mock_query = MagicMock()
mock_query.all.return_value = sample_application_list
mock_db.query.return_value = mock_query

        service = ApplicationService(db=mock_db)
result = service.list_applications()

        assert len(result) == 3


# ---------------------------------------------------------------------------
# Tests for create_application
# ---------------------------------------------------------------------------


class TestCreateApplication:
    """Tests for the create_application function."""

    def test_create_application_success(self, mock_db):
        """create_application should create and return a new application."""
mock_db.refresh.side_effect = lambda obj: setattr(obj, "id", 1)

        result = create_application(
db=mock_db,
candidate_id=101,
job_id=201,
cover_letter="I am excited to apply.",
resume_url="https://example.com/resume.pdf",
)

        assert result is not None
assert result.id == 1
assert result.candidate_id == 101
assert result.job_id == 201
assert result.cover_letter == "I am excited to apply."
assert result.resume_url == "https://example.com/resume.pdf"
assert result.status == "pending"
mock_db.add.assert_called_once()
mock_db.commit.assert_called_once()
mock_db.refresh.assert_called_once()

    def test_create_application_with_minimal_fields(self, mock_db):
        """create_application should work with only required fields."""
mock_db.refresh.side_effect = lambda obj: setattr(obj, "id", 2)

        result = create_application(
db=mock_db,
candidate_id=101,
job_id=201,
)

        assert result is not None
assert result.id == 2
assert result.candidate_id == 101
assert result.job_id == 201
mock_db.add.assert_called_once()
mock_db.commit.assert_called_once()

    def test_create_application_sets_default_status(self, mock_db):
        """create_application should set status to 'pending' by default."""
mock_db.refresh.side_effect = lambda obj: setattr(obj, "id", 3)

        result = create_application(
db=mock_db,
candidate_id=101,
job_id=201,
)

        assert result.status == "pending"

    def test_create_application_with_service_instance(self, mock_db):
        """create_application should work when called via service instance."""
mock_db.refresh.side_effect = lambda obj: setattr(obj, "id", 4)

        service = ApplicationService(db=mock_db)
result = service.create_application(
candidate_id=101,
job_id=201,
cover_letter="Test cover letter",
)

        assert result is not None
assert result.id == 4
mock_db.add.assert_called_once()
mock_db.commit.assert_called_once()

    def test_create_application_commits_to_db(self, mock_db):
        """create_application should persist the application to the database."""
mock_db.refresh.side_effect = lambda obj: setattr(obj, "id", 5)

        create_application(
db=mock_db,
candidate_id=101,
job_id=201,
)

        mock_db.add.assert_called_once()
mock_db.commit.assert_called_once()
mock_db.refresh.assert_called_once()

    def test_create_application_with_long_cover_letter(self, mock_db):
        """create_application should handle long cover letters."""
mock_db.refresh.side_effect = lambda obj: setattr(obj, "id", 6)
long_letter = "A" * 5000

        result = create_application(
db=mock_db,
candidate_id=101,
job_id=201,
cover_letter=long_letter,
)

        assert result.cover_letter == long_letter
assert len(result.cover_letter) == 5000


# ---------------------------------------------------------------------------
# Tests for update_application_status
# ---------------------------------------------------------------------------


class TestUpdateApplicationStatus:
    """Tests for the update_application_status function."""

    def test_update_application_status_success(self, mock_db, sample_application):
        """update_application_status should update and return the application."""
mock_query = MagicMock()
mock_query.filter.return_value.first.return_value = sample_application
mock_db.query.return_value = mock_query

        result = update_application_status(
db=mock_db,
application_id=1,
new_status="reviewed",
)

        assert result is not None
assert result.status == "reviewed"
mock_db.commit.assert_called_once()
mock_db.refresh.assert_called_once()

    def test_update_application_status_not_found(self, mock_db):
        """update_application_status should return None when application not found."""
mock_query = MagicMock()
mock_query.filter.return_value.first.return_value = None
mock_db.query.return_value = mock_query

        result = update_application_status(
db=mock_db,
application_id=999,
new_status="reviewed",
)

        assert result is None
mock_db.commit.assert_not_called()

    def test_update_application_status_to_accepted(self, mock_db, sample_application):
        """update_application_status should allow updating to 'accepted'."""
mock_query = MagicMock()
mock_query.filter.return_value.first.return_value = sample_application
mock_db.query.return_value = mock_query

        result = update_application_status(
db=mock_db,
application_id=1,
new_status="accepted",
)

        assert result.status == "accepted"

    def test_update_application_status_to_rejected(self, mock_db, sample_application):
        """update_application_status should allow updating to 'rejected'."""
mock_query = MagicMock()
mock_query.filter.return_value.first.return_value = sample_application
mock_db.query.return_value = mock_query

        result = update_application_status(
db=mock_db,
application_id=1,
new_status="rejected",
)

        assert result.status == "rejected"

    def test_update_application_status_to_interview(self, mock_db, sample_application):
        """update_application_status should allow updating to 'interview'."""
mock_query = MagicMock()
mock_query.filter.return_value.first.return_value = sample_application
mock_db.query.return_value = mock_query

        result = update_application_status(
db=mock_db,
application_id=1,
new_status="interview",
)

        assert result.status == "interview"

    def test_update_application_status_with_service_instance(self, mock_db, sample_application):
        """update_application_status should work when called via service instance."""
mock_query = MagicMock()
mock_query.filter.return_value.first.return_value = sample_application
mock_db.query.return_value = mock_query

        service = ApplicationService(db=mock_db)
result = service.update_application_status(
application_id=1,
new_status="reviewed",
)

        assert result is not None
assert result.status == "reviewed"

    def test_update_application_status_invalid_status(self, mock_db, sample_application):
        """update_application_status should handle invalid status values."""
mock_query = MagicMock()
mock_query.filter.return_value.first.return_value = sample_application
mock_db.query.return_value = mock_query

        result = update_application_status(
db=mock_db,
application_id=1,
new_status="invalid_status",
)

        assert result.status == "invalid_status"

    def test_update_application_status_same_status(self, mock_db, sample_application):
        """update_application_status should handle updating to the same status."""
mock_query = MagicMock()
mock_query.filter.return_value.first.return_value = sample_application
mock_db.query.return_value = mock_query

        result = update_application_status(
db=mock_db,
application_id=1,
new_status="pending",
)

        assert result.status == "pending"
mock_db.commit.assert_called_once()


# ---------------------------------------------------------------------------
# Tests for delete_application
# ---------------------------------------------------------------------------


class TestDeleteApplication:
    """Tests for the delete_application function."""

    def test_delete_application_success(self, mock_db, sample_application):
        """delete_application should delete and return True on success."""
mock_query = MagicMock()
mock_query.filter.return_value.first.return_value = sample_application
mock_db.query.return_value = mock_query

        result = delete_application(db=mock_db, application_id=1)

        assert result is True
mock_db.delete.assert_called_once_with(sample_application)
mock_db.commit.assert_called_once()

    def test_delete_application_not_found(self, mock_db):
        """delete_application should return False when application not found."""
mock_query = MagicMock()
mock_query.filter.return_value.first.return_value = None
mock_db.query.return_value = mock_query

        result = delete_application(db=mock_db, application_id=999)

        assert result is False
mock_db.delete.assert_not_called()
mock_db.commit.assert_not_called()

    def test_delete_application_with_service_instance(self, mock_db, sample_application):
        """delete_application should work when called via service instance."""
mock_query = MagicMock()
mock_query.filter.return_value.first.return_value = sample_application
mock_db.query.return_value = mock_query

        service = ApplicationService(db=mock_db)
result = service.delete_application(application_id=1)

        assert result is True
mock_db.delete.assert_called_once()
mock_db.commit.assert_called_once()

    def test_delete_application_commits_to_db(self, mock_db, sample_application):
        """delete_application should commit the deletion to the database."""
mock_query = MagicMock()
mock_query.filter.return_value.first.return_value = sample_application
mock_db.query.return_value = mock_query

        delete_application(db=mock_db, application_id=1)

        mock_db.delete.assert_called_once_with(sample_application)
mock_db.commit.assert_called_once()

    def test_delete_application_with_invalid_id(self, mock_db):
        """delete_application should handle invalid IDs gracefully."""
mock_query = MagicMock()
mock_query.filter.return_value.first.return_value = None
mock_db.query.return_value = mock_query

        result = delete_application(db=mock_db, application_id=-1)

        assert result is False
mock_db.delete.assert_not_called()

    def test_delete_application_cascades_correctly(self, mock_db, sample_application):
        """delete_application should properly remove the application object."""
mock_query = MagicMock()
mock_query.filter.return_value.first.return_value = sample_application
mock_db.query.return_value = mock_query

        delete_application(db=mock_db, application_id=1)

        args, _ = mock_db.delete.call_args
assert args[0] is sample_application


# ---------------------------------------------------------------------------
# Integration-style tests
# ---------------------------------------------------------------------------


class TestApplicationServiceIntegration:
    """Integration-style tests combining multiple service operations."""

    def test_full_application_lifecycle(self, mock_db, sample_application):
        """Test the complete lifecycle: create -> get -> update -> delete."""
mock_db.refresh.side_effect = lambda obj: setattr(obj, "id", 1)
created = create_application(
db=mock_db,
candidate_id=101,
job_id=201,
cover_letter="Test",
)
        assert created.id == 1
assert created.status == "pending"

        mock_query = MagicMock()
mock_query.filter.return_value.first.return_value = created
mock_db.query.return_value = mock_query

        fetched = get_application(db=mock_db, application_id=1)
assert fetched is not None
assert fetched.id == 1

        updated = update_application_status(
db=mock_db,
application_id=1,
new_status="reviewed",
)
        assert updated.status == "reviewed"

        deleted = delete_application(db=mock_db, application_id=1)
assert deleted is True

    def test_list_after_create(self, mock_db, sample_application):
        """Test that created applications appear in list results."""
mock_db.refresh.side_effect = lambda obj: setattr(obj, "id", 1)
created = create_application(
db=mock_db,
candidate_id=101,
job_id=201,
)

        mock_query = MagicMock()
mock_query.all.return_value = [created]
mock_db.query.return_value = mock_query

        result = list_applications(db=mock_db)
assert len(result) == 1
assert result[0].id == 1
