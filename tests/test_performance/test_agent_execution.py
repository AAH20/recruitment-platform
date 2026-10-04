"""Agent execution time benchmarks for recruitment-platform."""
import asyncio
import time
import statistics

import pytest

from recruitment_platform.agents.resume_parser.resume_parser_agent import ResumeParserAgent
from recruitment_platform.agents.resume_parser.contact_extractor_agent import ContactExtractorAgent
from recruitment_platform.agents.resume_parser.skills_extractor_agent import SkillsExtractorAgent
from recruitment_platform.agents.resume_parser.experience_extractor_agent import ExperienceExtractorAgent
from recruitment_platform.agents.resume_parser.education_extractor_agent import EducationExtractorAgent
from recruitment_platform.agents.candidate_matcher.bias_aware_ranker import BiasAwareRanker
from recruitment_platform.agents.candidate_matcher.culture_fit_assessor import CultureFitAssessor
from recruitment_platform.agents.candidate_matcher.match_explainer import MatchExplainer
from recruitment_platform.agents.candidate_matcher.semantic_matcher import SemanticMatcher
from recruitment_platform.agents.candidate_matcher.skills_gap_analyzer import SkillsGapAnalyzer
from recruitment_platform.agents.bias_detector.demographic_analyzer import DemographicAnalyzer
from recruitment_platform.agents.bias_detector.fairness_scorer import FairnessScorer
from recruitment_platform.agents.bias_detector.language_bias_detector import LanguageBiasDetector
from recruitment_platform.agents.bias_detector.pattern_detector import PatternDetector
from recruitment_platform.agents.interview_scheduler.availability_optimizer import AvailabilityOptimizer
from recruitment_platform.agents.interview_scheduler.conflict_detector import ConflictDetector
from recruitment_platform.agents.interview_scheduler.timezone_resolver import TimezoneResolver
from recruitment_platform.agents.skills_assessor.gap_analyzer import GapAnalyzer
from recruitment_platform.agents.skills_assessor.proficiency_scorer import ProficiencyScorer
from recruitment_platform.agents.skills_assessor.skill_extractor import SkillExtractor
from recruitment_platform.agents.skills_assessor.skill_validator import SkillValidator
from recruitment_platform.agents.talent_pool_manager.candidate_sourcer import CandidateSourcer
from recruitment_platform.agents.talent_pool_manager.engagement_tracker import EngagementTracker
from recruitment_platform.agents.talent_pool_manager.pool_analyzer import PoolAnalyzer
from recruitment_platform.agents.talent_pool_manager.talent_recommender import TalentRecommender
from recruitment_platform.agents.talent_pool_manager.talent_tagger import TalentTagger
from recruitment_platform.agents.onboarding_automator.compliance_checker import ComplianceChecker
from recruitment_platform.agents.onboarding_automator.document_generator import DocumentGenerator
from recruitment_platform.agents.onboarding_automator.progress_tracker import ProgressTracker
from recruitment_platform.agents.onboarding_automator.task_scheduler import TaskScheduler
from recruitment_platform.agents.onboarding_automator.welcome_message import WelcomeMessage
from recruitment_platform.agents.employer_branding.brand_strategy import BrandStrategy
from recruitment_platform.agents.employer_branding.content_generator import ContentGenerator
from recruitment_platform.agents.employer_branding.reputation_manager import ReputationManager
from recruitment_platform.agents.employer_branding.review_analyzer import ReviewAnalyzer
from recruitment_platform.agents.employer_branding.sentiment_analyzer import SentimentAnalyzer
from recruitment_platform.agents.job_description_optimizer.ats_compatibility import ATSCompatibility
from recruitment_platform.agents.job_description_optimizer.bias_remover import BiasRemover
from recruitment_platform.agents.job_description_optimizer.keyword_optimizer import KeywordOptimizer
from recruitment_platform.agents.job_description_optimizer.seo_optimizer import SEOOptimizer
from recruitment_platform.agents.job_description_optimizer.tone_analyzer import ToneAnalyzer
from recruitment_platform.agents.recruitment_analytics.cost_analyzer import CostAnalyzer
from recruitment_platform.agents.recruitment_analytics.diversity_analyzer import DiversityAnalyzer
from recruitment_platform.agents.recruitment_analytics.funnel_analyzer import FunnelAnalyzer
from recruitment_platform.agents.recruitment_analytics.predictive_hiring import PredictiveHiring
from recruitment_platform.agents.recruitment_analytics.source_tracker import SourceTracker


