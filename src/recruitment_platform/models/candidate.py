"""Compatibility shim for the canonical ``Candidate`` model.

``Candidate`` is defined once, in ``recruitment_platform.models`` (the package
``__init__``), which the service layer imports
(``from recruitment_platform.models import Candidate``).

This module previously declared a *second, incompatible* ``Candidate`` with the
same ``__tablename__ = "candidates"`` — a uuid primary key plus first_name /
last_name / resume_url / JSON skills columns, versus the package's int-keyed
version. Importing both the package and this module registered the table twice
on one ``MetaData`` and raised
``InvalidRequestError: Table 'candidates' is already defined``.

It now re-exports the canonical class, so
``from recruitment_platform.models.candidate import Candidate`` keeps working
without duplicating the table.
"""

from __future__ import annotations

from recruitment_platform.models import Candidate

__all__ = ["Candidate"]
