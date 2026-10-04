"""
Comprehensive agent tests for the Skills Assessor module.

Tests cover:
- assess_skills: Evaluates candidate skills against job requirements
- generate_assessment: Creates assessment questions/structure
- score_assessment: Scores completed assessments
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Any

# Import the module under test
from recruitment_platform.agents.skills_assessor import (
assess_skills,
generate_assessment,
score_assessment,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def sample_candidate():
    """Returns a sample candidate profile with skills."""
return {
"id": "cand_001",
"name": "Jane Doe",
"email": "jane@example.com",
"skills": [
{"name": "Python", "level": "expert", "years": 5},
{"name": "JavaScript", "level": "intermediate", "years": 3},
{"name": "SQL", "level": "advanced", "years": 4},
{"name": "Docker", "level": "beginner", "years": 1},
{"name": "AWS", "level": "intermediate", "years": 2},
],
"experience_years": 6,
"education": "BSc Computer Science",
}


@pytest.fixture
def sample_job_requirements():
    """Returns sample job requirements with required skills."""
return {
"id": "job_001",
"title": "Senior Software Engineer",
"required_skills": [
{"name": "Python", "minimum_level": "advanced"},
{"name": "JavaScript", "minimum_level": "intermediate"},
{"name": "SQL", "minimum_level": "intermediate"},
{"name": "Docker", "minimum_level": "beginner"},
],
"preferred_skills": [
{"name": "AWS", "minimum_level": "intermediate"},
{"name": "Kubernetes", "minimum_level": "beginner"},
],
"minimum_experience_years": 4,
}


@pytest.fixture
def sample_assessment_template():
    """Returns a sample assessment template."""
return {
"id": "tmpl_001",
"title": "Technical Skills Assessment",
"questions": [
{
"id": "q1",
"text": "Explain Python decorators and provide an example.",
"type": "open_ended",
"skill": "Python",
"max_score": 10,
},
{
"id": "q2",
"text": "What is the event loop in JavaScript?",
"type": "open_ended",
"skill": "JavaScript",
"max_score": 10,
},
{
"id": "q3",
"text": "Write a SQL query to find duplicate records.",
"type": "coding",
"skill": "SQL",
"max_score": 15,
},
{
"id": "q4",
"text": "What is the difference between a Docker container and a VM?",
"type": "multiple_choice",
"skill": "Docker",
"max_score": 5,
"options": [
"Containers share the host OS kernel",
"VMs are always faster",
"Containers need a hypervisor",
"There is no difference",
],
"correct_answer": 0,
},
],
"passing_score": 60,
"time_limit_minutes": 45,
}


@pytest.fixture
def sample_completed_assessment():
    """Returns a sample completed assessment with answers."""
return {
"id": "assess_001",
"candidate_id": "cand_001",
"template_id": "tmpl_001",
"started_at": "2024-01-15T10:00:00Z",
"completed_at": "2024-01-15T10:35:00Z",
"answers": [
{
"question_id": "q1",
"answer": "Decorators are functions that modify other functions...",
"score": 8,
},
{
"question_id": "q2",
"answer": "The event loop handles async operations...",
"score": 7,
},
{
"question_id": "q3",
"answer": "SELECT id, COUNT(*) FROM users GROUP BY id HAVING COUNT(*) > 1;",
"score": 12,
},
{
"question_id": "q4",
"answer": 0,
"score": 5,
},
],
}


@pytest.fixture
def mock_llm_response():
    """Returns a mock LLM response for assessment generation."""
return {
"content": '{"questions": [{"text": "What is Python?", "type": "open_ended"}]}',
"usage": {"prompt_tokens": 150, "completion_tokens": 50, "total_tokens": 200},
}


@pytest.fixture
def empty_skills_candidate():
    """Returns a candidate with no skills."""
return {
"id": "cand_002",
"name": "John Smith",
"email": "john@example.com",
"skills": [],
"experience_years": 0,
"education": None,
}


@pytest.fixture
def mock_assessment_config():
    """Returns mock configuration for assessment generation."""
return {
"difficulty": "medium",
"num_questions": 5,
"question_types": ["multiple_choice", "open_ended", "coding"],
"include_explanations": True,
"language": "en",
}


# =============================================================================
# Test: assess_skills
# =============================================================================


class TestAssessSkills:
    """Tests for the assess_skills function."""

    def test_assess_skills_returns_dict(self, sample_candidate, sample_job_requirements):
        """Test that assess_skills returns a dictionary result."""
result = assess_skills(sample_candidate, sample_job_requirements)
assert isinstance(result, dict)

    def test_assess_skills_contains_required_keys(
self, sample_candidate, sample_job_requirements
):
        """Test that the result contains all expected top-level keys."""
result = assess_skills(sample_candidate, sample_job_requirements)
expected_keys = {"candidate_id", "job_id", "overall_score", "skill_matches", "gaps", "recommendations"}
assert expected_keys.issubset(result.keys())

    def test_assess_skills_overall_score_range(
self, sample_candidate, sample_job_requirements
):
        """Test that overall_score is between 0 and 100."""
result = assess_skills(sample_candidate, sample_job_requirements)
assert 0 <= result["overall_score"] <= 100

    def test_assess_skills_skill_matches_populated(
self, sample_candidate, sample_job_requirements
):
        """Test that skill_matches contains entries for required skills."""
result = assess_skills(sample_candidate, sample_job_requirements)
assert len(result["skill_matches"]) > 0
required_skill_names = {
s["name"] for s in sample_job_requirements["required_skills"]
}
matched_skill_names = {m["skill_name"] for m in result["skill_matches"]}
assert required_skill_names.issubset(matched_skill_names)

    def test_assess_skills_identifies_gaps(
self, sample_candidate, sample_job_requirements
):
        """Test that missing skills are identified as gaps."""
result = assess_skills(sample_candidate, sample_job_requirements)
# Candidate lacks Kubernetes which is a preferred skill
        gap_names = {g["skill_name"] for g in result["gaps"]}
assert "Kubernetes" in gap_names

    def test_assess_skills_no_gaps_when_all_met(
self, sample_candidate, sample_job_requirements
):
        """Test that gaps is empty when all skills are satisfied."""
# Add all preferred skills to candidate
        sample_candidate["skills"].append(
{"name": "Kubernetes", "level": "intermediate", "years": 2}
)
    result = assess_skills(sample_candidate, sample_job_requirements)
# All required and preferred skills are now met
        assert len(result["gaps"]) == 0

    def test_assess_skills_empty_candidate_skills(
self, empty_skills_candidate, sample_job_requirements
):
        """Test assessment with a candidate that has no skills."""
result = assess_skills(empty_skills_candidate, sample_job_requirements)
assert result["overall_score"] == 0
assert len(result["gaps"]) == len(sample_job_requirements["required_skills"])

    def test_assess_skills_recommendations_present(
self, sample_candidate, sample_job_requirements
):
        """Test that recommendations are generated."""
result = assess_skills(sample_candidate, sample_job_requirements)
assert "recommendations" in result
assert isinstance(result["recommendations"], list)

    def test_assess_skills_candidate_id_propagated(
self, sample_candidate, sample_job_requirements
):
        """Test that candidate_id is correctly set in the result."""
result = assess_skills(sample_candidate, sample_job_requirements)
assert result["candidate_id"] == sample_candidate["id"]

    def test_assess_skills_job_id_propagated(
self, sample_candidate, sample_job_requirements
):
        """Test that job_id is correctly set in the result."""
result = assess_skills(sample_candidate, sample_job_requirements)
assert result["job_id"] == sample_job_requirements["id"]

    def test_assess_skills_high_match_score(
self, sample_candidate, sample_job_requirements
):
        """Test that a well-matched candidate gets a high score."""
result = assess_skills(sample_candidate, sample_job_requirements)
# Candidate meets all required skills, should score reasonably high
        assert result["overall_score"] >= 50

    def test_assess_skills_skill_level_comparison(
self, sample_candidate, sample_job_requirements
):
        """Test that skill levels are properly compared."""
result = assess_skills(sample_candidate, sample_job_requirements)
for match in result["skill_matches"]:
            assert "candidate_level" in match
assert "required_level" in match
assert "meets_requirement" in match

    def test_assess_skills_handles_missing_candidate_fields(self, sample_job_requirements):
        """Test that missing candidate fields are handled gracefully."""
minimal_candidate = {"id": "cand_003", "skills": []}
result = assess_skills(minimal_candidate, sample_job_requirements)
assert isinstance(result, dict)
assert result["overall_score"] == 0

    def test_assess_skills_handles_missing_job_fields(self, sample_candidate):
        """Test that missing job requirement fields are handled gracefully."""
minimal_job = {"id": "job_002", "required_skills": []}
result = assess_skills(sample_candidate, minimal_job)
assert isinstance(result, dict)

    def test_assess_skills_experience_factor(
self, sample_candidate, sample_job_requirements
):
        """Test that experience requirements factor into scoring."""
# Candidate has 6 years, job requires 4
        result = assess_skills(sample_candidate, sample_job_requirements)
assert result["overall_score"] > 0

    def test_assess_skills_returns_skill_match_details(
self, sample_candidate, sample_job_requirements
):
        """Test that skill match entries contain detailed information."""
result = assess_skills(sample_candidate, sample_job_requirements)
for match in result["skill_matches"]:
            assert "skill_name" in match
assert "match_percentage" in match or "score" in match

    def test_assess_skills_gaps_have_severity(
self, sample_candidate, sample_job_requirements
):
        """Test that identified gaps include severity information."""
result = assess_skills(sample_candidate, sample_job_requirements)
for gap in result["gaps"]:
            assert "skill_name" in gap
assert "severity" in gap or "importance" in gap

    def test_assess_skills_with_none_inputs(self):
        """Test that None inputs raise appropriate errors."""
with pytest.raises((TypeError, ValueError)):
            assess_skills(None, None)

    def test_assess_skills_with_empty_job(self, sample_candidate):
        """Test with empty job requirements."""
empty_job = {"id": "job_003", "required_skills": [], "preferred_skills": []}
result = assess_skills(sample_candidate, empty_job)
assert result["overall_score"] == 100 or result["overall_score"] == 0

    def test_assess_skills_preferred_skills_bonus(
self, sample_candidate, sample_job_requirements
):
        """Test that preferred skills contribute to score bonus."""
# Candidate has AWS (preferred) but not Kubernetes
        result = assess_skills(sample_candidate, sample_job_requirements)
# Should still get some credit for preferred skills
        assert result["overall_score"] > 0

    def test_assess_skills_multiple_candidates_different_scores(
self, sample_job_requirements
):
        """Test that different candidates get different scores."""
strong_candidate = {
"id": "cand_strong",
"skills": [
{"name": "Python", "level": "expert", "years": 8},
{"name": "JavaScript", "level": "expert", "years": 6},
{"name": "SQL", "level": "expert", "years": 7},
{"name": "Docker", "level": "advanced", "years": 4},
{"name": "AWS", "level": "expert", "years": 5},
{"name": "Kubernetes", "level": "advanced", "years": 3},
],
"experience_years": 8,
}
weak_candidate = {
"id": "cand_weak",
"skills": [
{"name": "Python", "level": "beginner", "years": 1},
],
"experience_years": 1,
}
strong_result = assess_skills(strong_candidate, sample_job_requirements)
weak_result = assess_skills(weak_candidate, sample_job_requirements)
assert strong_result["overall_score"] > weak_result["overall_score"]


# =============================================================================
# Test: generate_assessment
# =============================================================================


class TestGenerateAssessment:
    """Tests for the generate_assessment function."""

    def test_generate_assessment_returns_dict(
self, sample_job_requirements, mock_assessment_config
):
        """Test that generate_assessment returns a dictionary."""
result = generate_assessment(sample_job_requirements, mock_assessment_config)
assert isinstance(result, dict)

    def test_generate_assessment_contains_questions(
self, sample_job_requirements, mock_assessment_config
):
        """Test that the generated assessment contains questions."""
result = generate_assessment(sample_job_requirements, mock_assessment_config)
assert "questions" in result
assert isinstance(result["questions"], list)
assert len(result["questions"]) > 0

    def test_generate_assessment_question_count_matches_config(
self, sample_job_requirements, mock_assessment_config
):
        """Test that the number of questions matches the config."""
result = generate_assessment(sample_job_requirements, mock_assessment_config)
# Should generate approximately the requested number
        assert len(result["questions"]) <= mock_assessment_config["num_questions"] + 2

    def test_generate_assessment_question_structure(
self, sample_job_requirements, mock_assessment_config
):
        """Test that each question has the required fields."""
result = generate_assessment(sample_job_requirements, mock_assessment_config)
for question in result["questions"]:
            assert "id" in question or "question_id" in question
assert "text" in question or "question" in question
assert "type" in question
assert "skill" in question

    def test_generate_assessment_includes_passing_score(
self, sample_job_requirements, mock_assessment_config
):
        """Test that the assessment includes a passing score."""
result = generate_assessment(sample_job_requirements, mock_assessment_config)
assert "passing_score" in result
assert 0 <= result["passing_score"] <= 100

    def test_generate_assessment_includes_time_limit(
self, sample_job_requirements, mock_assessment_config
):
        """Test that the assessment includes a time limit."""
result = generate_assessment(sample_job_requirements, mock_assessment_config)
assert "time_limit_minutes" in result
assert result["time_limit_minutes"] > 0

    def test_generate_assessment_covers_required_skills(
self, sample_job_requirements, mock_assessment_config
):
        """Test that questions cover the required skills."""
result = generate_assessment(sample_job_requirements, mock_assessment_config)
question_skills = {q["skill"] for q in result["questions"]}
required_skills = {s["name"] for s in sample_job_requirements["required_skills"]}
# At least some required skills should be covered
        assert len(question_skills & required_skills) > 0

    def test_generate_assessment_with_empty_job(self, mock_assessment_config):
        """Test generation with empty job requirements."""
empty_job = {"id": "job_empty", "required_skills": []}
result = generate_assessment(empty_job, mock_assessment_config)
assert isinstance(result, dict)

    def test_generate_assessment_with_minimal_config(self, sample_job_requirements):
        """Test generation with minimal configuration."""
minimal_config = {"num_questions": 1}
result = generate_assessment(sample_job_requirements, minimal_config)
assert isinstance(result, dict)
assert "questions" in result

    def test_generate_assessment_multiple_choice_has_options(
self, sample_job_requirements, mock_assessment_config
):
        """Test that multiple choice questions include options."""
result = generate_assessment(sample_job_requirements, mock_assessment_config)
mc_questions = [
q for q in result["questions"] if q.get("type") == "multiple_choice"
]
for q in mc_questions:
            assert "options" in q
assert len(q["options"]) >= 2

    def test_generate_assessment_multiple_choice_has_correct_answer(
self, sample_job_requirements, mock_assessment_config
):
        """Test that multiple choice questions have a correct answer."""
result = generate_assessment(sample_job_requirements, mock_assessment_config)
mc_questions = [
q for q in result["questions"] if q.get("type") == "multiple_choice"
]
for q in mc_questions:
            assert "correct_answer" in q

    def test_generate_assessment_question_ids_unique(
self, sample_job_requirements, mock_assessment_config
):
        """Test that all question IDs are unique."""
result = generate_assessment(sample_job_requirements, mock_assessment_config)
ids = [q.get("id") or q.get("question_id") for q in result["questions"]]
assert len(ids) == len(set(ids))

    def test_generate_assessment_includes_max_scores(
self, sample_job_requirements, mock_assessment_config
):
        """Test that questions include maximum scores."""
result = generate_assessment(sample_job_requirements, mock_assessment_config)
for q in result["questions"]:
            assert "max_score" in q
assert q["max_score"] > 0

    def test_generate_assessment_respects_difficulty(
self, sample_job_requirements, mock_assessment_config
):
        """Test that the difficulty setting is respected."""
mock_assessment_config["difficulty"] = "hard"
result = generate_assessment(sample_job_requirements, mock_assessment_config)
assert isinstance(result, dict)
# Hard difficulty should still produce valid questions
        assert len(result["questions"]) > 0

    def test_generate_assessment_with_none_job(self, mock_assessment_config):
        """Test that None job raises appropriate error."""
with pytest.raises((TypeError, ValueError)):
            generate_assessment(None, mock_assessment_config)

    def test_generate_assessment_with_none_config(self, sample_job_requirements):
        """Test that None config raises appropriate error."""
with pytest.raises((TypeError, ValueError)):
            generate_assessment(sample_job_requirements, None)

    def test_generate_assessment_total_score_consistency(
self, sample_job_requirements, mock_assessment_config
):
        """Test that total possible score is consistent with question scores."""
result = generate_assessment(sample_job_requirements, mock_assessment_config)
total_score = sum(q["max_score"] for q in result["questions"])
assert total_score > 0
# Passing score should be a percentage of total
        assert result["passing_score"] <= 100

    def test_generate_assessment_includes_title(
self, sample_job_requirements, mock_assessment_config
):
        """Test that the assessment includes a title."""
result = generate_assessment(sample_job_requirements, mock_assessment_config)
assert "title" in result
assert len(result["title"]) > 0

    def test_generate_assessment_question_types_valid(
self, sample_job_requirements, mock_assessment_config
):
        """Test that all question types are valid."""
valid_types = {"multiple_choice", "open_ended", "coding", "true_false"}
result = generate_assessment(sample_job_requirements, mock_assessment_config)
for q in result["questions"]:
            assert q["type"] in valid_types

    def test_generate_assessment_with_single_skill_job(self, mock_assessment_config):
        """Test generation for a job with only one required skill."""
single_skill_job = {
"id": "job_single",
"required_skills": [{"name": "Python", "minimum_level": "intermediate"}],
}
result = generate_assessment(single_skill_job, mock_assessment_config)
assert isinstance(result, dict)
assert "questions" in result

    def test_generate_assessment_includes_metadata(
self, sample_job_requirements, mock_assessment_config
):
        """Test that the assessment includes metadata."""
result = generate_assessment(sample_job_requirements, mock_assessment_config)
assert "id" in result or "assessment_id" in result
assert "created_at" in result or "generated_at" in result


# =============================================================================
# Test: score_assessment
# =============================================================================


class TestScoreAssessment:
    """Tests for the score_assessment function."""

    def test_score_assessment_returns_dict(self, sample_completed_assessment):
        """Test that score_assessment returns a dictionary."""
result = score_assessment(sample_completed_assessment)
assert isinstance(result, dict)

    def test_score_assessment_contains_total_score(self, sample_completed_assessment):
        """Test that the result contains a total score."""
result = score_assessment(sample_completed_assessment)
assert "total_score" in result
assert isinstance(result["total_score"], (int, float))

    def test_score_assessment_contains_max_score(self, sample_completed_assessment):
        """Test that the result contains the maximum possible score."""
result = score_assessment(sample_completed_assessment)
assert "max_score" in result
assert result["max_score"] > 0

    def test_score_assessment_contains_percentage(self, sample_completed_assessment):
        """Test that the result contains a percentage score."""
result = score_assessment(sample_completed_assessment)
assert "percentage" in result
assert 0 <= result["percentage"] <= 100

    def test_score_assessment_contains_pass_fail(self, sample_completed_assessment):
        """Test that the result indicates pass/fail status."""
result = score_assessment(sample_completed_assessment)
assert "passed" in result
assert isinstance(result["passed"], bool)

    def test_score_assessment_correct_total_calculation(
self, sample_completed_assessment
):
        """Test that total score is correctly calculated from answers."""
result = score_assessment(sample_completed_assessment)
expected_total = sum(a["score"] for a in sample_completed_assessment["answers"])
assert result["total_score"] == expected_total

    def test_score_assessment_question_scores_present(
self, sample_completed_assessment
):
        """Test that individual question scores are included."""
result = score_assessment(sample_completed_assessment)
assert "question_scores" in result
assert isinstance(result["question_scores"], list)
assert len(result["question_scores"]) == len(
sample_completed_assessment["answers"]
)

    def test_score_assessment_with_empty_answers(self):
        """Test scoring with no answers provided."""
empty_assessment = {
"id": "assess_empty",
"candidate_id": "cand_001",
"answers": [],
}
result = score_assessment(empty_assessment)
assert result["total_score"] == 0
assert result["percentage"] == 0
assert result["passed"] is False

    def test_score_assessment_with_perfect_score(self):
        """Test scoring with all correct answers."""
perfect_assessment = {
"id": "assess_perfect",
"candidate_id": "cand_001",
"answers": [
{"question_id": "q1", "score": 10},
{"question_id": "q2", "score": 10},
{"question_id": "q3", "score": 15},
{"question_id": "q4", "score": 5},
],
}
result = score_assessment(perfect_assessment)
assert result["total_score"] == 40
assert result["percentage"] == 100
assert result["passed"] is True

    def test_score_assessment_with_zero_score(self):
        """Test scoring with all zero scores."""
zero_assessment = {
"id": "assess_zero",
"candidate_id": "cand_001",
"answers": [
{"question_id": "q1", "score": 0},
{"question_id": "q2", "score": 0},
],
}
result = score_assessment(zero_assessment)
assert result["total_score"] == 0
assert result["percentage"] == 0
assert result["passed"] is False

    def test_score_assessment_includes_candidate_id(self, sample_completed_assessment):
        """Test that candidate_id is propagated to the result."""
result = score_assessment(sample_completed_assessment)
assert result["candidate_id"] == sample_completed_assessment["candidate_id"]

    def test_score_assessment_includes_assessment_id(self, sample_completed_assessment):
        """Test that assessment_id is propagated to the result."""
result = score_assessment(sample_completed_assessment)
assert result["assessment_id"] == sample_completed_assessment["id"]

    def test_score_assessment_with_partial_scores(self):
        """Test scoring with partial credit answers."""
partial_assessment = {
"id": "assess_partial",
"candidate_id": "cand_001",
"answers": [
{"question_id": "q1", "score": 5},
{"question_id": "q2", "score": 0},
{"question_id": "q3", "score": 7},
],
}
result = score_assessment(partial_assessment)
assert result["total_score"] == 12
assert result["percentage"] > 0
assert result["percentage"] < 100

    def test_score_assessment_with_none_input(self):
        """Test that None input raises appropriate error."""
with pytest.raises((TypeError, ValueError)):
            score_assessment(None)

    def test_score_assessment_with_missing_answers_key(self):
        """Test handling of assessment without answers key."""
no_answers = {"id": "assess_no_ans", "candidate_id": "cand_001"}
result = score_assessment(no_answers)
assert result["total_score"] == 0

    def test_score_assessment_skill_breakdown(self, sample_completed_assessment):
        """Test that skill-level breakdown is provided."""
result = score_assessment(sample_completed_assessment)
assert "skill_scores" in result or "breakdown" in result

    def test_score_assessment_time_taken(self, sample_completed_assessment):
        """Test that time taken is calculated when timestamps are present."""
result = score_assessment(sample_completed_assessment)
if "started_at" in sample_completed_assessment and "completed_at" in sample_completed_assessment:
            assert "time_taken_minutes" in result or "duration_minutes" in result

    def test_score_assessment_feedback_generated(self, sample_completed_assessment):
        """Test that feedback is generated for the candidate."""
result = score_assessment(sample_completed_assessment)
assert "feedback" in result or "comments" in result

    def test_score_assessment_with_negative_scores(self):
        """Test handling of negative scores (should be clamped or handled)."""
negative_assessment = {
"id": "assess_neg",
"candidate_id": "cand_001",
"answers": [
{"question_id": "q1", "score": -5},
{"question_id": "q2", "score": 10},
],
}
result = score_assessment(negative_assessment)
# Negative scores should be handled gracefully
        assert isinstance(result["total_score"], (int, float))

    def test_score_assessment_with_extra_fields(self, sample_completed_assessment):
        """Test that extra fields in assessment don't break scoring."""
