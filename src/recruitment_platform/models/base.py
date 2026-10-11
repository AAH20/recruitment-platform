"""Declarative base for recruitment-platform ORM models.

``Base`` lives in its own module so every ORM module imports it from one
canonical path, ``recruitment_platform.models.base``.

Before this module existed, ``Base`` was declared in two other places —
``models/__init__.py`` and the legacy flat ``models.py`` — while ``job.py`` and
``interview.py`` did ``from recruitment_platform.models.base import Base``.
That path did not exist, so importing those modules raised
``ModuleNotFoundError`` and the ORM layer was unimportable.

Declaring ``Base`` more than once is also unsafe: two ``DeclarativeBase``
subclasses carry two ``MetaData`` instances, so the same ``__tablename__``
registers twice — the duplicate-table failure seen in gated-communities.
This module is therefore the single definition; ``models/__init__.py``
re-exports it rather than declaring its own.
"""

from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all ORM models."""
