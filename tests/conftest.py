"""Shared test fixtures for recruitment-platform.

Security middleware (Auth / RateLimit / InputSanitization) is intentionally NOT
disabled here. Tests that need to reach protected routes authenticate for real
via the ``auth_headers`` / ``client`` fixtures below, so the suite exercises the
same code path production does.

Only public endpoints (/, /health, /ready, /docs, /openapi.json) are reachable
without credentials; everything under /api requires a valid bearer token.
"""

from __future__ import annotations

import os
import tempfile
import uuid
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

# The auth routes use a module-level sqlite file captured at import time, so it
# must be redirected BEFORE recruitment_platform.api.routes.auth is imported.
_TMP_DB = os.path.join(tempfile.mkdtemp(prefix="rp_auth_test_"), "auth.db")
os.environ["DATABASE_PATH"] = _TMP_DB

from recruitment_platform.main import app  # noqa: E402
from recruitment_platform.models import Base  # noqa: E402

# Import all models so they register with Base.metadata and create_all() below
# actually creates their tables.
from recruitment_platform.models.employer import Employer  # noqa: E402, F401
from recruitment_platform.models.skill import Skill  # noqa: E402, F401
from recruitment_platform.api.dependencies import get_db  # noqa: E402
from recruitment_platform.security.auth import create_access_token  # noqa: E402
from recruitment_platform.security.rate_limit import rate_limiter  # noqa: E402

from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


# ---------------------------------------------------------------------------
# Rate limiting
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """Clear in-memory rate-limit state between tests.

    The limiter is a process-global keyed by client IP, and burst_size is only
    10, so without this a few tests would trip 429 and cascade into unrelated
    failures. This resets state, it does not disable enforcement - tests that
    assert on rate limiting re-populate it themselves.
    """
    rate_limiter._requests.clear()
    yield
    rate_limiter._requests.clear()


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------


@pytest.fixture
def registered_user() -> dict:
    """A unique user registered through the real /api/auth/register endpoint."""
    email = f"user-{uuid.uuid4().hex}@example.com"
    password = "Str0ng!Passw0rd"
    return {"name": "Test User", "email": email, "password": password}


@pytest.fixture
def auth_token(client: TestClient, registered_user: dict) -> str:
    """Register a real user and return the JWT issued by the login endpoint."""
    resp = client.post("/api/auth/register", json=registered_user)
    assert resp.status_code == 200, f"register failed: {resp.status_code} {resp.text}"
    return resp.json()["token"]


@pytest.fixture
def auth_headers(auth_token: str) -> dict[str, str]:
    """Authorization headers carrying a real, valid access token."""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def make_token():
    """Factory for tokens with custom claims (roles, subject, expiry)."""

    def _make(**claims) -> str:
        return create_access_token(claims)

    return _make


@pytest.fixture
def client(db_session) -> Iterator[TestClient]:
    """Test client with a fresh database and REAL auth enforcement."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def unauthenticated_client(db_session) -> Iterator[TestClient]:
    """Alias for :func:`client`, clarifying intent for auth-bypass tests.

    Nothing is stubbed - requests simply carry no Authorization header.
    """
    with TestClient(app) as c:
        yield c


# ---------------------------------------------------------------------------
# Sample payloads
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_employer():
    """Sample employer data."""
    return {
        "name": "Test Company",
        "industry": "Technology",
        "size": "50-200",
        "location": "San Francisco, CA",
        "website": "https://testcompany.com",
        "description": "A test company for testing",
    }


@pytest.fixture
def sample_candidate():
    """Sample candidate data matching CandidateCreate schema."""
    return {
        "first_name": "John",
        "last_name": "Doe",
        "email": f"candidate-{uuid.uuid4().hex}@example.com",
        "phone": "+1-555-0123",
        "role_applied": "Senior Software Engineer",
        "years_experience": 5,
        "experience_level": "senior",
        "skills": ["Python", "FastAPI", "SQL"],
        "location": "San Francisco, CA",
        "remote_ok": True,
    }


@pytest.fixture
def sample_job():
    """Sample job data matching JobCreate schema."""
    return {
        "title": "Senior Software Engineer",
        "description": "We are looking for a senior software engineer",
        "requirements": ["Python", "FastAPI", "PostgreSQL"],
        "salary_min": 120000,
        "salary_max": 180000,
        "location": "San Francisco, CA",
    }