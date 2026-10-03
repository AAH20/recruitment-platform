"""Talent pool service for recruitment platform."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


class TalentPoolError(Exception):
    """Base exception for talent pool operations."""


class PoolNotFoundError(TalentPoolError):
    """Raised when a talent pool is not found."""


class CandidateNotFoundError(TalentPoolError):
    """Raised when a candidate is not found."""


class DuplicateCandidateError(TalentPoolError):
    """Raised when a candidate is already in the pool."""


# In-memory storage for demonstration purposes
_pools: dict[str, dict[str, Any]] = {}
_candidates: dict[str, dict[str, Any]] = {}


def get_talent_pool(pool_id: str) -> dict:
    """Get a talent pool by its ID.

    Args:
        pool_id: The unique identifier of the talent pool.

    Returns:
        A dictionary containing the talent pool data.

    Raises:
        PoolNotFoundError: If no talent pool exists with the given ID.
        TalentPoolError: If pool_id is invalid.
    """
    if not pool_id or not isinstance(pool_id, str):
        raise TalentPoolError("pool_id must be a non-empty string")

    pool = _pools.get(pool_id)
    if pool is None:
        raise PoolNotFoundError(f"Talent pool '{pool_id}' not found")

    logger.info("Retrieved talent pool %s", pool_id)
    return pool


def list_talent_pools(filters: dict, page: int, page_size: int) -> list[dict]:
    """List talent pools with optional filtering and pagination.

    Args:
        filters: A dictionary of filter criteria (e.g., {"name": "Engineering",
                 "tags": ["senior"], "owner_id": "user-123"}).
        page: The page number (1-indexed).
        page_size: The number of results per page.

    Returns:
        A list of talent pool dictionaries matching the filters.

    Raises:
        ValueError: If page or page_size is less than 1.
    """
    if page < 1:
        raise ValueError("page must be >= 1")
    if page_size < 1:
        raise ValueError("page_size must be >= 1")

    results: list[dict] = []
    filters = filters or {}

    for pool in _pools.values():
        # Apply name filter (case-insensitive substring match)
        if "name" in filters:
            if filters["name"].lower() not in pool.get("name", "").lower():
                continue

        # Apply tags filter (pool must contain all specified tags)
        if "tags" in filters:
            required_tags = set(filters["tags"])
            pool_tags = set(pool.get("tags", []))
            if not required_tags.issubset(pool_tags):
                continue

        # Apply owner_id filter
        if "owner_id" in filters:
            if pool.get("owner_id") != filters["owner_id"]:
                continue

        # Apply created_after filter
        if "created_after" in filters:
            if pool.get("created_at", "") < filters["created_after"]:
                continue

        results.append(pool)

    # Sort by most recently updated
    results.sort(key=lambda p: p.get("updated_at", ""), reverse=True)

    # Apply pagination
    offset = (page - 1) * page_size
    paginated = results[offset : offset + page_size]

    logger.info(
        "Listed talent pools (page=%d, page_size=%d, total=%d)",
        page,
        page_size,
        len(results),
    )
    return paginated


def create_talent_pool(data: dict) -> dict:
    """Create a new talent pool.

    Args:
        data: A dictionary containing the talent pool attributes
              (e.g., {"name": "Engineering", "description": "..."}).

    Returns:
        A dictionary containing the created talent pool data, including its ID.

    Raises:
        ValueError: If required fields are missing from data.
    """
    if not data:
        raise ValueError("data must not be empty")
    if "name" not in data:
        raise ValueError("data must contain a 'name' field")

    pool_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    pool = {
        "id": pool_id,
        "name": data["name"],
        "description": data.get("description", ""),
        "tags": data.get("tags", []),
        "owner_id": data.get("owner_id"),
        "candidate_ids": [],
        "created_at": now,
        "updated_at": now,
    }

    _pools[pool_id] = pool
    logger.info("Created talent pool %s (%s)", pool_id, data["name"])
    return pool


def add_candidate_to_pool(pool_id: str, candidate_id: str) -> bool:
    """Add a candidate to a talent pool.

    Args:
        pool_id: The unique identifier of the talent pool.
        candidate_id: The unique identifier of the candidate to add.

    Returns:
        True if the candidate was successfully added to the pool.

    Raises:
        PoolNotFoundError: If the talent pool does not exist.
        CandidateNotFoundError: If the candidate does not exist.
        DuplicateCandidateError: If the candidate is already in the pool.
        TalentPoolError: If pool_id or candidate_id is invalid.
    """
    if not pool_id or not isinstance(pool_id, str):
        raise TalentPoolError("pool_id must be a non-empty string")
    if not candidate_id or not isinstance(candidate_id, str):
        raise TalentPoolError("candidate_id must be a non-empty string")

    pool = _pools.get(pool_id)
    if pool is None:
        raise PoolNotFoundError(f"Talent pool '{pool_id}' not found")

    if candidate_id not in _candidates:
        raise CandidateNotFoundError(f"Candidate '{candidate_id}' not found")

    if candidate_id in pool["candidate_ids"]:
        raise DuplicateCandidateError(
            f"Candidate '{candidate_id}' is already in pool '{pool_id}'"
        )

    pool["candidate_ids"].append(candidate_id)
    pool["updated_at"] = datetime.now(timezone.utc).isoformat()

    logger.info("Added candidate %s to pool %s", candidate_id, pool_id)
    return True


def remove_candidate_from_pool(pool_id: str, candidate_id: str) -> bool:
    """Remove a candidate from a talent pool.

    Args:
        pool_id: The unique identifier of the talent pool.
        candidate_id: The unique identifier of the candidate to remove.

    Returns:
        True if the candidate was successfully removed from the pool.

    Raises:
        PoolNotFoundError: If the talent pool does not exist.
        CandidateNotFoundError: If the candidate does not exist.
        TalentPoolError: If pool_id or candidate_id is invalid.
    """
    if not pool_id or not isinstance(pool_id, str):
        raise TalentPoolError("pool_id must be a non-empty string")
    if not candidate_id or not isinstance(candidate_id, str):
        raise TalentPoolError("candidate_id must be a non-empty string")

    pool = _pools.get(pool_id)
    if pool is None:
        raise PoolNotFoundError(f"Talent pool '{pool_id}' not found")

    if candidate_id not in _candidates:
        raise CandidateNotFoundError(f"Candidate '{candidate_id}' not found")

    if candidate_id not in pool["candidate_ids"]:
        logger.warning("Candidate %s is not in pool %s", candidate_id, pool_id)
        return False

    pool["candidate_ids"].remove(candidate_id)
    pool["updated_at"] = datetime.now(timezone.utc).isoformat()

    logger.info("Removed candidate %s from pool %s", candidate_id, pool_id)
    return True


# Legacy function names for backward compatibility
def create_pool(data: dict[str, Any]) -> dict[str, Any]:
    """Create a new talent pool (legacy alias for create_talent_pool).

    Args:
        data: Pool data containing at least 'name' and optionally
              'description', 'tags', 'owner_id'.

    Returns:
        The created pool record with generated 'id' and timestamps.

    Raises:
        TalentPoolError: If required fields are missing or invalid.
    """
    return create_talent_pool(data)


def search_pools(
    query: str | None = None,
    filters: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Search talent pools by query string and filters.

    Args:
        query: Optional text to match against pool name and description.
        filters: Optional filters such as 'tags', 'owner_id', 'created_after'.

    Returns:
        A list of matching pool records, sorted by most recently updated.
    """
    results: list[dict[str, Any]] = []
    filters = filters or {}

    for pool in _pools.values():
        # Text search on name and description
        if query:
            q = query.lower()
            name_match = q in pool.get("name", "").lower()
            desc_match = q in pool.get("description", "").lower()
            if not (name_match or desc_match):
                continue

        # Apply filters
        if "tags" in filters:
            required_tags = set(filters["tags"])
            pool_tags = set(pool.get("tags", []))
            if not required_tags.issubset(pool_tags):
                continue

        if "owner_id" in filters:
            if pool.get("owner_id") != filters["owner_id"]:
                continue

        if "created_after" in filters:
            if pool.get("created_at", "") < filters["created_after"]:
                continue

        results.append(pool)

    # Sort by most recently updated
    results.sort(key=lambda p: p.get("updated_at", ""), reverse=True)
    return results
