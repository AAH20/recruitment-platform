"""Concurrent request handling benchmarks for recruitment-platform."""
import time
import statistics
import concurrent.futures
import threading
from typing import Any

import pytest
from fastapi.testclient import TestClient

from recruitment_platform.main import app


class TestConcurrentRequests:
    """Benchmark concurrent request handling."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        with TestClient(app) as c:
            yield c

    def test_concurrent_health_checks(self, client: TestClient):
        """Benchmark concurrent health check requests."""
        num_requests = 50

        def make_request(_):
            start = time.perf_counter()
            response = client.get("/api/v1/health")
            end = time.perf_counter()
            assert response.status_code == 200
            return end - start

        start_total = time.perf_counter()
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            times = list(executor.map(make_request, range(num_requests)))
        total_time = time.perf_counter() - start_total

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nConcurrent health checks ({num_requests} req, 10 workers): "
              f"total={total_time:.4f}s, mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert total_time < 5.0, f"Concurrent health checks too slow: {total_time:.4f}s"

    def test_concurrent_mixed_reads(self, client: TestClient):
        """Benchmark concurrent mixed read operations."""
        num_requests = 50

        endpoints = [
            "/api/v1/health",
            "/api/v1/ready",
            "/api/v1/search/jobs?q=engineer",
            "/api/v1/search/candidates?q=python",
            "/api/v1/search/skills?q=python",
            "/api/v1/search/autocomplete?q=eng&entity_type=job",
        ]

        def make_request(i):
            endpoint = endpoints[i % len(endpoints)]
            start = time.perf_counter()
            response = client.get(endpoint)
            end = time.perf_counter()
            assert response.status_code == 200
            return end - start

        start_total = time.perf_counter()
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            times = list(executor.map(make_request, range(num_requests)))
        total_time = time.perf_counter() - start_total

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nConcurrent mixed reads ({num_requests} req, 10 workers): "
              f"total={total_time:.4f}s, mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert total_time < 10.0, f"Concurrent mixed reads too slow: {total_time:.4f}s"

    def test_sequential_vs_concurrent(self, client: TestClient):
        """Compare sequential vs concurrent request handling."""
        num_requests = 30

        # Sequential
        seq_times = []
        for i in range(num_requests):
            start = time.perf_counter()
            response = client.get("/api/v1/health")
            end = time.perf_counter()
            assert response.status_code == 200
            seq_times.append(end - start)

        seq_total = sum(seq_times)

        # Concurrent
        def make_request(_):
            start = time.perf_counter()
            response = client.get("/api/v1/health")
            end = time.perf_counter()
            assert response.status_code == 200
            return end - start

        start_total = time.perf_counter()
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            conc_times = list(executor.map(make_request, range(num_requests)))
        conc_total = time.perf_counter() - start_total

        speedup = seq_total / conc_total if conc_total > 0 else 0
        print(f"\nSequential: {seq_total:.4f}s, Concurrent: {conc_total:.4f}s, "
              f"Speedup: {speedup:.2f}x")
        # Concurrent should be faster
        assert conc_total < seq_total, "Concurrent should be faster than sequential"

    def test_concurrent_with_high_contention(self, client: TestClient):
        """Benchmark concurrent requests with high contention."""
        num_requests = 100

        def make_request(i):
            start = time.perf_counter()
            if i % 3 == 0:
                response = client.get("/api/v1/health")
            elif i % 3 == 1:
                response = client.get("/api/v1/ready")
            else:
                response = client.get("/api/v1/search/jobs?q=test")
            end = time.perf_counter()
            assert response.status_code == 200
            return end - start

        start_total = time.perf_counter()
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            times = list(executor.map(make_request, range(num_requests)))
        total_time = time.perf_counter() - start_total

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nHigh contention ({num_requests} req, 20 workers): "
              f"total={total_time:.4f}s, mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert total_time < 15.0, f"High contention too slow: {total_time:.4f}s"

    def test_concurrent_writes_with_reads(self, client: TestClient):
        """Benchmark concurrent writes mixed with reads."""
        num_writes = 15
        num_reads = 30

        def make_write(i):
            start = time.perf_counter()
            response = client.post(
                "/api/v1/candidate-matcher/match",
                json={
                    "candidates": [{"id": str(i), "skills": ["Python"]}],
                    "job_requirements": {"skills": ["Python"]},
                },
            )
            end = time.perf_counter()
            assert response.status_code == 200
            return end - start

        def make_read(_):
            start = time.perf_counter()
            response = client.get("/api/v1/health")
            end = time.perf_counter()
            assert response.status_code == 200
            return end - start

        start_total = time.perf_counter()
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            write_futures = [executor.submit(make_write, i) for i in range(num_writes)]
            read_futures = [executor.submit(make_read, i) for i in range(num_reads)]

            write_times = [f.result() for f in write_futures]
            read_times = [f.result() for f in read_futures]

        total_time = time.perf_counter() - start_total

        print(f"\nConcurrent writes+reads ({num_writes} writes, {num_reads} reads, 10 workers): "
              f"total={total_time:.4f}s")
        print(f"  Write mean: {statistics.mean(write_times):.4f}s")
        print(f"  Read mean: {statistics.mean(read_times):.4f}s")
        assert total_time < 15.0, f"Concurrent writes+reads too slow: {total_time:.4f}s"

    def test_stress_test_health_endpoint(self, client: TestClient):
        """Stress test the health endpoint."""
        num_requests = 200

        def make_request(_):
            response = client.get("/api/v1/health")
            assert response.status_code == 200

        start_total = time.perf_counter()
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            list(executor.map(make_request, range(num_requests)))
        total_time = time.perf_counter() - start_total

        rps = num_requests / total_time if total_time > 0 else 0
        print(f"\nStress test health ({num_requests} req, 20 workers): "
              f"total={total_time:.4f}s, RPS={rps:.1f}")
        assert total_time < 30.0, f"Stress test too slow: {total_time:.4f}s"

    def test_stress_test_mixed_endpoints(self, client: TestClient):
        """Stress test with mixed endpoint access patterns."""
        num_requests = 150

        def make_request(i):
            if i % 5 == 0:
                response = client.post(
                    "/api/v1/candidate-matcher/match",
                    json={
                        "candidates": [{"id": str(i), "skills": ["Python"]}],
                        "job_requirements": {"skills": ["Python"]},
                    },
                )
                assert response.status_code == 200
            elif i % 5 == 1:
                response = client.get("/api/v1/search/jobs?q=test")
                assert response.status_code == 200
            elif i % 5 == 2:
                response = client.get("/api/v1/search/candidates?q=test")
                assert response.status_code == 200
            elif i % 5 == 3:
                response = client.get("/api/v1/search/skills?q=test")
                assert response.status_code == 200
            else:
                response = client.get("/api/v1/health")
                assert response.status_code == 200

        start_total = time.perf_counter()
        with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
            list(executor.map(make_request, range(num_requests)))
        total_time = time.perf_counter() - start_total

        rps = num_requests / total_time if total_time > 0 else 0
        print(f"\nStress test mixed ({num_requests} req, 15 workers): "
              f"total={total_time:.4f}s, RPS={rps:.1f}")
        assert total_time < 30.0, f"Mixed stress test too slow: {total_time:.4f}s"

    def test_concurrent_search_operations(self, client: TestClient):
        """Benchmark concurrent search operations."""
        num_requests = 50

        def make_request(i):
            start = time.perf_counter()
            response = client.get(f"/api/v1/search/jobs?q=query{i}&limit=20")
            end = time.perf_counter()
            assert response.status_code == 200
            return end - start

        start_total = time.perf_counter()
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            times = list(executor.map(make_request, range(num_requests)))
        total_time = time.perf_counter() - start_total

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nConcurrent search ({num_requests} req, 10 workers): "
              f"total={total_time:.4f}s, mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert total_time < 10.0, f"Concurrent search too slow: {total_time:.4f}s"

    def test_concurrent_autocomplete_requests(self, client: TestClient):
        """Benchmark concurrent autocomplete requests."""
        num_requests = 50

        def make_request(i):
            start = time.perf_counter()
            response = client.get(f"/api/v1/search/autocomplete?q=query{i}&entity_type=job")
            end = time.perf_counter()
            assert response.status_code == 200
            return end - start

        start_total = time.perf_counter()
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            times = list(executor.map(make_request, range(num_requests)))
        total_time = time.perf_counter() - start_total

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nConcurrent autocomplete ({num_requests} req, 10 workers): "
              f"total={total_time:.4f}s, mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert total_time < 10.0, f"Concurrent autocomplete too slow: {total_time:.4f}s"
