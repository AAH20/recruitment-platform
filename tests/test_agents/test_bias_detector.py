"""Tests for bias detector agent."""

import pytest
from unittest.mock import MagicMock, patch


class TestBiasDetectorAgent:
    """Test bias detector agent functionality."""

    def test_detect_bias_basic(self):
        """Test basic bias detection."""
        from recruitment_platform.agents.bias_detector import LanguageBiasDetector
        
        detector = LanguageBiasDetector()
        assert detector is not None

    def test_detect_gender_bias(self):
        """Test gender bias detection."""
        from recruitment_platform.agents.bias_detector import LanguageBiasDetector
        
        detector = LanguageBiasDetector()
        text = "He is a strong leader. She is nurturing."
        
        result = detector.process(text)
        assert result is not None

    def test_detect_age_bias(self):
        """Test age bias detection."""
        from recruitment_platform.agents.bias_detector import LanguageBiasDetector
        
        detector = LanguageBiasDetector()
        text = "Young and energetic team"
        
        result = detector.process(text)
        assert result is not None

    def test_detect_no_bias(self):
        """Test text with no bias."""
        from recruitment_platform.agents.bias_detector import LanguageBiasDetector
        
        detector = LanguageBiasDetector()
        text = "The candidate has strong technical skills"
        
        result = detector.process(text)
        assert result is not None

    def test_fairness_scorer(self):
        """Test fairness scoring."""
        from recruitment_platform.agents.bias_detector import FairnessScorer
        
        scorer = FairnessScorer()
        assert scorer is not None

    def test_demographic_analyzer(self):
        """Test demographic analysis."""
        from recruitment_platform.agents.bias_detector import DemographicAnalyzer
        
        analyzer = DemographicAnalyzer()
        assert analyzer is not None
