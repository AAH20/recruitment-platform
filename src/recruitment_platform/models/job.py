"""Compatibility shim for the canonical ``Job`` model.

``Job`` is defined once, in ``recruitment_platform.models`` (the package
``__init__``), which the service layer imports
(``from recruitment_platform.models import Job``).

This module previously declared a *second, incompatible* ``Job`` carrying the
same ``__tablename__ = "jobs"`` — a uuid primary key and extra columns
(department, location, salary_range) with a ``Uuid`` FK to ``employers.id``,
versus the package's int-keyed version. Importing both the package and this
module therefore registered the ``jobs`` table twice on one ``MetaData`` and
raised ``InvalidRequestError: Table 'jobs' is already defined``.

It now re-exports the canonical class, so
``from recruitment_platform.models.job import Job`` keeps working without
duplicating the table.
"""

from __future__ import annotations

from recruitment_platform.models import Job

__all__ = ["Job"]
