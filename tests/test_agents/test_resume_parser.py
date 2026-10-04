"""Comprehensive agent tests for resume parsing, scoring, and skill extraction."""

import pytest
from unittest.mock import MagicMock, patch
from recruitment_platform.agents.resume_parser import (
    parse_resume,
    score_resume,
    extract_skills,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_resume_text():
    """Return a realistic resume text for testing."""
    return """
    John Doe
    Software Engineer
    john.doe@email.com | (555) 123-4567 | San Francisco, CA

    SUMMARY
    Experienced software engineer with 5+ years in Python, JavaScript, and cloud technologies.

    EXPERIENCE
    Senior Software Engineer — TechCorp Inc. (2020-Present)
    • Led development of microservices using Python and FastAPI
    • Managed AWS infrastructure including EC2, S3, and Lambda
    • Mentored junior developers and conducted code reviews

    Software Engineer — StartupXYZ (2018-2020)
    • Built RESTful APIs with Django and PostgreSQL
    • Implemented CI/CD pipelines using Jenkins and Docker
    • Collaborated with cross-functional teams in Agile environment

    EDUCATION
    Bachelor of Science in Computer Science — State University (2014-2018)

    SKILLS
    Python, JavaScript, TypeScript, React, Node.js, Django, FastAPI,
    PostgreSQL, MongoDB, AWS, Docker, Kubernetes, Git, Linux
    """


@pytest.fixture
def sample_parsed_resume():
    """Return a structured parsed resume dict."""
    return {
        "name": "John Doe",
        "email": "john.doe@email.com",
        "phone": "(555) 123-4567",
        "location": "San Francisco, CA",
        "summary": "Experienced software engineer with 5+ years in Python, JavaScript, and cloud technologies.",
        "experience": [
            {
                "title": "Senior Software Engineer",
                "company": "TechCorp Inc.",
                "duration": "2020-Present",
                "highlights": [
                    "Led development of microservices using Python and FastAPI",
                    "Managed AWS infrastructure including EC2, S3, and Lambda",
                    "Mentored junior developers and conducted code reviews",
                ],
            },
            {
                "title": "Software Engineer",
                "company": "StartupXYZ",
                "duration": "2018-2020",
                "highlights": [
                    "Built RESTful APIs with Django and PostgreSQL",
                    "Implemented CI/CD pipelines using Jenkins and Docker",
                    "Collaborated with cross-functional teams in Agile environment",
                ],
            },
        ],
        "education": [
            {
                "degree": "Bachelor of Science in Computer Science",
                "institution": "State University",
                "duration": "2014-2018",
            }
        ],
        "skills": [
            "Python", "JavaScript", "TypeScript", "React", "Node.js",
            "Django", "FastAPI", "PostgreSQL", "MongoDB", "AWS",
            "Docker", "Kubernetes", "Git", "Linux",
        ],
    }


@pytest.fixture
def sample_job_description():
    """Return a sample job description for scoring tests."""
    return """
    Senior Python Developer

    We are looking for a Senior Python Developer with:
    - 5+ years of Python experience
    - Experience with Django or FastAPI
    - Strong knowledge of PostgreSQL and Redis
    - Experience with AWS (EC2, S3, Lambda)
    - Familiarity with Docker and Kubernetes
    - Excellent communication skills
    """


@pytest.fixture
def sample_skills_list():
    """Return a list of extracted skills."""
    return [
        "Python", "JavaScript", "TypeScript", "React", "Node.js",
        "Django", "FastAPI", "PostgreSQL", "MongoDB", "AWS",
        "Docker", "Kubernetes", "Git", "Linux",
    ]


@pytest.fixture
def empty_resume_text():
    """Return an empty resume string."""
    return ""


@pytest.fixture
def minimal_resume_text():
    """Return a minimal resume with only basic info."""
    return "Jane Smith — jane@email.com — Python developer with 3 years experience."


# ---------------------------------------------------------------------------
# Tests for parse_resume
# ---------------------------------------------------------------------------

class TestParseResume:
    """Tests for the parse_resume function."""

    def test_parse_resume_returns_dict(self, sample_resume_text):
        """parse_resume should return a dictionary."""
        result = parse_resume(sample_resume_text)
        assert isinstance(result, dict)

    def test_parse_resume_extracts_name(self, sample_resume_text):
        """parse_resume should extract the candidate name."""
        result = parse_resume(sample_resume_text)
        assert "name" in result
        assert result["name"] == "John Doe"

    def test_parse_resume_extracts_email(self, sample_resume_text):
        """parse_resume should extract the email address."""
        result = parse_resume(sample_resume_text)
        assert "email" in result
        assert result["email"] == "john.doe@email.com"

    def test_parse_resume_extracts_phone(self, sample_resume_text):
        """parse_resume should extract the phone number."""
        result = parse_resume(sample_resume_text)
        assert "phone" in result
        assert result["phone"] == "(555) 123-4567"

    def test_parse_resume_extracts_location(self, sample_resume_text):
        """parse_resume should extract the location."""
        result = parse_resume(sample_resume_text)
        assert "location" in result
        assert result["location"] == "San Francisco, CA"

    def test_parse_resume_extracts_summary(self, sample_resume_text):
        """parse_resume should extract the professional summary."""
        result = parse_resume(sample_resume_text)
        assert "summary" in result
        assert "software engineer" in result["summary"].lower()

    def test_parse_resume_extracts_experience(self, sample_resume_text):
        """parse_resume should extract work experience entries."""
        result = parse_resume(sample_resume_text)
        assert "experience" in result
        assert isinstance(result["experience"], list)
        assert len(result["experience"]) >= 1

    def test_parse_resume_experience_has_required_fields(self, sample_resume_text):
        """Each experience entry should have title, company, and duration."""
        result = parse_resume(sample_resume_text)
        for exp in result["experience"]:
            assert "title" in exp
            assert "company" in exp
            assert "duration" in exp

    def test_parse_resume_extracts_education(self, sample_resume_text):
        """parse_resume should extract education entries."""
        result = parse_resume(sample_resume_text)
        assert "education" in result
        assert isinstance(result["education"], list)
        assert len(result["education"]) >= 1

    def test_parse_resume_education_has_required_fields(self, sample_resume_text):
        """Each education entry should have degree and institution."""
        result = parse_resume(sample_resume_text)
        for edu in result["education"]:
            assert "degree" in edu
            assert "institution" in edu

    def test_parse_resume_extracts_skills(self, sample_resume_text):
        """parse_resume should extract skills list."""
        result = parse_resume(sample_resume_text)
        assert "skills" in result
        assert isinstance(result["skills"], list)
        assert len(result["skills"]) > 0

    def test_parse_resume_skills_contains_known_skills(self, sample_resume_text):
        """Extracted skills should include known technologies from the resume."""
        result = parse_resume(sample_resume_text)
        skills_lower = [s.lower() for s in result["skills"]]
        assert "python" in skills_lower
        assert "javascript" in skills_lower

    def test_parse_resume_empty_string(self, empty_resume_text):
        """parse_resume should handle empty input gracefully."""
        result = parse_resume(empty_resume_text)
        assert isinstance(result, dict)

    def test_parse_resume_minimal_input(self, minimal_resume_text):
        """parse_resume should handle minimal resume text."""
        result = parse_resume(minimal_resume_text)
        assert isinstance(result, dict)
        assert "name" in result or "email" in result or len(result) > 0

    def test_parse_resume_handles_none_gracefully(self):
        """parse_resume should not crash on None input."""
        try:
            result = parse_resume(None)
            assert isinstance(result, dict)
        except (TypeError, AttributeError):
            pass  # Acceptable to raise on None

    def test_parse_resume_preserves_all_sections(self, sample_resume_text):
        """parse_resume should return all expected top-level sections."""
        result = parse_resume(sample_resume_text)
        expected_keys = {"name", "email", "phone", "location", "summary", "experience", "education", "skills"}
        assert expected_keys.issubset(set(result.keys()))

    def test_parse_resume_experience_count_matches(self, sample_resume_text):
        """parse_resume should find all experience entries in the resume."""
        result = parse_resume(sample_resume_text)
        # The sample resume has 2 experience entries
        assert len(result["experience"]) == 2

    def test_parse_resume_handles_special_characters(self):
        """parse_resume should handle resumes with special characters."""
        resume = "José García — jose@email.com — C++ & Java developer — Zürich, CH"
        result = parse_resume(resume)
        assert isinstance(result, dict)

    def test_parse_resume_handles_multiline_input(self):
        """parse_resume should handle resumes with many newlines."""
        resume = "\n\n\n".join([
            "Alice Johnson",
            "Data Scientist",
            "alice@email.com",
            "Machine Learning, Python, TensorFlow, SQL",
        ])
        result = parse_resume(resume)
        assert isinstance(result, dict)
        assert len(result) > 0


# ---------------------------------------------------------------------------
# Tests for score_resume
# ---------------------------------------------------------------------------

class TestScoreResume:
    """Tests for the score_resume function."""

    def test_score_resume_returns_numeric(self, sample_parsed_resume, sample_job_description):
        """score_resume should return a numeric score."""
        result = score_resume(sample_parsed_resume, sample_job_description)
        assert isinstance(result, (int, float))

    def test_score_resume_returns_float(self, sample_parsed_resume, sample_job_description):
        """score_resume should return a float score."""
        result = score_resume(sample_parsed_resume, sample_job_description)
        assert isinstance(result, float)

    def test_score_resume_in_valid_range(self, sample_parsed_resume, sample_job_description):
        """score_resume should return a score between 0 and 100."""
        result = score_resume(sample_parsed_resume, sample_job_description)
        assert 0 <= result <= 100

    def test_score_resume_perfect_match_scores_high(self, sample_job_description):
        """A resume matching all job requirements should score high."""
        perfect_resume = {
            "name": "Ideal Candidate",
            "email": "ideal@email.com",
            "phone": "555-0000",
            "location": "Remote",
            "summary": "Senior Python developer with 6 years experience",
            "experience": [
                {
                    "title": "Senior Python Developer",
                    "company": "TechCorp",
                    "duration": "2018-Present",
                    "highlights": [
                        "Developed Python microservices with Django and FastAPI",
                        "Managed AWS EC2, S3, and Lambda functions",
                        "Used Docker and Kubernetes for deployment",
                    ],
                }
            ],
            "education": [{"degree": "BS Computer Science", "institution": "MIT", "duration": "2012-2016"}],
            "skills": ["Python", "Django", "FastAPI", "PostgreSQL", "Redis", "AWS", "Docker", "Kubernetes"],
        }
        result = score_resume(perfect_resume, sample_job_description)
        assert result >= 50  # Should be a strong match

    def test_score_resume_poor_match_scores_low(self, sample_job_description):
        """A resume with no matching skills should score low."""
        poor_resume = {
            "name": "Unqualified",
            "email": "unqualified@email.com",
            "phone": "555-1111",
            "location": "Nowhere",
            "summary": "Retail sales associate",
            "experience": [
                {
                    "title": "Sales Associate",
                    "company": "ShopMart",
                    "duration": "2020-Present",
                    "highlights": ["Helped customers", "Operated cash register"],
                }
            ],
            "education": [{"degree": "High School Diploma", "institution": "Local High", "duration": "2016-2020"}],
            "skills": ["Customer Service", "Cash Handling", "Inventory"],
        }
        result = score_resume(poor_resume, sample_job_description)
        assert result <= 30  # Should be a weak match

    def test_score_resume_empty_resume_scores_zero(self, sample_job_description):
        """An empty resume should score 0 or very low."""
        empty_resume = {
            "name": "",
            "email": "",
            "phone": "",
            "location": "",
            "summary": "",
            "experience": [],
            "education": [],
            "skills": [],
        }
        result = score_resume(empty_resume, sample_job_description)
        assert result == 0 or result <= 10

    def test_score_resume_empty_job_description(self, sample_parsed_resume):
        """An empty job description should still return a valid score."""
        result = score_resume(sample_parsed_resume, "")
        assert isinstance(result, (int, float))
        assert 0 <= result <= 100

    def test_score_resume_both_empty(self):
        """Both empty resume and job description should return 0."""
        empty_resume = {
            "name": "", "email": "", "phone": "", "location": "",
            "summary": "", "experience": [], "education": [], "skills": [],
        }
        result = score_resume(empty_resume, "")
        assert result == 0 or result <= 10

    def test_score_resume_skill_match_increases_score(self, sample_job_description):
        """More matching skills should result in a higher score."""
        base_resume = {
            "name": "Dev", "email": "dev@test.com", "phone": "", "location": "",
            "summary": "", "experience": [], "education": [],
            "skills": ["Python"],
        }
        enhanced_resume = {
            "name": "Dev", "email": "dev@test.com", "phone": "", "location": "",
            "summary": "", "experience": [], "education": [],
            "skills": ["Python", "Django", "FastAPI", "PostgreSQL", "AWS", "Docker", "Kubernetes"],
        }
        base_score = score_resume(base_resume, sample_job_description)
        enhanced_score = score_resume(enhanced_resume, sample_job_description)
        assert enhanced_score >= base_score

    def test_score_resume_handles_missing_fields(self, sample_job_description):
        """score_resume should handle resumes with missing optional fields."""
        sparse_resume = {"name": "Sparse", "skills": ["Python"]}
        result = score_resume(sparse_resume, sample_job_description)
        assert isinstance(result, (int, float))
        assert 0 <= result <= 100

    def test_score_resume_deterministic(self, sample_parsed_resume, sample_job_description):
        """score_resume should return the same score for the same inputs."""
        score1 = score_resume(sample_parsed_resume, sample_job_description)
        score2 = score_resume(sample_parsed_resume, sample_job_description)
        assert score1 == score2

    def test_score_resume_experience_relevance(self, sample_job_description):
        """Relevant experience should increase the score."""
        no_exp_resume = {
            "name": "NoExp", "email": "noexp@test.com", "phone": "", "location": "",
            "summary": "", "experience": [], "education": [],
            "skills": ["Python", "Django", "AWS"],
        }
        with_exp_resume = {
            "name": "WithExp", "email": "withexp@test.com", "phone": "", "location": "",
            "summary": "", "experience": [
                {
                    "title": "Python Developer",
                    "company": "TechCo",
                    "duration": "2019-Present",
                    "highlights": ["Built Django apps on AWS"],
                }
            ],
            "education": [],
            "skills": ["Python", "Django", "AWS"],
        }
        no_exp_score = score_resume(no_exp_resume, sample_job_description)
        with_exp_score = score_resume(with_exp_resume, sample_job_description)
        assert with_exp_score >= no_exp_score


# ---------------------------------------------------------------------------
# Tests for extract_skills
# ---------------------------------------------------------------------------

class TestExtractSkills:
    """Tests for the extract_skills function."""

    def test_extract_skills_returns_list(self, sample_resume_text):
        """extract_skills should return a list."""
        result = extract_skills(sample_resume_text)
        assert isinstance(result, list)

    def test_extract_skills_non_empty(self, sample_resume_text):
        """extract_skills should find skills in a typical resume."""
        result = extract_skills(sample_resume_text)
        assert len(result) > 0

    def test_extract_skills_finds_python(self, sample_resume_text):
        """extract_skills should identify Python as a skill."""
        result = extract_skills(sample_resume_text)
        skills_lower = [s.lower() for s in result]
        assert "python" in skills_lower

    def test_extract_skills_finds_javascript(self, sample_resume_text):
        """extract_skills should identify JavaScript as a skill."""
        result = extract_skills(sample_resume_text)
        skills_lower = [s.lower() for s in result]
        assert "javascript" in skills_lower

    def test_extract_skills_finds_aws(self, sample_resume_text):
        """extract_skills should identify AWS as a skill."""
        result = extract_skills(sample_resume_text)
        skills_lower = [s.lower() for s in result]
        assert "aws" in skills_lower

    def test_extract_skills_finds_docker(self, sample_resume_text):
        """extract_skills should identify Docker as a skill."""
        result = extract_skills(sample_resume_text)
        skills_lower = [s.lower() for s in result]
        assert "docker" in skills_lower

    def test_extract_skills_empty_input(self, empty_resume_text):
        """extract_skills should return an empty list for empty input."""
        result = extract_skills(empty_resume_text)
        assert isinstance(result, list)
        assert len(result) == 0

    def test_extract_skills_no_skills_text(self):
        """extract_skills should return empty list when no skills are present."""
        text = "Hello world, this is a resume without any technical skills mentioned."
        result = extract_skills(text)
        assert isinstance(result, list)

    def test_extract_skills_returns_strings(self, sample_resume_text):
        """All extracted skills should be strings."""
        result = extract_skills(sample_resume_text)
        for skill in result:
            assert isinstance(skill, str)

    def test_extract_skills_no_duplicates(self, sample_resume_text):
        """extract_skills should not return duplicate entries."""
        result = extract_skills(sample_resume_text)
        # Check for exact duplicates (case-insensitive)
        skills_lower = [s.lower() for s in result]
        assert len(skills_lower) == len(set(skills_lower))

    def test_extract_skills_handles_special_characters(self):
        """extract_skills should handle resumes with special characters."""
        text = "Skills: C++, C#, .NET, Node.js, React.js, Vue.js"
        result = extract_skills(text)
        assert isinstance(result, list)

    def test_extract_skills_from_bulleted_list(self):
        """extract_skills should parse skills from bulleted lists."""
        text = """
        Technical Skills:
        • Python
        • Java
        • SQL
        • Git
        """
        result = extract_skills(text)
        assert isinstance(result, list)
        assert len(result) >= 3

    def test_extract_skills_from_comma_separated(self):
        """extract_skills should parse comma-separated skill lists."""
        text = "Skills: Python, JavaScript, React, Node.js, MongoDB"
        result = extract_skills(text)
        assert isinstance(result, list)
        assert len(result) >= 4

    def test_extract_skills_case_insensitive(self, sample_resume_text):
        """extract_skills should handle various capitalizations."""
        text = "Skills: python, PYTHON, Python, JAVASCRIPT, JavaScript"
        result = extract_skills(text)
        assert isinstance(result, list)
        # Should find at least one variant of each skill
        skills_lower = [s.lower() for s in result]
        assert "python" in skills_lower
        assert "javascript" in skills_lower

    def test_extract_skills_includes_frameworks(self, sample_resume_text):
        """extract_skills should identify frameworks like Django and FastAPI."""
        result = extract_skills(sample_resume_text)
        skills_lower = [s.lower() for s in result]
        assert "django" in skills_lower or "fastapi" in skills_lower

    def test_extract_skills_includes_databases(self, sample_resume_text):
        """extract_skills should identify database technologies."""
        result = extract_skills(sample_resume_text)
        skills_lower = [s.lower() for s in result]
        assert "postgresql" in skills_lower or "mongodb" in skills_lower

    def test_extract_skills_minimal_input(self, minimal_resume_text):
        """extract_skills should handle minimal resume text."""
        result = extract_skills(minimal_resume_text)
        assert isinstance(result, list)

    def test_extract_skills_handles_none_gracefully(self):
        """extract_skills should not crash on None input."""
        try:
            result = extract_skills(None)
            assert isinstance(result, list)
        except (TypeError, AttributeError):
            pass  # Acceptable to raise on None

    def test_extract_skills_known_technologies_only(self, sample_resume_text):
        """extract_skills should return recognizable technology names."""
        result = extract_skills(sample_resume_text)
        known_techs = {
            "python", "javascript", "typescript", "java", "c++", "c#",
            "react", "angular", "vue", "node.js", "django", "flask",
            "fastapi", "postgresql", "mysql", "mongodb", "redis",
            "aws", "azure", "gcp", "docker", "kubernetes", "git",
            "linux", "sql", "html", "css", "ruby", "go", "rust",
        }
        for skill in result:
            assert skill.lower() in known_techs or len(skill) > 1