def run_async(coro_func, *args, **kwargs):
    """Helper to run async functions."""
    return asyncio.run(coro_func(*args, **kwargs))


class TestResumeParserPerformance:
    """Benchmark resume parser agent performance."""

    def test_resume_parser_agent_process(self):
        """Benchmark resume parser agent process method."""
        agent = ResumeParserAgent()
        resume_data = {
            "text": """
            John Doe
            Software Engineer
            john.doe@email.com
            +1-555-0123

            Skills: Python, JavaScript, TypeScript, React, Node.js, SQL, Docker, Kubernetes

            Experience:
            Senior Software Engineer | TechCorp | 2020 - Present
            Led team of 5 engineers building microservices architecture.
            Designed and implemented REST APIs serving 10M+ requests/day.

            Software Engineer | StartupXYZ | 2017 - 2020
            Built full-stack web applications using React and Node.js.
            Implemented CI/CD pipelines reducing deployment time by 60%.

            Education:
            Master of Science in Computer Science, Stanford University, 2017
            Bachelor of Science in Software Engineering, MIT, 2015
            """
        }

        times = []
        for _ in range(30):
            start = time.perf_counter()
            result = run_async(agent.process, resume_data)
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nResume parser agent process: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.5, f"Resume parser agent too slow: {mean_time:.4f}s"

    def test_contact_extractor_agent(self):
        """Benchmark contact extractor agent."""
        agent = ContactExtractorAgent()
        resume_data = {
            "text": """
            John Doe
            Software Engineer
            john.doe@email.com
            +1-555-0123
            https://linkedin.com/in/johndoe
            """
        }

        times = []
        for _ in range(50):
            start = time.perf_counter()
            result = run_async(agent.process, resume_data)
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nContact extractor agent: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"Contact extractor too slow: {mean_time:.4f}s"

    def test_skills_extractor_agent(self):
        """Benchmark skills extractor agent."""
        agent = SkillsExtractorAgent()
        resume_data = {
            "text": """
            Experienced in Python, FastAPI, PostgreSQL, Docker, Kubernetes,
            AWS, Terraform, CI/CD, React, TypeScript, Node.js, GraphQL,
            Redis, Kafka, Elasticsearch, Spark, Hadoop, Airflow, dbt,
            Machine Learning, TensorFlow, PyTorch, scikit-learn, NLP,
            Computer Vision, Data Science, Data Engineering, Agile, Scrum,
            Jira, Confluence, Product Management, Roadmapping, User Research,
            A/B Testing, Figma, Sketch, Adobe XD, Accessibility, Tailwind CSS,
            REST API, Microservices, Serverless, Go, Rust, Ruby, PHP, Swift,
            Kotlin, Scala, R, MATLAB, Angular, Vue, Svelte, Next.js, Express,
            Django, Flask, Spring Boot, Rails, Jenkins, GitHub Actions, GitLab CI
            """
        }

        times = []
        for _ in range(50):
            start = time.perf_counter()
            result = run_async(agent.process, resume_data)
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nSkills extractor agent: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"Skills extractor too slow: {mean_time:.4f}s"

    def test_experience_extractor_agent(self):
        """Benchmark experience extractor agent."""
        agent = ExperienceExtractorAgent()
        resume_data = {
            "text": """
            Senior Software Engineer | TechCorp | Jan 2020 - Present
            Led team of 5 engineers building microservices architecture.

            Software Engineer | StartupXYZ | Jun 2017 - Dec 2019
            Built full-stack web applications using React and Node.js.

            Junior Developer | WebAgency | Aug 2015 - May 2017
            Developed client websites and maintained CMS platforms.
            """
        }

        times = []
        for _ in range(50):
            start = time.perf_counter()
            result = run_async(agent.process, resume_data)
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nExperience extractor agent: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"Experience extractor too slow: {mean_time:.4f}s"

    def test_education_extractor_agent(self):
        """Benchmark education extractor agent."""
        agent = EducationExtractorAgent()
        resume_data = {
            "text": """
            Education:
            Master of Science in Computer Science, Stanford University, 2017
            Bachelor of Science in Software Engineering, MIT, 2015
            MBA, Wharton School, 2020
            """
        }

        times = []
        for _ in range(50):
            start = time.perf_counter()
            result = run_async(agent.process, resume_data)
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nEducation extractor agent: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"Education extractor too slow: {mean_time:.4f}s"

    def test_resume_parser_agent_execute(self):
        """Benchmark resume parser agent execute method."""
        agent = ResumeParserAgent()
        resume_data = {
            "text": "John Doe, Software Engineer, john.doe@email.com, Python, FastAPI"
        }

        times = []
        for _ in range(30):
            start = time.perf_counter()
            result = run_async(agent.execute, resume_data)
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nResume parser agent execute: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.5, f"Resume parser execute too slow: {mean_time:.4f}s"


