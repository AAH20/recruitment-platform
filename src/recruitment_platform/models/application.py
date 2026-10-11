"""Compatibility shim for the canonical ``Application`` model.

``Application`` is defined once, in ``recruitment_platform.models`` (the package
``__init__``), which the service layer imports
(``from recruitment_platform.models import Application``).

This module previously declared a *second, incompatible* ``Application`` with
the same ``__tablename__ = "applications"`` — uuid keys, uuid FKs and a
cover_letter column, versus the package's int-keyed version. Importing both the
package and this module registered the table twice on one ``MetaData`` and
raised ``InvalidRequestError: Table 'applications' is already defined``.

It now re-exports the canonical class, so
``from recruitment_platform.models.application import Application`` keeps
working without duplicating the table.
"""

from __future__ import annotations

from recruitment_platform.models import Application

__all__ = ["Application"]
