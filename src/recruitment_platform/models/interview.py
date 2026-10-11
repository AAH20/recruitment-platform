"""Compatibility shim for the canonical ``Interview`` model.

``Interview`` is defined once, in ``recruitment_platform.models`` (the package
``__init__``), which the service layer imports
(``from recruitment_platform.models import Interview``).

This module previously declared a *second, incompatible* ``Interview`` with the
same ``__tablename__ = "interviews"`` — uuid keys, a duration column and an
interviewer FK to ``users.id``, versus the package's int-keyed version.
Importing both the package and this module registered the table twice on one
``MetaData`` and raised
``InvalidRequestError: Table 'interviews' is already defined``.

It now re-exports the canonical class, so
``from recruitment_platform.models.interview import Interview`` keeps working
without duplicating the table.
"""

from __future__ import annotations

from recruitment_platform.models import Interview

__all__ = ["Interview"]
