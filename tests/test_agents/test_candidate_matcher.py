"""Tests for candidate matcher agent."""

import pytest
from unittest.mock import MagicMock, patch


class TestCandidateMatcherAgent:
    """Test candidate matcher agent functionality."""

    def test_match_candidates_basic(self):
        """Test basic candidate matching."""
        from recruitment_platform.agents.candidate_matcher import SemanticMatcher
        
        matcher = SemanticMatcher()
        assert matcher is not None

    def test_match_candidates_with_job(self):
        """Test matching candidates to a job."""
        from recruitment_platform.agents.candidate_matcher import SemanticMatcher
        
        matcher = SemanticMatcher()
        job_requirements = ["Python", "FastAPI", "PostgreSQL"]
        candidate_skills = ["Python", "FastAPI", "Docker"]
        
        score = matcher.process(candidate_skills, job_requirements)
        assert isinstance(score, (int, float))
        assert 0 <= score <= 100

    def test_match_candidates_empty_requirements(self):
        """Test matching with empty requirements."""
        from recruitment_platform.agents.candidate_matcher import SemanticMatcher
        
        matcher = SemanticMatcher()
        score = matcher.process(["Python"], [])
        assert isinstance(score, (int, float))

    def test_match_candidates_no_match(self):
        """Test matching with no overlapping skills."""
        from recruitment_platform.agents.candidate_matcher import SemanticMatcher
        
        matcher = SemanticMatcher()
        score = matcher.process(["Python"], ["Java", "C++"])
        assert isinstance(score, (int, float))

    def test_bias_aware_ranking(self):
        """Test bias-aware ranking."""
        from recruitment_platform.agents.candidate_matcher import BiasAwareRanker
        
        ranker = BiasAwareRanker()
        assert ranker is not None

    def test_culture_fit_assessment(self):
        """Test culture fit assessment."""
        from recruitment_platform.agents.candidate_matcher import CultureFitAssessor
        
        assessor = CultureFitAssessor()
        assert assessor is not None
