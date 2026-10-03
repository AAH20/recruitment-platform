"""Comprehensive tests for the Interview service layer."""

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest

from src.recruitment_platform.models.interview import (
    Interview,
    InterviewStatus,
    InterviewType,
)
from src.recruitment_platform.services.interview_service import (
    InterviewService,
    InterviewNotFoundError,
    InvalidInterviewStateError,
    InterviewConflictError,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_repository():
    """Provide a fresh mock repository for each test."""
    return MagicMock()


@pytest.fixture
def service(mock_repository):
    """Provide an InterviewService wired to the mock repository."""
    return InterviewService(repository=mock_repository)


@pytest.fixture
def sample_interview():
    """Return a fully-populated Interview instance."""
    now = datetime.now(timezone.utc)
    return Interview(
        id="int-001",
        application_id="app-001",
        candidate_id="cand-001",
        job_id="job-001",
        interviewer_id="emp-001",
        scheduled_at=now + timedelta(days=2),
        duration_minutes=60,
        interview_type=InterviewType.TECHNICAL,
        status=InterviewStatus.SCHEDULED,
        location="Conference Room A",
        meeting_link="https://meet.example.com/abc",
        notes="Technical screening — algorithms round",
        created_at=now,
        updated_at=now,
    )


@pytest.fixture
def sample_interview_dict(sample_interview):
    """Return a dict representation of the sample interview."""
    return {
        "id": sample_interview.id,
        "application_id": sample_interview.application_id,
        "candidate_id": sample_interview.candidate_id,
        "job_id": sample_interview.job_id,
        "interviewer_id": sample_interview.interviewer_id,
        "scheduled_at": sample_interview.scheduled_at.isoformat(),
        "duration_minutes": sample_interview.duration_minutes,
        "interview_type": sample_interview.interview_type.value,
        "status": sample_interview.status.value,
        "location": sample_interview.location,
        "meeting_link": sample_interview.meeting_link,
        "notes": sample_interview.notes,
        "created_at": sample_interview.created_at.isoformat(),
        "updated_at": sample_interview.updated_at.isoformat(),
    }


# ---------------------------------------------------------------------------
# 1. get_interview
# ---------------------------------------------------------------------------


class TestGetInterview:
    """Tests for InterviewService.get_interview."""

    def test_get_interview_returns_interview(self, service, mock_repository, sample_interview):
        """get_interview returns the interview when found."""
        mock_repository.get_by_id.return_value = sample_interview

        result = service.get_interview("int-001")

        assert result is not None
        assert result.id == "int-001"
        assert result.application_id == "app-001"
        assert result.candidate_id == "cand-001"
        assert result.status == InterviewStatus.SCHEDULED
        mock_repository.get_by_id.assert_called_once_with("int-001")

    def test_get_interview_not_found_raises(self, service, mock_repository):
        """get_interview raises InterviewNotFoundError when the interview does not exist."""
        mock_repository.get_by_id.return_value = None

        with pytest.raises(InterviewNotFoundError, match="int-999"):
            service.get_interview("int-999")

        mock_repository.get_by_id.assert_called_once_with("int-999")

    def test_get_interview_repository_exception_propagates(self, service, mock_repository):
        """get_interview propagates unexpected repository exceptions."""
        mock_repository.get_by_id.side_effect = RuntimeError("DB connection lost")

        with pytest.raises(RuntimeError, match="DB connection lost"):
            service.get_interview("int-001")

    def test_get_interview_with_different_ids(self, service, mock_repository, sample_interview):
        """get_interview works with various ID formats."""
        mock_repository.get_by_id.return_value = sample_interview

        for interview_id in ["abc", "123", "interview-xyz-789"]:
            result = service.get_interview(interview_id)
            assert result.id == "int-001"
            mock_repository.get_by_id.assert_called_with(interview_id)


# ---------------------------------------------------------------------------
# 2. list_interviews
# ---------------------------------------------------------------------------


class TestListInterviews:
    """Tests for InterviewService.list_interviews with various filters."""

    def test_list_interviews_returns_all(self, service, mock_repository, sample_interview):
        """list_interviews without filters returns all interviews."""
        interviews = [sample_interview, sample_interview]
        mock_repository.list.return_value = interviews

        result = service.list_interviews()

        assert len(result) == 2
        mock_repository.list.assert_called_once()

    def test_list_interviews_empty_result(self, service, mock_repository):
        """list_interviews returns an empty list when no interviews exist."""
        mock_repository.list.return_value = []

        result = service.list_interviews()

        assert result == []

    def test_list_interviews_filter_by_status(self, service, mock_repository, sample_interview):
        """list_interviews filters by status correctly."""
        mock_repository.list.return_value = [sample_interview]

        result = service.list_interviews(status=InterviewStatus.SCHEDULED)

        assert len(result) == 1
        assert result[0].status == InterviewStatus.SCHEDULED
        mock_repository.list.assert_called_once()
        call_kwargs = mock_repository.list.call_args
        assert call_kwargs.kwargs.get("status") == InterviewStatus.SCHEDULED or \
               (call_kwargs.args and call_kwargs.args[0] == InterviewStatus.SCHEDULED)

    def test_list_interviews_filter_by_candidate(self, service, mock_repository, sample_interview):
        """list_interviews filters by candidate_id correctly."""
        mock_repository.list.return_value = [sample_interview]

        result = service.list_interviews(candidate_id="cand-001")

        assert len(result) == 1
        assert result[0].candidate_id == "cand-001"

    def test_list_interviews_filter_by_job(self, service, mock_repository, sample_interview):
        """list_interviews filters by job_id correctly."""
        mock_repository.list.return_value = [sample_interview]

        result = service.list_interviews(job_id="job-001")

        assert len(result) == 1
        assert result[0].job_id == "job-001"

    def test_list_interviews_filter_by_interviewer(self, service, mock_repository, sample_interview):
        """list_interviews filters by interviewer_id correctly."""
        mock_repository.list.return_value = [sample_interview]

        result = service.list_interviews(interviewer_id="emp-001")

        assert len(result) == 1
        assert result[0].interviewer_id == "emp-001"

    def test_list_interviews_filter_by_application(self, service, mock_repository, sample_interview):
        """list_interviews filters by application_id correctly."""
        mock_repository.list.return_value = [sample_interview]

        result = service.list_interviews(application_id="app-001")

        assert len(result) == 1
        assert result[0].application_id == "app-001"

    def test_list_interviews_filter_by_type(self, service, mock_repository, sample_interview):
        """list_interviews filters by interview_type correctly."""
        mock_repository.list.return_value = [sample_interview]

        result = service.list_interviews(interview_type=InterviewType.TECHNICAL)

        assert len(result) == 1
        assert result[0].interview_type == InterviewType.TECHNICAL

    def test_list_interviews_with_multiple_filters(self, service, mock_repository, sample_interview):
        """list_interviews applies multiple filters simultaneously."""
        mock_repository.list.return_value = [sample_interview]

        result = service.list_interviews(
            status=InterviewStatus.SCHEDULED,
            candidate_id="cand-001",
            job_id="job-001",
        )

        assert len(result) == 1
        mock_repository.list.assert_called_once()

    def test_list_interviews_with_date_range(self, service, mock_repository, sample_interview):
        """list_interviews filters by date range."""
        mock_repository.list.return_value = [sample_interview]
        start = datetime.now(timezone.utc)
        end = start + timedelta(days=7)

        result = service.list_interviews(start_date=start, end_date=end)

        assert len(result) == 1

    def test_list_interviews_pagination(self, service, mock_repository, sample_interview):
        """list_interviews supports pagination via limit and offset."""
        mock_repository.list.return_value = [sample_interview]

        result = service.list_interviews(limit=10, offset=0)

        assert len(result) == 1
        call_kwargs = mock_repository.list.call_args.kwargs
        assert call_kwargs.get("limit") == 10
        assert call_kwargs.get("offset") == 0

    def test_list_interviews_repository_exception(self, service, mock_repository):
        """list_interviews propagates repository exceptions."""
        mock_repository.list.side_effect = RuntimeError("DB error")

        with pytest.raises(RuntimeError, match="DB error"):
            service.list_interviews()


# ---------------------------------------------------------------------------
# 3. schedule_interview
# ---------------------------------------------------------------------------


class TestScheduleInterview:
    """Tests for InterviewService.schedule_interview."""

    def test_schedule_interview_creates_and_returns(self, service, mock_repository, sample_interview):
        """schedule_interview creates a new interview and returns it."""
        mock_repository.create.return_value = sample_interview

        result = service.schedule_interview(
            application_id="app-001",
            candidate_id="cand-001",
            job_id="job-001",
            interviewer_id="emp-001",
            scheduled_at=sample_interview.scheduled_at,
            duration_minutes=60,
            interview_type=InterviewType.TECHNICAL,
            location="Conference Room A",
            meeting_link="https://meet.example.com/abc",
            notes="Technical screening",
        )

        assert result is not None
        assert result.id == "int-001"
        assert result.status == InterviewStatus.SCHEDULED
        mock_repository.create.assert_called_once()

    def test_schedule_interview_sets_default_status(self, service, mock_repository, sample_interview):
        """schedule_interview sets status to SCHEDULED by default."""
        mock_repository.create.return_value = sample_interview

        result = service.schedule_interview(
            application_id="app-001",
            candidate_id="cand-001",
            job_id="job-001",
            interviewer_id="emp-001",
            scheduled_at=datetime.now(timezone.utc) + timedelta(days=1),
            duration_minutes=30,
            interview_type=InterviewType.PHONE,
        )

        assert result.status == InterviewStatus.SCHEDULED

    def test_schedule_interview_past_date_raises(self, service, mock_repository):
        """schedule_interview raises when scheduled_at is in the past."""
        past = datetime.now(timezone.utc) - timedelta(hours=1)

        with pytest.raises(ValueError, match="past"):
            service.schedule_interview(
                application_id="app-001",
                candidate_id="cand-001",
                job_id="job-001",
                interviewer_id="emp-001",
                scheduled_at=past,
                duration_minutes=60,
                interview_type=InterviewType.TECHNICAL,
            )

    def test_schedule_interview_conflict_raises(self, service, mock_repository, sample_interview):
        """schedule_interview raises InterviewConflictError on scheduling conflict."""
        mock_repository.has_conflict.return_value = True

        with pytest.raises(InterviewConflictError):
            service.schedule_interview(
                application_id="app-001",
                candidate_id="cand-001",
                job_id="job-001",
                interviewer_id="emp-001",
                scheduled_at=datetime.now(timezone.utc) + timedelta(days=1),
                duration_minutes=60,
                interview_type=InterviewType.TECHNICAL,
            )

    def test_schedule_interview_repository_exception(self, service, mock_repository):
        """schedule_interview propagates repository exceptions."""
        mock_repository.create.side_effect = RuntimeError("DB error")

        with pytest.raises(RuntimeError, match="DB error"):
            service.schedule_interview(
                application_id="app-001",
                candidate_id="cand-001",
                job_id="job-001",
                interviewer_id="emp-001",
                scheduled_at=datetime.now(timezone.utc) + timedelta(days=1),
                duration_minutes=60,
                interview_type=InterviewType.TECHNICAL,
            )

    def test_schedule_interview_with_all_optional_fields(self, service, mock_repository, sample_interview):
        """schedule_interview accepts all optional fields."""
        mock_repository.create.return_value = sample_interview

        result = service.schedule_interview(
            application_id="app-001",
            candidate_id="cand-001",
            job_id="job-001",
            interviewer_id="emp-001",
            scheduled_at=datetime.now(timezone.utc) + timedelta(days=3),
            duration_minutes=90,
            interview_type=InterviewType.ONSITE,
            location="Building B, Room 204",
            meeting_link="https://meet.example.com/xyz",
            notes="Final round — system design",
        )

        assert result is not None
        assert result.duration_minutes == 60  # from sample_interview mock
        mock_repository.create.assert_called_once()


# ---------------------------------------------------------------------------
# 4. update_interview
# ---------------------------------------------------------------------------


class TestUpdateInterview:
    """Tests for InterviewService.update_interview."""

    def test_update_interview_returns_updated(self, service, mock_repository, sample_interview):
        """update_interview returns the updated interview."""
        updated = Interview(
            **{**sample_interview.__dict__, "notes": "Updated notes", "duration_minutes": 90}
        )
        mock_repository.update.return_value = updated

        result = service.update_interview("int-001", notes="Updated notes", duration_minutes=90)

        assert result is not None
        assert result.notes == "Updated notes"
        assert result.duration_minutes == 90
        mock_repository.update.assert_called_once()

    def test_update_interview_not_found_raises(self, service, mock_repository):
        """update_interview raises InterviewNotFoundError when interview doesn't exist."""
        mock_repository.update.return_value = None

        with pytest.raises(InterviewNotFoundError, match="int-999"):
            service.update_interview("int-999", notes="New notes")

    def test_update_interview_status_transition(self, service, mock_repository, sample_interview):
        """update_interview allows valid status transitions."""
        updated = Interview(
            **{**sample_interview.__dict__, "status": InterviewStatus.COMPLETED}
        )
        mock_repository.update.return_value = updated

        result = service.update_interview("int-001", status=InterviewStatus.COMPLETED)

        assert result.status == InterviewStatus.COMPLETED

    def test_update_interview_invalid_status_transition_raises(self, service, mock_repository, sample_interview):
        """update_interview raises on invalid status transitions."""
        mock_repository.get_by_id.return_value = sample_interview

        with pytest.raises(InvalidInterviewStateError):
            service.update_interview("int-001", status=InterviewStatus.SCHEDULED)

    def test_update_interview_reschedule(self, service, mock_repository, sample_interview):
        """update_interview can reschedule the interview."""
        new_time = datetime.now(timezone.utc) + timedelta(days=5)
        updated = Interview(
            **{**sample_interview.__dict__, "scheduled_at": new_time}
        )
        mock_repository.update.return_value = updated

        result = service.update_interview("int-001", scheduled_at=new_time)

        assert result.scheduled_at == new_time

    def test_update_interview_repository_exception(self, service, mock_repository):
        """update_interview propagates repository exceptions."""
        mock_repository.update.side_effect = RuntimeError("DB error")

        with pytest.raises(RuntimeError, match="DB error"):
            service.update_interview("int-001", notes="Fail")

    def test_update_interview_no_fields_raises(self, service, mock_repository):
        """update_interview raises when no update fields are provided."""
        with pytest.raises(ValueError, match="No fields"):
            service.update_interview("int-001")


# ---------------------------------------------------------------------------
# 5. cancel_interview
# ---------------------------------------------------------------------------


class TestCancelInterview:
    """Tests for InterviewService.cancel_interview."""

    def test_cancel_interview_cancels_and_returns(self, service, mock_repository, sample_interview):
        """cancel_interview cancels the interview and returns it."""
        cancelled = Interview(
            **{**sample_interview.__dict__, "status": InterviewStatus.CANCELLED}
        )
        mock_repository.update.return_value = cancelled

        result = service.cancel_interview("int-001")

        assert result is not None
        assert result.status == InterviewStatus.CANCELLED
        mock_repository.update.assert_called_once()

    def test_cancel_interview_with_reason(self, service, mock_repository, sample_interview):
        """cancel_interview accepts a cancellation reason."""
        cancelled = Interview(
            **{**sample_interview.__dict__, "status": InterviewStatus.CANCELLED, "notes": "Candidate unavailable"}
        )
        mock_repository.update.return_value = cancelled

        result = service.cancel_interview("int-001", reason="Candidate unavailable")

        assert result.status == InterviewStatus.CANCELLED

    def test_cancel_interview_not_found_raises(self, service, mock_repository):
        """cancel_interview raises InterviewNotFoundError when interview doesn't exist."""
        mock_repository.get_by_id.return_value = None

        with pytest.raises(InterviewNotFoundError, match="int-999"):
            service.cancel_interview("int-999")

    def test_cancel_interview_already_cancelled_raises(self, service, mock_repository):
        """cancel_interview raises InvalidInterviewStateError if already cancelled."""
        already_cancelled = Interview(
            id="int-002",
            application_id="app-001",
            candidate_id="cand-001",
            job_id="job-001",
            interviewer_id="emp-001",
            scheduled_at=datetime.now(timezone.utc) + timedelta(days=1),
            duration_minutes=60,
            interview_type=InterviewType.TECHNICAL,
            status=InterviewStatus.CANCELLED,
        )
        mock_repository.get_by_id.return_value = already_cancelled

        with pytest.raises(InvalidInterviewStateError):
            service.cancel_interview("int-002")

    def test_cancel_interview_already_completed_raises(self, service, mock_repository):
        """cancel_interview raises InvalidInterviewStateError if already completed."""
        completed = Interview(
            id="int-003",
            application_id="app-001",
            candidate_id="cand-001",
            job_id="job-001",
            interviewer_id="emp-001",
            scheduled_at=datetime.now(timezone.utc) + timedelta(days=1),
            duration_minutes=60,
            interview_type=InterviewType.TECHNICAL,
            status=InterviewStatus.COMPLETED,
        )
        mock_repository.get_by_id.return_value = completed

        with pytest.raises(InvalidInterviewStateError):
            service.cancel_interview("int-003")

    def test_cancel_interview_repository_exception(self, service, mock_repository):
        """cancel_interview propagates repository exceptions."""
        mock_repository.get_by_id.side_effect = RuntimeError("DB error")

        with pytest.raises(RuntimeError, match="DB error"):
            service.cancel_interview("int-001")
