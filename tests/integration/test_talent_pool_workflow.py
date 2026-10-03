"""Integration tests for talent pool workflow."""

import pytest
from recruitment_platform import RecruitmentPlatform


@pytest.fixture
def platform():
    """Create a fresh platform instance for each test."""
    return RecruitmentPlatform()


@pytest.fixture
def talent_pool(platform):
    """Create a talent pool and yield it, cleaning up after the test."""
    pool = platform.create_talent_pool(name="Engineering Talent")
    yield pool
    # Cleanup: delete the pool if it still exists
    try:
        platform.delete_talent_pool(pool.id)
    except Exception:
        pass


@pytest.fixture
def candidate(platform):
    """Create a candidate and yield it, cleaning up after the test."""
    cand = platform.create_candidate(
        name="Jane Doe",
        email="jane.doe@example.com",
        skills=["Python", "AWS"],
    )
    yield cand
    try:
        platform.delete_candidate(cand.id)
    except Exception:
        pass


@pytest.fixture
def candidate_b(platform):
    """Create a second candidate for search tests."""
    cand = platform.create_candidate(
        name="John Smith",
        email="john.smith@example.com",
        skills=["Java", "Kubernetes"],
    )
    yield cand
    try:
        platform.delete_candidate(cand.id)
    except Exception:
        pass


class TestTalentPoolLifecycle:
    """Test the full lifecycle of a talent pool."""

    def test_full_talent_pool_lifecycle(self, platform, talent_pool, candidate):
        """Create pool → add candidate → remove candidate → delete."""
        # Pool was created by fixture
        assert talent_pool.id is not None
        assert talent_pool.name == "Engineering Talent"

        # Add candidate to pool
        platform.add_candidate_to_pool(talent_pool.id, candidate.id)
        members = platform.get_pool_members(talent_pool.id)
        assert len(members) == 1
        assert members[0].id == candidate.id

        # Remove candidate from pool
        platform.remove_candidate_from_pool(talent_pool.id, candidate.id)
        members = platform.get_pool_members(talent_pool.id)
        assert len(members) == 0

        # Delete the pool
        platform.delete_talent_pool(talent_pool.id)
        with pytest.raises(Exception):
            platform.get_talent_pool(talent_pool.id)


class TestTalentPoolSearch:
    """Test talent pool search functionality."""

    def test_talent_pool_search(self, platform, talent_pool, candidate, candidate_b):
        """Create pool → add candidates → search."""
        # Add both candidates to the pool
        platform.add_candidate_to_pool(talent_pool.id, candidate.id)
        platform.add_candidate_to_pool(talent_pool.id, candidate_b.id)

        # Search by name
        results = platform.search_talent_pool(talent_pool.id, query="Jane")
        assert len(results) == 1
        assert results[0].name == "Jane Doe"

        # Search by skill
        results = platform.search_talent_pool(talent_pool.id, query="Java")
        assert len(results) == 1
        assert results[0].name == "John Smith"

        # Search with no matches
        results = platform.search_talent_pool(talent_pool.id, query="NonExistent")
        assert len(results) == 0


class TestTalentPoolAnalytics:
    """Test talent pool analytics."""

    def test_talent_pool_analytics(self, platform, talent_pool, candidate, candidate_b):
        """Create pool → get analytics."""
        # Add candidates to the pool
        platform.add_candidate_to_pool(talent_pool.id, candidate.id)
        platform.add_candidate_to_pool(talent_pool.id, candidate_b.id)

        # Get analytics
        analytics = platform.get_talent_pool_analytics(talent_pool.id)
        assert analytics is not None
        assert analytics.total_candidates == 2
        assert "Python" in analytics.top_skills
        assert "Java" in analytics.top_skills
