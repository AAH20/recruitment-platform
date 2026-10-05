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
        import asyncio
        from recruitment_platform.agents.candidate_matcher import SemanticMatcher
        
        matcher = SemanticMatcher()
        input_data = {
            "candidate_skills": ["Python", "FastAPI", "Docker"],
            "job_requirements": ["Python", "FastAPI", "PostgreSQL"],
        }
        
        result = asyncio.run(matcher.process(input_data))
        assert isinstance(result, dict)

    def test_match_candidates_empty_requirements(self):
        """Test matching with empty requirements."""
        import asyncio
        from recruitment_platform.agents.candidate_matcher import SemanticMatcher
        
        matcher = SemanticMatcher()
        input_data = {"candidate_skills": ["Python"], "job_requirements": []}
        
        result = asyncio.run(matcher.process(input_data))
        assert isinstance(result, dict)

    def test_match_candidates_no_match(self):
        """Test matching with no overlapping skills."""
        import asyncio
        from recruitment_platform.agents.candidate_matcher import SemanticMatcher
        
        matcher = SemanticMatcher()
        input_data = {"candidate_skills": ["Python"], "job_requirements": ["Java", "C++"]}
        
        result = asyncio.run(matcher.process(input_data))
        assert isinstance(result, dict)

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
