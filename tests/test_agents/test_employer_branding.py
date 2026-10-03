"""Comprehensive agent tests for employer branding functions.

Tests analyze_employer_brand, generate_employer_profile, and
suggest_brand_improvements from the recruitment_platform agents module.
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from typing import Any

from src.recruitment_platform.agents.employer_branding import (
    analyze_employer_brand,
    generate_employer_profile,
    suggest_brand_improvements,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_company_data() -> dict[str, Any]:
    """Return a representative company data payload for branding analysis."""
    return {
        "company_id": "comp-001",
        "company_name": "TechCorp",
        "industry": "Technology",
        "size": "500-1000",
        "location": "San Francisco, CA",
        "website": "https://techcorp.example.com",
        "description": "Leading provider of cloud infrastructure solutions.",
        "culture": "Innovative, collaborative, fast-paced",
        "values": ["Innovation", "Integrity", "Customer Focus"],
        "benefits": ["Health insurance", "Remote work", "Stock options"],
        "employee_reviews": [
            {"rating": 4.5, "text": "Great place to work"},
            {"rating": 3.8, "text": "Good work-life balance"},
        ],
        "social_media": {
            "linkedin": "https://linkedin.com/company/techcorp",
            "twitter": "@techcorp",
        },
    }


@pytest.fixture
def sample_brand_analysis() -> dict[str, Any]:
    """Return a representative brand analysis result."""
    return {
        "overall_score": 78,
        "strengths": ["Strong social presence", "Clear company values"],
        "weaknesses": ["Limited employee testimonials", "Outdated website"],
        "recommendations": [
            "Add more employee testimonials",
            "Refresh website design",
        ],
        "sentiment": "positive",
        "employer_brand_score": 78,
    }


@pytest.fixture
def sample_employer_profile() -> dict[str, Any]:
    """Return a representative employer profile result."""
    return {
        "profile_id": "prof-001",
        "company_name": "TechCorp",
        "tagline": "Building the future of cloud",
        "overview": "TechCorp is a leading cloud infrastructure provider.",
        "culture_summary": "Innovative and collaborative environment",
        "key_benefits": ["Health insurance", "Remote work", "Stock options"],
        "employee_count": "500-1000",
        "headquarters": "San Francisco, CA",
        "social_links": {
            "linkedin": "https://linkedin.com/company/techcorp",
            "twitter": "@techcorp",
        },
        "rating": 4.2,
        "review_count": 150,
    }


@pytest.fixture
def sample_improvements() -> dict[str, Any]:
    """Return a representative brand improvements suggestion result."""
    return {
        "improvements": [
            {
                "category": "content",
                "priority": "high",
                "suggestion": "Add video testimonials from employees",
                "impact": "Increase candidate engagement by 25%",
            },
            {
                "category": "social_media",
                "priority": "medium",
                "suggestion": "Increase posting frequency on LinkedIn",
                "impact": "Improve brand visibility",
            },
            {
                "category": "career_page",
                "priority": "high",
                "suggestion": "Redesign career page with modern UI",
                "impact": "Reduce bounce rate by 15%",
            },
        ],
        "overall_priority": "high",
        "estimated_improvement": "+15 points",
    }


@pytest.fixture
def mock_llm_response():
    """Return a mock LLM response for branding queries."""
    return {
        "content": "TechCorp has a strong employer brand with room for improvement.",
        "tokens_used": 150,
        "model": "gpt-4",
    }


# ---------------------------------------------------------------------------
# Tests for analyze_employer_brand
# ---------------------------------------------------------------------------


class TestAnalyzeEmployerBrand:
    """Tests for the analyze_employer_brand function."""

    @pytest.mark.asyncio
    async def test_analyze_employer_brand_returns_analysis(
        self, sample_company_data, sample_brand_analysis
    ):
        """analyze_employer_brand should return a brand analysis dict."""
        with patch(
            "src.recruitment_platform.agents.employer_branding._call_llm",
            new_callable=AsyncMock,
        ) as mock_llm:
            mock_llm.return_value = sample_brand_analysis

            result = await analyze_employer_brand(sample_company_data)

            assert result is not None
            assert isinstance(result, dict)
            assert "overall_score" in result
            assert "strengths" in result
            assert "weaknesses" in result
            assert "recommendations" in result

    @pytest.mark.asyncio
    async def test_analyze_employer_brand_calls_llm_with_company_data(
        self, sample_company_data, sample_brand_analysis
    ):
        """analyze_employer_brand should pass company data to the LLM."""
        with patch(
            "src.recruitment_platform.agents.employer_branding._call_llm",
            new_callable=AsyncMock,
        ) as mock_llm:
            mock_llm.return_value = sample_brand_analysis

            await analyze_employer_brand(sample_company_data)

            mock_llm.assert_called_once()
            call_args = mock_llm.call_args
            assert call_args is not None

    @pytest.mark.asyncio
    async def test_analyze_employer_brand_handles_minimal_data(self):
        """analyze_employer_brand should handle minimal company data."""
        minimal_data = {"company_name": "StartupCo"}
        expected = {
            "overall_score": 50,
            "strengths": [],
            "weaknesses": ["Insufficient data"],
            "recommendations": ["Provide more company information"],
        }

        with patch(
            "src.recruitment_platform.agents.employer_branding._call_llm",
            new_callable=AsyncMock,
        ) as mock_llm:
            mock_llm.return_value = expected

            result = await analyze_employer_brand(minimal_data)

            assert result["overall_score"] == 50
            assert "Insufficient data" in result["weaknesses"]

    @pytest.mark.asyncio
    async def test_analyze_employer_brand_handles_empty_data(self):
        """analyze_employer_brand should handle empty company data gracefully."""
        with patch(
            "src.recruitment_platform.agents.employer_branding._call_llm",
            new_callable=AsyncMock,
        ) as mock_llm:
            mock_llm.return_value = {
                "overall_score": 0,
                "strengths": [],
                "weaknesses": ["No data provided"],
                "recommendations": [],
            }

            result = await analyze_employer_brand({})

            assert result is not None
            assert result["overall_score"] == 0

    @pytest.mark.asyncio
    async def test_analyze_employer_brand_score_range(
        self, sample_company_data
    ):
        """analyze_employer_brand should return a score between 0 and 100."""
        with patch(
            "src.recruitment_platform.agents.employer_branding._call_llm",
            new_callable=AsyncMock,
        ) as mock_llm:
            mock_llm.return_value = {
                "overall_score": 85,
                "strengths": ["Strong brand"],
                "weaknesses": [],
                "recommendations": [],
            }

            result = await analyze_employer_brand(sample_company_data)

            assert 0 <= result["overall_score"] <= 100

    @pytest.mark.asyncio
    async def test_analyze_employer_brand_handles_llm_error(
        self, sample_company_data
    ):
        """analyze_employer_brand should handle LLM errors gracefully."""
        with patch(
            "src.recruitment_platform.agents.employer_branding._call_llm",
            new_callable=AsyncMock,
        ) as mock_llm:
            mock_llm.side_effect = Exception("LLM service unavailable")

            with pytest.raises(Exception, match="LLM service unavailable"):
                await analyze_employer_brand(sample_company_data)

    @pytest.mark.asyncio
    async def test_analyze_employer_brand_includes_sentiment(
        self, sample_company_data
    ):
        """analyze_employer_brand should include sentiment in the result."""
        with patch(
            "src.recruitment_platform.agents.employer_branding._call_llm",
            new_callable=AsyncMock,
        ) as mock_llm:
            mock_llm.return_value = {
                "overall_score": 72,
                "strengths": ["Good culture"],
                "weaknesses": ["Low social presence"],
                "recommendations": ["Improve LinkedIn"],
                "sentiment": "neutral",
            }

            result = await analyze_employer_brand(sample_company_data)

            assert "sentiment" in result
            assert result["sentiment"] in ("positive", "neutral", "negative")

    @pytest.mark.asyncio
    async def test_analyze_employer_brand_with_reviews(
        self, sample_company_data
    ):
        """analyze_employer_brand should factor in employee reviews."""
        with patch(
            "src.recruitment_platform.agents.employer_branding._call_llm",
            new_callable=AsyncMock,
        ) as mock_llm:
            mock_llm.return_value = {
                "overall_score": 80,
                "strengths": ["Positive reviews"],
                "weaknesses": [],
                "recommendations": [],
                "sentiment": "positive",
            }

            result = await analyze_employer_brand(sample_company_data)

            assert result["overall_score"] > 70


# ---------------------------------------------------------------------------
# Tests for generate_employer_profile
# ---------------------------------------------------------------------------


class TestGenerateEmployerProfile:
    """Tests for the generate_employer_profile function."""

    @pytest.mark.asyncio
    async def test_generate_employer_profile_returns_profile(
        self, sample_company_data, sample_employer_profile
    ):
        """generate_employer_profile should return a complete employer profile."""
        with patch(
            "src.recruitment_platform.agents.employer_branding._call_llm",
            new_callable=AsyncMock,
        ) as mock_llm:
            mock_llm.return_value = sample_employer_profile

            result = await generate_employer_profile(sample_company_data)

            assert result is not None
            assert isinstance(result, dict)
            assert "company_name" in result
            assert "overview" in result
            assert "culture_summary" in result

    @pytest.mark.asyncio
    async def test_generate_employer_profile_includes_key_fields(
        self, sample_company_data, sample_employer_profile
    ):
        """generate_employer_profile should include all expected fields."""
        with patch(
            "src.recruitment_platform.agents.employer_branding._call_llm",
            new_callable=AsyncMock,
        ) as mock_llm:
            mock_llm.return_value = sample_employer_profile

            result = await generate_employer_profile(sample_company_data)

            expected_fields = [
                "company_name",
                "tagline",
                "overview",
                "culture_summary",
                "key_benefits",
                "employee_count",
                "headquarters",
            ]
            for field in expected_fields:
                assert field in result, f"Missing field: {field}"

    @pytest.mark.asyncio
    async def test_generate_employer_profile_calls_llm(
        self, sample_company_data, sample_employer_profile
    ):
        """generate_employer_profile should invoke the LLM."""
        with patch(
            "src.recruitment_platform.agents.employer_branding._call_llm",
            new_callable=AsyncMock,
        ) as mock_llm:
            mock_llm.return_value = sample_employer_profile

            await generate_employer_profile(sample_company_data)

            mock_llm.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_employer_profile_handles_minimal_data(self):
        """generate_employer_profile should handle minimal company data."""
        minimal_data = {"company_name": "SmallCo"}
        expected = {
            "company_name": "SmallCo",
            "tagline": "",
            "overview": "No description available.",
            "culture_summary": "",
            "key_benefits": [],
            "employee_count": "Unknown",
            "headquarters": "Unknown",
        }

        with patch(
            "src.recruitment_platform.agents.employer_branding._call_llm",
            new_callable=AsyncMock,
        ) as mock_llm:
            mock_llm.return_value = expected

            result = await generate_employer_profile(minimal_data)

            assert result["company_name"] == "SmallCo"
            assert result["employee_count"] == "Unknown"

    @pytest.mark.asyncio
    async def test_generate_employer_profile_handles_empty_data(self):
        """generate_employer_profile should handle empty data gracefully."""
        with patch(
            "src.recruitment_platform.agents.employer_branding._call_llm",
            new_callable=AsyncMock,
        ) as mock_llm:
            mock_llm.return_value = {
                "company_name": "Unknown",
                "tagline": "",
                "overview": "",
                "culture_summary": "",
                "key_benefits": [],
                "employee_count": "Unknown",
                "headquarters": "Unknown",
            }

            result = await generate_employer_profile({})

            assert result is not None
            assert result["company_name"] == "Unknown"

    @pytest.mark.asyncio
    async def test_generate_employer_profile_handles_llm_error(
        self, sample_company_data
    ):
        """generate_employer_profile should propagate LLM errors."""
        with patch(
            "src.recruitment_platform.agents.employer_branding._call_llm",
            new_callable=AsyncMock,
        ) as mock_llm:
            mock_llm.side_effect = Exception("LLM timeout")

            with pytest.raises(Exception, match="LLM timeout"):
                await generate_employer_profile(sample_company_data)

    @pytest.mark.asyncio
    async def test_generate_employer_profile_includes_social_links(
        self, sample_company_data, sample_employer_profile
    ):
        """generate_employer_profile should include social media links."""
        with patch(
            "src.recruitment_platform.agents.employer_branding._call_llm",
            new_callable=AsyncMock,
        ) as mock_llm:
            mock_llm.return_value = sample_employer_profile

            result = await generate_employer_profile(sample_company_data)

            assert "social_links" in result
            assert "linkedin" in result["social_links"]

    @pytest.mark.asyncio
    async def test_generate_employer_profile_with_full_data(
        self, sample_company_data, sample_employer_profile
    ):
        """generate_employer_profile should produce rich output for full data."""
        with patch(
            "src.recruitment_platform.agents.employer_branding._call_llm",
            new_callable=AsyncMock,
        ) as mock_llm:
            mock_llm.return_value = sample_employer_profile

            result = await generate_employer_profile(sample_company_data)

            assert result["company_name"] == "TechCorp"
            assert len(result["key_benefits"]) > 0
            assert result["employee_count"] == "500-1000"


# ---------------------------------------------------------------------------
# Tests for suggest_brand_improvements
# ---------------------------------------------------------------------------


class TestSuggestBrandImprovements:
    """Tests for the suggest_brand_improvements function."""

    @pytest.mark.asyncio
    async def test_suggest_brand_improvements_returns_suggestions(
        self, sample_company_data, sample_improvements
    ):
        """suggest_brand_improvements should return improvement suggestions."""
        with patch(
            "src.recruitment_platform.agents.employer_branding._call_llm",
            new_callable=AsyncMock,
        ) as mock_llm:
            mock_llm.return_value = sample_improvements

            result = await suggest_brand_improvements(sample_company_data)

            assert result is not None
            assert isinstance(result, dict)
            assert "improvements" in result
            assert len(result["improvements"]) > 0

    @pytest.mark.asyncio
    async def test_suggest_brand_improvements_calls_llm(
        self, sample_company_data, sample_improvements
    ):
        """suggest_brand_improvements should invoke the LLM."""
        with patch(
            "src.recruitment_platform.agents.employer_branding._call_llm",
            new_callable=AsyncMock,
        ) as mock_llm:
            mock_llm.return_value = sample_improvements

            await suggest_brand_improvements(sample_company_data)

            mock_llm.assert_called_once()

    @pytest.mark.asyncio
    async def test_suggest_brand_improvements_includes_priorities(
        self, sample_company_data, sample_improvements
    ):
        """suggest_brand_improvements should include priority levels."""
        with patch(
            "src.recruitment_platform.agents.employer_branding._call_llm",
            new_callable=AsyncMock,
        ) as mock_llm:
            mock_llm.return_value = sample_improvements

            result = await suggest_brand_improvements(sample_company_data)

            for improvement in result["improvements"]:
                assert "priority" in improvement
                assert improvement["priority"] in ("high", "medium", "low")

    @pytest.mark.asyncio
    async def test_suggest_brand_improvements_includes_categories(
        self, sample_company_data, sample_improvements
    ):
        """suggest_brand_improvements should categorize suggestions."""
        with patch(
            "src.recruitment_platform.agents.employer_branding._call_llm",
            new_callable=AsyncMock,
        ) as mock_llm:
            mock_llm.return_value = sample_improvements

            result = await suggest_brand_improvements(sample_company_data)

            for improvement in result["improvements"]:
                assert "category" in improvement
                assert "suggestion" in improvement

    @pytest.mark.asyncio
    async def test_suggest_brand_improvements_handles_minimal_data(self):
        """suggest_brand_improvements should handle minimal company data."""
        minimal_data = {"company_name": "NewCo"}
        expected = {
            "improvements": [
                {
                    "category": "general",
                    "priority": "high",
                    "suggestion": "Build employer brand from scratch",
                    "impact": "Establish foundation",
                }
            ],
            "overall_priority": "high",
            "estimated_improvement": "+20 points",
        }

        with patch(
            "src.recruitment_platform.agents.employer_branding._call_llm",
            new_callable=AsyncMock,
        ) as mock_llm:
            mock_llm.return_value = expected

            result = await suggest_brand_improvements(minimal_data)

            assert len(result["improvements"]) > 0
            assert result["overall_priority"] == "high"

    @pytest.mark.asyncio
    async def test_suggest_brand_improvements_handles_empty_data(self):
        """suggest_brand_improvements should handle empty data gracefully."""
        with patch(
            "src.recruitment_platform.agents.employer_branding._call_llm",
            new_callable=AsyncMock,
        ) as mock_llm:
            mock_llm.return_value = {
                "improvements": [],
                "overall_priority": "low",
                "estimated_improvement": "0 points",
            }

            result = await suggest_brand_improvements({})

            assert result is not None
            assert isinstance(result["improvements"], list)

    @pytest.mark.asyncio
    async def test_suggest_brand_improvements_handles_llm_error(
        self, sample_company_data
    ):
        """suggest_brand_improvements should propagate LLM errors."""
        with patch(
            "src.recruitment_platform.agents.employer_branding._call_llm",
            new_callable=AsyncMock,
        ) as mock_llm:
            mock_llm.side_effect = Exception("LLM rate limit exceeded")

            with pytest.raises(Exception, match="LLM rate limit exceeded"):
                await suggest_brand_improvements(sample_company_data)

    @pytest.mark.asyncio
    async def test_suggest_brand_improvements_includes_impact(
        self, sample_company_data, sample_improvements
    ):
        """suggest_brand_improvements should include expected impact."""
        with patch(
            "src.recruitment_platform.agents.employer_branding._call_llm",
            new_callable=AsyncMock,
        ) as mock_llm:
            mock_llm.return_value = sample_improvements

            result = await suggest_brand_improvements(sample_company_data)

            for improvement in result["improvements"]:
                assert "impact" in improvement
                assert len(improvement["impact"]) > 0

    @pytest.mark.asyncio
    async def test_suggest_brand_improvements_overall_priority(
        self, sample_company_data, sample_improvements
    ):
        """suggest_brand_improvements should include an overall priority."""
        with patch(
            "src.recruitment_platform.agents.employer_branding._call_llm",
            new_callable=AsyncMock,
        ) as mock_llm:
            mock_llm.return_value = sample_improvements

            result = await suggest_brand_improvements(sample_company_data)

            assert "overall_priority" in result
            assert result["overall_priority"] in ("high", "medium", "low")

    @pytest.mark.asyncio
    async def test_suggest_brand_improvements_estimated_improvement(
        self, sample_company_data, sample_improvements
    ):
        """suggest_brand_improvements should include estimated improvement."""
        with patch(
            "src.recruitment_platform.agents.employer_branding._call_llm",
            new_callable=AsyncMock,
        ) as mock_llm:
            mock_llm.return_value = sample_improvements

            result = await suggest_brand_improvements(sample_company_data)

            assert "estimated_improvement" in result
            assert result["estimated_improvement"] is not None
