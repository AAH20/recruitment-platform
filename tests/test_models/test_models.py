"""Tests for recruitment-platform models and schemas."""

import pytest
from pydantic import ValidationError


class TestEmployerModel:
    """Test employer Pydantic model."""

    def test_valid_employer(self):
        """Test valid employer data."""
        from recruitment_platform.models import EmployerCreate
        
        data = {
            "name": "Test Company",
            "industry": "Technology",
            "size": "50-200",
            "location": "San Francisco",
        }
        
        employer = EmployerCreate(**data)
        assert employer.name == "Test Company"

    def test_employer_name_too_short(self):
        """Test employer name validation."""
        from recruitment_platform.models import EmployerCreate
        
        with pytest.raises(ValidationError):
            EmployerCreate(name="")

    def test_employer_name_too_long(self):
        """Test employer name max length."""
        from recruitment_platform.models import EmployerCreate
        
        with pytest.raises(ValidationError):
            EmployerCreate(name="A" * 256)


class TestCandidateModel:
    """Test candidate Pydantic model."""

    def test_valid_candidate(self):
        """Test valid candidate data."""
        from recruitment_platform.models import CandidateCreate
        
        data = {
            "name": "John Doe",
            "email": "john@example.com",
            "skills": ["Python", "FastAPI"],
        }
        
        candidate = CandidateCreate(**data)
        assert candidate.name == "John Doe"

    def test_candidate_invalid_email(self):
        """Test candidate email validation."""
        from recruitment_platform.models import CandidateCreate
        
        with pytest.raises(ValidationError):
            CandidateCreate(name="John", email="invalid-email")

    def test_candidate_name_too_short(self):
        """Test candidate name validation."""
        from recruitment_platform.models import CandidateCreate
        
        with pytest.raises(ValidationError):
            CandidateCreate(name="", email="john@example.com")


class TestJobModel:
    """Test job Pydantic model."""

    def test_valid_job(self):
        """Test valid job data."""
        from recruitment_platform.models import JobCreate
        
        data = {
            "title": "Software Engineer",
            "description": "Great opportunity",
            "salary_min": 100000,
            "salary_max": 150000,
        }
        
        job = JobCreate(**data)
        assert job.title == "Software Engineer"

    def test_job_salary_validation(self):
        """Test job salary validation."""
        from recruitment_platform.models import JobCreate
        
        with pytest.raises(ValidationError):
            JobCreate(
                title="Test",
                description="Test",
                salary_min=-1000,
                salary_max=150000,
            )

    def test_job_title_too_long(self):
        """Test job title max length."""
        from recruitment_platform.models import JobCreate
        
        with pytest.raises(ValidationError):
            JobCreate(
                title="A" * 501,
                description="Test",
                salary_min=100000,
                salary_max=150000,
            )


class TestApplicationModel:
    """Test application Pydantic model."""

    def test_valid_application(self):
        """Test valid application data."""
        from recruitment_platform.models import ApplicationCreate
        
        data = {
            "job_id": 1,
            "candidate_id": 1,
            "cover_letter": "I am interested",
        }
        
        app = ApplicationCreate(**data)
        assert app.job_id == 1

    def test_application_status_validation(self):
        """Test application status validation."""
        from recruitment_platform.models import ApplicationCreate
        
        with pytest.raises(ValidationError):
            ApplicationCreate(
                job_id=1,
                candidate_id=1,
                status="invalid_status",
            )
