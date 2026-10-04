"""
Comprehensive agent tests for the Interview Scheduler module.

Tests cover:
- schedule_interview: creating new interviews
- reschedule_interview: moving existing interviews
- cancel_interview: cancelling interviews
"""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch, ANY
from uuid import uuid4

from recruitment_platform.agents.interview_scheduler import (
    schedule_interview,
    reschedule_interview,
    cancel_interview,
    InterviewSchedulerError,
    InterviewConflictError,
    InterviewNotFoundError,
    InvalidInterviewDataError,
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
def mock_notification_service():
    """Provide a mock notification service."""
    service = MagicMock()
    service.send_invitation = MagicMock(return_value={"status": "sent"})
    service.send_update = MagicMock(return_value={"status": "sent"})
    service.send_cancellation = MagicMock(return_value={"status": "sent"})
    return service


@pytest.fixture
def mock_calendar_service():
    """Provide a mock calendar service."""
    service = MagicMock()
    service.create_event = MagicMock(return_value={"event_id": "cal-123"})
    service.update_event = MagicMock(return_value={"event_id": "cal-123"})
    service.delete_event = MagicMock(return_value={"status": "deleted"})
    return service


@pytest.fixture
def sample_candidate():
    """Provide a sample candidate dict."""
    return {
        "id": str(uuid4()),
        "name": "Jane Doe",
        "email": "jane.doe@example.com",
        "phone": "+1-555-0100",
    }


@pytest.fixture
def sample_interviewer():
    """Provide a sample interviewer dict."""
    return {
        "id": str(uuid4()),
        "name": "John Smith",
        "email": "john.smith@example.com",
        "department": "Engineering",
    }


@pytest.fixture
def sample_job():
    """Provide a sample job dict."""
    return {
        "id": str(uuid4()),
        "title": "Senior Software Engineer",
        "department": "Engineering",
        "location": "Remote",
    }


@pytest.fixture
def valid_interview_data(sample_candidate, sample_interviewer, sample_job):
    """Provide valid data for scheduling an interview."""
    return {
        "candidate_id": sample_candidate["id"],
        "interviewer_id": sample_interviewer["id"],
        "job_id": sample_job["id"],
        "scheduled_at": datetime.now(timezone.utc) + timedelta(days=2),
        "duration_minutes": 60,
        "interview_type": "technical",
        "location": "Video Call",
        "notes": "First round technical interview",
    }


@pytest.fixture
def existing_interview(valid_interview_data):
    """Provide an existing interview record."""
    return {
        "id": str(uuid4()),
        **valid_interview_data,
        "status": "scheduled",
        "created_at": datetime.now(timezone.utc) - timedelta(days=1),
        "updated_at": datetime.now(timezone.utc) - timedelta(days=1),
    }


# ---------------------------------------------------------------------------
# Tests: schedule_interview
# ---------------------------------------------------------------------------


class TestScheduleInterview:
    """Tests for the schedule_interview function."""

    def test_schedule_interview_success(
        self,
        mock_db,
        mock_notification_service,
        mock_calendar_service,
        valid_interview_data,
    ):
        """Successfully schedule an interview with valid data."""
        result = schedule_interview(
            db=mock_db,
            notification_service=mock_notification_service,
            calendar_service=mock_calendar_service,
            **valid_interview_data,
        )

        assert result is not None
        assert result["status"] == "scheduled"
        assert result["candidate_id"] == valid_interview_data["candidate_id"]
        assert result["interviewer_id"] == valid_interview_data["interviewer_id"]
        assert result["job_id"] == valid_interview_data["job_id"]
        assert result["duration_minutes"] == 60
        assert result["interview_type"] == "technical"
        assert "id" in result

    def test_schedule_interview_creates_calendar_event(
        self,
        mock_db,
        mock_notification_service,
        mock_calendar_service,
        valid_interview_data,
    ):
        """Verify a calendar event is created when scheduling."""
        schedule_interview(
            db=mock_db,
            notification_service=mock_notification_service,
            calendar_service=mock_calendar_service,
            **valid_interview_data,
        )

        mock_calendar_service.create_event.assert_called_once()
        call_kwargs = mock_calendar_service.create_event.call_args
        assert call_kwargs.kwargs["title"] == "Interview: technical"
        assert call_kwargs.kwargs["start_time"] == valid_interview_data["scheduled_at"]

    def test_schedule_interview_sends_notification(
        self,
        mock_db,
        mock_notification_service,
        mock_calendar_service,
        valid_interview_data,
    ):
        """Verify notification is sent after scheduling."""
        schedule_interview(
            db=mock_db,
            notification_service=mock_notification_service,
            calendar_service=mock_calendar_service,
            **valid_interview_data,
        )

        mock_notification_service.send_invitation.assert_called_once()

    def test_schedule_interview_persists_to_db(
        self,
        mock_db,
        mock_notification_service,
        mock_calendar_service,
        valid_interview_data,
    ):
        """Verify the interview is persisted to the database."""
        schedule_interview(
            db=mock_db,
            notification_service=mock_notification_service,
            calendar_service=mock_calendar_service,
            **valid_interview_data,
        )

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_schedule_interview_missing_candidate_id_raises_error(
        self,
        mock_db,
        mock_notification_service,
        mock_calendar_service,
        valid_interview_data,
    ):
        """Raise error when candidate_id is missing."""
        del valid_interview_data["candidate_id"]

        with pytest.raises(InvalidInterviewDataError, match="candidate_id"):
            schedule_interview(
                db=mock_db,
                notification_service=mock_notification_service,
                calendar_service=mock_calendar_service,
                **valid_interview_data,
            )

    def test_schedule_interview_missing_interviewer_id_raises_error(
        self,
        mock_db,
        mock_notification_service,
        mock_calendar_service,
        valid_interview_data,
    ):
        """Raise error when interviewer_id is missing."""
        del valid_interview_data["interviewer_id"]

        with pytest.raises(InvalidInterviewDataError, match="interviewer_id"):
            schedule_interview(
                db=mock_db,
                notification_service=mock_notification_service,
                calendar_service=mock_calendar_service,
                **valid_interview_data,
            )

    def test_schedule_interview_missing_scheduled_at_raises_error(
        self,
        mock_db,
        mock_notification_service,
        mock_calendar_service,
        valid_interview_data,
    ):
        """Raise error when scheduled_at is missing."""
        del valid_interview_data["scheduled_at"]

        with pytest.raises(InvalidInterviewDataError, match="scheduled_at"):
            schedule_interview(
                db=mock_db,
                notification_service=mock_notification_service,
                calendar_service=mock_calendar_service,
                **valid_interview_data,
            )

    def test_schedule_interview_past_date_raises_error(
        self,
        mock_db,
        mock_notification_service,
        mock_calendar_service,
        valid_interview_data,
    ):
        """Raise error when scheduled_at is in the past."""
        valid_interview_data["scheduled_at"] = datetime.now(timezone.utc) - timedelta(hours=1)

        with pytest.raises(InvalidInterviewDataError, match="past"):
            schedule_interview(
                db=mock_db,
                notification_service=mock_notification_service,
                calendar_service=mock_calendar_service,
                **valid_interview_data,
            )

    def test_schedule_interview_conflict_raises_error(
        self,
        mock_db,
        mock_notification_service,
        mock_calendar_service,
        valid_interview_data,
    ):
        """Raise InterviewConflictError when there is a scheduling conflict."""
        mock_db.query.return_value.filter.return_value.first.return_value = {
            "id": "existing-interview-id",
            "status": "scheduled",
        }

        with pytest.raises(InterviewConflictError):
            schedule_interview(
                db=mock_db,
                notification_service=mock_notification_service,
                calendar_service=mock_calendar_service,
                **valid_interview_data,
            )

    def test_schedule_interview_db_error_rolls_back(
        self,
        mock_db,
        mock_notification_service,
        mock_calendar_service,
        valid_interview_data,
    ):
        """Verify rollback on database error."""
        mock_db.commit.side_effect = Exception("DB connection lost")

        with pytest.raises(InterviewSchedulerError):
            schedule_interview(
                db=mock_db,
                notification_service=mock_notification_service,
                calendar_service=mock_calendar_service,
                **valid_interview_data,
            )

        mock_db.rollback.assert_called_once()

    def test_schedule_interview_with_custom_duration(
        self,
        mock_db,
        mock_notification_service,
        mock_calendar_service,
        valid_interview_data,
    ):
        """Schedule interview with a custom duration."""
        valid_interview_data["duration_minutes"] = 90

        result = schedule_interview(
            db=mock_db,
            notification_service=mock_notification_service,
            calendar_service=mock_calendar_service,
            **valid_interview_data,
        )

        assert result["duration_minutes"] == 90

    def test_schedule_interview_with_notes(
        self,
        mock_db,
        mock_notification_service,
        mock_calendar_service,
        valid_interview_data,
    ):
        """Schedule interview with notes."""
        valid_interview_data["notes"] = "Candidate prefers morning slots"

        result = schedule_interview(
            db=mock_db,
            notification_service=mock_notification_service,
            calendar_service=mock_calendar_service,
            **valid_interview_data,
        )

        assert result["notes"] == "Candidate prefers morning slots"

    def test_schedule_interview_default_duration(
        self,
        mock_db,
        mock_notification_service,
        mock_calendar_service,
        valid_interview_data,
    ):
        """Verify default duration is applied when not specified."""
        del valid_interview_data["duration_minutes"]

        result = schedule_interview(
            db=mock_db,
            notification_service=mock_notification_service,
            calendar_service=mock_calendar_service,
            **valid_interview_data,
        )

        assert result["duration_minutes"] == 60

    def test_schedule_interview_multiple_types(
        self,
        mock_db,
        mock_notification_service,
        mock_calendar_service,
        valid_interview_data,
    ):
        """Schedule interviews of different types."""
        interview_types = ["technical", "behavioral", "hr", "final"]

        for itype in interview_types:
            valid_interview_data["interview_type"] = itype
            result = schedule_interview(
                db=mock_db,
                notification_service=mock_notification_service,
                calendar_service=mock_calendar_service,
                **valid_interview_data,
            )
            assert result["interview_type"] == itype


# ---------------------------------------------------------------------------
# Tests: reschedule_interview
# ---------------------------------------------------------------------------


class TestRescheduleInterview:
    """Tests for the reschedule_interview function."""

    def test_reschedule_interview_success(
        self,
        mock_db,
        mock_notification_service,
        mock_calendar_service,
        existing_interview,
    ):
        """Successfully reschedule an existing interview."""
        new_time = datetime.now(timezone.utc) + timedelta(days=5)
        mock_db.query.return_value.filter.return_value.first.return_value = existing_interview

        result = reschedule_interview(
            db=mock_db,
            notification_service=mock_notification_service,
            calendar_service=mock_calendar_service,
            interview_id=existing_interview["id"],
            new_scheduled_at=new_time,
        )

        assert result is not None
        assert result["id"] == existing_interview["id"]
        assert result["scheduled_at"] == new_time
        assert result["status"] == "scheduled"

    def test_reschedule_interview_updates_calendar(
        self,
        mock_db,
        mock_notification_service,
        mock_calendar_service,
        existing_interview,
    ):
        """Verify calendar event is updated on reschedule."""
        new_time = datetime.now(timezone.utc) + timedelta(days=5)
        mock_db.query.return_value.filter.return_value.first.return_value = existing_interview

        reschedule_interview(
            db=mock_db,
            notification_service=mock_notification_service,
            calendar_service=mock_calendar_service,
            interview_id=existing_interview["id"],
            new_scheduled_at=new_time,
        )

        mock_calendar_service.update_event.assert_called_once()

    def test_reschedule_interview_sends_update_notification(
        self,
        mock_db,
        mock_notification_service,
        mock_calendar_service,
        existing_interview,
    ):
        """Verify update notification is sent on reschedule."""
        new_time = datetime.now(timezone.utc) + timedelta(days=5)
        mock_db.query.return_value.filter.return_value.first.return_value = existing_interview

        reschedule_interview(
            db=mock_db,
            notification_service=mock_notification_service,
            calendar_service=mock_calendar_service,
            interview_id=existing_interview["id"],
            new_scheduled_at=new_time,
        )

        mock_notification_service.send_update.assert_called_once()

    def test_reschedule_interview_not_found_raises_error(
        self,
        mock_db,
        mock_notification_service,
        mock_calendar_service,
    ):
        """Raise InterviewNotFoundError when interview does not exist."""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(InterviewNotFoundError):
            reschedule_interview(
                db=mock_db,
                notification_service=mock_notification_service,
                calendar_service=mock_calendar_service,
                interview_id=str(uuid4()),
                new_scheduled_at=datetime.now(timezone.utc) + timedelta(days=3),
            )

    def test_reschedule_interview_past_date_raises_error(
        self,
        mock_db,
        mock_notification_service,
        mock_calendar_service,
        existing_interview,
    ):
        """Raise error when new time is in the past."""
        mock_db.query.return_value.filter.return_value.first.return_value = existing_interview
        past_time = datetime.now(timezone.utc) - timedelta(hours=2)

        with pytest.raises(InvalidInterviewDataError, match="past"):
            reschedule_interview(
                db=mock_db,
                notification_service=mock_notification_service,
                calendar_service=mock_calendar_service,
                interview_id=existing_interview["id"],
                new_scheduled_at=past_time,
            )

    def test_reschedule_interview_cancelled_raises_error(
        self,
        mock_db,
        mock_notification_service,
        mock_calendar_service,
        existing_interview,
    ):
        """Raise error when trying to reschedule a cancelled interview."""
        existing_interview["status"] = "cancelled"
        mock_db.query.return_value.filter.return_value.first.return_value = existing_interview

        with pytest.raises(InterviewSchedulerError, match="cancelled"):
            reschedule_interview(
                db=mock_db,
                notification_service=mock_notification_service,
                calendar_service=mock_calendar_service,
                interview_id=existing_interview["id"],
                new_scheduled_at=datetime.now(timezone.utc) + timedelta(days=3),
            )

    def test_reschedule_interview_completed_raises_error(
        self,
        mock_db,
        mock_notification_service,
        mock_calendar_service,
        existing_interview,
    ):
        """Raise error when trying to reschedule a completed interview."""
        existing_interview["status"] = "completed"
        mock_db.query.return_value.filter.return_value.first.return_value = existing_interview

        with pytest.raises(InterviewSchedulerError, match="completed"):
            reschedule_interview(
                db=mock_db,
                notification_service=mock_notification_service,
                calendar_service=mock_calendar_service,
                interview_id=existing_interview["id"],
                new_scheduled_at=datetime.now(timezone.utc) + timedelta(days=3),
            )

    def test_reschedule_interview_conflict_raises_error(
        self,
        mock_db,
        mock_notification_service,
        mock_calendar_service,
        existing_interview,
    ):
        """Raise InterviewConflictError when new time conflicts."""
        existing_interview["status"] = "scheduled"
        mock_db.query.return_value.filter.return_value.first.return_value = existing_interview
        # Simulate a conflict on the second query (conflict check)
        mock_db.query.return_value.filter.return_value.all.return_value = [
            {"id": "conflicting-id", "status": "scheduled"}
        ]

        with pytest.raises(InterviewConflictError):
            reschedule_interview(
                db=mock_db,
                notification_service=mock_notification_service,
                calendar_service=mock_calendar_service,
                interview_id=existing_interview["id"],
                new_scheduled_at=datetime.now(timezone.utc) + timedelta(days=3),
            )

    def test_reschedule_interview_updates_db(
        self,
        mock_db,
        mock_notification_service,
        mock_calendar_service,
        existing_interview,
    ):
        """Verify database is updated on reschedule."""
        new_time = datetime.now(timezone.utc) + timedelta(days=5)
        mock_db.query.return_value.filter.return_value.first.return_value = existing_interview

        reschedule_interview(
            db=mock_db,
            notification_service=mock_notification_service,
            calendar_service=mock_calendar_service,
            interview_id=existing_interview["id"],
            new_scheduled_at=new_time,
        )

        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_reschedule_interview_with_new_duration(
        self,
        mock_db,
        mock_notification_service,
        mock_calendar_service,
        existing_interview,
    ):
        """Reschedule with a new duration."""
        new_time = datetime.now(timezone.utc) + timedelta(days=5)
        mock_db.query.return_value.filter.return_value.first.return_value = existing_interview

        result = reschedule_interview(
            db=mock_db,
            notification_service=mock_notification_service,
            calendar_service=mock_calendar_service,
            interview_id=existing_interview["id"],
            new_scheduled_at=new_time,
            new_duration_minutes=90,
        )

        assert result["duration_minutes"] == 90

    def test_reschedule_interview_db_error_rolls_back(
        self,
        mock_db,
        mock_notification_service,
        mock_calendar_service,
        existing_interview,
    ):
        """Verify rollback on database error during reschedule."""
        new_time = datetime.now(timezone.utc) + timedelta(days=5)
        mock_db.query.return_value.filter.return_value.first.return_value = existing_interview
        mock_db.commit.side_effect = Exception("DB error")

        with pytest.raises(InterviewSchedulerError):
            reschedule_interview(
                db=mock_db,
                notification_service=mock_notification_service,
                calendar_service=mock_calendar_service,
                interview_id=existing_interview["id"],
                new_scheduled_at=new_time,
            )

        mock_db.rollback.assert_called_once()


# ---------------------------------------------------------------------------
# Tests: cancel_interview
# ---------------------------------------------------------------------------


class TestCancelInterview:
    """Tests for the cancel_interview function."""

    def test_cancel_interview_success(
        self,
        mock_db,
        mock_notification_service,
        mock_calendar_service,
        existing_interview,
    ):
        """Successfully cancel an existing interview."""
        mock_db.query.return_value.filter.return_value.first.return_value = existing_interview

        result = cancel_interview(
            db=mock_db,
            notification_service=mock_notification_service,
            calendar_service=mock_calendar_service,
            interview_id=existing_interview["id"],
            reason="Candidate requested reschedule",
        )

        assert result is not None
        assert result["id"] == existing_interview["id"]
        assert result["status"] == "cancelled"

    def test_cancel_interview_deletes_calendar_event(
        self,
        mock_db,
        mock_notification_service,
        mock_calendar_service,
        existing_interview,
    ):
        """Verify calendar event is deleted on cancel."""
        mock_db.query.return_value.filter.return_value.first.return_value = existing_interview

        cancel_interview(
            db=mock_db,
            notification_service=mock_notification_service,
            calendar_service=mock_calendar_service,
            interview_id=existing_interview["id"],
        )

        mock_calendar_service.delete_event.assert_called_once()

    def test_cancel_interview_sends_cancellation_notification(
        self,
        mock_db,
        mock_notification_service,
        mock_calendar_service,
        existing_interview,
    ):
        """Verify cancellation notification is sent."""
        mock_db.query.return_value.filter.return_value.first.return_value = existing_interview

        cancel_interview(
            db=mock_db,
            notification_service=mock_notification_service,
            calendar_service=mock_calendar_service,
            interview_id=existing_interview["id"],
            reason="Interviewer unavailable",
        )

        mock_notification_service.send_cancellation.assert_called_once()

    def test_cancel_interview_not_found_raises_error(
        self,
        mock_db,
        mock_notification_service,
        mock_calendar_service,
    ):
        """Raise InterviewNotFoundError when interview does not exist."""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(InterviewNotFoundError):
            cancel_interview(
                db=mock_db,
                notification_service=mock_notification_service,
                calendar_service=mock_calendar_service,
                interview_id=str(uuid4()),
            )

    def test_cancel_interview_already_cancelled_raises_error(
        self,
        mock_db,
        mock_notification_service,
        mock_calendar_service,
        existing_interview,
    ):
        """Raise error when trying to cancel an already cancelled interview."""
        existing_interview["status"] = "cancelled"
        mock_db.query.return_value.filter.return_value.first.return_value = existing_interview

        with pytest.raises(InterviewSchedulerError, match="already cancelled"):
            cancel_interview(
                db=mock_db,
                notification_service=mock_notification_service,
                calendar_service=mock_calendar_service,
                interview_id=existing_interview["id"],
            )

    def test_cancel_interview_completed_raises_error(
        self,
        mock_db,
        mock_notification_service,
        mock_calendar_service,
        existing_interview,
    ):
        """Raise error when trying to cancel a completed interview."""
        existing_interview["status"] = "completed"
        mock_db.query.return_value.filter.return_value.first.return_value = existing_interview

        with pytest.raises(InterviewSchedulerError, match="completed"):
            cancel_interview(
                db=mock_db,
                notification_service=mock_notification_service,
                calendar_service=mock_calendar_service,
                interview_id=existing_interview["id"],
            )

    def test_cancel_interview_updates_db(
        self,
        mock_db,
        mock_notification_service,
        mock_calendar_service,
        existing_interview,
    ):
        """Verify database is updated on cancel."""
        mock_db.query.return_value.filter.return_value.first.return_value = existing_interview

        cancel_interview(
            db=mock_db,
            notification_service=mock_notification_service,
            calendar_service=mock_calendar_service,
            interview_id=existing_interview["id"],
        )

        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_cancel_interview_without_reason(
        self,
        mock_db,
        mock_notification_service,
        mock_calendar_service,
        existing_interview,
    ):
        """Cancel interview without providing a reason."""
        mock_db.query.return_value.filter.return_value.first.return_value = existing_interview

        result = cancel_interview(
            db=mock_db,
            notification_service=mock_notification_service,
            calendar_service=mock_calendar_service,
            interview_id=existing_interview["id"],
        )

        assert result["status"] == "cancelled"

    def test_cancel_interview_db_error_rolls_back(
        self,
        mock_db,
        mock_notification_service,
        mock_calendar_service,
        existing_interview,
    ):
        """Verify rollback on database error during cancel."""
        mock_db.query.return_value.filter.return_value.first.return_value = existing_interview
        mock_db.commit.side_effect = Exception("DB error")

        with pytest.raises(InterviewSchedulerError):
            cancel_interview(
                db=mock_db,
                notification_service=mock_notification_service,
                calendar_service=mock_calendar_service,
                interview_id=existing_interview["id"],
            )

        mock_db.rollback.assert_called_once()

    def test_cancel_interview_notification_includes_reason(
        self,
        mock_db,
        mock_notification_service,
        mock_calendar_service,
        existing_interview,
    ):
        """Verify cancellation notification includes the reason."""
        mock_db.query.return_value.filter.return_value.first.return_value = existing_interview
        reason = "Candidate has another offer"

        cancel_interview(
            db=mock_db,
            notification_service=mock_notification_service,
            calendar_service=mock_calendar_service,
            interview_id=existing_interview["id"],
            reason=reason,
        )

        call_kwargs = mock_notification_service.send_cancellation.call_args
        assert reason in str(call_kwargs)
