"""Guard: the ORM layer must import, and ``Base`` must be a single object.

``job.py`` and ``interview.py`` import ``recruitment_platform.models.base``,
which did not exist, so the ORM layer was unimportable. ``Base`` was also
declared twice (``models/__init__.py`` and the legacy flat ``models.py``),
which would split the SQLAlchemy ``MetaData`` and register the same
``__tablename__`` more than once.

These tests pin both properties: every ORM module imports, and the ``Base``
reachable via the package is the *same object* as the one in
``models.base`` (so there is exactly one ``MetaData``).
"""

from __future__ import annotations

import importlib


def test_orm_modules_are_importable():
    """Every ORM module that imports models.base must import cleanly."""
    for name in (
        "recruitment_platform.models",
        "recruitment_platform.models.base",
        "recruitment_platform.models.job",
        "recruitment_platform.models.interview",
        "recruitment_platform.models.candidate",
        "recruitment_platform.models.employer",
        "recruitment_platform.models.application",
        "recruitment_platform.models.skill",
    ):
        module = importlib.import_module(name)
        assert module is not None, f"{name} failed to import"


def test_base_is_a_single_object():
    """models.Base and models.base.Base must be the identical class."""
    from recruitment_platform.models import Base as package_base
    from recruitment_platform.models.base import Base as module_base

    assert package_base is module_base, (
        "two distinct Base classes -> two MetaData instances -> duplicate tables"
    )
