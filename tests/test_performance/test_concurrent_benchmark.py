"""Benchmark: Concurrent request handling."""
import time
from concurrent.futures import ThreadPoolExecutor

from fastapi.testclient import TestClient

from recruitment_platform.main import app


def test_concurrent_requests():
    """Measure response time under concurrent load."""
    client = TestClient(app)
    num_threads = 10
    requests_per_thread = 10

    def make_requests():
        times = []
        for _ in range(requests_per_thread):
            start = time.perf_counter()
            resp = client.get("/health")
            elapsed = time.perf_counter() - start
            assert resp.status_code == 200
            times.append(elapsed)
        return times

    start_all = time.perf_counter()
    with ThreadPoolExecutor(max_workers=num_threads) as pool:
        results = list(pool.map(lambda _: make_requests(), range(num_threads)))
    total_elapsed = time.perf_counter() - start_all

    all_times = [t for sublist in results for t in sublist]
    total_requests = num_threads * requests_per_thread
    avg = sum(all_times) / len(all_times)
    p95 = sorted(all_times)[int(len(all_times) * 0.95)]
    throughput = total_requests / total_elapsed

    print(
        f"\n[concurrent] threads={num_threads} reqs/thread={requests_per_thread} "
        f"total={total_requests} wall={total_elapsed*1000:.2f}ms "
        f"avg={avg*1000:.2f}ms p95={p95*1000:.2f}ms throughput={throughput:.1f}req/s"
    )