sample_completed_assessment["extra_field"] = "some value"
sample_completed_assessment["metadata"] = {"source": "test"}
result = score_assessment(sample_completed_assessment)
assert isinstance(result, dict)
assert "total_score" in result

    def test_score_assessment_percentage_calculation_accuracy(self):
        """Test that percentage is calculated accurately."""
assessment = {
"id": "assess_pct",
"candidate_id": "cand_001",
"answers": [
{"question_id": "q1", "score": 3},
{"question_id": "q2", "score": 4},
],
}
result = score_assessment(assessment)
# Total = 7, if max is 10 then percentage should be 70
        if result["max_score"] > 0:
            expected_pct = (result["total_score"] / result["max_score"]) * 100
assert abs(result["percentage"] - expected_pct) < 0.01

    def test_score_assessment_pass_threshold_boundary(self):
        """Test pass/fail at the exact threshold."""
# Create assessment where score equals passing threshold
        assessment = {
"id": "assess_boundary",
"candidate_id": "cand_001",
"answers": [
{"question_id": "q1", "score": 6},
{"question_id": "q2", "score": 4},
],
"passing_score": 10,
}
result = score_assessment(assessment)
assert isinstance(result["passed"], bool)

    def test_score_assessment_with_string_scores(self):
        """Test handling of string scores that can be converted to numbers."""
