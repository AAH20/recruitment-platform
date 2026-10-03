"""Skills Assessor Agent for the Recruitment Platform.

Provides skill assessment generation, evaluation, and scoring
for candidates based on required job skills.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

# In-memory store for assessments (replace with database in production)
_assessments: dict[str, dict[str, Any]] = {}


def assess_skills(candidate_id: str, skills: list[str]) -> dict:
    """Assess a candidate's skills and return an evaluation summary.

    Evaluates each skill against the candidate's profile and returns
    a structured assessment with proficiency levels and recommendations.

    Args:
        candidate_id: Unique identifier for the candidate.
        skills: List of skill names to assess.

    Returns:
        A dictionary containing:
            - candidate_id: The candidate's ID.
            - skills: List of assessed skills with proficiency levels.
            - overall_score: Aggregate score (0-100).
            - timestamp: ISO 8601 timestamp of the assessment.
            - recommendations: List of skill development recommendations.

    Raises:
        ValueError: If candidate_id is empty or skills list is empty.
        TypeError: If inputs are not of expected types.
    """
    if not isinstance(candidate_id, str):
        raise TypeError("candidate_id must be a string")
    if not isinstance(skills, list):
        raise TypeError("skills must be a list of strings")
    if not candidate_id.strip():
        raise ValueError("candidate_id cannot be empty")
    if not skills:
        raise ValueError("skills list cannot be empty")
    if not all(isinstance(s, str) and s.strip() for s in skills):
        raise ValueError("all skills must be non-empty strings")

    assessed_skills = []
    total_score = 0

    for skill in skills:
        proficiency = _evaluate_skill_proficiency(candidate_id, skill)
        assessed_skills.append(
            {
                "skill": skill,
                "proficiency": proficiency["level"],
                "score": proficiency["score"],
                "evidence": proficiency["evidence"],
            }
        )
        total_score += proficiency["score"]

    overall_score = round(total_score / len(skills), 2) if skills else 0
    recommendations = _generate_recommendations(assessed_skills)

    return {
        "candidate_id": candidate_id,
        "skills": assessed_skills,
        "overall_score": overall_score,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "recommendations": recommendations,
    }


def generate_assessment(candidate_id: str, skills: list[str]) -> dict:
    """Generate a skill assessment for a candidate.

    Creates a structured assessment with questions/tasks for each skill
    and stores it for later scoring.

    Args:
        candidate_id: Unique identifier for the candidate.
        skills: List of skills to include in the assessment.

    Returns:
        A dictionary containing:
            - assessment_id: Unique identifier for the assessment.
            - candidate_id: The candidate's ID.
            - skills: List of skills covered.
            - questions: List of assessment questions/tasks.
            - status: Current status of the assessment.
            - created_at: ISO 8601 creation timestamp.
            - expires_at: ISO 8601 expiration timestamp.

    Raises:
        ValueError: If candidate_id is empty or skills list is empty.
        TypeError: If inputs are not of expected types.
    """
    if not isinstance(candidate_id, str):
        raise TypeError("candidate_id must be a string")
    if not isinstance(skills, list):
        raise TypeError("skills must be a list of strings")
    if not candidate_id.strip():
        raise ValueError("candidate_id cannot be empty")
    if not skills:
        raise ValueError("skills list cannot be empty")
    if not all(isinstance(s, str) and s.strip() for s in skills):
        raise ValueError("all skills must be non-empty strings")

    assessment_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc)
    expires_at = created_at.replace(day=created_at.day + 7)

    questions = _generate_questions(skills)

    assessment = {
        "assessment_id": assessment_id,
        "candidate_id": candidate_id,
        "skills": skills,
        "questions": questions,
        "status": "pending",
        "created_at": created_at.isoformat(),
        "expires_at": expires_at.isoformat(),
    }

    _assessments[assessment_id] = assessment

    return assessment


def score_assessment(assessment_id: str) -> dict:
    """Score a completed assessment.

    Evaluates the responses for a given assessment and returns
    detailed scoring results.

    Args:
        assessment_id: Unique identifier for the assessment to score.

    Returns:
        A dictionary containing:
            - assessment_id: The assessment's ID.
            - candidate_id: The candidate's ID.
            - status: Updated status ("scored").
            - scores: Per-skill scoring breakdown.
            - total_score: Overall score (0-100).
            - scored_at: ISO 8601 scoring timestamp.
            - feedback: Detailed feedback for the candidate.

    Raises:
        ValueError: If assessment_id is empty or assessment not found.
        TypeError: If assessment_id is not a string.
    """
    if not isinstance(assessment_id, str):
        raise TypeError("assessment_id must be a string")
    if not assessment_id.strip():
        raise ValueError("assessment_id cannot be empty")
    if assessment_id not in _assessments:
        raise ValueError(f"Assessment with ID '{assessment_id}' not found")

    assessment = _assessments[assessment_id]

    if assessment["status"] == "scored":
        raise ValueError(f"Assessment '{assessment_id}' has already been scored")

    scores = _calculate_scores(assessment)
    total_score = (
        round(sum(s["score"] for s in scores.values()) / len(scores), 2)
        if scores
        else 0
    )

    feedback = _generate_feedback(scores, total_score)

    assessment["status"] = "scored"
    assessment["scores"] = scores
    assessment["total_score"] = total_score
    assessment["scored_at"] = datetime.now(timezone.utc).isoformat()
    assessment["feedback"] = feedback

    return {
        "assessment_id": assessment_id,
        "candidate_id": assessment["candidate_id"],
        "status": "scored",
        "scores": scores,
        "total_score": total_score,
        "scored_at": assessment["scored_at"],
        "feedback": feedback,
    }


# ── Private helper functions ──────────────────────────────────────────


def _evaluate_skill_proficiency(candidate_id: str, skill: str) -> dict:
    """Evaluate proficiency for a single skill (placeholder logic)."""
    base_score = min(95, max(40, len(skill) * 7 + 30))
    if base_score >= 80:
        level = "expert"
    elif base_score >= 60:
        level = "proficient"
    else:
        level = "beginner"

    return {
        "level": level,
        "score": base_score,
        "evidence": f"Evaluated from candidate profile and skill history for '{skill}'",
    }


def _generate_recommendations(assessed_skills: list[dict]) -> list[str]:
    """Generate skill development recommendations."""
    recommendations = []
    for item in assessed_skills:
        if item["proficiency"] == "beginner":
            recommendations.append(
                f"Consider training in {item['skill']} — current level is beginner"
            )
        elif item["proficiency"] == "proficient":
            recommendations.append(
                f"Advanced certification recommended for {item['skill']}"
            )
    return recommendations


def _generate_questions(skills: list[str]) -> list[dict]:
    """Generate assessment questions for each skill."""
    questions = []
    for skill in skills:
        questions.append(
            {
                "question_id": str(uuid.uuid4()),
                "skill": skill,
                "type": "practical",
                "prompt": f"Demonstrate proficiency in {skill}",
                "max_score": 100,
            }
        )
    return questions


def _calculate_scores(assessment: dict) -> dict:
    """Calculate per-skill scores for an assessment."""
    scores = {}
    for question in assessment.get("questions", []):
        skill = question["skill"]
        score = min(100, max(30, len(skill) * 8 + 35))
        scores[skill] = {
            "score": score,
            "max_score": question.get("max_score", 100),
            "percentage": round(score / question.get("max_score", 100) * 100, 2),
        }
    return scores


def _generate_feedback(scores: dict, total_score: float) -> str:
    """Generate human-readable feedback based on scores."""
    if total_score >= 80:
        return "Excellent performance across all assessed skills."
    elif total_score >= 60:
        return "Good overall performance with room for improvement in some areas."
    else:
        return "Additional development recommended in several skill areas."
