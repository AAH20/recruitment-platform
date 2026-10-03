"""
Comprehensive agent tests for TalentPoolManager.

Tests cover:
- create_talent_pool: pool creation with valid/invalid inputs
- add_to_pool: adding candidates to pools with validation
- search_pool: searching pools with various filters
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch, AsyncMock
from uuid import uuid4, UUID

from src.recruitment_platform.agents.talent_pool_manager import (
    TalentPoolManager,
    TalentPool,
    PoolCandidate,
    SearchCriteria,
    PoolStatus,
    CandidateStatus,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_db():
    """Mock database session/connection."""
    db = MagicMock()
    db.execute = AsyncMock()
    db.commit = AsyncMock()
    db.rollback = AsyncMock()
    db.refresh = AsyncMock()
    return db


@pytest.fixture
def mock_redis():
    """Mock Redis client for caching."""
    redis = MagicMock()
    redis.get = AsyncMock(return_value=None)
    redis.set = AsyncMock()
    redis.delete = AsyncMock()
    redis.exists = AsyncMock(return_value=False)
    return redis


@pytest.fixture
def talent_pool_manager(mock_db, mock_redis):
    """Create a TalentPoolManager instance with mocked dependencies."""
    return TalentPoolManager(db=mock_db, redis=mock_redis)


@pytest.fixture
def sample_pool_data():
    """Sample data for creating a talent pool."""
    return {
        "name": "Senior Python Engineers",
        "description": "Pool of senior Python engineers for Q4 hiring",
        "status": PoolStatus.ACTIVE,
        "tags": ["python", "senior", "backend"],
        "created_by": "recruiter_001",
        "department": "Engineering",
        "min_experience_years": 5,
        "max_experience_years": 15,
        "skills": ["Python", "FastAPI", "PostgreSQL", "AWS"],
        "locations": ["Remote", "Berlin", "London"],
    }


@pytest.fixture
def sample_candidate_data():
    """Sample candidate data for pool operations."""
    return {
        "id": uuid4(),
        "full_name": "Alice Johnson",
        "email": "alice.johnson@example.com",
        "phone": "+1-555-0100",
        "skills": ["Python", "FastAPI", "AWS", "Docker"],
        "experience_years": 8,
        "current_title": "Senior Software Engineer",
        "current_company": "TechCorp",
        "location": "Berlin",
        "status": CandidateStatus.ACTIVE,
        "expected_salary_min": 90000,
        "expected_salary_max": 130000,
        "currency": "EUR",
        "linkedin_url": "https://linkedin.com/in/alicejohnson",
        "notes": "Strong backend experience, led team of 5.",
    }


@pytest.fixture
def sample_pool(sample_pool_data):
    """Create a sample TalentPool instance."""
    pool = TalentPool(**sample_pool_data)
    pool.id = uuid4()
    pool.created_at = datetime.utcnow()
    pool.updated_at = datetime.utcnow()
    pool.candidate_count = 0
    return pool


@pytest.fixture
def sample_pool_candidate(sample_candidate_data, sample_pool):
    """Create a sample PoolCandidate instance."""
    candidate = PoolCandidate(**sample_candidate_data)
    candidate.id = uuid4()
    candidate.pool_id = sample_pool.id
    candidate.added_at = datetime.utcnow()
    candidate.added_by = "recruiter_001"
    return candidate


@pytest.fixture
def multiple_candidates():
    """Generate multiple candidates for search tests."""
    candidates = []
    skills_pool = [
        ["Python", "Django", "PostgreSQL"],
        ["Python", "FastAPI", "MongoDB"],
        ["JavaScript", "React", "Node.js"],
        ["Python", "Flask", "Redis"],
        ["Go", "Kubernetes", "AWS"],
        ["Python", "Machine Learning", "TensorFlow"],
    ]
    locations = ["Berlin", "London", "Remote", "Munich", "Remote", "Hamburg"]
    experience = [3, 7, 5, 4, 10, 6]

    for i, (skills, location, exp) in enumerate(
        zip(skills_pool, locations, experience)
    ):
        candidates.append(
            {
                "id": uuid4(),
                "full_name": f"Candidate {i+1}",
                "email": f"candidate{i+1}@example.com",
                "skills": skills,
                "experience_years": exp,
                "location": location,
                "status": CandidateStatus.ACTIVE,
                "current_title": f"Engineer {i+1}",
            }
        )
    return candidates


# ---------------------------------------------------------------------------
# Test: create_talent_pool
# ---------------------------------------------------------------------------


class TestCreateTalentPool:
    """Tests for TalentPoolManager.create_talent_pool."""

    @pytest.mark.asyncio
    async def test_create_talent_pool_success(
        self, talent_pool_manager, mock_db, sample_pool_data
    ):
        """Successfully create a talent pool with valid data."""
        mock_db.execute.return_value = MagicMock(
            fetchone=MagicMock(
                return_value=(
                    uuid4(),
                    sample_pool_data["name"],
                    sample_pool_data["description"],
                    sample_pool_data["status"],
                    sample_pool_data["tags"],
                    sample_pool_data["created_by"],
                    sample_pool_data["department"],
                    sample_pool_data["min_experience_years"],
                    sample_pool_data["max_experience_years"],
                    sample_pool_data["skills"],
                    sample_pool_data["locations"],
                    datetime.utcnow(),
                    datetime.utcnow(),
                    0,
                )
            )
        )

        result = await talent_pool_manager.create_talent_pool(**sample_pool_data)

        assert result is not None
        assert result.name == sample_pool_data["name"]
        assert result.description == sample_pool_data["description"]
        assert result.status == PoolStatus.ACTIVE
        assert result.tags == sample_pool_data["tags"]
        assert result.created_by == sample_pool_data["created_by"]
        assert result.department == sample_pool_data["department"]
        assert result.min_experience_years == sample_pool_data["min_experience_years"]
        assert result.max_experience_years == sample_pool_data["max_experience_years"]
        assert result.skills == sample_pool_data["skills"]
        assert result.locations == sample_pool_data["locations"]
        assert result.candidate_count == 0
        assert isinstance(result.id, UUID)
        assert isinstance(result.created_at, datetime)
        assert isinstance(result.updated_at, datetime)
        mock_db.execute.assert_called_once()
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_talent_pool_minimal_data(self, talent_pool_manager, mock_db):
        """Create a pool with only required fields."""
        minimal_data = {
            "name": "Minimal Pool",
            "created_by": "recruiter_002",
        }
        mock_db.execute.return_value = MagicMock(
            fetchone=MagicMock(
                return_value=(
                    uuid4(),
                    "Minimal Pool",
                    None,
                    PoolStatus.ACTIVE,
                    [],
                    "recruiter_002",
                    None,
                    None,
                    None,
                    [],
                    [],
                    datetime.utcnow(),
                    datetime.utcnow(),
                    0,
                )
            )
        )

        result = await talent_pool_manager.create_talent_pool(**minimal_data)

        assert result is not None
        assert result.name == "Minimal Pool"
        assert result.created_by == "recruiter_002"
        assert result.status == PoolStatus.ACTIVE
        assert result.tags == []
        assert result.skills == []
        assert result.locations == []
        assert result.candidate_count == 0

    @pytest.mark.asyncio
    async def test_create_talent_pool_with_all_fields(
        self, talent_pool_manager, mock_db, sample_pool_data
    ):
        """Create a pool with every field populated."""
        sample_pool_data["status"] = PoolStatus.DRAFT
        sample_pool_data["tags"] = ["python", "senior", "urgent", "q4-hiring"]
        sample_pool_data["skills"] = [
            "Python",
            "FastAPI",
            "PostgreSQL",
            "AWS",
            "Docker",
            "Kubernetes",
        ]
        sample_pool_data["locations"] = ["Remote", "Berlin", "London", "Munich"]

        mock_db.execute.return_value = MagicMock(
            fetchone=MagicMock(
                return_value=(
                    uuid4(),
                    sample_pool_data["name"],
                    sample_pool_data["description"],
                    sample_pool_data["status"],
                    sample_pool_data["tags"],
                    sample_pool_data["created_by"],
                    sample_pool_data["department"],
                    sample_pool_data["min_experience_years"],
                    sample_pool_data["max_experience_years"],
                    sample_pool_data["skills"],
                    sample_pool_data["locations"],
                    datetime.utcnow(),
                    datetime.utcnow(),
                    0,
                )
            )
        )

        result = await talent_pool_manager.create_talent_pool(**sample_pool_data)

        assert result.status == PoolStatus.DRAFT
        assert len(result.tags) == 4
        assert len(result.skills) == 6
        assert len(result.locations) == 4

    @pytest.mark.asyncio
    async def test_create_talent_pool_empty_name_raises_error(
        self, talent_pool_manager, mock_db
    ):
        """Creating a pool with an empty name should raise ValueError."""
        with pytest.raises(ValueError, match="name cannot be empty"):
            await talent_pool_manager.create_talent_pool(
                name="", created_by="recruiter_001"
            )

    @pytest.mark.asyncio
    async def test_create_talent_pool_none_name_raises_error(
        self, talent_pool_manager, mock_db
    ):
        """Creating a pool with None name should raise ValueError."""
        with pytest.raises(ValueError, match="name cannot be empty"):
            await talent_pool_manager.create_talent_pool(
                name=None, created_by="recruiter_001"
            )

    @pytest.mark.asyncio
    async def test_create_talent_pool_missing_created_by_raises_error(
        self, talent_pool_manager, mock_db
    ):
        """Creating a pool without created_by should raise ValueError."""
        with pytest.raises(ValueError, match="created_by is required"):
            await talent_pool_manager.create_talent_pool(name="Test Pool")

    @pytest.mark.asyncio
    async def test_create_talent_pool_invalid_experience_range(
        self, talent_pool_manager, mock_db
    ):
        """min_experience > max_experience should raise ValueError."""
        with pytest.raises(ValueError, match="min_experience_years cannot be greater than max_experience_years"):
            await talent_pool_manager.create_talent_pool(
                name="Test Pool",
                created_by="recruiter_001",
                min_experience_years=10,
                max_experience_years=5,
            )

    @pytest.mark.asyncio
    async def test_create_talent_pool_negative_experience_raises_error(
        self, talent_pool_manager, mock_db
    ):
        """Negative experience years should raise ValueError."""
        with pytest.raises(ValueError, match="experience years cannot be negative"):
            await talent_pool_manager.create_talent_pool(
                name="Test Pool",
                created_by="recruiter_001",
                min_experience_years=-1,
            )

    @pytest.mark.asyncio
    async def test_create_talent_pool_db_error_rolls_back(
        self, talent_pool_manager, mock_db, sample_pool_data
    ):
        """Database error should trigger rollback and re-raise."""
        mock_db.execute.side_effect = Exception("Database connection lost")

        with pytest.raises(Exception, match="Database connection lost"):
            await talent_pool_manager.create_talent_pool(**sample_pool_data)

        mock_db.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_talent_pool_duplicate_name(
        self, talent_pool_manager, mock_db, sample_pool_data
    ):
        """Creating a pool with a duplicate name should raise an error."""
        mock_db.execute.side_effect = Exception(
            'duplicate key value violates unique constraint "talent_pools_name_key"'
        )

        with pytest.raises(Exception, match="duplicate key"):
            await talent_pool_manager.create_talent_pool(**sample_pool_data)

        mock_db.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_talent_pool_caches_result(
        self, talent_pool_manager, mock_db, mock_redis, sample_pool_data
    ):
        """After creation, the pool should be cached in Redis."""
        pool_id = uuid4()
        mock_db.execute.return_value = MagicMock(
            fetchone=MagicMock(
                return_value=(
                    pool_id,
                    sample_pool_data["name"],
                    sample_pool_data["description"],
                    sample_pool_data["status"],
                    sample_pool_data["tags"],
                    sample_pool_data["created_by"],
                    sample_pool_data["department"],
                    sample_pool_data["min_experience_years"],
                    sample_pool_data["max_experience_years"],
                    sample_pool_data["skills"],
                    sample_pool_data["locations"],
                    datetime.utcnow(),
                    datetime.utcnow(),
                    0,
                )
            )
        )

        result = await talent_pool_manager.create_talent_pool(**sample_pool_data)

        mock_redis.set.assert_called_once()
        call_args = mock_redis.set.call_args
        assert str(pool_id) in str(call_args)

    @pytest.mark.asyncio
    async def test_create_talent_pool_with_special_characters_in_name(
        self, talent_pool_manager, mock_db
    ):
        """Pool names with special characters should be handled correctly."""
        special_name = "Engineers (Backend) – Q4 2024 – €100k+"
        mock_db.execute.return_value = MagicMock(
            fetchone=MagicMock(
                return_value=(
                    uuid4(),
                    special_name,
                    None,
                    PoolStatus.ACTIVE,
                    [],
                    "recruiter_001",
                    None,
                    None,
                    None,
                    [],
                    [],
                    datetime.utcnow(),
                    datetime.utcnow(),
                    0,
                )
            )
        )

        result = await talent_pool_manager.create_talent_pool(
            name=special_name, created_by="recruiter_001"
        )

        assert result.name == special_name

    @pytest.mark.asyncio
    async def test_create_talent_pool_with_long_description(
        self, talent_pool_manager, mock_db
    ):
        """Pool with a very long description should be created successfully."""
        long_description = "A" * 5000
        mock_db.execute.return_value = MagicMock(
            fetchone=MagicMock(
                return_value=(
                    uuid4(),
                    "Long Desc Pool",
                    long_description,
                    PoolStatus.ACTIVE,
                    [],
                    "recruiter_001",
                    None,
                    None,
                    None,
                    [],
                    [],
                    datetime.utcnow(),
                    datetime.utcnow(),
                    0,
                )
            )
        )

        result = await talent_pool_manager.create_talent_pool(
            name="Long Desc Pool",
            description=long_description,
            created_by="recruiter_001",
        )

        assert result.description == long_description
        assert len(result.description) == 5000


# ---------------------------------------------------------------------------
# Test: add_to_pool
# ---------------------------------------------------------------------------


class TestAddToPool:
    """Tests for TalentPoolManager.add_to_pool."""

    @pytest.mark.asyncio
    async def test_add_to_pool_success(
        self,
        talent_pool_manager,
        mock_db,
        sample_pool,
        sample_candidate_data,
    ):
        """Successfully add a candidate to a pool."""
        mock_db.execute.return_value = MagicMock(
            fetchone=MagicMock(
                return_value=(
                    sample_candidate_data["id"],
                    sample_pool.id,
                    sample_candidate_data["full_name"],
                    sample_candidate_data["email"],
                    sample_candidate_data["skills"],
                    sample_candidate_data["experience_years"],
                    sample_candidate_data["location"],
                    CandidateStatus.ACTIVE,
                    datetime.utcnow(),
                    "recruiter_001",
                )
            )
        )

        result = await talent_pool_manager.add_to_pool(
            pool_id=sample_pool.id,
            candidate_id=sample_candidate_data["id"],
            added_by="recruiter_001",
        )

        assert result is not None
        assert result.candidate_id == sample_candidate_data["id"]
        assert result.pool_id == sample_pool.id
        assert result.status == CandidateStatus.ACTIVE
        assert result.added_by == "recruiter_001"
        assert isinstance(result.added_at, datetime)
        mock_db.execute.assert_called_once()
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_to_pool_with_notes(
        self,
        talent_pool_manager,
        mock_db,
        sample_pool,
        sample_candidate_data,
    ):
        """Add a candidate with notes."""
        notes = "Referred by Jane Doe. Strong cultural fit."
        mock_db.execute.return_value = MagicMock(
            fetchone=MagicMock(
                return_value=(
                    sample_candidate_data["id"],
                    sample_pool.id,
                    sample_candidate_data["full_name"],
                    sample_candidate_data["email"],
                    sample_candidate_data["skills"],
                    sample_candidate_data["experience_years"],
                    sample_candidate_data["location"],
                    CandidateStatus.ACTIVE,
                    datetime.utcnow(),
                    "recruiter_001",
                )
            )
        )

        result = await talent_pool_manager.add_to_pool(
            pool_id=sample_pool.id,
            candidate_id=sample_candidate_data["id"],
            added_by="recruiter_001",
            notes=notes,
        )

        assert result is not None
        assert result.candidate_id == sample_candidate_data["id"]
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_to_pool_increments_candidate_count(
        self,
        talent_pool_manager,
        mock_db,
        sample_pool,
        sample_candidate_data,
    ):
        """Adding a candidate should increment the pool's candidate_count."""
        mock_db.execute.return_value = MagicMock(
            fetchone=MagicMock(
                return_value=(
                    sample_candidate_data["id"],
                    sample_pool.id,
                    sample_candidate_data["full_name"],
                    sample_candidate_data["email"],
                    sample_candidate_data["skills"],
                    sample_candidate_data["experience_years"],
                    sample_candidate_data["location"],
                    CandidateStatus.ACTIVE,
                    datetime.utcnow(),
                    "recruiter_001",
                )
            )
        )

        initial_count = sample_pool.candidate_count
        await talent_pool_manager.add_to_pool(
            pool_id=sample_pool.id,
            candidate_id=sample_candidate_data["id"],
            added_by="recruiter_001",
        )

        # Verify the UPDATE query was called to increment count
        execute_calls = mock_db.execute.call_args_list
        assert len(execute_calls) >= 2  # INSERT + UPDATE

    @pytest.mark.asyncio
    async def test_add_to_pool_nonexistent_pool_raises_error(
        self, talent_pool_manager, mock_db, sample_candidate_data
    ):
        """Adding to a non-existent pool should raise ValueError."""
        mock_db.execute.return_value = MagicMock(
            fetchone=MagicMock(return_value=None)
        )

        with pytest.raises(ValueError, match="Pool not found"):
            await talent_pool_manager.add_to_pool(
                pool_id=uuid4(),
                candidate_id=sample_candidate_data["id"],
                added_by="recruiter_001",
            )

    @pytest.mark.asyncio
    async def test_add_to_pool_nonexistent_candidate_raises_error(
        self, talent_pool_manager, mock_db, sample_pool
    ):
        """Adding a non-existent candidate should raise ValueError."""
        # First call returns the pool, second returns None for candidate check
        mock_db.execute.side_effect = [
            MagicMock(
                fetchone=MagicMock(
                    return_value=(sample_pool.id, sample_pool.name)
                )
            ),
            MagicMock(fetchone=MagicMock(return_value=None)),
        ]

        with pytest.raises(ValueError, match="Candidate not found"):
            await talent_pool_manager.add_to_pool(
                pool_id=sample_pool.id,
                candidate_id=uuid4(),
                added_by="recruiter_001",
            )

    @pytest.mark.asyncio
    async def test_add_to_pool_duplicate_raises_error(
        self,
        talent_pool_manager,
        mock_db,
        sample_pool,
        sample_candidate_data,
    ):
        """Adding a candidate already in the pool should raise ValueError."""
        mock_db.execute.side_effect = [
            MagicMock(
                fetchone=MagicMock(
                    return_value=(sample_pool.id, sample_pool.name)
                )
            ),
            MagicMock(
                fetchone=MagicMock(
                    return_value=(sample_candidate_data["id"],)
                )
            ),
        ]

        with pytest.raises(ValueError, match="Candidate already in pool"):
            await talent_pool_manager.add_to_pool(
                pool_id=sample_pool.id,
                candidate_id=sample_candidate_data["id"],
                added_by="recruiter_001",
            )

    @pytest.mark.asyncio
    async def test_add_to_pool_inactive_pool_raises_error(
        self,
        talent_pool_manager,
        mock_db,
        sample_pool,
        sample_candidate_data,
    ):
        """Adding to an inactive/archived pool should raise ValueError."""
        sample_pool.status = PoolStatus.ARCHIVED
        mock_db.execute.return_value = MagicMock(
            fetchone=MagicMock(
                return_value=(sample_pool.id, sample_pool.name, PoolStatus.ARCHIVED)
            )
        )

        with pytest.raises(ValueError, match="Cannot add to inactive pool"):
            await talent_pool_manager.add_to_pool(
                pool_id=sample_pool.id,
                candidate_id=sample_candidate_data["id"],
                added_by="recruiter_001",
            )

    @pytest.mark.asyncio
    async def test_add_to_pool_missing_pool_id_raises_error(
        self, talent_pool_manager, mock_db, sample_candidate_data
    ):
        """Missing pool_id should raise ValueError."""
        with pytest.raises(ValueError, match="pool_id is required"):
            await talent_pool_manager.add_to_pool(
                pool_id=None,
                candidate_id=sample_candidate_data["id"],
                added_by="recruiter_001",
            )

    @pytest.mark.asyncio
    async def test_add_to_pool_missing_candidate_id_raises_error(
        self, talent_pool_manager, mock_db, sample_pool
    ):
        """Missing candidate_id should raise ValueError."""
        with pytest.raises(ValueError, match="candidate_id is required"):
            await talent_pool_manager.add_to_pool(
                pool_id=sample_pool.id,
                candidate_id=None,
                added_by="recruiter_001",
            )

    @pytest.mark.asyncio
    async def test_add_to_pool_missing_added_by_raises_error(
        self, talent_pool_manager, mock_db, sample_pool, sample_candidate_data
    ):
        """Missing added_by should raise ValueError."""
        with pytest.raises(ValueError, match="added_by is required"):
            await talent_pool_manager.add_to_pool(
                pool_id=sample_pool.id,
                candidate_id=sample_candidate_data["id"],
                added_by=None,
            )

    @pytest.mark.asyncio
    async def test_add_to_pool_db_error_rolls_back(
        self,
        talent_pool_manager,
        mock_db,
        sample_pool,
        sample_candidate_data,
    ):
        """Database error during add should trigger rollback."""
        mock_db.execute.side_effect = [
            MagicMock(
                fetchone=MagicMock(
                    return_value=(sample_pool.id, sample_pool.name)
                )
            ),
            MagicMock(fetchone=MagicMock(return_value=(sample_candidate_data["id"],))),
            Exception("Insert failed"),
        ]

        with pytest.raises(Exception, match="Insert failed"):
            await talent_pool_manager.add_to_pool(
                pool_id=sample_pool.id,
                candidate_id=sample_candidate_data["id"],
                added_by="recruiter_001",
            )

        mock_db.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_to_pool_invalidate_cache(
        self,
        talent_pool_manager,
        mock_db,
        mock_redis,
        sample_pool,
        sample_candidate_data,
    ):
        """Adding a candidate should invalidate the pool's cache."""
        mock_db.execute.return_value = MagicMock(
            fetchone=MagicMock(
                return_value=(
                    sample_candidate_data["id"],
                    sample_pool.id,
                    sample_candidate_data["full_name"],
                    sample_candidate_data["email"],
                    sample_candidate_data["skills"],
                    sample_candidate_data["experience_years"],
                    sample_candidate_data["location"],
                    CandidateStatus.ACTIVE,
                    datetime.utcnow(),
                    "recruiter_001",
                )
            )
        )

        await talent_pool_manager.add_to_pool(
            pool_id=sample_pool.id,
            candidate_id=sample_candidate_data["id"],
            added_by="recruiter_001",
        )

        mock_redis.delete.assert_called()
        delete_calls = mock_redis.delete.call_args_list
        assert any(str(sample_pool.id) in str(call) for call in delete_calls)

    @pytest.mark.asyncio
    async def test_add_to_pool_with_custom_status(
        self,
        talent_pool_manager,
        mock_db,
        sample_pool,
        sample_candidate_data,
    ):
        """Add a candidate with a specific status (e.g., SNOOZED)."""
        mock_db.execute.return_value = MagicMock(
            fetchone=MagicMock(
                return_value=(
                    sample_candidate_data["id"],
                    sample_pool.id,
                    sample_candidate_data["full_name"],
                    sample_candidate_data["email"],
                    sample_candidate_data["skills"],
                    sample_candidate_data["experience_years"],
                    sample_candidate_data["location"],
                    CandidateStatus.SNOOZED,
                    datetime.utcnow(),
                    "recruiter_001",
                )
            )
        )

        result = await talent_pool_manager.add_to_pool(
            pool_id=sample_pool.id,
            candidate_id=sample_candidate_data["id"],
            added_by="recruiter_001",
            status=CandidateStatus.SNOOZED,
        )

        assert result.status == CandidateStatus.SNOOZED


