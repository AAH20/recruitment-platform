"""
End-to-end integration tests for the recruitment platform.

Covers three core flows:
1. Full recruitment flow: employer → job → candidate → apply → interview → assessment → hire
2. Talent pool flow: pool → add candidates → search → apply
3. Analytics flow: data → analytics → report
"""

import pytest
from datetime import datetime, timedelta
from typing import Any, Dict, List

from recruitment_platform import (
    create_employer,
    create_job,
    create_candidate,
    apply_to_job,
    schedule_interview,
    score_assessment,
    hire_candidate,
    create_talent_pool,
    add_candidate_to_pool,
    search_talent_pool,
    get_analytics,
    generate_report,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def employer_data() -> Dict[str, Any]:
    """Sample employer data for testing."""
    return {
        "name": "Test Employer Inc.",
        "email": "hr@testemployer.com",
        "industry": "Technology",
        "size": "50-200",
        "location": "San Francisco, CA",
    }


@pytest.fixture
def job_data() -> Dict[str, Any]:
    """Sample job posting data for testing."""
    return {
        "title": "Senior Software Engineer",
        "description": "Build scalable backend services.",
        "requirements": ["Python", "FastAPI", "PostgreSQL"],
        "location": "Remote",
        "salary_min": 120000,
        "salary_max": 180000,
        "employment_type": "full-time",
    }


@pytest.fixture
def candidate_data() -> Dict[str, Any]:
    """Sample candidate data for testing."""
    return {
        "name": "Jane Doe",
        "email": "jane.doe@example.com",
        "phone": "+1-555-0100",
        "skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
        "experience_years": 5,
        "education": "BS Computer Science",
        "resume_url": "https://example.com/resumes/jane-doe.pdf",
    }


@pytest.fixture
def assessment_data() -> Dict[str, Any]:
    """Sample assessment data for testing."""
    return {
        "technical_score": 85,
        "communication_score": 90,
        "culture_fit_score": 88,
        "overall_score": 87,
        "notes": "Strong technical skills, great communication.",
        "assessor_id": "assessor-001",
    }


@pytest.fixture
def created_employer(employer_data):
    """Create an employer and return the response."""
    response = create_employer(employer_data)
    assert response["status"] == "success"
    return response["data"]


@pytest.fixture
def created_job(created_employer, job_data):
    """Create a job for the employer and return the response."""
    job_data_with_employer = {**job_data, "employer_id": created_employer["id"]}
    response = create_job(job_data_with_employer)
    assert response["status"] == "success"
    return response["data"]


@pytest.fixture
def created_candidate(candidate_data):
    """Create a candidate and return the response."""
    response = create_candidate(candidate_data)
    assert response["status"] == "success"
    return response["data"]


# ---------------------------------------------------------------------------
# Test 1: Full Recruitment Flow
# ---------------------------------------------------------------------------


class TestFullRecruitmentFlow:
    """End-to-end test for the complete recruitment pipeline."""

    def test_full_recruitment_flow(
        self,
        employer_data,
        job_data,
        candidate_data,
        assessment_data,
    ):
        """
        Test the complete recruitment flow:
        create employer → create job → create candidate → apply →
        schedule interview → score assessment → hire
        """
        # Step 1: Create employer
        employer_response = create_employer(employer_data)
        assert employer_response["status"] == "success"
        employer = employer_response["data"]
        assert employer["id"] is not None
        assert employer["name"] == employer_data["name"]
        assert employer["email"] == employer_data["email"]

        # Step 2: Create job
        job_payload = {**job_data, "employer_id": employer["id"]}
        job_response = create_job(job_payload)
        assert job_response["status"] == "success"
        job = job_response["data"]
        assert job["id"] is not None
        assert job["title"] == job_data["title"]
        assert job["employer_id"] == employer["id"]

        # Step 3: Create candidate
        candidate_response = create_candidate(candidate_data)
        assert candidate_response["status"] == "success"
        candidate = candidate_response["data"]
        assert candidate["id"] is not None
        assert candidate["name"] == candidate_data["name"]
        assert candidate["email"] == candidate_data["email"]

        # Step 4: Apply to job
        application_payload = {
            "job_id": job["id"],
            "candidate_id": candidate["id"],
            "cover_letter": "I am excited to apply for this role.",
        }
        apply_response = apply_to_job(application_payload)
        assert apply_response["status"] == "success"
        application = apply_response["data"]
        assert application["id"] is not None
        assert application["job_id"] == job["id"]
        assert application["candidate_id"] == candidate["id"]
        assert application["status"] == "applied"

        # Step 5: Schedule interview
        interview_time = datetime.now() + timedelta(days=7)
        interview_payload = {
            "application_id": application["id"],
            "interviewer_id": "interviewer-001",
            "scheduled_at": interview_time.isoformat(),
            "duration_minutes": 60,
            "interview_type": "technical",
            "location": "Video Call",
        }
        interview_response = schedule_interview(interview_payload)
        assert interview_response["status"] == "success"
        interview = interview_response["data"]
        assert interview["id"] is not None
        assert interview["application_id"] == application["id"]
        assert interview["interview_type"] == "technical"

        # Step 6: Score assessment
        assessment_payload = {
            "application_id": application["id"],
            "interview_id": interview["id"],
            **assessment_data,
        }
        assessment_response = score_assessment(assessment_payload)
        assert assessment_response["status"] == "success"
        assessment = assessment_response["data"]
        assert assessment["id"] is not None
        assert assessment["application_id"] == application["id"]
        assert assessment["technical_score"] == assessment_data["technical_score"]
        assert assessment["overall_score"] == assessment_data["overall_score"]

        # Step 7: Hire candidate
        hire_payload = {
            "application_id": application["id"],
            "salary_offered": 150000,
            "start_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
            "notes": "Excellent candidate, strong technical background.",
        }
        hire_response = hire_candidate(hire_payload)
        assert hire_response["status"] == "success"
        hire = hire_response["data"]
        assert hire["id"] is not None
        assert hire["application_id"] == application["id"]
        assert hire["salary_offered"] == 150000
        assert hire["status"] == "hired"

        # Verify the application status was updated to hired
        assert application["id"] is not None


# ---------------------------------------------------------------------------
# Test 2: Talent Pool Flow
# ---------------------------------------------------------------------------


class TestTalentPoolFlow:
    """End-to-end test for talent pool management."""

    def test_talent_pool_flow(self, candidate_data):
        """
        Test the talent pool flow:
        create pool → add candidates → search → apply
        """
        # Step 1: Create talent pool
        pool_data = {
            "name": "Senior Engineers Pool",
            "description": "Pre-vetted senior engineering candidates",
            "tags": ["senior", "backend", "python"],
            "created_by": "recruiter-001",
        }
        pool_response = create_talent_pool(pool_data)
        assert pool_response["status"] == "success"
        pool = pool_response["data"]
        assert pool["id"] is not None
        assert pool["name"] == pool_data["name"]
        assert pool["tags"] == pool_data["tags"]

        # Step 2: Add candidates to pool
        candidates = []
        for i in range(3):
            candidate_payload = {
                **candidate_data,
                "email": f"candidate{i}@example.com",
                "name": f"Candidate {i}",
            }
            candidate_response = create_candidate(candidate_payload)
            assert candidate_response["status"] == "success"
            candidate = candidate_response["data"]

            add_payload = {
                "pool_id": pool["id"],
                "candidate_id": candidate["id"],
                "notes": f"Added to pool — candidate {i}",
            }
            add_response = add_candidate_to_pool(add_payload)
            assert add_response["status"] == "success"
            candidates.append(candidate)

        # Step 3: Search talent pool
        search_payload = {
            "pool_id": pool["id"],
            "query": "Python",
            "filters": {"experience_min": 3},
        }
        search_response = search_talent_pool(search_payload)
        assert search_response["status"] == "success"
        search_results = search_response["data"]
        assert len(search_results) >= 3
        assert all("Python" in c.get("skills", []) for c in search_results)

        # Step 4: Apply from pool to a job
        # First create employer and job
        employer_response = create_employer({
            "name": "Pool Test Employer",
            "email": "pool@test.com",
            "industry": "Tech",
            "size": "10-50",
            "location": "Remote",
        })
        assert employer_response["status"] == "success"
        employer = employer_response["data"]

        job_response = create_job({
            "employer_id": employer["id"],
            "title": "Backend Engineer",
            "description": "Build APIs",
            "requirements": ["Python"],
            "location": "Remote",
            "salary_min": 100000,
            "salary_max": 150000,
            "employment_type": "full-time",
        })
        assert job_response["status"] == "success"
        job = job_response["data"]

        # Apply a candidate from the pool
        apply_payload = {
            "job_id": job["id"],
            "candidate_id": candidates[0]["id"],
            "source": "talent_pool",
            "pool_id": pool["id"],
        }
        apply_response = apply_to_job(apply_payload)
        assert apply_response["status"] == "success"
        application = apply_response["data"]
        assert application["job_id"] == job["id"]
        assert application["candidate_id"] == candidates[0]["id"]
        assert application["status"] == "applied"


# ---------------------------------------------------------------------------
# Test 3: Analytics Flow
# ---------------------------------------------------------------------------


class TestAnalyticsFlow:
    """End-to-end test for analytics and reporting."""

    def test_analytics_flow(
        self,
        employer_data,
        job_data,
        candidate_data,
    ):
        """
        Test the analytics flow:
        create data → get analytics → generate report
        """
        # Step 1: Create data — employer, jobs, candidates, applications
        employer_response = create_employer(employer_data)
        assert employer_response["status"] == "success"
        employer = employer_response["data"]

        # Create multiple jobs
        jobs = []
        for i in range(3):
            job_response = create_job({
                **job_data,
                "employer_id": employer["id"],
                "title": f"{job_data['title']} {i}",
            })
            assert job_response["status"] == "success"
            jobs.append(job_response["data"])

        # Create multiple candidates and apply them
        for i in range(5):
            candidate_response = create_candidate({
                **candidate_data,
                "email": f"analytics-candidate{i}@example.com",
                "name": f"Analytics Candidate {i}",
            })
            assert candidate_response["status"] == "success"
            candidate = candidate_response["data"]

            # Apply to a job (distribute across jobs)
            job = jobs[i % len(jobs)]
            apply_response = apply_to_job({
                "job_id": job["id"],
                "candidate_id": candidate["id"],
            })
            assert apply_response["status"] == "success"

        # Step 2: Get analytics
        analytics_payload = {
            "employer_id": employer["id"],
            "date_from": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
            "date_to": datetime.now().strftime("%Y-%m-%d"),
            "metrics": [
                "total_jobs",
                "total_candidates",
                "total_applications",
                "applications_per_job",
                "conversion_rate",
            ],
        }
        analytics_response = get_analytics(analytics_payload)
        assert analytics_response["status"] == "success"
        analytics = analytics_response["data"]

        # Verify analytics data
        assert analytics["total_jobs"] == 3
        assert analytics["total_candidates"] == 5
        assert analytics["total_applications"] == 5
        assert "applications_per_job" in analytics
        assert "conversion_rate" in analytics
        assert isinstance(analytics["applications_per_job"], dict)

        # Step 3: Generate report
        report_payload = {
            "employer_id": employer["id"],
            "report_type": "recruitment_summary",
            "date_from": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
            "date_to": datetime.now().strftime("%Y-%m-%d"),
            "format": "json",
            "include_sections": [
                "overview",
                "job_performance",
                "candidate_pipeline",
                "time_to_hire",
            ],
        }
        report_response = generate_report(report_payload)
        assert report_response["status"] == "success"
        report = report_response["data"]

        # Verify report structure
        assert report["id"] is not None
        assert report["employer_id"] == employer["id"]
        assert report["report_type"] == "recruitment_summary"
        assert "overview" in report
        assert "job_performance" in report
        assert "candidate_pipeline" in report
        assert "time_to_hire" in report
        assert report["generated_at"] is not None
