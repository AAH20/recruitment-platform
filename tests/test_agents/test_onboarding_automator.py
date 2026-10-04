"""
Comprehensive agent tests for the OnboardingAutomator module.

Tests cover:
- start_onboarding
- get_onboarding_status
- complete_onboarding_step
"""

import pytest
from unittest.mock import MagicMock, patch, call
from datetime import datetime, timezone

from recruitment_platform.agents.onboarding_automator import (
    OnboardingAutomator,
    OnboardingStep,
    OnboardingStatus,
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
    return db


@pytest.fixture
def mock_llm():
    """Provide a mock LLM client."""
    llm = MagicMock()
    llm.generate = MagicMock(return_value=MagicMock(content="mock response"))
    return llm


@pytest.fixture
def automator(mock_db, mock_llm):
    """Provide an OnboardingAutomator instance with mocked dependencies."""
    return OnboardingAutomator(db=mock_db, llm=mock_llm)


@pytest.fixture
def sample_candidate():
    """Provide a sample candidate dict."""
    return {
        "id": 1,
        "email": "candidate@example.com",
        "first_name": "Jane",
        "last_name": "Doe",
        "role": "Software Engineer",
        "department": "Engineering",
        "start_date": "2026-10-15",
    }


@pytest.fixture
def sample_onboarding_session():
    """Provide a sample onboarding session dict."""
    return {
        "id": 100,
        "candidate_id": 1,
        "status": OnboardingStatus.IN_PROGRESS,
        "current_step": OnboardingStep.PAPERWORK,
        "created_at": datetime(2026, 10, 1, tzinfo=timezone.utc),
        "updated_at": datetime(2026, 10, 1, tzinfo=timezone.utc),
    }


# ---------------------------------------------------------------------------
# Tests: start_onboarding
# ---------------------------------------------------------------------------


class TestStartOnboarding:
    """Tests for OnboardingAutomator.start_onboarding."""

    def test_start_onboarding_success(self, automator, mock_db, sample_candidate):
        """Test that start_onboarding creates a new session successfully."""
        mock_db.add = MagicMock()
        mock_db.flush = MagicMock()

        result = automator.start_onboarding(candidate=sample_candidate)

        assert result is not None
        assert result["candidate_id"] == sample_candidate["id"]
        assert result["status"] == OnboardingStatus.IN_PROGRESS
        assert result["current_step"] == OnboardingStep.PAPERWORK
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    def test_start_onboarding_with_custom_start_step(
        self, automator, mock_db, sample_candidate
    ):
        """Test start_onboarding with a custom initial step."""
        mock_db.add = MagicMock()
        mock_db.flush = MagicMock()

        result = automator.start_onboarding(
            candidate=sample_candidate, initial_step=OnboardingStep.IT_SETUP
        )

        assert result["current_step"] == OnboardingStep.IT_SETUP

    def test_start_onboarding_persists_to_database(
        self, automator, mock_db, sample_candidate
    ):
        """Test that start_onboarding persists the session to the database."""
        mock_db.add = MagicMock()
        mock_db.flush = MagicMock()

        automator.start_onboarding(candidate=sample_candidate)

        # Verify db.add was called with an object containing expected attributes
        added_obj = mock_db.add.call_args[0][0]
        assert added_obj.candidate_id == sample_candidate["id"]
        assert added_obj.status == OnboardingStatus.IN_PROGRESS

    def test_start_onboarding_missing_candidate_id(self, automator):
        """Test that start_onboarding raises ValueError when candidate_id is missing."""
        with pytest.raises(ValueError, match="candidate_id"):
            automator.start_onboarding(candidate={"email": "no-id@example.com"})

    def test_start_onboarding_database_error(
        self, automator, mock_db, sample_candidate
    ):
        """Test that start_onboarding rolls back on database error."""
        mock_db.add = MagicMock()
        mock_db.commit = MagicMock(side_effect=Exception("DB connection lost"))

        with pytest.raises(Exception, match="DB connection lost"):
            automator.start_onboarding(candidate=sample_candidate)

        mock_db.rollback.assert_called_once()

    def test_start_onboarding_returns_session_with_timestamps(
        self, automator, mock_db, sample_candidate
    ):
        """Test that the returned session includes created_at and updated_at."""
        mock_db.add = MagicMock()
        mock_db.flush = MagicMock()

        result = automator.start_onboarding(candidate=sample_candidate)

        assert "created_at" in result
        assert "updated_at" in result
        assert isinstance(result["created_at"], datetime)
        assert isinstance(result["updated_at"], datetime)

    def test_start_onboarding_default_initial_step(
        self, automator, mock_db, sample_candidate
    ):
        """Test that the default initial step is PAPERWORK."""
        mock_db.add = MagicMock()
        mock_db.flush = MagicMock()

        result = automator.start_onboarding(candidate=sample_candidate)

        assert result["current_step"] == OnboardingStep.PAPERWORK


# ---------------------------------------------------------------------------
# Tests: get_onboarding_status
# ---------------------------------------------------------------------------


class TestGetOnboardingStatus:
    """Tests for OnboardingAutomator.get_onboarding_status."""

    def test_get_onboarding_status_success(
        self, automator, mock_db, sample_onboarding_session
    ):
        """Test that get_onboarding_status returns the session when found."""
        mock_query = MagicMock()
        mock_query.filter_by.return_value.first.return_value = MagicMock(
            **sample_onboarding_session
        )
        mock_db.query.return_value = mock_query

        result = automator.get_onboarding_status(session_id=100)

        assert result is not None
        assert result["id"] == 100
        assert result["candidate_id"] == 1
        assert result["status"] == OnboardingStatus.IN_PROGRESS

    def test_get_onboarding_status_not_found(self, automator, mock_db):
        """Test that get_onboarding_status returns None when session not found."""
        mock_query = MagicMock()
        mock_query.filter_by.return_value.first.return_value = None
        mock_db.query.return_value = mock_query

        result = automator.get_onboarding_status(session_id=999)

        assert result is None

    def test_get_onboarding_status_by_candidate(
        self, automator, mock_db, sample_onboarding_session
    ):
        """Test that get_onboarding_status can look up by candidate_id."""
        mock_query = MagicMock()
        mock_query.filter_by.return_value.first.return_value = MagicMock(
            **sample_onboarding_session
        )
        mock_db.query.return_value = mock_query

        result = automator.get_onboarding_status(candidate_id=1)

        assert result is not None
        assert result["candidate_id"] == 1

    def test_get_onboarding_status_completed_session(
        self, automator, mock_db, sample_onboarding_session
    ):
        """Test that get_onboarding_status correctly reports a completed session."""
        sample_onboarding_session["status"] = OnboardingStatus.COMPLETED
        sample_onboarding_session["current_step"] = OnboardingStep.DONE

        mock_query = MagicMock()
        mock_query.filter_by.return_value.first.return_value = MagicMock(
            **sample_onboarding_session
        )
        mock_db.query.return_value = mock_query

        result = automator.get_onboarding_status(session_id=100)

        assert result["status"] == OnboardingStatus.COMPLETED
        assert result["current_step"] == OnboardingStep.DONE

    def test_get_onboarding_status_database_error(self, automator, mock_db):
        """Test that get_onboarding_status propagates database errors."""
        mock_db.query.side_effect = Exception("Query failed")

        with pytest.raises(Exception, match="Query failed"):
            automator.get_onboarding_status(session_id=100)

    def test_get_onboarding_status_includes_all_fields(
        self, automator, mock_db, sample_onboarding_session
    ):
        """Test that the returned status includes all expected fields."""
        mock_query = MagicMock()
        mock_query.filter_by.return_value.first.return_value = MagicMock(
            **sample_onboarding_session
        )
        mock_db.query.return_value = mock_query

        result = automator.get_onboarding_status(session_id=100)

        expected_fields = [
            "id",
            "candidate_id",
            "status",
            "current_step",
            "created_at",
            "updated_at",
        ]
        for field in expected_fields:
            assert field in result, f"Missing field: {field}"


# ---------------------------------------------------------------------------
# Tests: complete_onboarding_step
# ---------------------------------------------------------------------------


class TestCompleteOnboardingStep:
    """Tests for OnboardingAutomator.complete_onboarding_step."""

    def test_complete_onboarding_step_success(
        self, automator, mock_db, sample_onboarding_session
    ):
        """Test that complete_onboarding_step advances the step successfully."""
        mock_session_obj = MagicMock(**sample_onboarding_session)
        mock_query = MagicMock()
        mock_query.filter_by.return_value.first.return_value = mock_session_obj
        mock_db.query.return_value = mock_query

        result = automator.complete_onboarding_step(
            session_id=100, step=OnboardingStep.PAPERWORK
        )

        assert result is not None
        assert result["current_step"] != OnboardingStep.PAPERWORK
        mock_db.commit.assert_called_once()

    def test_complete_onboarding_step_updates_timestamp(
        self, automator, mock_db, sample_onboarding_session
    ):
        """Test that completing a step updates the updated_at timestamp."""
        mock_session_obj = MagicMock(**sample_onboarding_session)
        mock_query = MagicMock()
        mock_query.filter_by.return_value.first.return_value = mock_session_obj
        mock_db.query.return_value = mock_query

        original_updated_at = sample_onboarding_session["updated_at"]

        result = automator.complete_onboarding_step(
            session_id=100, step=OnboardingStep.PAPERWORK
        )

        assert result["updated_at"] >= original_updated_at

    def test_complete_onboarding_step_not_found(self, automator, mock_db):
        """Test that complete_onboarding_step raises when session not found."""
        mock_query = MagicMock()
        mock_query.filter_by.return_value.first.return_value = None
        mock_db.query.return_value = mock_query

        with pytest.raises(ValueError, match="not found"):
            automator.complete_onboarding_step(
                session_id=999, step=OnboardingStep.PAPERWORK
            )

    def test_complete_onboarding_step_wrong_current_step(
        self, automator, mock_db, sample_onboarding_session
    ):
        """Test that completing a step not matching current_step raises error."""
        mock_session_obj = MagicMock(**sample_onboarding_session)
        mock_query = MagicMock()
        mock_query.filter_by.return_value.first.return_value = mock_session_obj
        mock_db.query.return_value = mock_query

        # Try to complete IT_SETUP when current step is PAPERWORK
        with pytest.raises(ValueError, match="step"):
            automator.complete_onboarding_step(
                session_id=100, step=OnboardingStep.IT_SETUP
            )

    def test_complete_onboarding_step_final_step_marks_completed(
        self, automator, mock_db, sample_onboarding_session
    ):
        """Test that completing the final step marks the session as COMPLETED."""
        sample_onboarding_session["current_step"] = OnboardingStep.DONE
        mock_session_obj = MagicMock(**sample_onboarding_session)
        mock_query = MagicMock()
        mock_query.filter_by.return_value.first.return_value = mock_session_obj
        mock_db.query.return_value = mock_query

        result = automator.complete_onboarding_step(
            session_id=100, step=OnboardingStep.DONE
        )

        assert result["status"] == OnboardingStatus.COMPLETED

    def test_complete_onboarding_step_database_error(
        self, automator, mock_db, sample_onboarding_session
    ):
        """Test that complete_onboarding_step rolls back on database error."""
        mock_session_obj = MagicMock(**sample_onboarding_session)
        mock_query = MagicMock()
        mock_query.filter_by.return_value.first.return_value = mock_session_obj
        mock_db.query.return_value = mock_query
        mock_db.commit = MagicMock(side_effect=Exception("Commit failed"))

        with pytest.raises(Exception, match="Commit failed"):
            automator.complete_onboarding_step(
                session_id=100, step=OnboardingStep.PAPERWORK
            )

        mock_db.rollback.assert_called_once()

    def test_complete_onboarding_step_persists_changes(
        self, automator, mock_db, sample_onboarding_session
    ):
        """Test that the step completion is persisted to the database."""
        mock_session_obj = MagicMock(**sample_onboarding_session)
        mock_query = MagicMock()
        mock_query.filter_by.return_value.first.return_value = mock_session_obj
        mock_db.query.return_value = mock_query

        automator.complete_onboarding_step(
            session_id=100, step=OnboardingStep.PAPERWORK
        )

        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_complete_onboarding_step_returns_updated_session(
        self, automator, mock_db, sample_onboarding_session
    ):
        """Test that the returned session reflects the new step."""
        mock_session_obj = MagicMock(**sample_onboarding_session)
        mock_query = MagicMock()
        mock_query.filter_by.return_value.first.return_value = mock_session_obj
        mock_db.query.return_value = mock_query

        result = automator.complete_onboarding_step(
            session_id=100, step=OnboardingStep.PAPERWORK
        )

        assert result["id"] == 100
        assert result["candidate_id"] == 1
        assert result["status"] == OnboardingStatus.IN_PROGRESS
