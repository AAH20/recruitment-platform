"""Comprehensive tests for the BiasDetector agent."""

import pytest
from unittest.mock import MagicMock, patch
from recruitment_platform.agents.bias_detector import (
BiasDetector,
detect_bias,
suggest_improvements,
score_inclusivity,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def detector():
    """Return a fresh BiasDetector instance."""
return BiasDetector()


@pytest.fixture
def sample_job_description():
    """Return a sample job description with known biased language."""
return (
"We are looking for a rockstar ninja developer who is a digital native. "
"The ideal candidate is a recent college grad, aged 25-35, who is a "
"culture fit and can work long hours in a fast-paced environment. "
"Must be a native English speaker and have a strong personality."
)


@pytest.fixture
def inclusive_job_description():
    """Return a sample job description with inclusive language."""
return (
"We are looking for a skilled software engineer. "
"The ideal candidate has experience with Python and cloud technologies. "
"We welcome applicants from all backgrounds and provide reasonable accommodations. "
"Competitive salary and flexible working hours."
)


@pytest.fixture
def mock_openai_response():
    """Return a mock OpenAI API response."""
return {
"choices": [
{
"message": {
"content": '{"biased_terms": ["rockstar", "ninja", "digital native", "culture fit", "long hours", "native English speaker", "strong personality", "recent college grad", "aged 25-35"], "suggestions": ["Use skilled professional instead of rockstar/ninja", "Remove age requirements", "Replace culture fit with values alignment", "Specify flexible hours instead of long hours", "Use proficient English instead of native English speaker"], "inclusivity_score": 35}'
}
}
]
}


# ---------------------------------------------------------------------------
# Tests for detect_bias
# ---------------------------------------------------------------------------


class TestDetectBias:
    """Tests for the detect_bias function."""

    def test_detect_bias_returns_dict_with_expected_keys(self, detector, sample_job_description):
        """detect_bias should return a dict with biased_terms and suggestions keys."""
with patch("src.recruitment_platform.agents.bias_detector.openai") as mock_openai:
            mock_openai.chat.completions.create.return_value = MagicMock(
choices=[MagicMock(message=MagicMock(content='{"biased_terms": ["rockstar"], "suggestions": ["Use skilled professional"]}'))]
)
            result = detector.detect_bias(sample_job_description)

        assert isinstance(result, dict)
assert "biased_terms" in result
assert "suggestions" in result

    def test_detect_bias_empty_string(self, detector):
        """detect_bias should handle empty job descriptions gracefully."""
with patch("src.recruitment_platform.agents.bias_detector.openai") as mock_openai:
            mock_openai.chat.completions.create.return_value = MagicMock(
choices=[MagicMock(message=MagicMock(content='{"biased_terms": [], "suggestions": []}'))]
)
            result = detector.detect_bias("")

        assert isinstance(result, dict)
assert result["biased_terms"] == []
assert result["suggestions"] == []

    def test_detect_bias_no_bias_found(self, detector, inclusive_job_description):
        """detect_bias should return empty lists when no bias is detected."""
with patch("src.recruitment_platform.agents.bias_detector.openai") as mock_openai:
            mock_openai.chat.completions.create.return_value = MagicMock(
choices=[MagicMock(message=MagicMock(content='{"biased_terms": [], "suggestions": []}'))]
)
            result = detector.detect_bias(inclusive_job_description)

        assert result["biased_terms"] == []
assert result["suggestions"] == []

    def test_detect_bias_multiple_biased_terms(self, detector, sample_job_description):
        """detect_bias should identify multiple biased terms."""
with patch("src.recruitment_platform.agents.bias_detector.openai") as mock_openai:
            mock_openai.chat.completions.create.return_value = MagicMock(
choices=[MagicMock(message=MagicMock(content='{"biased_terms": ["rockstar", "ninja", "digital native", "culture fit"], "suggestions": ["Use skilled professional", "Use expert", "Remove jargon", "Use values alignment"]}'))]
)
            result = detector.detect_bias(sample_job_description)

        assert len(result["biased_terms"]) == 4
assert "rockstar" in result["biased_terms"]
assert "ninja" in result["biased_terms"]
assert "digital native" in result["biased_terms"]
assert "culture fit" in result["biased_terms"]

    def test_detect_bias_suggestions_match_terms(self, detector, sample_job_description):
        """detect_bias should provide suggestions for each biased term."""
with patch("src.recruitment_platform.agents.bias_detector.openai") as mock_openai:
            mock_openai.chat.completions.create.return_value = MagicMock(
choices=[MagicMock(message=MagicMock(content='{"biased_terms": ["rockstar", "ninja"], "suggestions": ["Use skilled professional", "Use expert"]}'))]
)
            result = detector.detect_bias(sample_job_description)

        assert len(result["suggestions"]) == len(result["biased_terms"])

    def test_detect_bias_api_error_handling(self, detector, sample_job_description):
        """detect_bias should handle API errors gracefully."""
with patch("src.recruitment_platform.agents.bias_detector.openai") as mock_openai:
            mock_openai.chat.completions.create.side_effect = Exception("API Error")
result = detector.detect_bias(sample_job_description)

        assert isinstance(result, dict)
assert "error" in result or "biased_terms" in result

    def test_detect_bias_standalone_function(self, sample_job_description):
        """The standalone detect_bias function should work without instantiating BiasDetector."""
with patch("src.recruitment_platform.agents.bias_detector.openai") as mock_openai:
            mock_openai.chat.completions.create.return_value = MagicMock(
choices=[MagicMock(message=MagicMock(content='{"biased_terms": ["rockstar"], "suggestions": ["Use skilled professional"]}'))]
)
            result = detect_bias(sample_job_description)

        assert isinstance(result, dict)
assert "biased_terms" in result

    def test_detect_bias_passes_correct_model(self, detector, sample_job_description):
        """detect_bias should use the correct model for analysis."""
with patch("src.recruitment_platform.agents.bias_detector.openai") as mock_openai:
            mock_openai.chat.completions.create.return_value = MagicMock(
choices=[MagicMock(message=MagicMock(content='{"biased_terms": [], "suggestions": []}'))]
)
            detector.detect_bias(sample_job_description)

        call_kwargs = mock_openai.chat.completions.create.call_args
assert call_kwargs is not None
assert "model" in call_kwargs.kwargs
assert "messages" in call_kwargs.kwargs

    def test_detect_bias_includes_job_description_in_prompt(self, detector, sample_job_description):
        """detect_bias should include the job description in the prompt."""
with patch("src.recruitment_platform.agents.bias_detector.openai") as mock_openai:
            mock_openai.chat.completions.create.return_value = MagicMock(
choices=[MagicMock(message=MagicMock(content='{"biased_terms": [], "suggestions": []}'))]
)
            detector.detect_bias(sample_job_description)

        call_kwargs = mock_openai.chat.completions.create.call_args
messages = call_kwargs.kwargs["messages"]
prompt_content = str(messages)
assert sample_job_description in prompt_content


# ---------------------------------------------------------------------------
# Tests for suggest_improvements
# ---------------------------------------------------------------------------


class TestSuggestImprovements:
    """Tests for the suggest_improvements function."""

    def test_suggest_improvements_returns_list(self, detector, sample_job_description):
        """suggest_improvements should return a list of improvement suggestions."""
with patch("src.recruitment_platform.agents.bias_detector.openai") as mock_openai:
            mock_openai.chat.completions.create.return_value = MagicMock(
choices=[MagicMock(message=MagicMock(content='{"improvements": ["Remove gendered language", "Add diversity statement", "Specify flexible hours"]}'))]
)
            result = detector.suggest_improvements(sample_job_description)

        assert isinstance(result, list)
assert len(result) == 3

    def test_suggest_improvements_empty_description(self, detector):
        """suggest_improvements should handle empty descriptions."""
with patch("src.recruitment_platform.agents.bias_detector.openai") as mock_openai:
            mock_openai.chat.completions.create.return_value = MagicMock(
choices=[MagicMock(message=MagicMock(content='{"improvements": []}'))]
)
            result = detector.suggest_improvements("")

        assert isinstance(result, list)
assert result == []

    def test_suggest_improvements_inclusive_description(self, detector, inclusive_job_description):
        """suggest_improvements should return fewer suggestions for inclusive descriptions."""
with patch("src.recruitment_platform.agents.bias_detector.openai") as mock_openai:
            mock_openai.chat.completions.create.return_value = MagicMock(
choices=[MagicMock(message=MagicMock(content='{"improvements": ["Consider adding specific accommodation details"]}'))]
)
            result = detector.suggest_improvements(inclusive_job_description)

        assert isinstance(result, list)
assert len(result) <= 2

    def test_suggest_improvements_standalone_function(self, sample_job_description):
        """The standalone suggest_improvements function should work without instantiating BiasDetector."""
with patch("src.recruitment_platform.agents.bias_detector.openai") as mock_openai:
            mock_openai.chat.completions.create.return_value = MagicMock(
choices=[MagicMock(message=MagicMock(content='{"improvements": ["Remove gendered language"]}'))]
)
            result = suggest_improvements(sample_job_description)

        assert isinstance(result, list)
assert len(result) == 1

    def test_suggest_improvements_api_error_handling(self, detector, sample_job_description):
        """suggest_improvements should handle API errors gracefully."""
with patch("src.recruitment_platform.agents.bias_detector.openai") as mock_openai:
            mock_openai.chat.completions.create.side_effect = Exception("API Error")
result = detector.suggest_improvements(sample_job_description)

        assert isinstance(result, list)
assert result == [] or all(isinstance(item, str) for item in result)

    def test_suggest_improvements_returns_strings(self, detector, sample_job_description):
        """All suggestions should be strings."""
with patch("src.recruitment_platform.agents.bias_detector.openai") as mock_openai:
            mock_openai.chat.completions.create.return_value = MagicMock(
choices=[MagicMock(message=MagicMock(content='{"improvements": ["Suggestion one", "Suggestion two", "Suggestion three"]}'))]
)
            result = detector.suggest_improvements(sample_job_description)

        assert all(isinstance(s, str) for s in result)

    def test_suggest_improvements_includes_context_in_prompt(self, detector, sample_job_description):
        """suggest_improvements should include the job description in the prompt."""
with patch("src.recruitment_platform.agents.bias_detector.openai") as mock_openai:
            mock_openai.chat.completions.create.return_value = MagicMock(
choices=[MagicMock(message=MagicMock(content='{"improvements": []}'))]
)
            detector.suggest_improvements(sample_job_description)

        call_kwargs = mock_openai.chat.completions.create.call_args
messages = call_kwargs.kwargs["messages"]
prompt_content = str(messages)
assert sample_job_description in prompt_content


# ---------------------------------------------------------------------------
# Tests for score_inclusivity
# ---------------------------------------------------------------------------


class TestScoreInclusivity:
    """Tests for the score_inclusivity function."""

    def test_score_inclusivity_returns_numeric(self, detector, sample_job_description):
        """score_inclusivity should return a numeric score."""
with patch("src.recruitment_platform.agents.bias_detector.openai") as mock_openai:
            mock_openai.chat.completions.create.return_value = MagicMock(
choices=[MagicMock(message=MagicMock(content='{"score": 42}'))]
)
            result = detector.score_inclusivity(sample_job_description)

        assert isinstance(result, (int, float))

    def test_score_inclusivity_biased_description_low_score(self, detector, sample_job_description):
        """Biased job descriptions should receive a low inclusivity score."""
with patch("src.recruitment_platform.agents.bias_detector.openai") as mock_openai:
            mock_openai.chat.completions.create.return_value = MagicMock(
choices=[MagicMock(message=MagicMock(content='{"score": 30}'))]
)
            result = detector.score_inclusivity(sample_job_description)

        assert result < 50

    def test_score_inclusivity_inclusive_description_high_score(self, detector, inclusive_job_description):
        """Inclusive job descriptions should receive a high inclusivity score."""
with patch("src.recruitment_platform.agents.bias_detector.openai") as mock_openai:
            mock_openai.chat.completions.create.return_value = MagicMock(
choices=[MagicMock(message=MagicMock(content='{"score": 85}'))]
)
            result = detector.score_inclusivity(inclusive_job_description)

        assert result >= 70

    def test_score_inclusivity_empty_description(self, detector):
        """score_inclusivity should handle empty descriptions."""
with patch("src.recruitment_platform.agents.bias_detector.openai") as mock_openai:
            mock_openai.chat.completions.create.return_value = MagicMock(
choices=[MagicMock(message=MagicMock(content='{"score": 50}'))]
)
            result = detector.score_inclusivity("")

        assert isinstance(result, (int, float))

    def test_score_inclusivity_standalone_function(self, sample_job_description):
        """The standalone score_inclusivity function should work without instantiating BiasDetector."""
with patch("src.recruitment_platform.agents.bias_detector.openai") as mock_openai:
            mock_openai.chat.completions.create.return_value = MagicMock(
choices=[MagicMock(message=MagicMock(content='{"score": 55}'))]
)
            result = score_inclusivity(sample_job_description)

        assert isinstance(result, (int, float))

    def test_score_inclusivity_api_error_handling(self, detector, sample_job_description):
        """score_inclusivity should handle API errors gracefully."""
with patch("src.recruitment_platform.agents.bias_detector.openai") as mock_openai:
            mock_openai.chat.completions.create.side_effect = Exception("API Error")
result = detector.score_inclusivity(sample_job_description)

        assert isinstance(result, (int, float)) or result is None

    def test_score_inclusivity_includes_description_in_prompt(self, detector, sample_job_description):
        """score_inclusivity should include the job description in the prompt."""
with patch("src.recruitment_platform.agents.bias_detector.openai") as mock_openai:
            mock_openai.chat.completions.create.return_value = MagicMock(
choices=[MagicMock(message=MagicMock(content='{"score": 60}'))]
)
            detector.score_inclusivity(sample_job_description)

        call_kwargs = mock_openai.chat.completions.create.call_args
messages = call_kwargs.kwargs["messages"]
prompt_content = str(messages)
assert sample_job_description in prompt_content

    def test_score_inclusivity_score_range(self, detector, sample_job_description):
        """score_inclusivity should return a score within a reasonable range (0-100)."""
with patch("src.recruitment_platform.agents.bias_detector.openai") as mock_openai:
            mock_openai.chat.completions.create.return_value = MagicMock(
choices=[MagicMock(message=MagicMock(content='{"score": 75}'))]
)
            result = detector.score_inclusivity(sample_job_description)

        assert 0 <= result <= 100
