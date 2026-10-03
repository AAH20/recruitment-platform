"""Onboarding Automator Agent for the Recruitment Platform.

Provides functions to manage the candidate onboarding lifecycle:
starting an onboarding process, checking its status, and completing
individual onboarding steps.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

# In-memory store for onboarding sessions (replace with persistent storage in production)
_onboarding_sessions: dict[str, dict[str, Any]] = {}

# Valid onboarding steps
VALID_STEPS: frozenset[str] = frozenset({
    "personal_info",
    "document_verification",
    "background_check",
    "employment_contract",
    "it_setup",
    "orientation",
})


class OnboardingError(Exception):
    """Base exception for onboarding-related errors."""


class CandidateNotFoundError(OnboardingError):
    """Raised when a candidate is not found in the system."""


class JobNotFoundError(OnboardingError):
    """Raised when a job is not found in the system."""


class OnboardingAlreadyStartedError(OnboardingError):
    """Raised when onboarding has already been started for a candidate."""


class InvalidStepError(OnboardingError):
    """Raised when an invalid onboarding step is provided."""


def _utc_now_iso() -> str:
    """Return the current UTC time as an ISO-8601 string."""
    return datetime.now(timezone.utc).isoformat()


def start_onboarding(candidate_id: str, job_id: str) -> dict:
    """Start the onboarding process for a candidate.

    Args:
        candidate_id: The unique identifier of the candidate.
        job_id: The unique identifier of the position being onboarded for.

    Returns:
        A dictionary containing the onboarding session details:
            - candidate_id: The candidate's ID.
            - job_id: The job's ID.
            - status: The initial status ("in_progress").
            - steps: A dict mapping each step to its completion status.
            - started_at: ISO-8601 timestamp of when onboarding started.

    Raises:
        ValueError: If candidate_id or job_id is empty.
        CandidateNotFoundError: If the candidate does not exist.
        JobNotFoundError: If the job does not exist.
        OnboardingAlreadyStartedError: If onboarding was already started.
    """
    if not candidate_id or not candidate_id.strip():
        raise ValueError("candidate_id must be a non-empty string")
    if not job_id or not job_id.strip():
        raise ValueError("job_id must be a non-empty string")

    session_key = f"{candidate_id}:{job_id}"

    if session_key in _onboarding_sessions:
        raise OnboardingAlreadyStartedError(
            f"Onboarding already started for candidate '{candidate_id}' and job '{job_id}'"
        )

    session: dict[str, Any] = {
        "candidate_id": candidate_id,
        "job_id": job_id,
        "status": "in_progress",
        "steps": {step: False for step in sorted(VALID_STEPS)},
        "started_at": _utc_now_iso(),
        "completed_at": None,
    }

    _onboarding_sessions[session_key] = session
    logger.info("Onboarding started for candidate=%s job=%s", candidate_id, job_id)

    return session


def get_onboarding_status(candidate_id: str) -> dict:
    """Get the current onboarding status for a candidate.

    Args:
        candidate_id: The unique identifier of the candidate.

    Returns:
        A dictionary containing the onboarding status:
            - candidate_id: The candidate's ID.
            - job_id: The job's ID.
            - status: Current status ("in_progress", "completed", or "not_started").
            - steps: A dict mapping each step to its completion status.
            - started_at: ISO-8601 timestamp of when onboarding started.
            - completed_at: ISO-8601 timestamp of completion, or None.

    Raises:
        ValueError: If candidate_id is empty.
        CandidateNotFoundError: If no onboarding session exists for the candidate.
    """
    if not candidate_id or not candidate_id.strip():
        raise ValueError("candidate_id must be a non-empty string")

    sessions = [
        s for s in _onboarding_sessions.values() if s["candidate_id"] == candidate_id
    ]

    if not sessions:
        raise CandidateNotFoundError(
            f"No onboarding session found for candidate '{candidate_id}'"
        )

    # Return the most recent session
    latest = max(sessions, key=lambda s: s["started_at"])
    return latest


def complete_onboarding_step(candidate_id: str, step: str) -> bool:
    """Mark an onboarding step as completed for a candidate.

    Args:
        candidate_id: The unique identifier of the candidate.
        step: The onboarding step to complete (must be one of VALID_STEPS).

    Returns:
        True if the step was successfully marked as completed.

    Raises:
        ValueError: If candidate_id or step is empty.
        InvalidStepError: If the step is not a valid onboarding step.
        CandidateNotFoundError: If no onboarding session exists for the candidate.
    """
    if not candidate_id or not candidate_id.strip():
        raise ValueError("candidate_id must be a non-empty string")
    if not step or not step.strip():
        raise ValueError("step must be a non-empty string")

    step = step.strip()
    if step not in VALID_STEPS:
        raise InvalidStepError(
            f"Invalid onboarding step '{step}'. Valid steps: {sorted(VALID_STEPS)}"
        )

    sessions = [
        s for s in _onboarding_sessions.values() if s["candidate_id"] == candidate_id
    ]

    if not sessions:
        raise CandidateNotFoundError(
            f"No onboarding session found for candidate '{candidate_id}'"
        )

    latest = max(sessions, key=lambda s: s["started_at"])
    latest["steps"][step] = True

    # Check if all steps are complete
    if all(latest["steps"].values()):
        latest["status"] = "completed"
        latest["completed_at"] = _utc_now_iso()
        logger.info(
            "Onboarding completed for candidate=%s", candidate_id
        )

    logger.info(
        "Step '%s' completed for candidate=%s", step, candidate_id
    )
    return True