class TestCandidateMatcherPerformance:
    """Benchmark candidate matcher agent performance."""

    def test_bias_aware_ranker(self):
        """Benchmark bias-aware ranker agent."""
        agent = BiasAwareRanker()
        input_data = {
            "candidates": [
                {"candidate_id": f"cand-{i}", "match_score": float(100 - i)}
                for i in range(50)
            ],
            "job_requirements": {"title": "Engineer"},
        }

        times = []
        for _ in range(50):
            start = time.perf_counter()
            result = run_async(agent.process, input_data)
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nBias-aware ranker (50 cands): mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"Bias-aware ranker too slow: {mean_time:.4f}s"

    def test_culture_fit_assessor(self):
        """Benchmark culture fit assessor agent."""
        agent = CultureFitAssessor()
        input_data = {
            "candidate": {"name": "Test", "values": ["innovation", "teamwork"]},
            "company_culture": {"values": ["innovation", "excellence"]},
        }

        times = []
        for _ in range(50):
            start = time.perf_counter()
            result = run_async(agent.process, input_data)
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nCulture fit assessor: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"Culture fit assessor too slow: {mean_time:.4f}s"

    def test_match_explainer(self):
        """Benchmark match explainer agent."""
        agent = MatchExplainer()
        input_data = {
            "candidate": {"name": "Test"},
            "job": {"title": "Engineer"},
            "match_result": {"score": 85.0},
        }

        times = []
        for _ in range(50):
            start = time.perf_counter()
            result = run_async(agent.process, input_data)
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nMatch explainer: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"Match explainer too slow: {mean_time:.4f}s"

    def test_semantic_matcher(self):
        """Benchmark semantic matcher agent."""
        agent = SemanticMatcher()
        input_data = {
            "candidate_profile": {"skills": ["Python", "FastAPI"]},
            "job_description": "Looking for Python developer",
        }

        times = []
        for _ in range(50):
            start = time.perf_counter()
            result = run_async(agent.process, input_data)
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nSemantic matcher: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"Semantic matcher too slow: {mean_time:.4f}s"

    def test_skills_gap_analyzer(self):
        """Benchmark skills gap analyzer agent."""
        agent = SkillsGapAnalyzer()
        input_data = {
            "candidate_skills": ["Python", "FastAPI", "PostgreSQL"],
            "required_skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Kubernetes"],
        }

        times = []
        for _ in range(50):
            start = time.perf_counter()
            result = run_async(agent.process, input_data)
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nSkills gap analyzer: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"Skills gap analyzer too slow: {mean_time:.4f}s"