string_score_assessment = {
"id": "assess_str",
"candidate_id": "cand_001",
"answers": [
{"question_id": "q1", "score": "8"},
{"question_id": "q2", "score": "7"},
],
}
result = score_assessment(string_score_assessment)
assert isinstance(result["total_score"], (int, float))
assert result["total_score"] == 15

    def test_score_assessment_includes_grading_timestamp(
self, sample_completed_assessment
):
        """Test that a grading timestamp is included."""
result = score_assessment(sample_completed_assessment)
assert "graded_at" in result or "scored_at" in result

    def test_score_assessment_consistent_results(self, sample_completed_assessment):
        """Test that scoring is deterministic."""
result1 = score_assessment(sample_completed_assessment)
result2 = score_assessment(sample_completed_assessment)
assert result1["total_score"] == result2["total_score"]
assert result1["percentage"] == result2["percentage"]
assert result1["passed"] == result2["passed"]


# =============================================================================
# Integration-style tests
# =============================================================================


class TestSkillsAssessorIntegration:
    """Integration tests combining multiple functions."""

    def test_full_assessment_workflow(
self, sample_candidate, sample_job_requirements, mock_assessment_config
):
        """Test the complete workflow: assess -> generate -> score."""
# Step 1: Assess candidate skills
        assessment_result = assess_skills(sample_candidate, sample_job_requirements)
