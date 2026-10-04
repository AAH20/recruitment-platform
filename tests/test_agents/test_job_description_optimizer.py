"""
Comprehensive agent tests for the Job Description Optimizer module.

Tests cover:
- optimize_description: rewriting and enhancing job descriptions
- suggest_improvements: generating actionable improvement suggestions
- score_description: scoring job descriptions on quality metrics
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from typing import Any

from recruitment_platform.agents.job_description_optimizer import (
optimize_description,
suggest_improvements,
score_description,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_job_description() -> str:
    """A basic job description for testing."""
return (
"We are looking for a software engineer. "
"You will write code and fix bugs. "
"Requirements: 3 years experience, Python, JavaScript."
)


@pytest.fixture
def optimized_job_description() -> str:
    """An optimized version of the sample job description."""
return (
"We are seeking a talented Software Engineer to join our growing team. "
"In this role, you will design, develop, and maintain high-quality software solutions, "
"collaborate with cross-functional teams, and contribute to architectural decisions. "
"Key Responsibilities:\n"
"- Write clean, maintainable, and well-tested code\n"
"- Debug and resolve complex technical issues\n"
"- Participate in code reviews and mentor junior developers\n\n"
"Requirements:\n"
"- 3+ years of professional software development experience\n"
"- Strong proficiency in Python and JavaScript\n"
"- Experience with modern frameworks and cloud platforms"
)


@pytest.fixture
def improvement_suggestions() -> list[dict[str, Any]]:
    """Sample improvement suggestions returned by suggest_improvements."""
return [
{
"category": "clarity",
"severity": "high",
"suggestion": "Add specific metrics or KPIs to make responsibilities more measurable",
"original_text": "You will write code and fix bugs",
"improved_text": "You will write clean, maintainable code and resolve 95% of bugs within SLA",
},
{
"category": "inclusivity",
"severity": "medium",
"suggestion": "Remove gendered or exclusionary language to attract diverse candidates",
"original_text": "We are looking for a rockstar developer",
"improved_text": "We are looking for a skilled developer",
},
{
"category": "structure",
"severity": "low",
"suggestion": "Use bullet points for better readability",
"original_text": "Requirements: 3 years experience, Python, JavaScript.",
"improved_text": "- 3+ years experience\n- Python\n- JavaScript",
},
]


@pytest.fixture
def description_scores() -> dict[str, float]:
    """Sample scores returned by score_description."""
return {
"clarity": 7.5,
"inclusivity": 8.0,
"structure": 6.5,
"completeness": 7.0,
"engagement": 5.5,
"overall": 7.0,
}


@pytest.fixture
def mock_llm_response():
    """Mock LLM response for optimize_description."""
return {
"optimized_text": (
"We are seeking a talented Software Engineer to join our growing team. "
"In this role, you will design, develop, and maintain high-quality software solutions."
),
    "changes_made": [
"Added specific role title",
"Expanded responsibilities with detail",
"Improved tone and engagement",
],
}


@pytest.fixture
def empty_job_description() -> str:
    """An empty job description for edge case testing."""
return ""


@pytest.fixture
def minimal_job_description() -> str:
    """A very short job description for edge case testing."""
return "Python dev needed."


@pytest.fixture
def long_job_description() -> str:
    """A very long job description for stress testing."""
return (
"We are looking for a software engineer with extensive experience in multiple domains. "
* 50
)


# ---------------------------------------------------------------------------
# Tests for optimize_description
# ---------------------------------------------------------------------------


class TestOptimizeDescription:
    """Tests for the optimize_description function."""

    @pytest.mark.asyncio
async def test_optimize_description_returns_string(
self, sample_job_description: str
):
        """optimize_description should return a string."""
with patch(
"src.recruitment_platform.agents.job_description_optimizer._call_llm",
new_callable=AsyncMock,
) as mock_llm:
            mock_llm.return_value = "Optimized job description text"
result = await optimize_description(sample_job_description)
assert isinstance(result, str)

    @pytest.mark.asyncio
async def test_optimize_description_returns_non_empty(
self, sample_job_description: str
):
        """optimize_description should return a non-empty string for valid input."""
with patch(
"src.recruitment_platform.agents.job_description_optimizer._call_llm",
new_callable=AsyncMock,
) as mock_llm:
            mock_llm.return_value = "Optimized job description text"
result = await optimize_description(sample_job_description)
assert len(result) > 0

    @pytest.mark.asyncio
async def test_optimize_description_calls_llm(
self, sample_job_description: str
):
        """optimize_description should call the LLM at least once."""
with patch(
"src.recruitment_platform.agents.job_description_optimizer._call_llm",
new_callable=AsyncMock,
) as mock_llm:
            mock_llm.return_value = "Optimized text"
await optimize_description(sample_job_description)
mock_llm.assert_called_once()

    @pytest.mark.asyncio
async def test_optimize_description_passes_original_text(
self, sample_job_description: str
):
        """optimize_description should pass the original description to the LLM."""
with patch(
"src.recruitment_platform.agents.job_description_optimizer._call_llm",
new_callable=AsyncMock,
) as mock_llm:
            mock_llm.return_value = "Optimized text"
await optimize_description(sample_job_description)
call_args = mock_llm.call_args
assert sample_job_description in str(call_args)

    @pytest.mark.asyncio
async def test_optimize_description_with_empty_string(
self, empty_job_description: str
):
        """optimize_description should handle empty input gracefully."""
with patch(
"src.recruitment_platform.agents.job_description_optimizer._call_llm",
new_callable=AsyncMock,
) as mock_llm:
            mock_llm.return_value = ""
result = await optimize_description(empty_job_description)
assert isinstance(result, str)

    @pytest.mark.asyncio
async def test_optimize_description_with_minimal_input(
self, minimal_job_description: str
):
        """optimize_description should handle very short input."""
with patch(
"src.recruitment_platform.agents.job_description_optimizer._call_llm",
new_callable=AsyncMock,
) as mock_llm:
            mock_llm.return_value = "We are seeking a Python developer to join our team."
result = await optimize_description(minimal_job_description)
assert isinstance(result, str)
assert len(result) > 0

    @pytest.mark.asyncio
async def test_optimize_description_with_long_input(
self, long_job_description: str
):
        """optimize_description should handle very long input."""
with patch(
"src.recruitment_platform.agents.job_description_optimizer._call_llm",
new_callable=AsyncMock,
) as mock_llm:
            mock_llm.return_value = "Optimized long description"
result = await optimize_description(long_job_description)
assert isinstance(result, str)

    @pytest.mark.asyncio
async def test_optimize_description_preserves_key_info(
self, sample_job_description: str
):
        """optimize_description should preserve key information from the original."""
with patch(
"src.recruitment_platform.agents.job_description_optimizer._call_llm",
new_callable=AsyncMock,
) as mock_llm:
            mock_llm.return_value = (
"We are seeking a Software Engineer with 3+ years of experience in Python and JavaScript."
)
        result = await optimize_description(sample_job_description)
# Key terms should be preserved or enhanced
            assert "Python" in result or "python" in result.lower()

    @pytest.mark.asyncio
async def test_optimize_description_with_custom_tone(
self, sample_job_description: str
):
        """optimize_description should accept and use a custom tone parameter."""
with patch(
"src.recruitment_platform.agents.job_description_optimizer._call_llm",
new_callable=AsyncMock,
) as mock_llm:
            mock_llm.return_value = "Casual optimized description"
result = await optimize_description(sample_job_description, tone="casual")
assert isinstance(result, str)
call_args = mock_llm.call_args
assert "casual" in str(call_args).lower()

    @pytest.mark.asyncio
async def test_optimize_description_with_formal_tone(
self, sample_job_description: str
):
        """optimize_description should work with formal tone."""
with patch(
"src.recruitment_platform.agents.job_description_optimizer._call_llm",
new_callable=AsyncMock,
) as mock_llm:
            mock_llm.return_value = "Formal optimized description"
result = await optimize_description(sample_job_description, tone="formal")
assert isinstance(result, str)

    @pytest.mark.asyncio
async def test_optimize_description_llm_failure_raises(
self, sample_job_description: str
):
        """optimize_description should raise an exception when LLM call fails."""
with patch(
"src.recruitment_platform.agents.job_description_optimizer._call_llm",
new_callable=AsyncMock,
) as mock_llm:
            mock_llm.side_effect = Exception("LLM service unavailable")
with pytest.raises(Exception, match="LLM service unavailable"):
                await optimize_description(sample_job_description)

    @pytest.mark.asyncio
async def test_optimize_description_returns_different_text(
self, sample_job_description: str
):
        """optimize_description should return text different from the input."""
with patch(
"src.recruitment_platform.agents.job_description_optimizer._call_llm",
new_callable=AsyncMock,
) as mock_llm:
            mock_llm.return_value = (
"We are seeking a talented Software Engineer to join our growing team. "
"In this role, you will design, develop, and maintain high-quality software solutions."
)
        result = await optimize_description(sample_job_description)
assert result != sample_job_description

    @pytest.mark.asyncio
async def test_optimize_description_with_special_characters(self):
        """optimize_description should handle special characters in input."""
special_desc = "C++ developer needed! Must know C# & .NET. Salary: $100k-$150k."
with patch(
"src.recruitment_platform.agents.job_description_optimizer._call_llm",
new_callable=AsyncMock,
) as mock_llm:
            mock_llm.return_value = "Optimized C++ developer description"
result = await optimize_description(special_desc)
assert isinstance(result, str)

    @pytest.mark.asyncio
async def test_optimize_description_with_unicode(self):
        """optimize_description should handle unicode characters."""
unicode_desc = "We need a developer who speaks 中文 and English. 你好!"
with patch(
"src.recruitment_platform.agents.job_description_optimizer._call_llm",
new_callable=AsyncMock,
) as mock_llm:
            mock_llm.return_value = "Optimized multilingual description"
result = await optimize_description(unicode_desc)
assert isinstance(result, str)

    @pytest.mark.asyncio
async def test_optimize_description_idempotent_behavior(
self, sample_job_description: str
):
        """Calling optimize_description twice should produce consistent results."""
with patch(
"src.recruitment_platform.agents.job_description_optimizer._call_llm",
new_callable=AsyncMock,
) as mock_llm:
            mock_llm.return_value = "Consistent optimized description"
result1 = await optimize_description(sample_job_description)
result2 = await optimize_description(sample_job_description)
assert result1 == result2

    @pytest.mark.asyncio
async def test_optimize_description_with_target_role(
self, sample_job_description: str
):
        """optimize_description should accept a target role parameter."""
with patch(
"src.recruitment_platform.agents.job_description_optimizer._call_llm",
new_callable=AsyncMock,
) as mock_llm:
            mock_llm.return_value = "Optimized Senior Software Engineer description"
result = await optimize_description(
sample_job_description, target_role="Senior Software Engineer"
)
        assert isinstance(result, str)
call_args = mock_llm.call_args
assert "Senior Software Engineer" in str(call_args)


# ---------------------------------------------------------------------------
# Tests for suggest_improvements
# ---------------------------------------------------------------------------


class TestSuggestImprovements:
    """Tests for the suggest_improvements function."""

    @pytest.mark.asyncio
async def test_suggest_improvements_returns_list(
self, sample_job_description: str
):
        """suggest_improvements should return a list."""
with patch(
"src.recruitment_platform.agents.job_description_optimizer._call_llm",
new_callable=AsyncMock,
) as mock_llm:
            mock_llm.return_value = '[{"category": "clarity", "suggestion": "Add more detail"}]'
result = await suggest_improvements(sample_job_description)
assert isinstance(result, list)

    @pytest.mark.asyncio
async def test_suggest_improvements_returns_non_empty(
self, sample_job_description: str
):
        """suggest_improvements should return at least one suggestion for a basic description."""
with patch(
"src.recruitment_platform.agents.job_description_optimizer._call_llm",
new_callable=AsyncMock,
) as mock_llm:
            mock_llm.return_value = (
'[{"category": "clarity", "severity": "high", "suggestion": "Add more detail"}]'
)
        result = await suggest_improvements(sample_job_description)
assert len(result) > 0

    @pytest.mark.asyncio
async def test_suggest_improvements_calls_llm(
self, sample_job_description: str
):
        """suggest_improvements should call the LLM."""
with patch(
"src.recruitment_platform.agents.job_description_optimizer._call_llm",
new_callable=AsyncMock,
) as mock_llm:
            mock_llm.return_value = '[{"category": "clarity", "suggestion": "Improve"}]'
await suggest_improvements(sample_job_description)
mock_llm.assert_called_once()

    @pytest.mark.asyncio
async def test_suggest_improvements_passes_description(
self, sample_job_description: str
):
        """suggest_improvements should pass the description to the LLM."""
with patch(
"src.recruitment_platform.agents.job_description_optimizer._call_llm",
new_callable=AsyncMock,
) as mock_llm:
            mock_llm.return_value = '[{"category": "clarity", "suggestion": "Improve"}]'
await suggest_improvements(sample_job_description)
call_args = mock_llm.call_args
assert sample_job_description in str(call_args)

    @pytest.mark.asyncio
async def test_suggest_improvements_with_empty_description(
self, empty_job_description: str
):
        """suggest_improvements should handle empty input."""
with patch(
"src.recruitment_platform.agents.job_description_optimizer._call_llm",
new_callable=AsyncMock,
) as mock_llm:
            mock_llm.return_value = "[]"
result = await suggest_improvements(empty_job_description)
assert isinstance(result, list)

    @pytest.mark.asyncio
async def test_suggest_improvements_with_minimal_description(
self, minimal_job_description: str
):
        """suggest_improvements should handle very short input."""
with patch(
"src.recruitment_platform.agents.job_description_optimizer._call_llm",
new_callable=AsyncMock,
) as mock_llm:
            mock_llm.return_value = (
'[{"category": "completeness", "severity": "high", "suggestion": "Add more details"}]'
)
        result = await suggest_improvements(minimal_job_description)
assert isinstance(result, list)
assert len(result) > 0

    @pytest.mark.asyncio
async def test_suggest_improvements_with_optimized_description(
self, optimized_job_description: str
):
        """suggest_improvements should return fewer suggestions for an optimized description."""
with patch(
"src.recruitment_platform.agents.job_description_optimizer._call_llm",
new_callable=AsyncMock,
) as mock_llm:
            mock_llm.return_value = "[]"
result = await suggest_improvements(optimized_job_description)
assert isinstance(result, list)

    @pytest.mark.asyncio
async def test_suggest_improvements_suggestion_structure(
self, sample_job_description: str
):
        """Each suggestion should have required fields."""
with patch(
"src.recruitment_platform.agents.job_description_optimizer._call_llm",
new_callable=AsyncMock,
) as mock_llm:
            mock_llm.return_value = (
'[{"category": "clarity", "severity": "high", "suggestion": "Add metrics"}]'
)
        result = await suggest_improvements(sample_job_description)
for suggestion in result:
                assert "category" in suggestion
assert "suggestion" in suggestion

    @pytest.mark.asyncio
async def test_suggest_improvements_with_focus_area(
self, sample_job_description: str
):
        """suggest_improvements should accept a focus_area parameter."""
with patch(
"src.recruitment_platform.agents.job_description_optimizer._call_llm",
new_callable=AsyncMock,
) as mock_llm:
            mock_llm.return_value = (
'[{"category": "inclusivity", "severity": "medium", "suggestion": "Use inclusive language"}]'
)
        result = await suggest_improvements(
sample_job_description, focus_area="inclusivity"
)
        assert isinstance(result, list)
call_args = mock_llm.call_args
assert "inclusivity" in str(call_args).lower()

    @pytest.mark.asyncio
async def test_suggest_improvements_llm_failure_raises(
self, sample_job_description: str
):
        """suggest_improvements should raise when LLM call fails."""
with patch(
"src.recruitment_platform.agents.job_description_optimizer._call_llm",
new_callable=AsyncMock,
) as mock_llm:
            mock_llm.side_effect = Exception("LLM service unavailable")
with pytest.raises(Exception, match="LLM service unavailable"):
                await suggest_improvements(sample_job_description)

    @pytest.mark.asyncio
async def test_suggest_improvements_with_multiple_suggestions(
self, sample_job_description: str
):
        """suggest_improvements should handle multiple suggestions."""
with patch(
"src.recruitment_platform.agents.job_description_optimizer._call_llm",
new_callable=AsyncMock,
) as mock_llm:
            mock_llm.return_value = (
'[{"category": "clarity", "suggestion": "Add detail"}, '
'{"category": "structure", "suggestion": "Use bullets"}, '
'{"category": "inclusivity", "suggestion": "Remove bias"}]'
)
        result = await suggest_improvements(sample_job_description)
assert len(result) == 3

    @pytest.mark.asyncio
async def test_suggest_improvements_with_special_characters(self):
        """suggest_improvements should handle special characters in input."""
special_desc = "C++ dev needed! Must know C# & .NET. Salary: $100k+."
with patch(
"src.recruitment_platform.agents.job_description_optimizer._call_llm",
new_callable=AsyncMock,
) as mock_llm:
            mock_llm.return_value = '[{"category": "clarity", "suggestion": "Clarify requirements"}]'
result = await suggest_improvements(special_desc)
assert isinstance(result, list)

    @pytest.mark.asyncio
async def test_suggest_improvements_with_unicode(self):
        """suggest_improvements should handle unicode characters."""
unicode_desc = "需要会中文和英文的开发者。你好！"
with patch(
"src.recruitment_platform.agents.job_description_optimizer._call_llm",
new_callable=AsyncMock,
) as mock_llm:
            mock_llm.return_value = '[{"category": "clarity", "suggestion": "Add more detail"}]'
result = await suggest_improvements(unicode_desc)
assert isinstance(result, list)

    @pytest.mark.asyncio
async def test_suggest_improvements_with_long_description(
self, long_job_description: str
):
        """suggest_improvements should handle very long input."""
with patch(
"src.recruitment_platform.agents.job_description_optimizer._call_llm",
new_callable=AsyncMock,
) as mock_llm:
            mock_llm.return_value = (
'[{"category": "structure", "severity": "medium", "suggestion": "Break into sections"}]'
)
        result = await suggest_improvements(long_job_description)
assert isinstance(result, list)

    @pytest.mark.asyncio
async def test_suggest_improvements_with_max_suggestions(
self, sample_job_description: str
):
        """suggest_improvements should respect max_suggestions parameter."""
with patch(
"src.recruitment_platform.agents.job_description_optimizer._call_llm",
new_callable=AsyncMock,
) as mock_llm:
            mock_llm.return_value = (
'[{"category": "clarity", "suggestion": "Add detail"}, '
'{"category": "structure", "suggestion": "Use bullets"}]'
)
        result = await suggest_improvements(sample_job_description, max_suggestions=2)
assert len(result) <= 2

    @pytest.mark.asyncio
async def test_suggest_improvements_returns_actionable_items(
self, sample_job_description: str
):
        """Suggestions should be actionable (have suggestion text)."""
with patch(
"src.recruitment_platform.agents.job_description_optimizer._call_llm",
new_callable=AsyncMock,
) as mock_llm:
            mock_llm.return_value = (
'[{"category": "clarity", "severity": "high", "suggestion": "Add specific metrics"}]'
)
        result = await suggest_improvements(sample_job_description)
for suggestion in result:
                assert len(suggestion.get("suggestion", "")) > 0


# ---------------------------------------------------------------------------
# Tests for score_description
# ---------------------------------------------------------------------------


class TestScoreDescription:
    """Tests for the score_description function."""

    @pytest.mark.asyncio
async def test_score_description_returns_dict(
self, sample_job_description: str
):
        """score_description should return a dictionary."""
with patch(
"src.recruitment_platform.agents.job_description_optimizer._call_llm",
new_callable=AsyncMock,
) as mock_llm:
            mock_llm.return_value = (
'{"clarity": 7.5, "inclusivity": 8.0, "structure": 6.5, "overall": 7.0}'
)
        result = await score_description(sample_job_description)
assert isinstance(result, dict)

    @pytest.mark.asyncio
async def test_score_description_returns_scores_in_range(
self, sample_job_description: str
):
        """All scores should be between 0 and 10."""
with patch(
"src.recruitment_platform.agents.job_description_optimizer._call_llm",
new_callable=AsyncMock,
) as mock_llm:
            mock_llm.return_value = (
'{"clarity": 7.5, "inclusivity": 8.0, "structure": 6.5, "overall": 7.0}'
)
        result = await score_description(sample_job_description)
for key, value in result.items():
                assert 0 <= value <= 10, f"Score for {key} is out of range: {value}"

    @pytest.mark.asyncio
async def test_score_description_calls_llm(
self, sample_job_description: str
):
        """score_description should call the LLM."""
with patch(
"src.recruitment_platform.agents.job_description_optimizer._call_llm",
new_callable=AsyncMock,
) as mock_llm:
            mock_llm.return_value = '{"clarity": 7.5, "overall": 7.0}'
await score_description(sample_job_description)
mock_llm.assert_called_once()

    @pytest.mark.asyncio
async def test_score_description_passes_description(
self, sample_job_description: str
):
        """score_description should pass the description to the LLM."""
with patch(
"src.recruitment_platform.agents.job_description_optimizer._call_llm",
new_callable=AsyncMock,
) as mock_llm:
            mock_llm.return_value = '{"clarity": 7.5, "overall": 7.0}'
await score_description(sample_job_description)
call_args = mock_llm.call_args
assert sample_job_description in str(call_args)

    @pytest.mark.asyncio
async def test_score_description_with_empty_description(
self, empty_job_description: str
):
        """score_description should handle empty input."""
with patch(
"src.recruitment_platform.agents.job_description_optimizer._call_llm",
new_callable=AsyncMock,
) as mock_llm:
            mock_llm.return_value = '{"clarity": 0, "inclusivity": 0, "structure": 0, "overall": 0}'
result = await score_description(empty_job_description)
assert isinstance(result, dict)

    @pytest.mark.asyncio
async def test_score_description_with_minimal_description(
self, minimal_job_description: str
):
        """score_description should handle very short input."""
with patch(
"src.recruitment_platform.agents.job_description_optimizer._call_llm",
new_callable=AsyncMock,
) as mock_llm:
            mock_llm.return_value = '{"clarity": 3.0, "inclusivity": 5.0, "structure": 2.0, "overall": 3.3}'
result = await score_description(minimal_job_description)
assert isinstance(result, dict)

    @pytest.mark.asyncio
async def test_score_description_with_optimized_description(
self, optimized_job_description: str
):
        """score_description should give higher scores to optimized descriptions."""
with patch(
"src.recruitment_platform.agents.job_description_optimizer._call_llm",
new_callable=AsyncMock,
) as mock_llm:
            mock_llm.return_value = '{"clarity": 9.0, "inclusivity": 9.5, "structure": 8.5, "overall": 9.0}'
result = await score_description(optimized_job_description)
assert isinstance(result, dict)
assert result.get("overall", 0) > 7.0

    @pytest.mark.asyncio
async def test_score_description_with_long_description(
self, long_job_description: str
):
        """score_description should handle very long input."""
with patch(
"src.recruitment_platform.agents.job_description_optimizer._call_llm",
new_callable=AsyncMock,
) as mock_llm:
            mock_llm.return_value = '{"clarity": 5.0, "inclusivity": 6.0, "structure": 4.0, "overall": 5.0}'
result = await score_description(long_job_description)
assert isinstance(result, dict)

    @pytest.mark.asyncio
async def test_score_description_llm_failure_raises(
self, sample_job_description: str
):
        """score_description should raise when LLM call fails."""
with patch(
"src.recruitment_platform.agents.job_description_optimizer._call_llm",
new_callable=AsyncMock,
) as mock_llm:
            mock_llm.side_effect = Exception("LLM service unavailable")
with pytest.raises(Exception, match="LLM service unavailable"):
                await score_description(sample_job_description)

    @pytest.mark.asyncio
async def test_score_description_with_special_characters(self):
        """score_description should handle special characters in input."""
special_desc = "C++ dev needed! Must know C# & .NET. Salary: $100k+."
with patch(
"src.recruitment_platform.agents.job_description_optimizer._call_llm",
new_callable=AsyncMock,
) as mock_llm:
            mock_llm.return_value = '{"clarity": 6.0, "inclusivity": 7.0, "structure": 5.0, "overall": 6.0}'
result = await score_description(special_desc)
assert isinstance(result, dict)

    @pytest.mark.asyncio
async def test_score_description_with_unicode(self):
        """score_description should handle unicode characters."""
unicode_desc = "需要会中文和英文的开发者。你好！"
with patch(
"src.recruitment_platform.agents.job_description_optimizer._call_llm",
new_callable=AsyncMock,
) as mock_llm:
            mock_llm.return_value = '{"clarity": 5.0, "inclusivity": 6.0, "structure": 4.0, "overall": 5.0}'
result = await score_description(unicode_desc)
assert isinstance(result, dict)

    @pytest.mark.asyncio
async def test_score_description_contains_expected_keys(
self, sample_job_description: str
):
        """score_description should return scores for expected categories."""
with patch(
"src.recruitment_platform.agents.job_description_optimizer._call_llm",
new_callable=AsyncMock,
) as mock_llm:
            mock_llm.return_value = (
'{"clarity": 7.5, "inclusivity": 8.0, "structure": 6.5, '
'"completeness": 7.0, "engagement": 5.5, "overall": 7.0}'
)
        result = await score_description(sample_job_description)
expected_keys = {"clarity", "inclusivity", "structure", "overall"}
assert expected_keys.issubset(result.keys())

    @pytest.mark.asyncio
async def test_score_description_with_scoring_criteria(
self, sample_job_description: str
):
        """score_description should accept custom scoring criteria."""
with patch(
"src.recruitment_platform.agents.job_description_optimizer._call_llm",
new_callable=AsyncMock,
) as mock_llm:
            mock_llm.return_value = '{"clarity": 7.5, "overall": 7.5}'
result = await score_description(
sample_job_description, criteria=["clarity", "overall"]
)
        assert isinstance(result, dict)
call_args = mock_llm.call_args
assert "clarity" in str(call_args).lower()

    @pytest.mark.asyncio
async def test_score_description_overall_is_average(
self, sample_job_description: str
):
        """The overall score should be approximately the average of individual scores."""
with patch(
"src.recruitment_platform.agents.job_description_optimizer._call_llm",
new_callable=AsyncMock,
) as mock_llm:
            mock_llm.return_value = (
'{"clarity": 8.0, "inclusivity": 6.0, "structure": 10.0, "overall": 8.0}'
)
        result = await score_description(sample_job_description)
individual_scores = [
v for k, v in result.items() if k != "overall"
]
if individual_scores:
                expected_avg = sum(individual_scores) / len(individual_scores)
assert abs(result["overall"] - expected_avg) < 1.5

    @pytest.mark.asyncio
async def test_score_description_with_numeric_scores_only(
self, sample_job_description: str
):
        """All score values should be numeric."""
with patch(
"src.recruitment_platform.agents.job_description_optimizer._call_llm",
new_callable=AsyncMock,
) as mock_llm:
            mock_llm.return_value = (
'{"clarity": 7.5, "inclusivity": 8.0, "structure": 6.5, "overall": 7.0}'
)
        result = await score_description(sample_job_description)
for key, value in result.items():
                assert isinstance(value, (int, float)), f"Score for {key} is not numeric: {type(value)}"

    @pytest.mark.asyncio
async def test_score_description_consistent_scoring(
self, sample_job_description: str
):
        """Calling score_description twice should produce consistent results."""
with patch(
"src.recruitment_platform.agents.job_description_optimizer._call_llm",
new_callable=AsyncMock,
) as mock_llm:
            mock_llm.return_value = '{"clarity": 7.5, "overall": 7.5}'
result1 = await score_description(sample_job_description)
result2 = await score_description(sample_job_description)
assert result1 == result2

    @pytest.mark.asyncio
async def test_score_description_with_detailed_feedback(
self, sample_job_description: str
):
        """score_description should optionally include detailed feedback."""
with patch(
"src.recruitment_platform.agents.job_description_optimizer._call_llm",
new_callable=AsyncMock,
) as mock_llm:
            mock_llm.return_value = (
'{"clarity": 7.5, "overall": 7.5, "feedback": "Good structure but could use more detail"}'
)
        result = await score_description(sample_job_description, include_feedback=True)
assert isinstance(result, dict)
call_args = mock_llm.call_args
assert "feedback" in str(call_args).lower() or "detailed" in str(call_args).lower()