class TestBiasDetectorPerformance:
    """Benchmark bias detector agent performance."""

    def test_demographic_analyzer(self):
        """Benchmark demographic analyzer agent."""
        agent = DemographicAnalyzer()
        input_data = {
            "candidates": [
                {"id": f"cand-{i}", "gender": "F" if i % 2 == 0 else "M", "age": 25 + i % 20}
                for i in range(50)
            ]
        }

        times = []
        for _ in range(30):
            start = time.perf_counter()
            result = run_async(agent.process, input_data)
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nDemographic analyzer: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"Demographic analyzer too slow: {mean_time:.4f}s"

    def test_fairness_scorer(self):
        """Benchmark fairness scorer agent."""
        agent = FairnessScorer()
        input_data = {
            "matches": [
                {"candidate_id": f"cand-{i}", "score": float(100 - i)}
                for i in range(30)
            ]
        }

        times = []
        for _ in range(30):
            start = time.perf_counter()
            result = run_async(agent.process, input_data)
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nFairness scorer: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"Fairness scorer too slow: {mean_time:.4f}s"

    def test_language_bias_detector(self):
        """Benchmark language bias detector agent."""
        agent = LanguageBiasDetector()
        text = """
        We are looking for a rockstar ninja developer who can be our guru
        in building amazing products. The ideal candidate is a young,
        energetic digital native with a millennial mindset.
        """

        times = []
        for _ in range(30):
            start = time.perf_counter()
            result = run_async(agent.process, text)
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nLanguage bias detector: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"Language bias detector too slow: {mean_time:.4f}s"

    def test_pattern_detector(self):
        """Benchmark pattern detector agent."""
        agent = PatternDetector()
        input_data = {
            "job_descriptions": [
                f"Looking for candidate {i} with skills in Python and Java"
                for i in range(20)
            ]
        }

        times = []
        for _ in range(30):
            start = time.perf_counter()
            result = run_async(agent.process, input_data)
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nPattern detector: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"Pattern detector too slow: {mean_time:.4f}s"


class TestInterviewSchedulerPerformance:
    """Benchmark interview scheduler agent performance."""

    def test_availability_optimizer(self):
        """Benchmark availability optimizer agent."""
        agent = AvailabilityOptimizer()
        input_data = {
            "participants": [
                {"id": f"int-{i}", "available_slots": [(9 + i % 8, 10 + i % 8)]}
                for i in range(5)
            ],
            "duration_minutes": 60,
        }

        times = []
        for _ in range(30):
            start = time.perf_counter()
            result = run_async(agent.process, input_data)
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nAvailability optimizer: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"Availability optimizer too slow: {mean_time:.4f}s"

    def test_conflict_detector(self):
        """Benchmark conflict detector agent."""
        agent = ConflictDetector()
        input_data = {
            "existing_interviews": [
                {"id": f"ivw-{i}", "time": f"2026-10-{15 + i % 10}T10:00:00"}
                for i in range(10)
            ],
            "new_slot": {"start": "2026-10-15T10:00:00", "end": "2026-10-15T11:00:00"},
        }

        times = []
        for _ in range(30):
            start = time.perf_counter()
            result = run_async(agent.process, input_data)
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nConflict detector: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"Conflict detector too slow: {mean_time:.4f}s"

    def test_timezone_resolver(self):
        """Benchmark timezone resolver agent."""
        agent = TimezoneResolver()
        input_data = {
            "participants": [
                {"id": f"int-{i}", "timezone": ["US/Eastern", "US/Pacific", "Europe/London"][i % 3]}
                for i in range(6)
            ],
            "preferred_time": "2026-10-15T14:00:00Z",
        }

        times = []
        for _ in range(30):
            start = time.perf_counter()
            result = run_async(agent.process, input_data)
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nTimezone resolver: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"Timezone resolver too slow: {mean_time:.4f}s"


class TestSkillsAssessorPerformance:
    """Benchmark skills assessor agent performance."""

    def test_gap_analyzer(self):
        """Benchmark gap analyzer agent."""
        agent = GapAnalyzer()
        input_data = {
            "candidate_skills": ["Python", "FastAPI", "PostgreSQL"],
            "required_skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Kubernetes"],
        }

        times = []
        for _ in range(50):
            start = time.perf_counter()
            result = run_async(agent.process, input_data)
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nGap analyzer: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"Gap analyzer too slow: {mean_time:.4f}s"

    def test_proficiency_scorer(self):
        """Benchmark proficiency scorer agent."""
        agent = ProficiencyScorer()
        input_data = {
            "skill": "Python",
            "assessments": [
                {"score": 85, "level": "proficient"},
                {"score": 90, "level": "expert"},
            ],
        }

        times = []
        for _ in range(50):
            start = time.perf_counter()
            result = run_async(agent.process, input_data)
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nProficiency scorer: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"Proficiency scorer too slow: {mean_time:.4f}s"

    def test_skill_extractor(self):
        """Benchmark skill extractor agent."""
        agent = SkillExtractor()
        input_data = {
            "text": "Experienced in Python, FastAPI, PostgreSQL, Docker, Kubernetes, AWS"
        }

        times = []
        for _ in range(50):
            start = time.perf_counter()
            result = run_async(agent.process, input_data)
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nSkill extractor: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"Skill extractor too slow: {mean_time:.4f}s"

    def test_skill_validator(self):
        """Benchmark skill validator agent."""
        agent = SkillValidator()
        input_data = {
            "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Kubernetes"]
        }

        times = []
        for _ in range(50):
            start = time.perf_counter()
            result = run_async(agent.process, input_data)
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nSkill validator: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"Skill validator too slow: {mean_time:.4f}s"


