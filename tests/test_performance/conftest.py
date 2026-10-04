"""Performance-specific fixtures for benchmark tests."""
import time
import statistics
from dataclasses import dataclass, field
from typing import Any, Callable

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from recruitment_platform.main import app
from recruitment_platform.models import Base
from recruitment_platform.api.dependencies import get_db


# Benchmark database
BENCH_DATABASE_URL = "sqlite:///:memory:"

bench_engine = create_engine(
    BENCH_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
BenchSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=bench_engine)


def override_get_db_bench():
    db = BenchSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db_bench


@dataclass
class BenchmarkResult:
    """Stores timing results for a benchmark run."""
    name: str
    times: list[float] = field(default_factory=list)

    @property
    def mean(self) -> float:
        return statistics.mean(self.times) if self.times else 0.0

    @property
    def median(self) -> float:
        return statistics.median(self.times) if self.times else 0.0

    @property
    def stdev(self) -> float:
        return statistics.stdev(self.times) if len(self.times) > 1 else 0.0

    @property
    def min_time(self) -> float:
        return min(self.times) if self.times else 0.0

    @property
    def max_time(self) -> float:
        return max(self.times) if self.times else 0.0

    @property
    def p95(self) -> float:
        if not self.times:
            return 0.0
        sorted_times = sorted(self.times)
        idx = int(len(sorted_times) * 0.95)
        return sorted_times[min(idx, len(sorted_times) - 1)]

    def __str__(self) -> str:
        return (
            f"{self.name}: "
            f"mean={self.mean:.4f}s, "
            f"median={self.median:.4f}s, "
            f"stdev={self.stdev:.4f}s, "
            f"min={self.min_time:.4f}s, "
            f"max={self.max_time:.4f}s, "
            f"p95={self.p95:.4f}s"
        )


class Benchmark:
    """Custom benchmark utility for measuring execution time."""

    def __init__(self, name: str, iterations: int = 10, warmup: int = 2):
        self.name = name
        self.iterations = iterations
        self.warmup = warmup
        self.result = BenchmarkResult(name=name)

    def run(self, func: Callable, *args: Any, **kwargs: Any) -> BenchmarkResult:
        """Run a function multiple times and collect timing statistics."""
        # Warmup runs
        for _ in range(self.warmup):
            func(*args, **kwargs)

        # Timed runs
        for _ in range(self.iterations):
            start = time.perf_counter()
            func(*args, **kwargs)
            end = time.perf_counter()
            self.result.times.append(end - start)

        return self.result

    async def run_async(self, func: Callable, *args: Any, **kwargs: Any) -> BenchmarkResult:
        """Run an async function multiple times and collect timing statistics."""
        import asyncio

        # Warmup runs
        for _ in range(self.warmup):
            await func(*args, **kwargs)

        # Timed runs
        for _ in range(self.iterations):
            start = time.perf_counter()
            await func(*args, **kwargs)
            end = time.perf_counter()
            self.result.times.append(end - start)

        return self.result


@pytest.fixture
def benchmark_factory():
    """Factory for creating benchmark instances."""
    benchmarks: list[BenchmarkResult] = []

    def factory(name: str, iterations: int = 10, warmup: int = 2) -> Benchmark:
        return Benchmark(name=name, iterations=iterations, warmup=warmup)

    yield factory

    # Print summary after all tests
    if benchmarks:
        print("\n" + "=" * 70)
        print("PERFORMANCE BENCHMARK SUMMARY")
        print("=" * 70)
        for result in benchmarks:
            print(result)
        print("=" * 70)


@pytest.fixture
def bench_client():
    """Create a test client with benchmark database."""
    Base.metadata.create_all(bind=bench_engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=bench_engine)


@pytest.fixture
def bench_db_session():
    """Create a fresh database session for benchmarking."""
    Base.metadata.create_all(bind=bench_engine)
    session = BenchSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=bench_engine)


@pytest.fixture
def populated_bench_db(bench_db_session):
    """Create a database with test data for benchmarking."""
    from recruitment_platform.models.candidate import Candidate
    from recruitment_platform.models.job import Job
    from recruitment_platform.models.application import Application

    # Create test candidates
    candidates = []
    for i in range(100):
        candidate = Candidate(
            name=f"Candidate {i}",
            email=f"candidate{i}@test.com",
            phone=f"+1-555-{i:04d}",
            skills=f"Python,FastAPI,SQL,Docker,Kubernetes",
            experience=f"{i % 10} years of experience",
            education="Bachelor's in Computer Science",
        )
        candidates.append(candidate)
    bench_db_session.add_all(candidates)

    # Create test jobs
    jobs = []
    for i in range(50):
        job = Job(
            title=f"Job Position {i}",
            description=f"Description for job {i}",
            requirements="Python,FastAPI,PostgreSQL",
            status="open",
            employer_id=i % 10 + 1,
        )
        jobs.append(job)
    bench_db_session.add_all(jobs)
    bench_db_session.flush()

    # Create test applications
    applications = []
    for i in range(200):
        application = Application(
            candidate_id=(i % 100) + 1,
            job_id=(i % 50) + 1,
            status=["pending", "reviewing", "interview", "offer", "hired"][i % 5],
        )
        applications.append(application)
    bench_db_session.add_all(applications)
    bench_db_session.commit()

    return bench_db_session
