"""
Core Schemas — canonical schema enforcement for the control plane.

This module re-exports the WOSDS WorkOrder schema and validation function
so that the rest of the control-plane stack imports from a single, stable
location inside the ``core`` package.

Schema rules (enforced by ``enforce``)
--------------------------------------
* ``id``       — non-empty string
* ``action``   — non-empty string
* ``payload``  — dict (may be empty only when explicitly allowed)
* ``metadata`` — dict
* ``replay``   — bool

Raises :exc:`SchemaValidationError` immediately when any rule is violated.
"""

from __future__ import annotations

# Re-export the canonical types so callers can write:
#   from core.schemas import WorkOrder, SchemaValidationError, enforce
from wosds.schema import SchemaValidationError, WorkOrder, validate_work_order


def enforce(order: WorkOrder) -> None:
    """
    Validate *order* against the mandatory schema.

    This is a thin wrapper around :func:`wosds.schema.validate_work_order`
    that provides the control-plane's primary entry point for schema checks.
    Raises :exc:`SchemaValidationError` on the first violation found.
    """
    validate_work_order(order)


__all__ = [
    "WorkOrder",
    "SchemaValidationError",
    "enforce",
    "validate_work_order",
]
