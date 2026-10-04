"""Tests for job service."""

import pytest
from unittest.mock import MagicMock, patch


class TestJobService:
    """Test job service functionality."""

    def test_create_job(self, db_session):
        """Test creating a job."""
        from recruitment_platform.services.job_service import create_job
        
        job_data = {
            "title": "Software Engineer",
            "description": "Great opportunity",
            "salary_min": 100000,
            "salary_max": 150000,
        }
        
        result = create_job(db_session, job_data)
        assert result is not None
        assert result.title == "Software Engineer"

    def test_get_job(self, db_session):
        """Test getting a job."""
        from recruitment_platform.services.job_service import get_job, create_job
        
        job_data = {"title": "DevOps Engineer", "description": "Cloud role"}
        created = create_job(db_session, job_data)
        
        result = get_job(db_session, created.id)
        assert result is not None
        assert result.title == "DevOps Engineer"

    def test_list_jobs(self, db_session):
        """Test listing jobs."""
        from recruitment_platform.services.job_service import list_jobs
        
        result = list_jobs(db_session)
        assert isinstance(result, list)

    def test_update_job(self, db_session):
        """Test updating a job."""
        from recruitment_platform.services.job_service import update_job, create_job
        
        job_data = {"title": "Backend Engineer", "description": "API role"}
        created = create_job(db_session, job_data)
        
        update_data = {"title": "Senior Backend Engineer"}
        result = update_job(db_session, created.id, update_data)
        assert result is not None
        assert result.title == "Senior Backend Engineer"

    def test_delete_job(self, db_session):
        """Test deleting a job."""
        from recruitment_platform.services.job_service import delete_job, create_job
        
        job_data = {"title": "Temp Role", "description": "Temporary"}
        created = create_job(db_session, job_data)
        
        result = delete_job(db_session, created.id)
        assert result is True

    def test_filter_jobs(self, db_session):
        """Test filtering jobs."""
        from recruitment_platform.services.job_service import filter_jobs
        
        result = filter_jobs(db_session, location="Remote")
        assert isinstance(result, list)