class TestTalentPoolManagerPerformance:
    """Benchmark talent pool manager agent performance."""

    def test_candidate_sourcer(self):
        """Benchmark candidate sourcer agent."""
        agent = CandidateSourcer()
        input_data = {
            "job_requirements": {"skills": ["Python", "FastAPI"], "location": "Remote"},
            "sources": ["linkedind", "indeed", "github"],
        }

        times = []
        for _ in range(30):
            start = time.perf_counter()
            result = run_async(agent.process, input_data)
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nCandidate sourcer: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"Candidate sourcer too slow: {mean_time:.4f}s"

    def test_engagement_tracker(self):
        """Benchmark engagement tracker agent."""
        agent = EngagementTracker()
        input_data = {
            "candidates": [
                {"id": f"cand-{i}", "last_contact": f"2026-10-{1 + i % 15}"}
                for i in range(30)
            ]
        }

        times = []
        for _ in range(30):
            start = time.perf_counter()
            result = run_async(agent.process, input_data)
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nEngagement tracker: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"Engagement tracker too slow: {mean_time:.4f}s"

    def test_pool_analyzer(self):
        """Benchmark pool analyzer agent."""
        agent = PoolAnalyzer()
        input_data = {
            "pool": [
                {"id": f"cand-{i}", "skills": ["Python", "FastAPI"], "status": "active"}
                for i in range(50)
            ]
        }

        times = []
        for _ in range(30):
            start = time.perf_counter()
            result = run_async(agent.process, input_data)
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nPool analyzer: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"Pool analyzer too slow: {mean_time:.4f}s"

    def test_talent_recommender(self):
        """Benchmark talent recommender agent."""
        agent = TalentRecommender()
        input_data = {
            "job_requirements": {"skills": ["Python", "FastAPI"]},
            "pool_size": 100,
        }

        times = []
        for _ in range(30):
            start = time.perf_counter()
            result = run_async(agent.process, input_data)
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nTalent recommender: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"Talent recommender too slow: {mean_time:.4f}s"

    def test_talent_tagger(self):
        """Benchmark talent tagger agent."""
        agent = TalentTagger()
        input_data = {
            "candidates": [
                {"id": f"cand-{i}", "skills": ["Python", "FastAPI", "Docker"][: i % 3 + 1]}
                for i in range(30)
            ]
        }

        times = []
        for _ in range(30):
            start = time.perf_counter()
            result = run_async(agent.process, input_data)
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nTalent tagger: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"Talent tagger too slow: {mean_time:.4f}s"


class TestOnboardingAutomatorPerformance:
    """Benchmark onboarding automator agent performance."""

    def test_compliance_checker(self):
        """Benchmark compliance checker agent."""
        agent = ComplianceChecker()
        input_data = {
            "employee_data": {
                "id": "emp-001",
                "documents": ["id_proof", "address_proof", "offer_letter"],
            }
        }

        times = []
        for _ in range(30):
            start = time.perf_counter()
            result = run_async(agent.process, input_data)
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nCompliance checker: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"Compliance checker too slow: {mean_time:.4f}s"

    def test_document_generator(self):
        """Benchmark document generator agent."""
        agent = DocumentGenerator()
        input_data = {
            "template": "offer_letter",
            "employee_data": {"name": "John Doe", "role": "Engineer"},
        }

        times = []
        for _ in range(30):
            start = time.perf_counter()
            result = run_async(agent.process, input_data)
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nDocument generator: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"Document generator too slow: {mean_time:.4f}s"

    def test_progress_tracker(self):
        """Benchmark progress tracker agent."""
        agent = ProgressTracker()
        input_data = {
            "employee_id": "emp-001",
            "tasks": [
                {"id": f"task-{i}", "status": "completed" if i % 2 == 0 else "pending"}
                for i in range(20)
            ],
        }

        times = []
        for _ in range(30):
            start = time.perf_counter()
            result = run_async(agent.process, input_data)
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nProgress tracker: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"Progress tracker too slow: {mean_time:.4f}s"

    def test_task_scheduler(self):
        """Benchmark task scheduler agent."""
        agent = TaskScheduler()
        input_data = {
            "employee_id": "emp-001",
            "start_date": "2026-10-15",
            "tasks": [
                {"id": f"task-{i}", "duration_days": i % 5 + 1}
                for i in range(10)
            ],
        }

        times = []
        for _ in range(30):
            start = time.perf_counter()
            result = run_async(agent.process, input_data)
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nTask scheduler: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"Task scheduler too slow: {mean_time:.4f}s"

    def test_welcome_message(self):
        """Benchmark welcome message agent."""
        agent = WelcomeMessage()
        input_data = {
            "employee_name": "John Doe",
            "role": "Software Engineer",
            "start_date": "2026-10-15",
        }

        times = []
        for _ in range(50):
            start = time.perf_counter()
            result = run_async(agent.process, input_data)
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nWelcome message: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"Welcome message too slow: {mean_time:.4f}s"


