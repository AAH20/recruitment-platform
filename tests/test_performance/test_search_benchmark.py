"""Benchmark: API health endpoint response time (Read operation)."""
import time

from fastapi.testclient import TestClient

from recruitment_platform.main import app


def test_api_health_response_time():
    """Measure response time for GET /api/health (Read operation)."""
    client = TestClient(app)
    times = []
    for _ in range(50):
        start = time.perf_counter()
        resp = client.get("/api/health")
        elapsed = time.perf_counter() - start
        assert resp.status_code == 200
        times.append(elapsed)
    avg = sum(times) / len(times)
    p95 = sorted(times)[int(len(times) * 0.95)]
    print(f"\n[api-health:read] avg={avg*1000:.2f}ms p95={p95*1000:.2f}ms min={min(times)*1000:.2f}ms max={max(times)*1000:.2f}ms")
