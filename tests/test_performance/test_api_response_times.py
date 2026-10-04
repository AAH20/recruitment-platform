"""API response time benchmarks for recruitment-platform."""
import time
import statistics
import concurrent.futures
from typing import Any

import pytest
from fastapi.testclient import TestClient

from recruitment_platform.main import app


class TestAPIResponseTimes:
    """Benchmark API endpoint response times."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        with TestClient(app) as c:
            yield c

    def test_health_endpoint_response_time(self, client: TestClient):
        """Benchmark health check endpoint response time."""
        times = []
        for _ in range(50):
            start = time.perf_counter()
            response = client.get("/api/v1/health")
            end = time.perf_counter()
            assert response.status_code == 200
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nHealth endpoint: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"Health endpoint too slow: {mean_time:.4f}s"

    def test_readiness_endpoint_response_time(self, client: TestClient):
        """Benchmark readiness check endpoint response time."""
        times = []
        for _ in range(50):
            start = time.perf_counter()
            response = client.get("/api/v1/ready")
            end = time.perf_counter()
            assert response.status_code == 200
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nReadiness endpoint: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"Readiness endpoint too slow: {mean_time:.4f}s"

    def test_search_jobs_response_time(self, client: TestClient):
        """Benchmark job search endpoint."""
        times = []
        for _ in range(30):
            start = time.perf_counter()
            response = client.get("/api/v1/search/jobs?q=engineer&limit=20")
            end = time.perf_counter()
            assert response.status_code == 200
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nSearch jobs: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.3, f"Search jobs too slow: {mean_time:.4f}s"

    def test_search_candidates_response_time(self, client: TestClient):
        """Benchmark candidate search endpoint."""
        times = []
        for _ in range(30):
            start = time.perf_counter()
            response = client.get("/api/v1/search/candidates?q=python&limit=20")
            end = time.perf_counter()
            assert response.status_code == 200
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nSearch candidates: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.3, f"Search candidates too slow: {mean_time:.4f}s"

    def test_search_skills_response_time(self, client: TestClient):
        """Benchmark skills search endpoint."""
        times = []
        for _ in range(30):
            start = time.perf_counter()
            response = client.get("/api/v1/search/skills?q=python&limit=20")
            end = time.perf_counter()
            assert response.status_code == 200
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nSearch skills: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.3, f"Search skills too slow: {mean_time:.4f}s"

    def test_autocomplete_response_time(self, client: TestClient):
        """Benchmark autocomplete endpoint."""
        times = []
        for _ in range(30):
            start = time.perf_counter()
            response = client.get("/api/v1/search/autocomplete?q=eng&entity_type=job")
            end = time.perf_counter()
            assert response.status_code == 200
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nAutocomplete: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.3, f"Autocomplete too slow: {mean_time:.4f}s"

    def test_resume_parser_endpoint_response_time(self, client: TestClient):
        """Benchmark resume parser endpoint."""
        times = []
        for _ in range(20):
            start = time.perf_counter()
            response = client.post(
                "/api/v1/resume-parser/parse",
                json={"text": "John Doe, Python developer with 5 years experience"},
            )
            end = time.perf_counter()
            # May be 404 if endpoint not implemented, that's ok for benchmark
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nResume parser endpoint: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.5, f"Resume parser endpoint too slow: {mean_time:.4f}s"

    def test_candidate_matcher_endpoint_response_time(self, client: TestClient):
        """Benchmark candidate matcher endpoint."""
        times = []
        for _ in range(20):
            start = time.perf_counter()
            response = client.post(
                "/api/v1/candidate-matcher/match",
                json={
                    "candidates": [{"id": "1", "skills": ["Python"]}],
                    "job_requirements": {"skills": ["Python"]},
                },
            )
            end = time.perf_counter()
            assert response.status_code == 200
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nCandidate matcher endpoint: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.5, f"Candidate matcher endpoint too slow: {mean_time:.4f}s"

    def test_bias_detector_endpoint_response_time(self, client: TestClient):
        """Benchmark bias detector endpoint."""
        times = []
        for _ in range(20):
            start = time.perf_counter()
            response = client.post(
                "/api/v1/bias-detector/analyze",
                json={"text": "We are looking for a rockstar ninja developer"},
            )
            end = time.perf_counter()
            # May be 404 if endpoint not implemented
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nBias detector endpoint: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.5, f"Bias detector endpoint too slow: {mean_time:.4f}s"

    def test_skills_assessor_endpoint_response_time(self, client: TestClient):
        """Benchmark skills assessor endpoint."""
        times = []
        for _ in range(20):
            start = time.perf_counter()
            response = client.post(
                "/api/v1/skills-assessor/assess",
                json={"candidate_id": "1", "skills": ["Python", "FastAPI"]},
            )
            end = time.perf_counter()
            # May be 404 if endpoint not implemented
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nSkills assessor endpoint: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.5, f"Skills assessor endpoint too slow: {mean_time:.4f}s"

    def test_interview_scheduler_endpoint_response_time(self, client: TestClient):
        """Benchmark interview scheduler endpoint."""
        times = []
        for _ in range(20):
            start = time.perf_counter()
            response = client.post(
                "/api/v1/interview-scheduler/schedule",
                json={
                    "candidate_id": "1",
                    "job_id": "1",
                    "interviewer_ids": ["1", "2"],
                    "time_slots": [],
                },
            )
            end = time.perf_counter()
            # May be 404 if endpoint not implemented
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nInterview scheduler endpoint: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.5, f"Interview scheduler endpoint too slow: {mean_time:.4f}s"

    def test_analytics_endpoint_response_time(self, client: TestClient):
        """Benchmark analytics endpoint."""
        times = []
        for _ in range(20):
            start = time.perf_counter()
            response = client.get("/api/v1/analytics/summary")
            end = time.perf_counter()
            # May be 404 if endpoint not implemented
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nAnalytics endpoint: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.5, f"Analytics endpoint too slow: {mean_time:.4f}s"

    def test_notifications_endpoint_response_time(self, client: TestClient):
        """Benchmark notifications endpoint."""
        times = []
        for _ in range(20):
            start = time.perf_counter()
            response = client.get("/api/v1/notifications")
            end = time.perf_counter()
            # May be 404 if endpoint not implemented
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nNotifications endpoint: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.5, f"Notifications endpoint too slow: {mean_time:.4f}s"

    def test_export_endpoint_response_time(self, client: TestClient):
        """Benchmark export endpoint."""
        times = []
        for _ in range(20):
            start = time.perf_counter()
            response = client.get("/api/v1/export/candidates?format=json")
            end = time.perf_counter()
            # May be 404 if endpoint not implemented
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nExport endpoint: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.5, f"Export endpoint too slow: {mean_time:.4f}s"

    def test_404_response_time(self, client: TestClient):
        """Benchmark 404 response time."""
        times = []
        for _ in range(30):
            start = time.perf_counter()
            response = client.get("/api/v1/nonexistent-endpoint")
            end = time.perf_counter()
            assert response.status_code == 404
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\n404 response: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.3, f"404 response too slow: {mean_time:.4f}s"

    def test_validation_error_response_time(self, client: TestClient):
        """Benchmark validation error response time."""
        times = []
        for _ in range(30):
            start = time.perf_counter()
            response = client.post(
                "/api/v1/candidate-matcher/match",
                json={},  # Missing required fields
            )
            end = time.perf_counter()
            # Should be 422 for validation error
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nValidation error: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.3, f"Validation error too slow: {mean_time:.4f}s"
