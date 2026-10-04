"""Shared test fixtures for recruitment-platform."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from recruitment_platform.main import app
from recruitment_platform.database import Base, get_db


# Test database
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


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with fresh database."""
    with TestClient(app) as c:
        yield c


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
    """Sample candidate data."""
    return {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "+1-555-0123",
        "skills": ["Python", "FastAPI", "SQL"],
        "experience_years": 5,
        "education": "Bachelor's in Computer Science",
    }


@pytest.fixture
def sample_job():
    """Sample job data."""
    return {
        "title": "Senior Software Engineer",
        "description": "We are looking for a senior software engineer",
        "requirements": ["Python", "FastAPI", "PostgreSQL"],
        "salary_min": 120000,
        "salary_max": 180000,
        "location": "San Francisco, CA",
        "employer_id": 1,
    }


@pytest.fixture
def sample_application():
    """Sample application data."""
    return {
        "job_id": 1,
        "candidate_id": 1,
        "cover_letter": "I am very interested in this position",
        "status": "pending",
    }
