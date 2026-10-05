"""Authentication and authorization module."""

from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from recruitment_platform.config.settings import get_settings

security_bearer = HTTPBearer(auto_error=False)

# bcrypt has a hard 72-byte limit on input and rejects longer input outright.
# Truncate once, consistently, on both hash and verify so the operation is
# reversible and hashes stay comparable across calls.
BCRYPT_MAX_BYTES = 72


def _prepare_password(password: str) -> bytes:
    """Encode and truncate a password to bcrypt's 72-byte input limit."""
    return password.encode("utf-8")[:BCRYPT_MAX_BYTES]


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    if not hashed_password:
        return False
    try:
        return bcrypt.checkpw(
            _prepare_password(plain_password),
            hashed_password.encode("utf-8"),
        )
    except (ValueError, TypeError):
        # Malformed/unsupported hash - treat as a failed match, never a crash.
        return False


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return bcrypt.hashpw(
        _prepare_password(password),
        bcrypt.gensalt(rounds=12),
    ).decode("utf-8")


def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    """Create a JWT access token.

    The `sub` claim is normalised to a string: JWT requires it and python-jose
    raises "Subject must be a string" on decode, so an int subject produces a
    token that is signed but permanently rejected at verification time.
    """
    settings = get_settings()
    to_encode = data.copy()
    if "sub" in to_encode and not isinstance(to_encode["sub"], str):
        to_encode["sub"] = str(to_encode["sub"])
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode.update({"exp": expire, "iat": datetime.now(UTC)})
    return jwt.encode(to_encode, settings.secret_key, algorithm="HS256")


def create_refresh_token(data: dict[str, Any]) -> str:
    """Create a JWT refresh token with longer expiry."""
    settings = get_settings()
    to_encode = data.copy()
    if "sub" in to_encode and not isinstance(to_encode["sub"], str):
        to_encode["sub"] = str(to_encode["sub"])
    expire = datetime.now(UTC) + timedelta(days=7)
    to_encode.update({"exp": expire, "iat": datetime.now(UTC), "type": "refresh"})
    return jwt.encode(to_encode, settings.secret_key, algorithm="HS256")


def verify_token(token: str) -> dict[str, Any]:
    """Verify and decode a JWT token."""
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = None,
) -> dict[str, Any]:
    """Get the current authenticated user from JWT token."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = verify_token(credentials.credentials)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    return {
        "id": user_id,
        "email": payload.get("email"),
        "roles": payload.get("roles", []),
    }


async def get_current_active_user(
    current_user: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Get the current active user."""
    if not current_user.get("is_active", True):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


class RoleChecker:
    """Role-based access control dependency."""

    def __init__(self, allowed_roles: list[str]) -> None:
        self.allowed_roles = allowed_roles

    async def __call__(
        self, current_user: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        user_roles = current_user.get("roles", [])
        if not any(role in self.allowed_roles for role in user_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user


def generate_api_key() -> str:
    """Generate a secure API key."""
    return secrets.token_urlsafe(32)


def verify_api_key(api_key: str, hashed_key: str) -> bool:
    """Verify an API key against its hash."""
    return hmac.compare_digest(
        hashlib.sha256(api_key.encode()).hexdigest(),
        hashed_key,
    )


def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent injection attacks."""
    import html

    sanitized = html.escape(text)
    # Remove null bytes
    sanitized = sanitized.replace("\x00", "")
    return sanitized


def generate_secure_id() -> str:
    """Generate a cryptographically secure unique identifier."""
    return secrets.token_hex(16)
