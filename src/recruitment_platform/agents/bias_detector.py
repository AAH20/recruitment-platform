"""
Bias Detector Agent for Recruitment Platform.

Detects biased language in job descriptions, candidate communications,
and other recruitment-related text. Provides inclusive alternatives
for flagged terms.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple


# ─── Data Structures ────────────────────────────────────────────────────────

@dataclass
class BiasResult:
    """Result of bias detection on a text."""
    score: float  # 0.0 (no bias) to 1.0 (high bias)
    flagged_terms: List[str]
    categories: List[str]
    suggestions: Dict[str, List[str]] = field(default_factory=dict)


@dataclass
class FlaggedTerm:
    """A single flagged biased term with metadata."""
    term: str
    category: str
    severity: float  # 0.0 to 1.0
    position: int  # character position in original text


# ─── Mock Bias Database ─────────────────────────────────────────────────────

# Biased terms mapped to their category and severity
BIAS_DATABASE: Dict[str, Tuple[str, float]] = {
    # Gender bias
    "rockstar": ("gender", 0.6),
    "ninja": ("gender", 0.7),
    "guru": ("gender", 0.5),
    "superhero": ("gender", 0.6),
    "aggressive": ("gender", 0.4),
    "dominant": ("gender", 0.5),
    "manly": ("gender", 0.9),
    "feminine": ("gender", 0.7),
    "he": ("gender", 0.3),
    "she": ("gender", 0.3),
    "his": ("gender", 0.3),
    "her": ("gender", 0.3),
    "chairman": ("gender", 0.8),
    "manpower": ("gender", 0.7),
    "mankind": ("gender", 0.6),
    "guys": ("gender", 0.4),
    "bro": ("gender", 0.5),
    "dude": ("gender", 0.5),

    # Age bias
    "young": ("age", 0.5),
    "energetic": ("age", 0.3),
    "fresh": ("age", 0.4),
    "mature": ("age", 0.4),
    "experienced": ("age", 0.2),
    "digital native": ("age", 0.7),
    "millennial mindset": ("age", 0.6),
    "gen z": ("age", 0.5),
    "recent graduate": ("age", 0.4),
    "seasoned": ("age", 0.3),

    # Racial / Ethnic bias
    "native speaker": ("racial", 0.8),
    "fluent english": ("racial", 0.4),
    "western": ("racial", 0.5),
    "exotic": ("racial", 0.7),
    "articulate": ("racial", 0.6),
    "well-spoken": ("racial", 0.5),
    "cultural fit": ("racial", 0.6),

    # Disability bias
    "able-bodied": ("disability", 0.9),
    "physically fit": ("disability", 0.6),
    "must be able to lift": ("disability", 0.5),
    "stand for long periods": ("disability", 0.4),
    "no disabilities": ("disability", 0.9),
    "handicap": ("disability", 0.8),
    "crazy": ("disability", 0.5),
    "insane": ("disability", 0.5),
    "lame": ("disability", 0.4),
    "dumb": ("disability", 0.5),
    "blind to": ("disability", 0.3),
    "deaf to": ("disability", 0.3),
    "suffers from": ("disability", 0.7),
    "wheelchair-bound": ("disability", 0.8),

    # Socioeconomic bias
    "prestigious university": ("socioeconomic", 0.6),
    "elite school": ("socioeconomic", 0.7),
    "top-tier college": ("socioeconomic", 0.5),
    "ivy league": ("socioeconomic", 0.6),
    "polished": ("socioeconomic", 0.4),
    "well-bred": ("socioeconomic", 0.8),
    "ghetto": ("socioeconomic", 0.9),
    "trailer park": ("socioeconomic", 0.9),

    # LGBTQ+ bias
    "normal family": ("lgbtq", 0.6),
    "traditional family": ("lgbtq", 0.5),
    "husband": ("lgbtq", 0.3),
    "wife": ("lgbtq", 0.3),
    "motherly": ("lgbtq", 0.4),
    "fatherly": ("lgbtq", 0.4),

    # Religious bias
    "christian values": ("religious", 0.7),
    "jewish holidays": ("religious", 0.5),
    "muslim-friendly": ("religious", 0.4),
    "church-going": ("religious", 0.6),
}

# Inclusive alternatives for flagged terms
ALTERNATIVES_DATABASE: Dict[str, List[str]] = {
    "rockstar": ["skilled", "high-performing", "exceptional", "talented"],
    "ninja": ["expert", "specialist", "proficient", "adept"],
    "guru": ["expert", "authority", "specialist", "mentor"],
    "superhero": ["high-performer", "top talent", "exceptional contributor"],
    "aggressive": ["ambitious", "driven", "assertive", "proactive"],
    "dominant": ["leading", "prominent", "influential"],
    "manly": ["strong", "capable", "resilient"],
    "feminine": ["collaborative", "empathetic", "nurturing"],
    "he": ["they", "the candidate", "the applicant"],
    "she": ["they", "the candidate", "the applicant"],
    "his": ["their", "the candidate's"],
    "her": ["their", "the candidate's"],
    "chairman": ["chair", "chairperson", "coordinator"],
    "manpower": ["workforce", "staffing", "personnel", "team members"],
    "mankind": ["humanity", "people", "humankind"],
    "guys": ["everyone", "team", "folks", "all"],
    "bro": ["colleague", "teammate", "peer"],
    "dude": ["colleague", "person", "individual"],
    "young": ["early-career", "emerging", "developing"],
    "energetic": ["motivated", "enthusiastic", "dynamic"],
    "fresh": ["new", "current", "up-to-date"],
    "mature": ["experienced", "seasoned", "developed"],
    "experienced": ["skilled", "proficient", "knowledgeable"],
    "digital native": ["tech-savvy", "digitally fluent", "comfortable with technology"],
    "millennial mindset": ["innovative mindset", "modern approach", "fresh perspective"],
    "gen z": ["early-career", "new professional", "emerging talent"],
    "recent graduate": ["early-career professional", "new graduate", "entry-level candidate"],
    "seasoned": ["experienced", "veteran", "long-tenured"],
    "native speaker": ["fluent", "proficient", "skilled in English"],
    "fluent english": ["strong English communication", "English proficiency"],
    "western": ["global", "international", "diverse"],
    "exotic": ["unique", "distinctive", "unusual"],
    "articulate": ["clear communicator", "effective communicator"],
    "well-spoken": ["clear communicator", "polished communicator"],
    "cultural fit": ["values alignment", "team compatibility", "shared mission"],
    "able-bodied": ["able to perform essential functions", "capable of meeting physical requirements"],
    "physically fit": ["able to meet physical requirements", "physically capable"],
    "must be able to lift": ["able to lift (with or without reasonable accommodation)"],
    "stand for long periods": ["able to stand as needed for the role"],
    "no disabilities": ["able to perform essential job functions with or without accommodation"],
    "handicap": ["disability", "accessibility need"],
    "crazy": ["intense", "unpredictable", "remarkable"],
    "insane": ["extraordinary", "incredible", "remarkable"],
    "lame": ["inadequate", "unsatisfactory", "disappointing"],
    "dumb": ["uninformed", "unaware", "simplistic"],
    "blind to": ["unaware of", "overlooking", "missing"],
    "deaf to": ["unresponsive to", "ignoring", "dismissive of"],
    "suffers from": ["has", "experiences", "lives with"],
    "wheelchair-bound": ["wheelchair user", "uses a wheelchair"],
    "prestigious university": ["accredited university", "recognized institution"],
    "elite school": ["accredited institution", "recognized program"],
    "top-tier college": ["accredited college", "recognized institution"],
    "ivy league": ["accredited university", "recognized institution"],
    "polished": ["professional", "refined", "well-presented"],
    "well-bred": ["well-mannered", "professional", "courteous"],
    "ghetto": ["under-resourced", "underserved", "low-income"],
    "trailer park": ["under-resourced community", "underserved area"],
    "normal family": ["all family types", "diverse family structures"],
    "traditional family": ["all family types", "diverse family structures"],
    "husband": ["spouse", "partner"],
    "wife": ["spouse", "partner"],
    "motherly": ["nurturing", "supportive", "caring"],
    "fatherly": ["supportive", "guiding", "mentoring"],
    "christian values": ["shared values", "organizational values", "core principles"],
    "jewish holidays": ["religious holidays", "cultural observances"],
    "muslim-friendly": ["inclusive", "accommodating", "respectful of all faiths"],
    "church-going": ["community-oriented", "values-driven"],
}


# ─── Agent Class ─────────────────────────────────────────────────────────────

class BiasDetectorAgent:
    """
    Agent that detects biased language in recruitment text and suggests
    inclusive alternatives.
    """

    def __init__(self) -> None:
        """Initialize the bias detector with mock databases."""
        self.bias_db: Dict[str, Tuple[str, float]] = BIAS_DATABASE.copy()
        self.alternatives_db: Dict[str, List[str]] = ALTERNATIVES_DATABASE.copy()

    def detect_bias(self, text: str) -> BiasResult:
        """
        Detect biased language in the given text.

        Args:
            text: The text to analyze (job description, email, etc.)

        Returns:
            BiasResult with score (0.0-1.0), flagged terms, categories,
            and suggestions for each flagged term.
        """
        if not text or not text.strip():
            return BiasResult(
                score=0.0,
                flagged_terms=[],
                categories=[],
                suggestions={}
            )

        text_lower = text.lower()
        flagged: List[str] = []
        categories: Set[str] = set()
        suggestions: Dict[str, List[str]] = {}
        total_severity: float = 0.0
        match_count: int = 0

        for term, (category, severity) in self.bias_db.items():
            # Use word boundary matching for single words,
            # substring matching for multi-word phrases
            if " " in term:
                pattern = re.escape(term)
            else:
                pattern = r'\b' + re.escape(term) + r'\b'

            matches = list(re.finditer(pattern, text_lower, re.IGNORECASE))

            if matches:
                flagged.append(term)
                categories.add(category)
                total_severity += severity * len(matches)
                match_count += len(matches)

                if term in self.alternatives_db:
                    suggestions[term] = self.alternatives_db[term]

        # Calculate score: weighted by severity and frequency, capped at 1.0
        if match_count > 0:
            raw_score = total_severity / max(len(text.split()), 1) * 10
            score = min(raw_score, 1.0)
        else:
            score = 0.0

        return BiasResult(
            score=round(score, 3),
            flagged_terms=flagged,
            categories=sorted(categories),
            suggestions=suggestions
        )

    def suggest_alternatives(self, flagged_terms: List[str]) -> Dict[str, List[str]]:
        """
        Suggest inclusive alternatives for flagged biased terms.

        Args:
            flagged_terms: List of biased terms to find alternatives for.

        Returns:
            Dictionary mapping each flagged term to a list of inclusive
            alternative phrases.
        """
        if not flagged_terms:
            return {}

        result: Dict[str, List[str]] = {}

        for term in flagged_terms:
            term_lower = term.lower().strip()
            if term_lower in self.alternatives_db:
                result[term] = self.alternatives_db[term_lower]
            else:
                # Fuzzy match: check if any key contains this term
                for key, alts in self.alternatives_db.items():
                    if term_lower in key or key in term_lower:
                        result[term] = alts
                        break
                else:
                    result[term] = ["[No alternative found — review manually]"]

        return result

    def analyze_job_description(self, text: str) -> Dict[str, object]:
        """
        Comprehensive analysis of a job description.

        Args:
            text: Job description text to analyze.

        Returns:
            Dictionary with full analysis results.
        """
        bias_result = self.detect_bias(text)

        return {
            "bias_score": bias_result.score,
            "risk_level": self._score_to_risk_level(bias_result.score),
            "flagged_terms": bias_result.flagged_terms,
            "categories": bias_result.categories,
            "suggestions": bias_result.suggestions,
            "total_flags": len(bias_result.flagged_terms),
            "summary": self._generate_summary(bias_result),
        }

    def _score_to_risk_level(self, score: float) -> str:
        """Convert numeric score to risk level string."""
        if score < 0.1:
            return "low"
        elif score < 0.3:
            return "medium"
        elif score < 0.6:
            return "high"
        else:
            return "critical"

    def _generate_summary(self, result: BiasResult) -> str:
        """Generate a human-readable summary of the bias analysis."""
        if not result.flagged_terms:
            return "No biased language detected. This text appears inclusive."

        categories_str = ", ".join(result.categories)
        terms_str = ", ".join(result.flagged_terms[:5])
        if len(result.flagged_terms) > 5:
            terms_str += f" (and {len(result.flagged_terms) - 5} more)"

        return (
            f"Detected {len(result.flagged_terms)} potentially biased term(s) "
            f"across {len(result.categories)} categor{'ies' if len(result.categories) != 1 else 'y'} "
            f"({categories_str}). "
            f"Flagged terms include: {terms_str}. "
            f"Consider using the suggested alternatives to make this text more inclusive."
        )


# ─── Module-Level Convenience Functions ─────────────────────────────────────

_default_agent = BiasDetectorAgent()


def detect_bias_as_result(text: str) -> BiasResult:
    """
    Detect biased language in text.

    Args:
        text: Text to analyze.

    Returns:
        BiasResult with score, flagged terms, categories, and suggestions.
    """
    return _default_agent.detect_bias(text)


def suggest_alternatives(flagged_terms: List[str]) -> Dict[str, List[str]]:
    """
    Suggest inclusive alternatives for flagged terms.

    Args:
        flagged_terms: List of biased terms.

    Returns:
        Dictionary mapping terms to inclusive alternatives.
    """
    return _default_agent.suggest_alternatives(flagged_terms)


# ─── Required Agent Functions ───────────────────────────────────────────────


def detect_bias(job_description: str) -> dict:
    """Detect biased language in a job description.

    Analyzes the provided job description text for terms and phrases
    associated with various bias categories (gender, age, race/ethnicity,
    disability, LGBTQ+, socioeconomic status, religion).

    Args:
        job_description: The job description text to analyze.

    Returns:
        A dictionary containing:
            - 'has_bias': bool indicating if any biased terms were found
            - 'bias_categories': dict mapping category names to lists of
              found biased terms
            - 'biased_terms': flat list of all biased terms found
            - 'suggestions': list of suggested inclusive alternatives
            - 'bias_score': float from 0.0 (no bias) to 1.0 (high bias)

    Raises:
        TypeError: If job_description is not a string.
        ValueError: If job_description is empty or contains only whitespace.
    """
    if not isinstance(job_description, str):
        raise TypeError(
            f"job_description must be a string, got {type(job_description).__name__}"
        )

    if not job_description.strip():
        raise ValueError("job_description cannot be empty or whitespace only")

    text_lower = job_description.lower()
    bias_categories: dict[str, list[str]] = {}
    all_biased_terms: list[str] = []
    all_suggestions: list[str] = []

    for term, (category, _severity) in BIAS_DATABASE.items():
        if " " in term:
            pattern = re.escape(term)
        else:
            pattern = r'\b' + re.escape(term) + r'\b'

        matches = list(re.finditer(pattern, text_lower, re.IGNORECASE))

        if matches:
            if category not in bias_categories:
                bias_categories[category] = []
            bias_categories[category].append(term)
            all_biased_terms.append(term)

            if term in ALTERNATIVES_DATABASE:
                all_suggestions.extend(ALTERNATIVES_DATABASE[term])

    # Calculate bias score based on density of biased terms
    word_count = len(job_description.split())
    if word_count == 0:
        bias_score = 0.0
    else:
        bias_score = min(1.0, len(all_biased_terms) / max(word_count * 0.05, 1.0))

    return {
        "has_bias": len(all_biased_terms) > 0,
        "bias_categories": bias_categories,
        "biased_terms": all_biased_terms,
        "suggestions": list(set(all_suggestions)),
        "bias_score": round(bias_score, 3),
    }


def suggest_improvements(bias_report: dict) -> list[str]:
    """Suggest improvements to reduce bias based on a bias report.

    Takes the output from detect_bias() and generates actionable
    suggestions for making the job description more inclusive.

    Args:
        bias_report: A dictionary containing bias analysis results,
            as returned by detect_bias().

    Returns:
        A list of strings, each containing a specific suggestion
        for improving the job description's inclusivity.

    Raises:
        TypeError: If bias_report is not a dictionary.
        ValueError: If bias_report is missing required keys.
    """
    if not isinstance(bias_report, dict):
        raise TypeError(
            f"bias_report must be a dictionary, got {type(bias_report).__name__}"
        )

    required_keys = {"has_bias", "bias_categories", "biased_terms", "suggestions"}
    missing_keys = required_keys - set(bias_report.keys())
    if missing_keys:
        raise ValueError(f"bias_report missing required keys: {missing_keys}")

    suggestions: list[str] = []

    if not bias_report["has_bias"]:
        suggestions.append(
            "No biased language detected. Continue to review for "
            "unconscious bias in requirements and qualifications."
        )
        return suggestions

    # Category-specific suggestions
    category_suggestions: dict[str, list[str]] = {
        "gender": [
            "Use gender-neutral language throughout the job description.",
            "Replace gendered pronouns with 'they/them' or restructure sentences.",
            "Use gender-neutral job titles (e.g., 'salesperson' instead of 'salesman').",
            "Avoid terms like 'guys' or 'ladies'; use 'team' or 'everyone' instead.",
        ],
        "age": [
            "Focus on skills and competencies rather than age-related terms.",
            "Avoid terms like 'young', 'energetic', or 'digital native'.",
            "Use 'early-career' or 'experienced' instead of age indicators.",
            "Do not specify graduation years or age ranges.",
        ],
        "racial": [
            "Avoid requiring 'native' language proficiency; specify required "
            "proficiency level instead.",
            "Remove 'cultural fit' requirements; focus on 'culture add'.",
            "Avoid terms that may signal racial or ethnic bias.",
        ],
        "disability": [
            "Focus on essential job functions and state that reasonable "
            "accommodations are available.",
            "Avoid physical requirements unless truly essential to the role.",
            "Remove stigmatizing terms related to disability or mental health.",
        ],
        "lgbtq": [
            "Use inclusive language that welcomes all gender identities "
            "and sexual orientations.",
            "Avoid assumptions about gender or family structure.",
        ],
        "socioeconomic": [
            "Avoid requiring degrees from 'prestigious' or 'ivy league' "
            "institutions unless truly necessary.",
            "Focus on skills and competencies rather than school prestige.",
            "Remove appearance-based requirements unless job-related.",
        ],
        "religious": [
            "Avoid religious language unless it is a genuine occupational requirement.",
            "Use 'shared values' or 'organizational values' instead of specific religious terms.",
        ],
    }

    for category in bias_report.get("bias_categories", {}):
        if category in category_suggestions:
            suggestions.extend(category_suggestions[category])

    # Add general suggestions
    suggestions.extend([
        "Review the job description with a diverse group of reviewers.",
        "Use structured interviews with consistent questions for all candidates.",
        "Focus on essential job functions and required competencies.",
        "Consider using blind resume screening to reduce unconscious bias.",
    ])

    # Remove duplicates while preserving order
    seen: set[str] = set()
    unique_suggestions: list[str] = []
    for s in suggestions:
        if s not in seen:
            seen.add(s)
            unique_suggestions.append(s)

    return unique_suggestions


def score_inclusivity(text: str) -> float:
    """Score the inclusivity of a given text.

    Returns a score from 0.0 (not inclusive) to 1.0 (highly inclusive)
    based on the presence of inclusive language and absence of biased terms.

    Args:
        text: The text to score for inclusivity.

    Returns:
        A float between 0.0 and 1.0 representing the inclusivity score.
        Higher scores indicate more inclusive language.

    Raises:
        TypeError: If text is not a string.
        ValueError: If text is empty or contains only whitespace.
    """
    if not isinstance(text, str):
        raise TypeError(f"text must be a string, got {type(text).__name__}")

    if not text.strip():
        raise ValueError("text cannot be empty or whitespace only")

    text_lower = text.lower()
    words = text_lower.split()
    total_words = len(words)

    if total_words == 0:
        return 0.0

    # Count biased terms
    biased_count = 0
    for term, (_category, _severity) in BIAS_DATABASE.items():
        if " " in term:
            pattern = re.escape(term)
        else:
            pattern = r'\b' + re.escape(term) + r'\b'
        biased_count += len(re.findall(pattern, text_lower, re.IGNORECASE))

    # Count inclusive terms
    inclusive_terms = [
        "they", "them", "their", "theirs", "themselves",
        "inclusive", "diversity", "equity", "belonging",
        "accessible", "accommodation", "flexible",
        "remote", "work-life balance", "parental leave",
        "all backgrounds", "all genders", "all identities",
        "underrepresented", "equal opportunity",
    ]

    inclusive_count = 0
    for term in inclusive_terms:
        if " " in term:
            pattern = re.escape(term)
        else:
            pattern = r'\b' + re.escape(term) + r'\b'
        inclusive_count += len(re.findall(pattern, text_lower, re.IGNORECASE))

    # Calculate score: start at 1.0, penalize for biased terms,
    # bonus for inclusive terms
    bias_penalty = min(1.0, biased_count / max(total_words * 0.02, 1.0))
    inclusive_bonus = min(0.3, inclusive_count / max(total_words * 0.02, 1.0))

    score = 1.0 - bias_penalty + inclusive_bonus
    score = max(0.0, min(1.0, score))

    return round(score, 3)


# ─── Example Usage ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    sample_jd = """
    We are looking for a rockstar ninja developer who can be our guru
    in building amazing products. The ideal candidate is a young,
    energetic digital native with a millennial mindset. Must be
    able-bodied and able to lift 50 lbs. We value cultural fit and
    want someone who is a native English speaker with a polished,
    western education from a prestigious university.
    """

    agent = BiasDetectorAgent()
    result = agent.analyze_job_description(sample_jd)

    print("=" * 60)
    print("BIAS DETECTION REPORT")
    print("=" * 60)
    print(f"Risk Level: {result['risk_level']}")
    print(f"Bias Score: {result['bias_score']}")
    print(f"Total Flags: {result['total_flags']}")
    print(f"Categories: {result['categories']}")
    print(f"\nFlagged Terms: {result['flagged_terms']}")
    print(f"\nSummary: {result['summary']}")
    print("\nSuggestions:")
    for term, alts in result["suggestions"].items():
        print(f"  '{term}' → {alts}")
