"""Comprehensive tests for candidate matcher agent functions."""

import pytest
from unittest.mock import MagicMock, patch
from recruitment_platform.agents.candidate_matcher import (
match_candidates,
rank_matches,
get_top_matches,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_job():
    """Return a sample job description dict."""
return {
"id": "job-001",
"title": "Senior Python Developer",
"required_skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
"preferred_skills": ["Redis", "Kubernetes"],
"min_experience_years": 5,
"max_experience_years": 12,
"location": "Remote",
"salary_min": 120000,
"salary_max": 180000,
}


@pytest.fixture
def sample_candidates():
    """Return a list of sample candidate dicts."""
return [
{
"id": "cand-001",
"name": "Alice Johnson",
"skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Redis"],
"experience_years": 7,
"location": "Remote",
"expected_salary": 150000,
},
{
"id": "cand-002",
"name": "Bob Smith",
"skills": ["Python", "Django", "MySQL"],
"experience_years": 3,
"location": "New York, NY",
"expected_salary": 100000,
},
{
"id": "cand-003",
"name": "Carol Williams",
"skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Kubernetes"],
"experience_years": 10,
"location": "Remote",
"expected_salary": 170000,
},
{
"id": "cand-004",
"name": "David Brown",
"skills": ["Java", "Spring", "PostgreSQL"],
"experience_years": 8,
"location": "Remote",
"expected_salary": 140000,
},
{
"id": "cand-005",
"name": "Eve Davis",
"skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Redis", "Kubernetes"],
"experience_years": 6,
"location": "Remote",
"expected_salary": 130000,
},
]


@pytest.fixture
def empty_candidates():
    """Return an empty candidate list."""
return []


@pytest.fixture
def mock_matcher_response():
    """Return a mock response from the matcher LLM."""
return {
"matches": [
{"candidate_id": "cand-001", "score": 0.92, "reasoning": "Strong skill match"},
{"candidate_id": "cand-003", "score": 0.88, "reasoning": "Excellent fit"},
{"candidate_id": "cand-005", "score": 0.85, "reasoning": "Very good match"},
]
}


# ---------------------------------------------------------------------------
# Tests for match_candidates
# ---------------------------------------------------------------------------


class TestMatchCandidates:
    """Tests for the match_candidates function."""

    def test_match_candidates_returns_list(self, sample_job, sample_candidates):
        """match_candidates should return a list of match results."""
result = match_candidates(sample_job, sample_candidates)
assert isinstance(result, list)

    def test_match_candidates_returns_dicts(self, sample_job, sample_candidates):
        """Each match result should be a dict."""
result = match_candidates(sample_job, sample_candidates)
for item in result:
            assert isinstance(item, dict)

    def test_match_candidates_contains_candidate_ids(self, sample_job, sample_candidates):
        """Each match result should reference a candidate id."""
result = match_candidates(sample_job, sample_candidates)
candidate_ids = {c["id"] for c in sample_candidates}
for item in result:
            assert "candidate_id" in item
assert item["candidate_id"] in candidate_ids

    def test_match_candidates_contains_scores(self, sample_job, sample_candidates):
        """Each match result should have a numeric score."""
result = match_candidates(sample_job, sample_candidates)
for item in result:
            assert "score" in item
assert isinstance(item["score"], (int, float))
assert 0.0 <= item["score"] <= 1.0

    def test_match_candidates_empty_candidates(self, sample_job, empty_candidates):
        """match_candidates with no candidates should return an empty list."""
result = match_candidates(sample_job, empty_candidates)
assert result == []

    def test_match_candidates_empty_job(self, sample_candidates):
        """match_candidates with an empty job should still return results or handle gracefully."""
empty_job = {}
result = match_candidates(empty_job, sample_candidates)
assert isinstance(result, list)

    def test_match_candidates_preserves_all_candidates(self, sample_job, sample_candidates):
        """All candidates should appear in the match results."""
result = match_candidates(sample_job, sample_candidates)
result_ids = {item["candidate_id"] for item in result}
candidate_ids = {c["id"] for c in sample_candidates}
assert result_ids == candidate_ids

    def test_match_candidates_score_ordering(self, sample_job, sample_candidates):
        """Results should be ordered by descending score."""
result = match_candidates(sample_job, sample_candidates)
scores = [item["score"] for item in result]
assert scores == sorted(scores, reverse=True)

    def test_match_candidates_single_candidate(self, sample_job):
        """match_candidates should work with a single candidate."""
single = [
{
"id": "cand-solo",
"name": "Solo Dev",
"skills": ["Python", "FastAPI"],
"experience_years": 5,
"location": "Remote",
"expected_salary": 120000,
}
]
result = match_candidates(sample_job, single)
assert len(result) == 1
assert result[0]["candidate_id"] == "cand-solo"

    def test_match_candidates_includes_reasoning(self, sample_job, sample_candidates):
        """Each match result should include reasoning text."""
result = match_candidates(sample_job, sample_candidates)
for item in result:
            assert "reasoning" in item