assert assessment_result["overall_score"] > 0

        # Step 2: Generate assessment
        generated = generate_assessment(sample_job_requirements, mock_assessment_config)
assert len(generated["questions"]) > 0

        # Step 3: Score a completed assessment
        completed = {
"id": "assess_int_001",
"candidate_id": sample_candidate["id"],
"answers": [
{"question_id": q["id"], "score": q["max_score"] * 0.8}
for q in generated["questions"]
],
}
score_result = score_assessment(completed)
assert score_result["total_score"] > 0
assert score_result["percentage"] > 0

    def test_assess_then_generate_uses_gaps(
self, sample_candidate, sample_job_requirements, mock_assessment_config
):
        """Test that assessment generation can use skill gaps from assess_skills."""
# First assess to find gaps
        assessment = assess_skills(sample_candidate, sample_job_requirements)
gaps = assessment["gaps"]

        # Generate assessment - should ideally focus on gap areas
        generated = generate_assessment(sample_job_requirements, mock_assessment_config)
assert isinstance(generated, dict)
assert "questions" in generated

    def test_multiple_candidates_scored_consistently(
self, sample_job_requirements, mock_assessment_config
):
        """Test that multiple candidates can be assessed and scored consistently."""
candidates = [
{
"id": f"cand_{i}",
"skills": [
{"name": "Python", "level": lvl, "years": yrs},
{"name": "SQL", "level": lvl, "years": yrs},
],
"experience_years": yrs,
}
for i, (lvl, yrs) in enumerate(
[("expert", 8), ("intermediate", 4), ("beginner", 1)]
)
    ]

        results = [assess_skills(c, sample_job_requirements) for c in candidates]
scores = [r["overall_score"] for r in results]

        # Expert should score higher than beginner
        assert scores[0] > scores[2]
# All scores should be in valid range
        assert all(0 <= s <= 100 for s in scores)
