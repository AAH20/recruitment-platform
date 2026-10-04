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


def get_talent_pool(db_session, pool_id: int) -> dict:
    """Get a talent pool by its ID."""
    pool = _pools.get(str(pool_id))
    if pool is None:
        raise PoolNotFoundError(f"Talent pool '{pool_id}' not found")
    logger.info("Retrieved talent pool %s", pool_id)
    return pool


def list_talent_pools(db_session) -> list[dict]:
    """List all talent pools."""
    return list(_pools.values())


def create_talent_pool(db_session, data: dict) -> dict:
    """Create a new talent pool."""
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


def update_talent_pool(db_session, pool_id: int, data: dict) -> dict:
    """Update an existing talent pool."""
    pool = get_talent_pool(db_session, pool_id)
    pool.update(data)
    pool["updated_at"] = datetime.now(timezone.utc).isoformat()
    return pool


def delete_talent_pool(db_session, pool_id: int) -> bool:
    """Delete a talent pool."""
    pool = get_talent_pool(db_session, pool_id)
    del _pools[pool["id"]]
    return True


def add_candidate_to_pool(pool_id: str, candidate_id: str) -> bool:
    """Add a candidate to a talent pool."""
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
    """Remove a candidate from a talent pool."""
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
    """Create a new talent pool (legacy alias for create_talent_pool)."""
    return create_talent_pool(None, data)


def search_pools(
    query: str | None = None,
    filters: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Search talent pools by query string and filters."""
    results: list[dict[str, Any]] = []
    filters = filters or {}

    for pool in _pools.values():
        if query:
            q = query.lower()
            name_match = q in pool.get("name", "").lower()
            desc_match = q in pool.get("description", "").lower()
            if not (name_match or desc_match):
                continue

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

    results.sort(key=lambda p: p.get("updated_at", ""), reverse=True)
    return results
