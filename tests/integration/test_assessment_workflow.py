"""
Integration tests for the Assessment Workflow API.

Tests cover:
- Full assessment lifecycle (create → score → delete)
- Candidate flow (create candidate → create assessment → score)
- Analytics retrieval (create assessment → get analytics)
"""

import pytest
import requests
from typing import Any, Dict, Generator

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BASE_URL = "http://localhost:8000/api/v1"
TIMEOUT = 10


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def api_client() -> Generator[requests.Session, None, None]:
    """Provide a requests session with base URL configured."""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    yield session
    session.close()


@pytest.fixture
def sample_assessment_payload() -> Dict[str, Any]:
    """Return a valid payload for creating an assessment."""
    return {
        "title": "Python Developer Assessment",
        "description": "Evaluate Python programming skills",
        "questions": [
            {
                "text": "What is the output of len([1, 2, 3])?",
                "type": "multiple_choice",
                "options": ["2", "3", "4", "Error"],
                "correct_answer": "3",
            },
            {
                "text": "Explain the difference between a list and a tuple.",
                "type": "free_text",
                "correct_answer": "Lists are mutable, tuples are immutable.",
            },
        ],
        "time_limit_minutes": 30,
        "passing_score": 70,
    }


@pytest.fixture
def sample_candidate_payload() -> Dict[str, Any]:
    """Return a valid payload for creating a candidate."""
    return {
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane.doe@example.com",
        "phone": "+1-555-0123",
        "resume_url": "https://example.com/resumes/jane-doe.pdf",
    }


@pytest.fixture
def created_assessment(
    api_client: requests.Session, sample_assessment_payload: Dict[str, Any]
) -> Generator[Dict[str, Any], None, None]:
    """Create an assessment and yield it; clean up after the test."""
    response = api_client.post(
        f"{BASE_URL}/assessments", json=sample_assessment_payload, timeout=TIMEOUT
    )
    assert response.status_code == 201, f"Failed to create assessment: {response.text}"
    assessment = response.json()
    yield assessment

    # Cleanup: delete the assessment
    assessment_id = assessment.get("id")
    if assessment_id:
        api_client.delete(f"{BASE_URL}/assessments/{assessment_id}", timeout=TIMEOUT)


@pytest.fixture
def created_candidate(
    api_client: requests.Session, sample_candidate_payload: Dict[str, Any]
) -> Generator[Dict[str, Any], None, None]:
    """Create a candidate and yield it; clean up after the test."""
    response = api_client.post(
        f"{BASE_URL}/candidates", json=sample_candidate_payload, timeout=TIMEOUT
    )
    assert response.status_code == 201, f"Failed to create candidate: {response.text}"
    candidate = response.json()
    yield candidate

    # Cleanup: delete the candidate
    candidate_id = candidate.get("id")
    if candidate_id:
        api_client.delete(f"{BASE_URL}/candidates/{candidate_id}", timeout=TIMEOUT)


# ---------------------------------------------------------------------------
# Test 1: Full Assessment Lifecycle (create → score → delete)
# ---------------------------------------------------------------------------
class TestFullAssessmentLifecycle:
    """Test the complete lifecycle of an assessment."""

    def test_full_assessment_lifecycle(
        self,
        api_client: requests.Session,
        sample_assessment_payload: Dict[str, Any],
    ) -> None:
        """Create an assessment, score it, then delete it."""
        # --- Step 1: Create ---
        create_response = api_client.post(
            f"{BASE_URL}/assessments",
            json=sample_assessment_payload,
            timeout=TIMEOUT,
        )
        assert create_response.status_code == 201, (
            f"Expected 201, got {create_response.status_code}: {create_response.text}"
        )
        assessment = create_response.json()
        assert "id" in assessment, "Assessment response must contain 'id'"
        assert assessment["title"] == sample_assessment_payload["title"]
        assert assessment["description"] == sample_assessment_payload["description"]
        assert len(assessment["questions"]) == len(
            sample_assessment_payload["questions"]
        )
        assessment_id = assessment["id"]

        # --- Step 2: Score ---
        score_payload = {
            "answers": [
                {"question_index": 0, "answer": "3"},
                {
                    "question_index": 1,
                    "answer": "Lists are mutable, tuples are immutable.",
                },
            ]
        }
        score_response = api_client.post(
            f"{BASE_URL}/assessments/{assessment_id}/score",
            json=score_payload,
            timeout=TIMEOUT,
        )
        assert score_response.status_code == 200, (
            f"Expected 200, got {score_response.status_code}: {score_response.text}"
        )
        score_result = score_response.json()
        assert "score" in score_result, "Score response must contain 'score'"
        assert "passed" in score_result, "Score response must contain 'passed'"
        assert isinstance(score_result["score"], (int, float))
        assert isinstance(score_result["passed"], bool)
        assert 0 <= score_result["score"] <= 100

        # --- Step 3: Delete ---
        delete_response = api_client.delete(
            f"{BASE_URL}/assessments/{assessment_id}", timeout=TIMEOUT
        )
        assert delete_response.status_code in (200, 204), (
            f"Expected 200/204, got {delete_response.status_code}"
        )

        # Verify deletion
        get_response = api_client.get(
            f"{BASE_URL}/assessments/{assessment_id}", timeout=TIMEOUT
        )
        assert get_response.status_code == 404, (
            "Deleted assessment should return 404 on subsequent GET"
        )


