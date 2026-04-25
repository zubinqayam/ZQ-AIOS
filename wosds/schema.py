"""
WOSDS Schema — canonical Work Order definition and validation.

A WorkOrder must carry:
  - id        : unique identifier (non-empty string)
  - action    : the operation requested (non-empty string)
  - payload   : arbitrary dict of operation parameters
  - metadata  : optional dict (defaults to empty)
  - replay    : bool flag — True when this is a replay of a prior order
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any


class SchemaValidationError(ValueError):
    """Raised when a WorkOrder fails schema validation."""


@dataclass
class WorkOrder:
    id: str
    action: str
    payload: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)
    replay: bool = False

    # ------------------------------------------------------------------ #
    # factory                                                              #
    # ------------------------------------------------------------------ #

    @classmethod
    def new(
        cls,
        action: str,
        payload: dict[str, Any],
        metadata: dict[str, Any] | None = None,
        replay: bool = False,
        order_id: str | None = None,
    ) -> "WorkOrder":
        return cls(
            id=order_id or str(uuid.uuid4()),
            action=action,
            payload=payload,
            metadata=metadata or {},
            replay=replay,
        )


def validate_work_order(order: WorkOrder) -> None:
    """
    Validate *order* against the canonical schema.

    Raises SchemaValidationError on the first violation found.
    """
    errors: list[str] = []

    if not isinstance(order.id, str) or not order.id.strip():
        errors.append("'id' must be a non-empty string")

    if not isinstance(order.action, str) or not order.action.strip():
        errors.append("'action' must be a non-empty string")

    if not isinstance(order.payload, dict):
        errors.append("'payload' must be a dict")

    if not isinstance(order.metadata, dict):
        errors.append("'metadata' must be a dict")

    if not isinstance(order.replay, bool):
        errors.append("'replay' must be a bool")

    if errors:
        raise SchemaValidationError(
            f"WorkOrder {order.id!r} failed schema validation: {'; '.join(errors)}"
        )
