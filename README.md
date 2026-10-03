# Recruitment Platform

> **Unified AI-Powered Recruitment Automation Platform**
>
> A production-grade, modular recruitment system that unifies 10 independent recruitment sub-projects into a single FastAPI application with 50 AI-powered agents across 10 recruitment domains.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL%203.0-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF.svg)](https://github.com/features/actions)

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
- [Deployment](#deployment)
- [Configuration](#configuration)
- [Testing](#testing)
- [Monitoring](#monitoring)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

The Recruitment Platform consolidates the entire recruitment lifecycle — from resume parsing and candidate matching to onboarding and employer branding — into a single, cohesive system. Each domain is powered by 5 specialized AI agents, enabling intelligent automation at every stage of the hiring funnel.

### Key Capabilities

| Domain | Capability | Agents |
|--------|-----------|--------|
| Resume Parsing | Extract structured data from resumes | 5 |
| Candidate Matching | Bias-aware ranking and culture fit | 5 |
| Interview Scheduling | Smart scheduling with conflict detection | 5 |
| Skills Assessment | Gap analysis and proficiency scoring | 5 |
| Bias Detection | Fairness metrics and mitigation | 5 |
| Talent Pool Management | Sourcing, engagement, and tagging | 5 |
| Recruitment Analytics | Funnel analysis and predictive hiring | 5 |
| Onboarding Automation | Compliance, documents, and task tracking | 5 |
| Job Description Optimization | ATS compatibility and SEO | 5 |
| Employer Branding | Reputation management and content | 5 |

---

## Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        Web[Web Dashboard]
        Mobile[Mobile App]
        API[External API Clients]
    end

    subgraph "API Gateway"
        GW[FastAPI Router]
        Auth[Authentication]
        RateLimit[Rate Limiting]
    end

    subgraph "Agent Orchestration Layer"
        subgraph "Resume Parser Domain"
            RP1[ResumeParserAgent]
            RP2[ContactExtractorAgent]
            RP3[EducationExtractorAgent]
            RP4[ExperienceExtractorAgent]
            RP5[SkillsExtractorAgent]
        end
        subgraph "Candidate Matcher Domain"
            CM1[BiasAwareRanker]
            CM2[CultureFitAssessor]
            CM3[MatchExplainer]
            CM4[SemanticMatcher]
            CM5[SkillsGapAnalyzer]
        end
        subgraph "Interview Scheduler Domain"
            IS1[AvailabilityOptimizer]
            IS2[CalendarSync]
            IS3[ConflictDetector]
            IS4[Reminder]
            IS5[TimezoneResolver]
        end
        subgraph "Skills Assessor Domain"
            SA1[GapAnalyzer]
            SA2[LearningPathRecommender]
            SA3[ProficiencyScorer]
            SA4[SkillExtractor]
            SA5[SkillValidator]
        end
        subgraph "Bias Detector Domain"
            BD1[DemographicAnalyzer]
            BD2[FairnessScorer]
            BD3[LanguageBiasDetector]
            BD4[PatternDetector]
            BD5[Recommendation]
        end
        subgraph "Talent Pool Domain"
            TP1[CandidateSourcer]
            TP2[EngagementTracker]
            TP3[PoolAnalyzer]
            TP4[TalentRecommender]
            TP5[TalentTagger]
        end
        subgraph "Analytics Domain"
            AN1[CostAnalyzer]
            AN2[DiversityAnalyzer]
            AN3[FunnelAnalyzer]
            AN4[PredictiveHiring]
            AN5[SourceTracker]
        end
        subgraph "Onboarding Domain"
            OB1[ComplianceChecker]
            OB2[DocumentGenerator]
            OB3[ProgressTracker]
            OB4[TaskScheduler]
            OB5[WelcomeMessage]
        end
        subgraph "Job Description Domain"
            JD1[ATSCompatibility]
            JD2[BiasRemover]
            JD3[KeywordOptimizer]
            JD4[SEOOptimizer]
            JD5[ToneAnalyzer]
        end
        subgraph "Employer Branding Domain"
            EB1[BrandStrategy]
            EB2[ContentGenerator]
            EB3[ReputationManager]
            EB4[ReviewAnalyzer]
            EB5[SentimentAnalyzer]
        end
    end

    subgraph "Service Layer"
        SV1[Resume Service]
        SV2[Matching Service]
        SV3[Scheduling Service]
        SV4[Assessment Service]
        SV5[Analytics Service]
    end

    subgraph "Integration Layer"
        INT1[OpenAI / LLM]
        INT2[Calendar APIs]
        INT3[Email / Notifications]
        INT4[ATS Integrations]
        INT5[Storage]
    end

    subgraph "Data Layer"
        DB[(PostgreSQL)]
        CACHE[(Redis)]
        VECTOR[(Vector DB)]
    end

    Web --> GW
    Mobile --> GW
    API --> GW
    GW --> Auth --> RateLimit

    RateLimit --> RP1 & RP2 & RP3 & RP4 & RP5
    RateLimit --> CM1 & CM2 & CM3 & CM4 & CM5
    RateLimit --> IS1 & IS2 & IS3 & IS4 & IS5
    RateLimit --> SA1 & SA2 & SA3 & SA4 & SA5
    RateLimit --> BD1 & BD2 & BD3 & BD4 & BD5
    RateLimit --> TP1 & TP2 & TP3 & TP4 & TP5
    RateLimit --> AN1 & AN2 & AN3 & AN4 & AN5
    RateLimit --> OB1 & OB2 & OB3 & OB4 & OB5
    RateLimit --> JD1 & JD2 & JD3 & JD4 & JD5
    RateLimit --> EB1 & EB2 & EB3 & EB4 & EB5

    RP1 & RP2 & RP3 & RP4 & RP5 --> SV1
    CM1 & CM2 & CM3 & CM4 & CM5 --> SV2
    IS1 & IS2 & IS3 & IS4 & IS5 --> SV3
    SA1 & SA2 & SA3 & SA4 & SA5 --> SV4
    AN1 & AN2 & AN3 & AN4 & AN5 --> SV5

    SV1 & SV2 & SV3 & SV4 & SV5 --> INT1 & INT2 & INT3 & INT4 & INT5
    INT1 & INT2 & INT3 & INT4 & INT5 --> DB & CACHE & VECTOR
```

### Project Structure

```
recruitment-platform/
├── src/recruitment_platform/
│   ├── agents/                    # 50 AI agents across 10 domains
│   │   ├── resume_parser/          # Resume parsing agents
│   │   ├── candidate_matcher/      # Candidate matching agents
│   │   ├── interview_scheduler/    # Interview scheduling agents
│   │   ├── skills_assessor/        # Skills assessment agents
│   │   ├── bias_detector/          # Bias detection agents
│   │   ├── talent_pool_manager/    # Talent pool agents
│   │   ├── recruitment_analytics/  # Analytics agents
│   │   ├── onboarding_automator/   # Onboarding agents
│   │   ├── job_description_optimizer/ # JD optimization agents
│   │   └── employer_branding/      # Employer branding agents
│   ├── api/
│   │   ├── routes/                # API endpoint handlers
│   │   ├── router.py              # API router configuration
│   │   └── dependencies.py        # Shared dependencies
│   ├── config/                    # Configuration management
│   ├── integrations/              # External service clients
│   ├── models/                    # Pydantic schemas
│   ├── services/                  # Business logic layer
│   └── tests/                     # Test suite
├── k8s/                           # Kubernetes manifests
├── docs/                          # Documentation
├── diagrams/                      # Architecture diagrams
├── monitoring/                    # Monitoring configuration
├── .github/workflows/             # CI/CD pipelines
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

---

## Features

- **50 AI-Powered Agents** — Specialized agents for every recruitment domain
- **Bias-Aware Matching** — Built-in fairness metrics and bias mitigation
- **Semantic Search** — Embedding-based candidate and job matching
- **Smart Scheduling** — Conflict detection, timezone handling, calendar sync
- **Predictive Analytics** — Funnel analysis, diversity metrics, hiring predictions
- **ATS Integration** — Compatible with major applicant tracking systems
- **RESTful API** — 42 endpoints with OpenAPI documentation
- **Production-Ready** — Docker, Kubernetes, monitoring, and CI/CD included

---

## Quick Start

### Prerequisites

- Python 3.12+
- Docker & Docker Compose (optional)
- Kubernetes cluster (for production)

### Local Development

```bash
# Clone the repository
git clone https://github.com/AAH20/recruitment-platform.git
cd recruitment-platform

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Run the application
python -m recruitment_platform.main
```

The API will be available at `http://localhost:8000`

### Docker

```bash
# Build and run with Docker Compose
docker-compose up --build

# Access the application
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### Kubernetes

```bash
# Deploy to Kubernetes
kubectl apply -f k8s/base/
kubectl apply -f k8s/overlays/production/
```

---

## API Reference

All endpoints are prefixed with `/api/v1`:

### Health & Status

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/ready` | Readiness probe |
| GET | `/metrics` | Prometheus metrics |

### Resume Parser

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/resume-parser/parse` | Parse a resume document |
| POST | `/api/v1/resume-parser/extract-contact` | Extract contact information |
| POST | `/api/v1/resume-parser/extract-skills` | Extract skills from text |

### Candidate Matcher

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/candidate-matcher/match` | Match candidates to job |
| POST | `/api/v1/candidate-matcher/rank` | Rank candidates with bias mitigation |
| GET | `/api/v1/candidate-matcher/explain/:match_id` | Explain match decision |

### Interview Scheduler

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/interview-scheduler/schedule` | Schedule an interview |
| GET | `/api/v1/interview-scheduler/availability` | Get available time slots |
| POST | `/api/v1/interview-scheduler/reminder` | Set interview reminder |

### Skills Assessor

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/skills-assessor/assess` | Assess candidate skills |
| POST | `/api/v1/skills-assessor/gap-analysis` | Analyze skill gaps |
| GET | `/api/v1/skills-assessor/learning-path/:skill` | Get learning path |

### Bias Detector

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/bias-detector/analyze` | Analyze for bias |
| GET | `/api/v1/bias-detector/fairness-metrics` | Get fairness metrics |
| POST | `/api/v1/bias-detector/mitigation` | Get mitigation recommendations |
| POST | `/api/v1/bias-detector/language-check` | Check language for bias |

### Talent Pool

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/talent-pool/source` | Source candidates from pool |
| GET | `/api/v1/talent-pool/health` | Get pool health metrics |
| POST | `/api/v1/talent-pool/recommend` | Recommend talent for position |
| POST | `/api/v1/talent-pool/engage` | Track candidate engagement |

### Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/analytics/funnel` | Recruitment funnel analysis |
| GET | `/api/v1/analytics/diversity` | Diversity metrics |
| GET | `/api/v1/analytics/cost` | Cost analysis |
| GET | `/api/v1/analytics/sources` | Source effectiveness |
| POST | `/api/v1/analytics/predict` | Predict hiring outcomes |

### Onboarding

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/onboarding/start` | Start onboarding process |
| GET | `/api/v1/onboarding/progress/:candidate_id` | Track onboarding progress |
| POST | `/api/v1/onboarding/documents` | Generate onboarding documents |
| POST | `/api/v1/onboarding/tasks` | Schedule onboarding tasks |
| POST | `/api/v1/onboarding/compliance` | Check compliance requirements |

### Job Description

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/job-description/optimize` | Optimize job description |
| POST | `/api/v1/job-description/ats-check` | Check ATS compatibility |
| POST | `/api/v1/job-description/keywords` | Optimize keywords |
| POST | `/api/v1/job-description/seo` | SEO optimization |
| POST | `/api/v1/job-description/tone` | Analyze tone |

### Employer Branding

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/employer-branding/strategy` | Develop branding strategy |
| POST | `/api/v1/employer-branding/content` | Generate branding content |
| GET | `/api/v1/employer-branding/reputation` | Get reputation metrics |
| POST | `/api/v1/employer-branding/reviews` | Analyze reviews |
| POST | `/api/v1/employer-branding/sentiment` | Analyze sentiment |

**Total: 42 API endpoints**

---

## Deployment

### Docker Compose (Development)

```bash
docker-compose up -d
```

### Kubernetes (Production)

```bash
# Apply base manifests
kubectl apply -f k8s/base/

# Apply production overlay
kubectl apply -f k8s/overlays/production/

# Verify deployment
kubectl get pods -n recruitment-platform
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | `Recruitment Platform` | Application name |
| `APP_VERSION` | `1.0.0` | Application version |
| `DEBUG` | `false` | Debug mode |
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `8000` | Server port |
| `WORKERS` | `1` | Number of workers |
| `SECRET_KEY` | — | Application secret key |
| `DATABASE_URL` | `sqlite:///./recruitment.db` | Database connection |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection |
| `OPENAI_API_KEY` | — | OpenAI API key |
| `OPENAI_MODEL` | `gpt-4` | OpenAI model |
| `LOG_LEVEL` | `INFO` | Logging level |
| `LOG_FORMAT` | `json` | Log format |

---

## Configuration

Configuration is managed via environment variables or `.env` file:

```env
APP_NAME=Recruitment Platform
APP_VERSION=1.0.0
DEBUG=false
HOST=0.0.0.0
PORT=8000
WORKERS=1
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/recruitment
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=your-openai-key
OPENAI_MODEL=gpt-4
LOG_LEVEL=INFO
LOG_FORMAT=json
```

---

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=recruitment_platform --cov-report=html

# Run specific test file
pytest src/recruitment_platform/tests/test_agents.py

# Run with verbose output
pytest -v
```

---

## Monitoring

Prometheus metrics and health checks are available at:

- `/api/v1/health` — Health check
- `/api/v1/ready` — Readiness check
- `/metrics` — Prometheus metrics

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the AGPL-3.0 License — see the [LICENSE](LICENSE) file for details.