# ---------------------------------------------------------------------------
# Test 2: Assessment Candidate Flow (create candidate → create assessment → score)
# ---------------------------------------------------------------------------
class TestAssessmentCandidateFlow:
    """Test the flow of creating a candidate, an assessment, and scoring."""

    def test_assessment_candidate_flow(
        self,
        api_client: requests.Session,
        sample_candidate_payload: Dict[str, Any],
        sample_assessment_payload: Dict[str, Any],
    ) -> None:
        """Create a candidate, create an assessment, and score the candidate."""
        # --- Step 1: Create Candidate ---
        candidate_response = api_client.post(
            f"{BASE_URL}/candidates",
            json=sample_candidate_payload,
            timeout=TIMEOUT,
        )
        assert candidate_response.status_code == 201, (
            f"Failed to create candidate: {candidate_response.text}"
        )
        candidate = candidate_response.json()
        assert "id" in candidate, "Candidate response must contain 'id'"
        assert candidate["email"] == sample_candidate_payload["email"]
        candidate_id = candidate["id"]

        # --- Step 2: Create Assessment ---
        assessment_response = api_client.post(
            f"{BASE_URL}/assessments",
            json=sample_assessment_payload,
            timeout=TIMEOUT,
        )
        assert assessment_response.status_code == 201, (
            f"Failed to create assessment: {assessment_response.text}"
        )
        assessment = assessment_response.json()
        assert "id" in assessment, "Assessment response must contain 'id'"
        assessment_id = assessment["id"]

        # --- Step 3: Score the candidate on the assessment ---
        score_payload = {
            "candidate_id": candidate_id,
            "answers": [
                {"question_index": 0, "answer": "3"},
                {
                    "question_index": 1,
                    "answer": "Lists are mutable, tuples are immutable.",
                },
            ],
        }
        score_response = api_client.post(
            f"{BASE_URL}/assessments/{assessment_id}/score",
            json=score_payload,
            timeout=TIMEOUT,
        )
        assert score_response.status_code == 200, (
            f"Failed to score candidate: {score_response.text}"
        )
        score_result = score_response.json()
        assert "score" in score_result
        assert "passed" in score_result
        assert "candidate_id" in score_result
        assert score_result["candidate_id"] == candidate_id
        assert isinstance(score_result["score"], (int, float))
        assert isinstance(score_result["passed"], bool)

        # Cleanup
        api_client.delete(f"{BASE_URL}/assessments/{assessment_id}", timeout=TIMEOUT)
        api_client.delete(f"{BASE_URL}/candidates/{candidate_id}", timeout=TIMEOUT)


# ---------------------------------------------------------------------------
# Test 3: Assessment Analytics (create assessment → get analytics)
# ---------------------------------------------------------------------------
class TestAssessmentAnalytics:
    """Test analytics retrieval for an assessment."""

    def test_assessment_analytics(
        self,
        api_client: requests.Session,
        sample_assessment_payload: Dict[str, Any],
    ) -> None:
        """Create an assessment and retrieve its analytics."""
        # --- Step 1: Create Assessment ---
        create_response = api_client.post(
            f"{BASE_URL}/assessments",
            json=sample_assessment_payload,
            timeout=TIMEOUT,
        )
        assert create_response.status_code == 201, (
            f"Failed to create assessment: {create_response.text}"
        )
        assessment = create_response.json()
        assessment_id = assessment["id"]

        # --- Step 2: Get Analytics ---
        analytics_response = api_client.get(
            f"{BASE_URL}/assessments/{assessment_id}/analytics", timeout=TIMEOUT
        )
        assert analytics_response.status_code == 200, (
            f"Failed to get analytics: {analytics_response.text}"
        )
        analytics = analytics_response.json()

        # Validate analytics structure
        assert "assessment_id" in analytics
        assert analytics["assessment_id"] == assessment_id
        assert "total_attempts" in analytics
        assert "average_score" in analytics
        assert "pass_rate" in analytics
        assert "completion_rate" in analytics
        assert isinstance(analytics["total_attempts"], int)
        assert analytics["total_attempts"] >= 0
        assert isinstance(analytics["average_score"], (int, float))
        assert 0 <= analytics["average_score"] <= 100
        assert isinstance(analytics["pass_rate"], (int, float))
        assert 0 <= analytics["pass_rate"] <= 100
        assert isinstance(analytics["completion_rate"], (int, float))
        assert 0 <= analytics["completion_rate"] <= 100

        # Cleanup
        api_client.delete(f"{BASE_URL}/assessments/{assessment_id}", timeout=TIMEOUT)