class TestEmployerBrandingPerformance:
    """Benchmark employer branding agent performance."""

    def test_brand_strategy(self):
        """Benchmark brand strategy agent."""
        agent = BrandStrategy()
        input_data = {
            "company_data": {"name": "TechCorp", "industry": "Technology"},
            "target_audience": "Software Engineers",
        }

        times = []
        for _ in range(30):
            start = time.perf_counter()
            result = run_async(agent.process, input_data)
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nBrand strategy: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"Brand strategy too slow: {mean_time:.4f}s"

    def test_content_generator(self):
        """Benchmark content generator agent."""
        agent = ContentGenerator()
        input_data = {
            "content_type": "job_posting",
            "company_data": {"name": "TechCorp", "values": ["innovation", "excellence"]},
        }

        times = []
        for _ in range(30):
            start = time.perf_counter()
            result = run_async(agent.process, input_data)
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nContent generator: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"Content generator too slow: {mean_time:.4f}s"

    def test_reputation_manager(self):
        """Benchmark reputation manager agent."""
        agent = ReputationManager()
        input_data = {
            "company_name": "TechCorp",
            "reviews": [
                {"rating": 4, "text": "Great place to work"}
                for _ in range(20)
            ],
        }

        times = []
        for _ in range(30):
            start = time.perf_counter()
            result = run_async(agent.process, input_data)
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nReputation manager: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"Reputation manager too slow: {mean_time:.4f}s"

    def test_review_analyzer(self):
        """Benchmark review analyzer agent."""
        agent = ReviewAnalyzer()
        input_data = {
            "reviews": [
                {"rating": i % 5 + 1, "text": f"Review text {i} with some content"}
                for i in range(30)
            ]
        }

        times = []
        for _ in range(30):
            start = time.perf_counter()
            result = run_async(agent.process, input_data)
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nReview analyzer: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"Review analyzer too slow: {mean_time:.4f}s"

    def test_sentiment_analyzer(self):
        """Benchmark sentiment analyzer agent."""
        agent = SentimentAnalyzer()
        input_data = {
            "texts": [
                "Great company to work for",
                "Excellent benefits and culture",
                "Good work-life balance",
                "Amazing team and leadership",
                "Outstanding growth opportunities",
            ] * 10
        }

        times = []
        for _ in range(30):
            start = time.perf_counter()
            result = run_async(agent.process, input_data)
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nSentiment analyzer: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"Sentiment analyzer too slow: {mean_time:.4f}s"


