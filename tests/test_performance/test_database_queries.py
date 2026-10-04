"""Database query performance benchmarks for recruitment-platform."""
import time
import statistics

import pytest
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import Session

from recruitment_platform.models.candidate import Candidate
from recruitment_platform.models.job import Job
from recruitment_platform.models.application import Application
from recruitment_platform.models.interview import Interview
from recruitment_platform.models.assessment import Assessment


class TestDatabaseQueryPerformance:
    """Benchmark database query performance."""

    def test_insert_single_candidate(self, populated_bench_db: Session):
        """Benchmark inserting a single candidate."""
        times = []
        for i in range(50):
            start = time.perf_counter()
            candidate = Candidate(
                name=f"Bench Candidate {i}",
                email=f"bench{i}@test.com",
                phone=f"+1-555-{i:04d}",
                skills="Python,FastAPI,SQL",
                experience="5 years",
                education="Bachelor's",
            )
            populated_bench_db.add(candidate)
            populated_bench_db.commit()
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nInsert single candidate: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"Insert too slow: {mean_time:.4f}s"

    def test_bulk_insert_candidates(self, bench_db_session: Session):
        """Benchmark bulk inserting candidates."""
        times = []
        for batch_size in [10, 50, 100]:
            candidates = [
                Candidate(
                    name=f"Bulk {batch_size} Candidate {i}",
                    email=f"bulk{batch_size}_{i}@test.com",
                    phone=f"+1-555-{i:04d}",
                    skills="Python,FastAPI,SQL",
                    experience="5 years",
                    education="Bachelor's",
                )
                for i in range(batch_size)
            ]
            start = time.perf_counter()
            bench_db_session.add_all(candidates)
            bench_db_session.commit()
            end = time.perf_counter()
            times.append(end - start)
            print(f"Bulk insert {batch_size} candidates: {times[-1]:.4f}s")

        # Bulk insert should be efficient
        assert times[2] < 1.0, f"Bulk insert of 100 too slow: {times[2]:.4f}s"

    def test_select_all_candidates(self, populated_bench_db: Session):
        """Benchmark selecting all candidates."""
        times = []
        for _ in range(30):
            start = time.perf_counter()
            result = populated_bench_db.execute(select(Candidate)).scalars().all()
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nSelect all candidates (100 rows): mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"Select all too slow: {mean_time:.4f}s"

    def test_select_candidates_with_filter(self, populated_bench_db: Session):
        """Benchmark filtered candidate query."""
        times = []
        for _ in range(30):
            start = time.perf_counter()
            result = populated_bench_db.execute(
                select(Candidate).where(
                    and_(
                        Candidate.name.like("%Candidate 5%"),
                        Candidate.email.like("%test.com"),
                    )
                )
            ).scalars().all()
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nSelect candidates (filtered): mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"Filtered select too slow: {mean_time:.4f}s"

    def test_select_with_pagination(self, populated_bench_db: Session):
        """Benchmark paginated query."""
        times = []
        for page in range(1, 11):
            start = time.perf_counter()
            result = populated_bench_db.execute(
                select(Candidate).offset((page - 1) * 10).limit(10)
            ).scalars().all()
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nPaginated select (10 pages): mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.05, f"Paginated select too slow: {mean_time:.4f}s"

    def test_select_with_join(self, populated_bench_db: Session):
        """Benchmark query with join."""
        times = []
        for _ in range(30):
            start = time.perf_counter()
            result = populated_bench_db.execute(
                select(Candidate, Application)
                .join(Application, Candidate.id == Application.candidate_id)
            ).all()
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nSelect with join: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.2, f"Join query too slow: {mean_time:.4f}s"

    def test_select_with_aggregation(self, populated_bench_db: Session):
        """Benchmark aggregation query."""
        times = []
        for _ in range(30):
            start = time.perf_counter()
            result = populated_bench_db.execute(
                select(
                    Application.status,
                    func.count(Application.id).label("count"),
                ).group_by(Application.status)
            ).all()
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nAggregation query: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"Aggregation too slow: {mean_time:.4f}s"

    def test_select_with_order_by(self, populated_bench_db: Session):
        """Benchmark ordered query."""
        times = []
        for _ in range(30):
            start = time.perf_counter()
            result = populated_bench_db.execute(
                select(Candidate).order_by(Candidate.name).limit(50)
            ).scalars().all()
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nOrdered select: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"Ordered select too slow: {mean_time:.4f}s"

    def test_update_single_candidate(self, populated_bench_db: Session):
        """Benchmark updating a single candidate."""
        # Get a candidate to update
        candidate = populated_bench_db.execute(
            select(Candidate).limit(1)
        ).scalars().first()

        times = []
        for i in range(30):
            start = time.perf_counter()
            candidate.name = f"Updated {i}"
            populated_bench_db.commit()
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nUpdate single candidate: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"Update too slow: {mean_time:.4f}s"

    def test_delete_single_candidate(self, populated_bench_db: Session):
        """Benchmark deleting a single candidate."""
        times = []
        for i in range(30):
            # Create a candidate to delete
            candidate = Candidate(
                name=f"To Delete {i}",
                email=f"todelete{i}@test.com",
                skills="Python",
                experience="1 year",
                education="Bachelor's",
            )
            populated_bench_db.add(candidate)
            populated_bench_db.commit()

            start = time.perf_counter()
            populated_bench_db.delete(candidate)
            populated_bench_db.commit()
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nDelete single candidate: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"Delete too slow: {mean_time:.4f}s"

    def test_complex_query_multiple_joins(self, populated_bench_db: Session):
        """Benchmark complex query with multiple joins."""
        times = []
        for _ in range(30):
            start = time.perf_counter()
            result = populated_bench_db.execute(
                select(Candidate, Job, Application)
                .join(Application, Candidate.id == Application.candidate_id)
                .join(Job, Application.job_id == Job.id)
                .where(
                    or_(
                        Application.status == "pending",
                        Application.status == "reviewing",
                    )
                )
                .order_by(Candidate.name)
                .limit(20)
            ).all()
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nComplex multi-join query: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.3, f"Complex query too slow: {mean_time:.4f}s"

    def test_count_query(self, populated_bench_db: Session):
        """Benchmark count query."""
        times = []
        for _ in range(30):
            start = time.perf_counter()
            result = populated_bench_db.execute(
                select(func.count(Candidate.id))
            ).scalar()
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nCount query: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.05, f"Count query too slow: {mean_time:.4f}s"

    def test_select_with_subquery(self, populated_bench_db: Session):
        """Benchmark query with subquery."""
        times = []
        for _ in range(30):
            start = time.perf_counter()
            subq = (
                select(Application.candidate_id)
                .group_by(Application.candidate_id)
                .having(func.count(Application.id) > 1)
                .subquery()
            )
            result = populated_bench_db.execute(
                select(Candidate).where(Candidate.id.in_(select(subq.c.candidate_id)))
            ).scalars().all()
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nSubquery: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.2, f"Subquery too slow: {mean_time:.4f}s"

    def test_insert_application(self, populated_bench_db: Session):
        """Benchmark inserting an application."""
        times = []
        for i in range(50):
            start = time.perf_counter()
            application = Application(
                candidate_id=(i % 100) + 1,
                job_id=(i % 50) + 1,
                status="pending",
            )
            populated_bench_db.add(application)
            populated_bench_db.commit()
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nInsert application: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"Insert application too slow: {mean_time:.4f}s"

    def test_select_applications_by_status(self, populated_bench_db: Session):
        """Benchmark querying applications by status."""
        times = []
        for status in ["pending", "reviewing", "interview", "offer", "hired"]:
            start = time.perf_counter()
            result = populated_bench_db.execute(
                select(Application).where(Application.status == status)
            ).scalars().all()
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nSelect applications by status: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.1, f"Select by status too slow: {mean_time:.4f}s"

    def test_eager_load_relationships(self, populated_bench_db: Session):
        """Benchmark eager loading of relationships."""
        from sqlalchemy.orm import selectinload

        times = []
        for _ in range(30):
            start = time.perf_counter()
            result = populated_bench_db.execute(
                select(Candidate)
                .options(selectinload(Candidate.applications))
                .limit(20)
            ).scalars().all()
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        print(f"\nEager load relationships: mean={mean_time:.4f}s, p95={p95_time:.4f}s")
        assert mean_time < 0.2, f"Eager load too slow: {mean_time:.4f}s"
