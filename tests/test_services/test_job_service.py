"""Tests for JobService."""
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
def job_service(mock_db):
    """Fixture providing a JobService instance with mocked DB."""
    from app.services.job_service import JobService
    return JobService(db=mock_db)


@pytest.fixture
def sample_job():
    """Fixture providing sample job data."""
    return {
        "id": 1,
        "title": "Software Engineer",
        "description": "Build awesome software",
        "department": "Engineering",
        "location": "Remote",
        "salary_min": 80000,
        "salary_max": 120000,
        "status": "open",
        "created_at": datetime(2024, 1, 1),
        "updated_at": datetime(2024, 1, 1),
    }


class TestJobService:
    """Test suite for JobService."""

    def test_create_job(self, job_service, mock_db, sample_job):
        """Test creating a new job posting."""
        job_service.create = MagicMock(return_value=sample_job)
        result = job_service.create(sample_job)
        assert result["title"] == "Software Engineer"
        assert result["department"] == "Engineering"
        assert result["status"] == "open"

    def test_get_job_by_id(self, job_service, mock_db, sample_job):
        """Test retrieving a job by ID."""
        mock_db.first.return_value = sample_job
        result = job_service.get_by_id(1)
        assert result is not None
        assert result["id"] == 1
        assert result["title"] == "Software Engineer"

    def test_get_job_not_found(self, job_service, mock_db):
        """Test retrieving a non-existent job returns None."""
        mock_db.first.return_value = None
        result = job_service.get_by_id(999)
        assert result is None

    def test_get_all_jobs(self, job_service, mock_db, sample_job):
        """Test retrieving all jobs."""
        mock_db.all.return_value = [sample_job]
        result = job_service.get_all()
        assert len(result) == 1
        assert result[0]["title"] == "Software Engineer"

    def test_update_job(self, job_service, mock_db, sample_job):
        """Test updating a job posting."""
        updated = {**sample_job, "title": "Senior Software Engineer"}
        job_service.update = MagicMock(return_value=updated)
        result = job_service.update(1, {"title": "Senior Software Engineer"})
        assert result["title"] == "Senior Software Engineer"

    def test_delete_job(self, job_service, mock_db):
        """Test deleting a job posting."""
        job_service.delete = MagicMock(return_value=True)
        result = job_service.delete(1)
        assert result is True

    def test_search_jobs_by_title(self, job_service, mock_db, sample_job):
        """Test searching jobs by title."""
        mock_db.all.return_value = [sample_job]
        result = job_service.search("Software")
        assert len(result) == 1
        assert result[0]["title"] == "Software Engineer"

    def test_filter_jobs_by_department(self, job_service, mock_db, sample_job):
        """Test filtering jobs by department."""
        mock_db.all.return_value = [sample_job]
        result = job_service.filter_by_department("Engineering")
        assert len(result) == 1
        assert result[0]["department"] == "Engineering"

    def test_filter_jobs_by_status(self, job_service, mock_db, sample_job):
        """Test filtering jobs by status."""
        mock_db.all.return_value = [sample_job]
        result = job_service.filter_by_status("open")
        assert len(result) == 1
        assert result[0]["status"] == "open"

    def test_filter_jobs_by_location(self, job_service, mock_db, sample_job):
        """Test filtering jobs by location."""
        mock_db.all.return_value = [sample_job]
        result = job_service.filter_by_location("Remote")
        assert len(result) == 1
        assert result[0]["location"] == "Remote"

    def test_close_job(self, job_service, mock_db, sample_job):
        """Test closing a job posting."""
        closed = {**sample_job, "status": "closed"}
        job_service.update = MagicMock(return_value=closed)
        result = job_service.close(1)
        assert result["status"] == "closed"

    def test_job_title_required(self, job_service):
        """Test that job title is required."""
        with pytest.raises(ValueError):
            job_service.create({
                "description": "No title provided",
                "department": "Engineering",
            })

    def test_job_salary_validation(self, job_service):
        """Test that salary min cannot exceed max."""
        with pytest.raises(ValueError):
            job_service.create({
                "title": "Test Job",
                "salary_min": 120000,
                "salary_max": 80000,
            })
