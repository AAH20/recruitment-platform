"""Comprehensive tests for the job service module."""

import pytest
from datetime import datetime
from unittest.mock import patch

from recruitment_platform.services import job_service
from recruitment_platform.services.job_service import (
get_job,
list_jobs,
create_job,
update_job,
delete_job,
Job,
JobNotFoundError,
JobValidationError,
JobServiceError,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def clear_jobs_store():
    """Clear the in-memory jobs store before and after each test."""
job_service._jobs.clear()
yield
job_service._jobs.clear()


@pytest.fixture
def sample_job_data():
    """Return a valid job data dict for creation."""
return {
"title": "Senior Python Developer",
"description": "Build scalable backend services.",
"company": "TechCorp",
"location": "Remote",
"salary_min": 120000,
"salary_max": 180000,
"employment_type": "full-time",
"tags": ["python", "backend"],
}


@pytest.fixture
def created_job(sample_job_data):
    """Create a job in the store and return its dict representation."""
return create_job(sample_job_data)


@pytest.fixture
def multiple_jobs():
    """Create multiple jobs and return their dict representations."""
jobs_data = [
{
"title": "Backend Engineer",
"description": "API development",
"company": "Alpha Inc",
"location": "New York",
"salary_min": 100000,
"salary_max": 150000,
"employment_type": "full-time",
"status": "open",
"tags": ["python", "api"],
},
{
"title": "Frontend Developer",
"description": "React and TypeScript",
"company": "Beta LLC",
"location": "Remote",
"salary_min": 90000,
"salary_max": 130000,
"employment_type": "contract",
"status": "open",
"tags": ["react", "typescript"],
},
{
"title": "DevOps Engineer",
"description": "CI/CD and cloud infra",
"company": "Gamma Co",
"location": "San Francisco",
"salary_min": 130000,
"salary_max": 170000,
"employment_type": "full-time",
"status": "closed",
"tags": ["aws", "kubernetes"],
},
{
"title": "Data Scientist",
"description": "ML models and analytics",
"company": "Alpha Inc",
"location": "Remote",
"salary_min": 110000,
"salary_max": 160000,
"employment_type": "full-time",
"status": "open",
"tags": ["ml", "python"],
},
]
return [create_job(data) for data in jobs_data]


# ---------------------------------------------------------------------------
# Tests for get_job
# ---------------------------------------------------------------------------


class TestGetJob:
    """Tests for the get_job service function."""

    def test_get_job_returns_job_when_found(self, created_job):
        """get_job should return the job dict when it exists."""
result = get_job(created_job["id"])

        assert result is not None
assert result["id"] == created_job["id"]
assert result["title"] == "Senior Python Developer"
assert result["company"] == "TechCorp"
assert result["location"] == "Remote"
assert result["status"] == "open"

    def test_get_job_returns_dict_with_all_fields(self, created_job):
        """get_job should return a dict containing all expected fields."""
result = get_job(created_job["id"])

        assert isinstance(result, dict)
assert "id" in result
assert "title" in result
assert "description" in result
assert "company" in result
assert "location" in result
assert "salary_min" in result
assert "salary_max" in result
assert "employment_type" in result
assert "status" in result
assert "created_at" in result
assert "updated_at" in result
assert "tags" in result
assert "metadata" in result

    def test_get_job_raises_not_found_for_missing_id(self):
        """get_job should raise JobNotFoundError when the job does not exist."""
with pytest.raises(JobNotFoundError):
            get_job("nonexistent-id")

    def test_get_job_with_empty_string_id(self):
        """get_job should raise JobNotFoundError for an empty string ID."""
with pytest.raises(JobNotFoundError):
            get_job("")

    def test_get_job_does_not_mutate_store(self, created_job):
        """get_job should not modify the internal store."""
job_id = created_job["id"]
original = get_job(job_id)
get_job(job_id)
after = get_job(job_id)
assert original == after


# ---------------------------------------------------------------------------
# Tests for list_jobs
# ---------------------------------------------------------------------------


class TestListJobs:
    """Tests for the list_jobs service function."""

    def test_list_jobs_returns_empty_when_no_jobs(self):
        """list_jobs should return an empty list when no jobs exist."""
results = list_jobs(filters={}, page=1, page_size=10)

        assert results == []

    def test_list_jobs_returns_all_when_no_filters(self, multiple_jobs):
        """list_jobs should return all jobs when no filters are applied."""
results = list_jobs(filters={}, page=1, page_size=10)

        assert len(results) == 4
titles = [j["title"] for j in results]
assert "Backend Engineer" in titles
assert "Frontend Developer" in titles
assert "DevOps Engineer" in titles
assert "Data Scientist" in titles

    def test_list_jobs_filter_by_status(self, multiple_jobs):
        """list_jobs should filter by status when provided."""
results = list_jobs(filters={"status": "open"}, page=1, page_size=10)

        assert len(results) == 3
assert all(j["status"] == "open" for j in results)

    def test_list_jobs_filter_by_company(self, multiple_jobs):
        """list_jobs should filter by company when provided."""
results = list_jobs(filters={"company": "Alpha Inc"}, page=1, page_size=10)

        assert len(results) == 2
assert all(j["company"] == "Alpha Inc" for j in results)

    def test_list_jobs_filter_by_location(self, multiple_jobs):
        """list_jobs should filter by location when provided."""
results = list_jobs(filters={"location": "Remote"}, page=1, page_size=10)

        assert len(results) == 2
assert all(j["location"] == "Remote" for j in results)

    def test_list_jobs_filter_by_employment_type(self, multiple_jobs):
        """list_jobs should filter by employment_type when provided."""
results = list_jobs(
filters={"employment_type": "full-time"}, page=1, page_size=10
)

        assert len(results) == 3
assert all(j["employment_type"] == "full-time" for j in results)

    def test_list_jobs_filter_by_tags(self, multiple_jobs):
        """list_jobs should filter by tags when provided."""
results = list_jobs(filters={"tags": ["python"]}, page=1, page_size=10)

        assert len(results) == 2
assert all("python" in j["tags"] for j in results)

    def test_list_jobs_pagination_first_page(self, multiple_jobs):
        """list_jobs should return the correct page of results."""
results = list_jobs(filters={}, page=1, page_size=2)

        assert len(results) == 2

    def test_list_jobs_pagination_second_page(self, multiple_jobs):
        """list_jobs should return the second page of results."""
results = list_jobs(filters={}, page=2, page_size=2)

        assert len(results) == 2

    def test_list_jobs_pagination_empty_page(self, multiple_jobs):
        """list_jobs should return empty list when page is beyond available data."""
results = list_jobs(filters={}, page=10, page_size=2)

        assert results == []

    def test_list_jobs_invalid_page_raises_error(self):
        """list_jobs should raise ValueError for invalid page numbers."""
with pytest.raises(ValueError):
            list_jobs(filters={}, page=0, page_size=10)

    def test_list_jobs_invalid_page_size_raises_error(self):
        """list_jobs should raise ValueError for invalid page sizes."""
with pytest.raises(ValueError):
            list_jobs(filters={}, page=1, page_size=0)

    def test_list_jobs_combined_filters(self, multiple_jobs):
        """list_jobs should apply multiple filters simultaneously."""
results = list_jobs(
filters={"company": "Alpha Inc", "status": "open"},
page=1,
page_size=10,
)

        assert len(results) == 2
assert all(
j["company"] == "Alpha Inc" and j["status"] == "open" for j in results
)

    def test_list_jobs_filter_no_match_returns_empty(self, multiple_jobs):
        """list_jobs should return empty list when no jobs match the filter."""
results = list_jobs(filters={"company": "NonExistent"}, page=1, page_size=10)

        assert results == []


# ---------------------------------------------------------------------------
# Tests for create_job
# ---------------------------------------------------------------------------


class TestCreateJob:
    """Tests for the create_job service function."""

    def test_create_job_success(self, sample_job_data):
        """create_job should create and return a new job dict."""
result = create_job(sample_job_data)

        assert result is not None
assert "id" in result
assert result["title"] == "Senior Python Developer"
assert result["company"] == "TechCorp"
assert result["location"] == "Remote"
assert result["salary_min"] == 120000
assert result["salary_max"] == 180000
assert result["employment_type"] == "full-time"
assert result["status"] == "open"
assert result["tags"] == ["python", "backend"]
assert "created_at" in result
assert "updated_at" in result

    def test_create_job_generates_unique_ids(self, sample_job_data):
        """create_job should generate unique IDs for each job."""
job1 = create_job(sample_job_data)
job2 = create_job(sample_job_data)

        assert job1["id"] != job2["id"]

    def test_create_job_sets_default_status(self, sample_job_data):
        """create_job should default status to 'open' when not provided."""
result = create_job(sample_job_data)

        assert result["status"] == "open"

    def test_create_job_sets_default_employment_type(self, sample_job_data):
        """create_job should default employment_type to 'full-time'."""
result = create_job(sample_job_data)

        assert result["employment_type"] == "full-time"

    def test_create_job_with_explicit_status(self, sample_job_data):
        """create_job should respect an explicitly provided status."""
sample_job_data["status"] = "draft"
result = create_job(sample_job_data)

        assert result["status"] == "draft"

    def test_create_job_missing_title_raises_error(self, sample_job_data):
        """create_job should raise JobValidationError when title is missing."""
del sample_job_data["title"]

        with pytest.raises(JobValidationError):
            create_job(sample_job_data)

    def test_create_job_missing_description_raises_error(self, sample_job_data):
        """create_job should raise JobValidationError when description is missing."""
del sample_job_data["description"]

        with pytest.raises(JobValidationError):
            create_job(sample_job_data)

    def test_create_job_missing_company_raises_error(self, sample_job_data):
        """create_job should raise JobValidationError when company is missing."""
del sample_job_data["company"]

        with pytest.raises(JobValidationError):
            create_job(sample_job_data)

    def test_create_job_missing_location_raises_error(self, sample_job_data):
        """create_job should raise JobValidationError when location is missing."""
del sample_job_data["location"]

        with pytest.raises(JobValidationError):
            create_job(sample_job_data)

    def test_create_job_empty_title_raises_error(self, sample_job_data):
        """create_job should raise JobValidationError when title is empty."""
sample_job_data["title"] = ""

        with pytest.raises(JobValidationError):
            create_job(sample_job_data)

    def test_create_job_invalid_salary_range(self, sample_job_data):
        """create_job should raise JobValidationError when salary_min > salary_max."""
sample_job_data["salary_min"] = 200000
sample_job_data["salary_max"] = 100000

        with pytest.raises(JobValidationError):
            create_job(sample_job_data)

    def test_create_job_invalid_employment_type(self, sample_job_data):
        """create_job should raise JobValidationError for invalid employment_type."""
sample_job_data["employment_type"] = "invalid-type"

        with pytest.raises(JobValidationError):
            create_job(sample_job_data)

    def test_create_job_with_empty_data_raises_error(self):
        """create_job should raise ValueError when data is empty."""
with pytest.raises(ValueError):
            create_job({})

    def test_create_job_with_none_data_raises_error(self):
        """create_job should raise ValueError when data is None."""
with pytest.raises(ValueError):
            create_job(None)

    def test_create_job_with_minimal_fields(self):
        """create_job should work with only required fields."""
minimal_data = {
"title": "Junior Developer",
"description": "Entry-level position",
"company": "StartupInc",
"location": "Remote",
}
result = create_job(minimal_data)

        assert result is not None
assert result["title"] == "Junior Developer"
assert result["company"] == "StartupInc"
assert result["salary_min"] is None
assert result["salary_max"] is None
assert result["tags"] == []
assert result["metadata"] == {}

    def test_create_job_with_tags_and_metadata(self):
        """create_job should store tags and metadata when provided."""
data = {
"title": "Full Stack Developer",
"description": "Build web apps",
"company": "WebCo",
"location": "Remote",
"tags": ["react", "node"],
"metadata": {"department": "Engineering", "level": "senior"},
}
result = create_job(data)

        assert result["tags"] == ["react", "node"]
assert result["metadata"] == {"department": "Engineering", "level": "senior"}

    def test_create_job_stores_in_internal_store(self, sample_job_data):
        """create_job should store the job in the internal _jobs dict."""
result = create_job(sample_job_data)

        assert result["id"] in job_service._jobs
assert job_service._jobs[result["id"]].title == "Senior Python Developer"


# ---------------------------------------------------------------------------
# Tests for update_job
# ---------------------------------------------------------------------------


class TestUpdateJob:
    """Tests for the update_job service function."""

    def test_update_job_success(self, created_job):
        """update_job should update and return the modified job."""
updates = {"title": "Staff Python Developer", "salary_max": 200000}
result = update_job(created_job["id"], updates)

        assert result is not None
assert result["title"] == "Staff Python Developer"
assert result["salary_max"] == 200000
assert result["company"] == "TechCorp"

    def test_update_job_not_found_raises_error(self):
        """update_job should raise JobNotFoundError when job doesn't exist."""
with pytest.raises(JobNotFoundError):
            update_job("nonexistent-id", {"title": "New Title"})

    def test_update_job_partial_update(self, created_job):
        """update_job should allow partial updates (only some fields)."""
original_company = created_job["company"]
original_title = created_job["title"]
updates = {"location": "Hybrid"}
result = update_job(created_job["id"], updates)

        assert result["location"] == "Hybrid"
assert result["company"] == original_company
assert result["title"] == original_title

    def test_update_job_status_transition(self, created_job):
        """update_job should allow status transitions."""
updates = {"status": "closed"}
result = update_job(created_job["id"], updates)

        assert result["status"] == "closed"

    def test_update_job_empty_data_raises_error(self, created_job):
        """update_job should raise ValueError when data is empty."""
with pytest.raises(ValueError):
            update_job(created_job["id"], {})

    def test_update_job_none_data_raises_error(self, created_job):
        """update_job should raise ValueError when data is None."""
with pytest.raises(ValueError):
            update_job(created_job["id"], None)

    def test_update_job_invalid_field_ignored(self, created_job):
        """update_job should ignore unknown fields in updates."""
updates = {"nonexistent_field": "value", "title": "Updated Title"}
result = update_job(created_job["id"], updates)

        assert result["title"] == "Updated Title"
assert "nonexistent_field" not in result

    def test_update_job_updates_updated_at_timestamp(self, created_job):
        """update_job should update the updated_at timestamp."""
original_updated_at = created_job["updated_at"]
updates = {"title": "New Title"}
result = update_job(created_job["id"], updates)

        assert result["updated_at"] >= original_updated_at

    def test_update_job_salary_update(self, created_job):
        """update_job should correctly update salary fields."""
updates = {"salary_min": 130000, "salary_max": 190000}
result = update_job(created_job["id"], updates)

        assert result["salary_min"] == 130000
assert result["salary_max"] == 190000

    def test_update_job_invalid_salary_range_raises_error(self, created_job):
        """update_job should raise JobValidationError for invalid salary range."""
updates = {"salary_min": 200000, "salary_max": 100000}

        with pytest.raises(JobValidationError):
            update_job(created_job["id"], updates)

    def test_update_job_tags_update(self, created_job):
        """update_job should correctly update tags."""
updates = {"tags": ["python", "backend", "senior"]}
result = update_job(created_job["id"], updates)

        assert result["tags"] == ["python", "backend", "senior"]

    def test_update_job_metadata_update(self, created_job):
        """update_job should correctly update metadata."""
updates = {"metadata": {"department": "Engineering", "team": "Platform"}}
result = update_job(created_job["id"], updates)

        assert result["metadata"] == {"department": "Engineering", "team": "Platform"}


# ---------------------------------------------------------------------------
# Tests for delete_job
# ---------------------------------------------------------------------------


class TestDeleteJob:
    """Tests for the delete_job service function."""

    def test_delete_job_success(self, created_job):
        """delete_job should remove the job and return True."""
result = delete_job(created_job["id"])

        assert result is True
assert created_job["id"] not in job_service._jobs

    def test_delete_job_not_found_raises_error(self):
        """delete_job should raise JobNotFoundError when job doesn't exist."""
with pytest.raises(JobNotFoundError):
            delete_job("nonexistent-id")

    def test_delete_job_removes_from_store(self, multiple_jobs):
        """delete_job should remove the job from the internal store."""
job_id = multiple_jobs[0]["id"]
delete_job(job_id)

        assert job_id not in job_service._jobs

    def test_delete_job_other_jobs_remain(self, multiple_jobs):
        """delete_job should not affect other jobs in the store."""
job_id = multiple_jobs[0]["id"]
remaining_ids = [j["id"] for j in multiple_jobs[1:]]
delete_job(job_id)

        for rid in remaining_ids:
            assert rid in job_service._jobs

    def test_delete_job_then_get_raises_not_found(self, created_job):
        """After deletion, get_job should raise JobNotFoundError."""
job_id = created_job["id"]
delete_job(job_id)

        with pytest.raises(JobNotFoundError):
            get_job(job_id)

    def test_delete_job_then_update_raises_not_found(self, created_job):
        """After deletion, update_job should raise JobNotFoundError."""
job_id = created_job["id"]
delete_job(job_id)

        with pytest.raises(JobNotFoundError):
            update_job(job_id, {"title": "New Title"})

    def test_delete_job_then_list_excludes_it(self, multiple_jobs):
        """After deletion, list_jobs should not include the deleted job."""
job_id = multiple_jobs[0]["id"]
delete_job(job_id)

        results = list_jobs(filters={}, page=1, page_size=10)
result_ids = [j["id"] for j in results]

        assert job_id not in result_ids
assert len(results) == 3