class TestJobDescriptionOptimizerPerformance:
    """Benchmark job description optimizer agent performance."""

    def test_ats_compatibility(self):
        """Benchmark ATS compatibility agent."""
        agent = ATSCompatibility()
        input_data = {
            "job_description": "Looking for a Python developer with FastAPI experience"
        }

        times = []
        for _ in range(30):
            start = time.perf_counter()
            result = run_async(agent.process, input_data)
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nATS compatibility: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"ATS compatibility too slow: {mean_time:.4f}s"

    def test_bias_remover(self):
        """Benchmark bias remover agent."""
        agent = BiasRemover()
        input_data = {
            "text": "We need a rockstar ninja developer who is young and energetic"
        }

        times = []
        for _ in range(30):
            start = time.perf_counter()
            result = run_async(agent.process, input_data)
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nBias remover: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"Bias remover too slow: {mean_time:.4f}s"

    def test_keyword_optimizer(self):
        """Benchmark keyword optimizer agent."""
        agent = KeywordOptimizer()
        input_data = {
            "job_description": "Software engineer needed for web development role",
            "target_keywords": ["Python", "FastAPI", "React", "PostgreSQL"],
        }

        times = []
        for _ in range(30):
            start = time.perf_counter()
            result = run_async(agent.process, input_data)
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nKeyword optimizer: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"Keyword optimizer too slow: {mean_time:.4f}s"

    def test_seo_optimizer(self):
        """Benchmark SEO optimizer agent."""
        agent = SEOOptimizer()
        input_data = {
            "job_title": "Software Engineer",
            "job_description": "Build web applications using modern technologies",
        }

        times = []
        for _ in range(30):
            start = time.perf_counter()
            result = run_async(agent.process, input_data)
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nSEO optimizer: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"SEO optimizer too slow: {mean_time:.4f}s"

    def test_tone_analyzer(self):
        """Benchmark tone analyzer agent."""
        agent = ToneAnalyzer()
        input_data = {
            "text": "We are looking for a passionate and driven individual to join our dynamic team"
        }

        times = []
        for _ in range(30):
            start = time.perf_counter()
            result = run_async(agent.process, input_data)
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nTone analyzer: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"Tone analyzer too slow: {mean_time:.4f}s"


class TestRecruitmentAnalyticsPerformance:
    """Benchmark recruitment analytics agent performance."""

    def test_cost_analyzer(self):
        """Benchmark cost analyzer agent."""
        agent = CostAnalyzer()
        input_data = {
            "hiring_data": [
                {"cost": 5000 + i * 100, "source": "linkedin"}
                for i in range(20)
            ]
        }

        times = []
        for _ in range(30):
            start = time.perf_counter()
            result = run_async(agent.process, input_data)
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nCost analyzer: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"Cost analyzer too slow: {mean_time:.4f}s"

    def test_diversity_analyzer(self):
        """Benchmark diversity analyzer agent."""
        agent = DiversityAnalyzer()
        input_data = {
            "candidates": [
                {"id": f"cand-{i}", "gender": ["F", "M", "NB"][i % 3], "ethnicity": ["A", "B", "C", "D"][i % 4]}
                for i in range(50)
            ]
        }

        times = []
        for _ in range(30):
            start = time.perf_counter()
            result = run_async(agent.process, input_data)
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nDiversity analyzer: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"Diversity analyzer too slow: {mean_time:.4f}s"

    def test_funnel_analyzer(self):
        """Benchmark funnel analyzer agent."""
        agent = FunnelAnalyzer()
        input_data = {
            "stages": [
                {"name": "applied", "count": 1000},
                {"name": "screened", "count": 500},
                {"name": "interviewed", "count": 200},
                {"name": "offered", "count": 50},
                {"name": "hired", "count": 20},
            ]
        }

        times = []
        for _ in range(30):
            start = time.perf_counter()
            result = run_async(agent.process, input_data)
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nFunnel analyzer: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"Funnel analyzer too slow: {mean_time:.4f}s"

    def test_predictive_hiring(self):
        """Benchmark predictive hiring agent."""
        agent = PredictiveHiring()
        input_data = {
            "historical_data": [
                {"quarter": f"Q{i % 4 + 1}", "hires": 10 + i, "openings": 15 + i}
                for i in range(20)
            ]
        }

        times = []
        for _ in range(30):
            start = time.perf_counter()
            result = run_async(agent.process, input_data)
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nPredictive hiring: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"Predictive hiring too slow: {mean_time:.4f}s"

    def test_source_tracker(self):
        """Benchmark source tracker agent."""
        agent = SourceTracker()
        input_data = {
            "applications": [
                {"source": ["linkedin", "indeed", "referral", "direct"][i % 4], "hired": i % 3 == 0}
                for i in range(100)
            ]
        }

        times = []
        for _ in range(30):
            start = time.perf_counter()
            result = run_async(agent.process, input_data)
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nSource tracker: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"Source tracker too slow: {mean_time:.4f}s"