assert isinstance(item["reasoning"], str)
assert len(item["reasoning"]) > 0

    def test_match_candidates_with_min_experience_filter(self, sample_job, sample_candidates):
        """Candidates below min experience should have lower scores or be filtered."""
result = match_candidates(sample_job, sample_candidates)
# Bob has 3 years, job requires 5 — should have a lower score
        bob_match = next(m for m in result if m["candidate_id"] == "cand-002")
alice_match = next(m for m in result if m["candidate_id"] == "cand-001")
assert bob_match["score"] <= alice_match["score"]

    def test_match_candidates_with_location_preference(self, sample_job, sample_candidates):
        """Remote candidates should score higher for a remote job."""
result = match_candidates(sample_job, sample_candidates)
remote_candidates = [c for c in sample_candidates if c["location"] == "Remote"]
non_remote = [c for c in sample_candidates if c["location"] != "Remote"]
if remote_candidates and non_remote:
            remote_scores = [
m["score"] for m in result if m["candidate_id"] in {c["id"] for c in remote_candidates}
]
non_remote_scores = [
m["score"] for m in result if m["candidate_id"] in {c["id"] for c in non_remote}
]
assert max(remote_scores) >= min(non_remote_scores)

    def test_match_candidates_does_not_mutate_inputs(self, sample_job, sample_candidates):
        """match_candidates should not mutate the input job or candidates."""
job_copy = {k: v for k, v in sample_job.items()}
candidates_copy = [{k: v for k, v in c.items()} for c in sample_candidates]
match_candidates(sample_job, sample_candidates)
assert sample_job == job_copy
assert sample_candidates == candidates_copy

    def test_match_candidates_with_large_candidate_pool(self, sample_job):
        """match_candidates should handle a large pool of candidates."""
large_pool = [
{
"id": f"cand-{i:03d}",
"name": f"Candidate {i}",
"skills": ["Python"] if i % 2 == 0 else ["Java"],
"experience_years": i,
"location": "Remote" if i % 3 == 0 else "On-site",
"expected_salary": 80000 + i * 1000,
}
for i in range(100)
]
result = match_candidates(sample_job, large_pool)
assert len(result) == 100


# ---------------------------------------------------------------------------
# Tests for rank_matches
# ---------------------------------------------------------------------------


class TestRankMatches:
    """Tests for the rank_matches function."""

    def test_rank_matches_returns_list(self, sample_job, sample_candidates):
        """rank_matches should return a list of ranked results."""
matches = match_candidates(sample_job, sample_candidates)
result = rank_matches(matches)
assert isinstance(result, list)

    def test_rank_matches_sorts_by_score_descending(self, sample_job, sample_candidates):
        """rank_matches should sort matches by score in descending order."""
matches = match_candidates(sample_job, sample_candidates)
result = rank_matches(matches)
scores = [m["score"] for m in result]
assert scores == sorted(scores, reverse=True)

    def test_rank_matches_preserves_all_items(self, sample_job, sample_candidates):
        """rank_matches should not drop any items."""
matches = match_candidates(sample_job, sample_candidates)
result = rank_matches(matches)
assert len(result) == len(matches)

    def test_rank_matches_empty_list(self):
        """rank_matches with an empty list should return an empty list."""
result = rank_matches([])
assert result == []

    def test_rank_matches_single_item(self):
        """rank_matches with a single item should return a single-item list."""
single = [{"candidate_id": "cand-001", "score": 0.9, "reasoning": "Good"}]
result = rank_matches(single)
assert len(result) == 1
assert result[0]["candidate_id"] == "cand-001"

    def test_rank_matches_includes_rank_field(self, sample_job, sample_candidates):
        """Each ranked result should include a rank field."""
matches = match_candidates(sample_job, sample_candidates)
result = rank_matches(matches)
for i, item in enumerate(result):
            assert "rank" in item
assert item["rank"] == i + 1

    def test_rank_matches_handles_tied_scores(self):
        """rank_matches should handle tied scores without errors."""
tied = [
{"candidate_id": "cand-001", "score": 0.85, "reasoning": "A"},
{"candidate_id": "cand-002", "score": 0.85, "reasoning": "B"},
{"candidate_id": "cand-003", "score": 0.85, "reasoning": "C"},
]
result = rank_matches(tied)
assert len(result) == 3
ranks = [m["rank"] for m in result]
assert ranks == [1, 2, 3]

    def test_rank_matches_does_not_mutate_input(self, sample_job, sample_candidates):
        """rank_matches should not mutate the input matches list."""
matches = match_candidates(sample_job, sample_candidates)
matches_copy = [dict(m) for m in matches]
rank_matches(matches)
assert matches == matches_copy

    def test_rank_matches_with_custom_weights(self, sample_job, sample_candidates):
        """rank_matches should accept custom scoring weights."""
