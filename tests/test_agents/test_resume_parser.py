"""Tests for resume parser agent."""

import pytest
from unittest.mock import MagicMock, patch


class TestResumeParserAgent:
    """Test resume parser agent functionality."""

    def test_parse_resume_basic(self):
        """Test basic resume parsing."""
        import asyncio
        from recruitment_platform.agents.resume_parser import ResumeParserAgent
        
        agent = ResumeParserAgent()
        assert agent is not None
        assert hasattr(agent, "process")

    def test_parse_resume_with_text(self):
        """Test parsing resume from text."""
        from recruitment_platform.agents.resume_parser import ResumeParserAgent
        
        agent = ResumeParserAgent()
        resume_text = """
        John Doe
        Software Engineer
        Skills: Python, JavaScript, SQL
        Experience: 5 years
        """
        
        result = agent.process(resume_text)
        assert result is not None

    def test_score_resume(self):
        """Test resume scoring."""
        import asyncio
        from recruitment_platform.agents.resume_parser import ResumeParserAgent
        
        agent = ResumeParserAgent()
        input_data = {
            "resume_text": "Python developer with 5 years experience",
            "job_requirements": ["Python", "5 years"],
        }
        
        result = asyncio.run(agent.process(input_data))
        assert isinstance(result, dict)

    def test_extract_skills(self):
        """Test skill extraction from resume."""
        import asyncio
        from recruitment_platform.agents.resume_parser import ResumeParserAgent
        
        agent = ResumeParserAgent()
        input_data = {"resume_text": "Experienced in Python, FastAPI, PostgreSQL, Docker"}
        
        result = asyncio.run(agent.process(input_data))
        assert isinstance(result, dict)

    def test_parse_resume_empty_input(self):
        """Test parsing empty resume."""
        from recruitment_platform.agents.resume_parser import ResumeParserAgent
        
        agent = ResumeParserAgent()
        result = agent.process("")
        assert result is not None

    def test_parse_resume_invalid_input(self):
        """Test parsing invalid resume input."""
        from recruitment_platform.agents.resume_parser import ResumeParserAgent
        
        agent = ResumeParserAgent()
        result = agent.process(None)
        assert result is not None