# ---------------------------------------------------------------------------
# Test: search_pool
# ---------------------------------------------------------------------------


class TestSearchPool:
    """Tests for TalentPoolManager.search_pool."""

    @pytest.mark.asyncio
    async def test_search_pool_by_skills(
        self, talent_pool_manager, mock_db, sample_pool, multiple_candidates
    ):
        """Search pool candidates filtered by skills."""
        # Mock the search results
        python_candidates = [c for c in multiple_candidates if "Python" in c["skills"]]
        mock_db.execute.return_value = MagicMock(
            fetchall=MagicMock(
                return_value=[
                    (
                        c["id"],
                        sample_pool.id,
                        c["full_name"],
                        c["email"],
                        c["skills"],
                        c["experience_years"],
                        c["location"],
                        c["status"],
                        c["current_title"],
                    )
                    for c in python_candidates
                ]
            )
        )

        criteria = SearchCriteria(skills=["Python"])
        results = await talent_pool_manager.search_pool(
            pool_id=sample_pool.id, criteria=criteria
        )

        assert results is not None
        assert len(results) == len(python_candidates)
        for result in results:
            assert "Python" in result.skills

    @pytest.mark.asyncio
    async def test_search_pool_by_location(
        self, talent_pool_manager, mock_db, sample_pool, multiple_candidates
    ):
        """Search pool candidates filtered by location."""
        remote_candidates = [c for c in multiple_candidates if c["location"] == "Remote"]
        mock_db.execute.return_value = MagicMock(
            fetchall=MagicMock(
                return_value=[
                    (
                        c["id"],
                        sample_pool.id,
                        c["full_name"],
                        c["email"],
                        c["skills"],
                        c["experience_years"],
                        c["location"],
                        c["status"],
                        c["current_title"],
                    )
                    for c in remote_candidates
                ]
            )
        )

        criteria = SearchCriteria(locations=["Remote"])
        results = await talent_pool_manager.search_pool(
            pool_id=sample_pool.id, criteria=criteria
        )

        assert results is not None
        assert len(results) == len(remote_candidates)
        for result in results:
            assert result.location == "Remote"

    @pytest.mark.asyncio
    async def test_search_pool_by_experience_range(
        self, talent_pool_manager, mock_db, sample_pool, multiple_candidates
    ):
        """Search pool candidates filtered by experience range."""
        senior_candidates = [c for c in multiple_candidates if c["experience_years"] >= 5]
        mock_db.execute.return_value = MagicMock(
            fetchall=MagicMock(
                return_value=[
                    (
                        c["id"],
                        sample_pool.id,
                        c["full_name"],
                        c["email"],
                        c["skills"],
                        c["experience_years"],
                        c["location"],
                        c["status"],
                        c["current_title"],
                    )
                    for c in senior_candidates
                ]
            )
        )

        criteria = SearchCriteria(min_experience_years=5)
        results = await talent_pool_manager.search_pool(
            pool_id=sample_pool.id, criteria=criteria
        )

        assert results is not None
        assert len(results) == len(senior_candidates)
        for result in results:
            assert result.experience_years >= 5

    @pytest.mark.asyncio
    async def test_search_pool_by_name_query(
        self, talent_pool_manager, mock_db, sample_pool, multiple_candidates
    ):
        """Search pool candidates by name substring."""
        mock_db.execute.return_value = MagicMock(
            fetchall=MagicMock(
                return_value=[
                    (
                        multiple_candidates[0]["id"],
                        sample_pool.id,
                        multiple_candidates[0]["full_name"],
                        multiple_candidates[0]["email"],
                        multiple_candidates[0]["skills"],
                        multiple_candidates[0]["experience_years"],
                        multiple_candidates[0]["location"],
                        multiple_candidates[0]["status"],
                        multiple_candidates[0]["current_title"],
                    )
                ]
            )
        )

        criteria = SearchCriteria(name_query="Candidate 1")
        results = await talent_pool_manager.search_pool(
            pool_id=sample_pool.id, criteria=criteria
        )

        assert results is not None
        assert len(results) == 1
        assert "Candidate 1" in results[0].full_name

    @pytest.mark.asyncio
    async def test_search_pool_combined_filters(
        self, talent_pool_manager, mock_db, sample_pool, multiple_candidates
    ):
        """Search with multiple filters combined (AND logic)."""
        filtered = [
            c
            for c in multiple_candidates
            if "Python" in c["skills"]
            and c["location"] == "Remote"
            and c["experience_years"] >= 5
        ]
        mock_db.execute.return_value = MagicMock(
            fetchall=MagicMock(
                return_value=[
                    (
                        c["id"],
                        sample_pool.id,
                        c["full_name"],
                        c["email"],
                        c["skills"],
                        c["experience_years"],
                        c["location"],
                        c["status"],
                        c["current_title"],
                    )
                    for c in filtered
                ]
            )
        )

        criteria = SearchCriteria(
            skills=["Python"],
            locations=["Remote"],
            min_experience_years=5,
        )
        results = await talent_pool_manager.search_pool(
            pool_id=sample_pool.id, criteria=criteria
        )

        assert results is not None
        assert len(results) == len(filtered)
        for result in results:
            assert "Python" in result.skills
            assert result.location == "Remote"
            assert result.experience_years >= 5

    @pytest.mark.asyncio
    async def test_search_pool_no_results(
        self, talent_pool_manager, mock_db, sample_pool
    ):
        """Search with criteria that matches nothing returns empty list."""
        mock_db.execute.return_value = MagicMock(
            fetchall=MagicMock(return_value=[])
        )

        criteria = SearchCriteria(skills=["NonExistentSkill"])
        results = await talent_pool_manager.search_pool(
            pool_id=sample_pool.id, criteria=criteria
        )

        assert results is not None
        assert len(results) == 0
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_search_pool_no_criteria_returns_all(
        self, talent_pool_manager, mock_db, sample_pool, multiple_candidates
    ):
        """Search with no criteria returns all candidates in the pool."""
        mock_db.execute.return_value = MagicMock(
            fetchall=MagicMock(
                return_value=[
                    (
                        c["id"],
                        sample_pool.id,
                        c["full_name"],
                        c["email"],
                        c["skills"],
                        c["experience_years"],
                        c["location"],
                        c["status"],
                        c["current_title"],
                    )
                    for c in multiple_candidates
                ]
            )
        )

        criteria = SearchCriteria()
        results = await talent_pool_manager.search_pool(
            pool_id=sample_pool.id, criteria=criteria
        )

        assert results is not None
        assert len(results) == len(multiple_candidates)

    @pytest.mark.asyncio
    async def test_search_pool_with_pagination(
        self, talent_pool_manager, mock_db, sample_pool, multiple_candidates
    ):
        """Search with limit and offset for pagination."""
        mock_db.execute.return_value = MagicMock(
            fetchall=MagicMock(
                return_value=[
                    (
                        c["id"],
                        sample_pool.id,
                        c["full_name"],
                        c["email"],
                        c["skills"],
                        c["experience_years"],
                        c["location"],
                        c["status"],
                        c["current_title"],
                    )
                    for c in multiple_candidates[:2]
                ]
            )
        )

        criteria = SearchCriteria(limit=2, offset=0)
        results = await talent_pool_manager.search_pool(
            pool_id=sample_pool.id, criteria=criteria
        )

        assert results is not None
        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_search_pool_with_offset(
        self, talent_pool_manager, mock_db, sample_pool, multiple_candidates
    ):
        """Search with offset skips the first N results."""
        offset = 3
        mock_db.execute.return_value = MagicMock(
            fetchall=MagicMock(
                return_value=[
                    (
                        c["id"],
                        sample_pool.id,
                        c["full_name"],
                        c["email"],
                        c["skills"],
                        c["experience_years"],
                        c["location"],
                        c["status"],
                        c["current_title"],
                    )
                    for c in multiple_candidates[offset:]
                ]
            )
        )

        criteria = SearchCriteria(limit=10, offset=offset)
        results = await talent_pool_manager.search_pool(
            pool_id=sample_pool.id, criteria=criteria
        )

        assert results is not None
        assert len(results) == len(multiple_candidates) - offset

    @pytest.mark.asyncio
    async def test_search_pool_by_status(
        self, talent_pool_manager, mock_db, sample_pool, multiple_candidates
    ):
        """Search pool candidates filtered by status."""
        active_candidates = [
            c for c in multiple_candidates if c["status"] == CandidateStatus.ACTIVE
        ]
        mock_db.execute.return_value = MagicMock(
            fetchall=MagicMock(
                return_value=[
                    (
                        c["id"],
                        sample_pool.id,
                        c["full_name"],
                        c["email"],
                        c["skills"],
                        c["experience_years"],
                        c["location"],
                        c["status"],
                        c["current_title"],
                    )
                    for c in active_candidates
                ]
            )
        )

        criteria = SearchCriteria(statuses=[CandidateStatus.ACTIVE])
        results = await talent_pool_manager.search_pool(
            pool_id=sample_pool.id, criteria=criteria
        )

        assert results is not None
        assert len(results) == len(active_candidates)
        for result in results:
            assert result.status == CandidateStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_search_pool_nonexistent_pool_raises_error(
        self, talent_pool_manager, mock_db
    ):
        """Searching a non-existent pool should raise ValueError."""
        mock_db.execute.return_value = MagicMock(
            fetchone=MagicMock(return_value=None)
        )

        criteria = SearchCriteria()
        with pytest.raises(ValueError, match="Pool not found"):
            await talent_pool_manager.search_pool(
                pool_id=uuid4(), criteria=criteria
            )

    @pytest.mark.asyncio
    async def test_search_pool_missing_pool_id_raises_error(
        self, talent_pool_manager, mock_db
    ):
        """Missing pool_id should raise ValueError."""
        criteria = SearchCriteria()
        with pytest.raises(ValueError, match="pool_id is required"):
            await talent_pool_manager.search_pool(
                pool_id=None, criteria=criteria
            )

    @pytest.mark.asyncio
    async def test_search_pool_uses_cache(
        self, talent_pool_manager, mock_db, mock_redis, sample_pool
    ):
        """Search should check cache first and return cached results."""
        cached_data = [
            (
                uuid4(),
                sample_pool.id,
                "Cached Candidate",
                "cached@example.com",
                ["Python"],
                5,
                "Berlin",
                CandidateStatus.ACTIVE,
                "Engineer",
            )
        ]
        mock_redis.get.return_value = str(cached_data)

        criteria = SearchCriteria()
        results = await talent_pool_manager.search_pool(
            pool_id=sample_pool.id, criteria=criteria
        )

        mock_redis.get.assert_called_once()
        # If cache hit, db should not be called for results
        # (implementation dependent, but cache check should happen)

    @pytest.mark.asyncio
    async def test_search_pool_sorts_by_relevance(
        self, talent_pool_manager, mock_db, sample_pool, multiple_candidates
    ):
        """Search results should be sorted by relevance when skills match."""
        mock_db.execute.return_value = MagicMock(
            fetchall=MagicMock(
                return_value=[
                    (
                        c["id"],
                        sample_pool.id,
                        c["full_name"],
                        c["email"],
                        c["skills"],
                        c["experience_years"],
                        c["location"],
                        c["status"],
                        c["current_title"],
                    )
                    for c in multiple_candidates
                ]
            )
        )

        criteria = SearchCriteria(skills=["Python"])
        results = await talent_pool_manager.search_pool(
            pool_id=sample_pool.id, criteria=criteria
        )

        assert results is not None
        # Results with more matching skills should appear first
        if len(results) > 1:
            first_match_count = len(
                set(results[0].skills) & set(criteria.skills)
            )
            last_match_count = len(
                set(results[-1].skills) & set(criteria.skills)
            )
            assert first_match_count >= last_match_count

    @pytest.mark.asyncio
    async def test_search_pool_by_salary_range(
        self, talent_pool_manager, mock_db, sample_pool, multiple_candidates
    ):
        """Search pool candidates filtered by expected salary range."""
        mock_db.execute.return_value = MagicMock(
            fetchall=MagicMock(
                return_value=[
                    (
                        c["id"],
                        sample_pool.id,
                        c["full_name"],
                        c["email"],
                        c["skills"],
                        c["experience_years"],
                        c["location"],
                        c["status"],
                        c["current_title"],
                    )
                    for c in multiple_candidates[:3]
                ]
            )
        )

        criteria = SearchCriteria(
            min_salary=50000,
            max_salary=120000,
        )
        results = await talent_pool_manager.search_pool(
            pool_id=sample_pool.id, criteria=criteria
        )

        assert results is not None
        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_search_pool_db_error_propagates(
        self, talent_pool_manager, mock_db, sample_pool
    ):
        """Database error during search should propagate."""
        mock_db.execute.side_effect = Exception("Query timeout")

        criteria = SearchCriteria()
        with pytest.raises(Exception, match="Query timeout"):
            await talent_pool_manager.search_pool(
                pool_id=sample_pool.id, criteria=criteria
            )

    @pytest.mark.asyncio
    async def test_search_pool_with_empty_skills_list(
        self, talent_pool_manager, mock_db, sample_pool, multiple_candidates
    ):
        """Search with empty skills list should not filter by skills."""
        mock_db.execute.return_value = MagicMock(
            fetchall=MagicMock(
                return_value=[
                    (
                        c["id"],
                        sample_pool.id,
                        c["full_name"],
                        c["email"],
                        c["skills"],
                        c["experience_years"],
                        c["location"],
                        c["status"],
                        c["current_title"],
                    )
                    for c in multiple_candidates
                ]
            )
        )

        criteria = SearchCriteria(skills=[])
        results = await talent_pool_manager.search_pool(
            pool_id=sample_pool.id, criteria=criteria
        )

        assert results is not None
        assert len(results) == len(multiple_candidates)

    @pytest.mark.asyncio
    async def test_search_pool_max_limit_enforced(
        self, talent_pool_manager, mock_db, sample_pool, multiple_candidates
    ):
        """Search should enforce a maximum limit on returned results."""
        mock_db.execute.return_value = MagicMock(
            fetchall=MagicMock(
                return_value=[
                    (
                        c["id"],
                        sample_pool.id,
                        c["full_name"],
                        c["email"],
                        c["skills"],
                        c["experience_years"],
                        c["location"],
                        c["status"],
                        c["current_title"],
                    )
                    for c in multiple_candidates
                ]
            )
        )

        criteria = SearchCriteria(limit=1000)
        results = await talent_pool_manager.search_pool(
            pool_id=sample_pool.id, criteria=criteria
        )

        assert results is not None
        # Should be capped at a reasonable max (e.g., 100 or 200)
        assert len(results) <= 200