matches = match_candidates(sample_job, sample_candidates)
weights = {"skills": 0.5, "experience": 0.3, "location": 0.2}
result = rank_matches(matches, weights=weights)
assert isinstance(result, list)
assert len(result) == len(matches)

    def test_rank_matches_stable_ordering(self, sample_job, sample_candidates):
        """rank_matches should produce stable ordering across multiple calls."""
matches = match_candidates(sample_job, sample_candidates)
result1 = rank_matches(matches)
result2 = rank_matches(matches)
assert result1 == result2


# ---------------------------------------------------------------------------
# Tests for get_top_matches
# ---------------------------------------------------------------------------


class TestGetTopMatches:
    """Tests for the get_top_matches function."""

    def test_get_top_matches_returns_list(self, sample_job, sample_candidates):
        """get_top_matches should return a list."""
result = get_top_matches(sample_job, sample_candidates, top_n=3)
assert isinstance(result, list)

    def test_get_top_matches_respects_top_n(self, sample_job, sample_candidates):
        """get_top_matches should return at most top_n results."""
result = get_top_matches(sample_job, sample_candidates, top_n=3)
assert len(result) <= 3

    def test_get_top_matches_returns_exact_count_when_enough_candidates(self, sample_job, sample_candidates):
        """get_top_matches should return exactly top_n when enough candidates exist."""
result = get_top_matches(sample_job, sample_candidates, top_n=3)
assert len(result) == 3

    def test_get_top_matches_returns_all_when_fewer_candidates(self, sample_job):
        """get_top_matches should return all candidates when fewer than top_n."""
few_candidates = [
{"id": "cand-001", "name": "Alice", "skills": ["Python"], "experience_years": 5, "location": "Remote", "expected_salary": 120000},
{"id": "cand-002", "name": "Bob", "skills": ["Java"], "experience_years": 3, "location": "NYC", "expected_salary": 90000},
]
result = get_top_matches(sample_job, few_candidates, top_n=5)
assert len(result) == 2

    def test_get_top_matches_empty_candidates(self, sample_job, empty_candidates):
        """get_top_matches with no candidates should return an empty list."""
result = get_top_matches(sample_job, empty_candidates, top_n=5)
assert result == []

    def test_get_top_matches_top_n_zero(self, sample_job, sample_candidates):
        """get_top_matches with top_n=0 should return an empty list."""
result = get_top_matches(sample_job, sample_candidates, top_n=0)
assert result == []

    def test_get_top_matches_top_n_one(self, sample_job, sample_candidates):
        """get_top_matches with top_n=1 should return exactly one result."""
result = get_top_matches(sample_job, sample_candidates, top_n=1)
assert len(result) == 1

    def test_get_top_matches_returns_highest_scored(self, sample_job, sample_candidates):
        """get_top_matches should return the highest-scoring candidates."""
all_matches = match_candidates(sample_job, sample_candidates)
all_matches_sorted = sorted(all_matches, key=lambda m: m["score"], reverse=True)
top_3 = get_top_matches(sample_job, sample_candidates, top_n=3)
expected_ids = {m["candidate_id"] for m in all_matches_sorted[:3]}
result_ids = {m["candidate_id"] for m in top_3}
assert result_ids == expected_ids

    def test_get_top_matches_includes_full_candidate_data(self, sample_job, sample_candidates):
        """get_top_matches results should include full candidate information."""
result = get_top_matches(sample_job, sample_candidates, top_n=2)
for item in result:
            assert "candidate_id" in item
assert "score" in item
assert "rank" in item

    def test_get_top_matches_with_threshold(self, sample_job, sample_candidates):
        """get_top_matches should respect a minimum score threshold."""
result = get_top_matches(sample_job, sample_candidates, top_n=10, min_score=0.5)
for item in result:
            assert item["score"] >= 0.5

    def test_get_top_matches_does_not_mutate_inputs(self, sample_job, sample_candidates):
        """get_top_matches should not mutate the input job or candidates."""
job_copy = {k: v for k, v in sample_job.items()}
candidates_copy = [{k: v for k, v in c.items()} for c in sample_candidates]
get_top_matches(sample_job, sample_candidates, top_n=3)
assert sample_job == job_copy
assert sample_candidates == candidates_copy

    def test_get_top_matches_default_top_n(self, sample_job, sample_candidates):
        """get_top_matches should use a sensible default top_n when not specified."""
result = get_top_matches(sample_job, sample_candidates)
assert isinstance(result, list)
assert len(result) > 0
assert len(result) <= len(sample_candidates)

    def test_get_top_matches_ordered_by_rank(self, sample_job, sample_candidates):
        """get_top_matches results should be ordered by rank."""
result = get_top_matches(sample_job, sample_candidates, top_n=3)
ranks = [m["rank"] for m in result]
assert ranks == sorted(ranks)

    def test_get_top_matches_with_large_top_n(self, sample_job, sample_candidates):
        """get_top_matches with top_n larger than candidate pool should return all."""
result = get_top_matches(sample_job, sample_candidates, top_n=100)
assert len(result) == len(sample_candidates)
