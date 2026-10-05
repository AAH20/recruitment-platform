"""Authentication routes for recruitment-platform."""

from __future__ import annotations

import os
import sqlite3

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from recruitment_platform.security.auth import (
    create_access_token,
    get_password_hash,
    sanitize_input,
    verify_password,
)

router = APIRouter()

DB_PATH = os.getenv("DATABASE_PATH", "./test_validation.db")


def _get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def _init_db() -> None:
    conn = _get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'recruiter',
            is_active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)
    # Add missing columns if they don't exist (for pre-existing tables)
    existing_cols = {row["name"] for row in conn.execute("PRAGMA table_info(users)")}
    if "password_hash" not in existing_cols:
        conn.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")
    if "is_active" not in existing_cols:
        conn.execute("ALTER TABLE users ADD COLUMN is_active INTEGER DEFAULT 1")
    conn.commit()
    conn.close()


_init_db()


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


class AuthResponse(BaseModel):
    user: dict
    token: str


def _normalize_email(email: str) -> str:
    """Normalize an email for storage/lookup.

    Note: InputSanitizationMiddleware has already HTML-escaped string values in
    the request body by the time a route runs. Escaping is a transport-level
    defence for HTML contexts, not a storage encoding - re-escaping here (or
    escaping twice) corrupts real addresses into "&#x27;"-style garbage, so
    we only normalise case/whitespace and never re-escape.
    """
    return email.strip().lower()


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest) -> AuthResponse:
    email = _normalize_email(request.email)
    conn = _get_db()
    row = conn.execute(
        "SELECT * FROM users WHERE email = ?", (email,)
    ).fetchone()
    conn.close()

    if not row or not verify_password(request.password, row["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    user = {
        "id": row["id"],
        "name": row["name"],
        "email": row["email"],
        "role": row["role"],
    }
    # The `sub` claim MUST be a string: python-jose rejects non-string subjects
    # ("Subject must be a string"), so a token minted from the raw SQLite row id
    # (an int) is signed successfully but fails validation on every request.
    # register() already stringifies its id - keep login consistent with it.
    token = create_access_token({"sub": str(row["id"]), "email": row["email"]})
    return AuthResponse(user=user, token=token)


@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest) -> AuthResponse:
    # Name is rendered in HTML contexts, so keep escaping it. Email is an
    # identifier used for lookup/login - normalise it instead of escaping.
    name = sanitize_input(request.name)
    email = _normalize_email(request.email)
    conn = _get_db()
    existing = conn.execute(
        "SELECT id FROM users WHERE email = ?", (email,)
    ).fetchone()
    if existing:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    password_hash = get_password_hash(request.password)
    cursor = conn.execute(
        "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
        (name, email, password_hash, "recruiter"),
    )
    user_id = str(cursor.lastrowid)
    conn.commit()
    conn.close()

    user = {
        "id": user_id,
        "name": name,
        "email": email,
        "role": "recruiter",
    }
    token = create_access_token({"sub": user_id, "email": email})
    return AuthResponse(user=user, token=token)
