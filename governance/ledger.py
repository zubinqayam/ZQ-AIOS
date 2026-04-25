"""
Immutable append-only ledger.

EventType represents every distinct stage in the governed pipeline.
LedgerEntry is a frozen record for a single event.
Ledger collects entries and exposes query helpers.
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class EventType(str, Enum):
    SCHEMA_PASS = "SCHEMA_PASS"
    SCHEMA_FAIL = "SCHEMA_FAIL"
    PRE_POLICY_ALLOW = "PRE_POLICY_ALLOW"
    PRE_POLICY_DENY = "PRE_POLICY_DENY"
    EXECUTION_START = "EXECUTION_START"
    EXECUTION_COMPLETE = "EXECUTION_COMPLETE"
    POST_POLICY_ALLOW = "POST_POLICY_ALLOW"
    POST_POLICY_DENY = "POST_POLICY_DENY"
    REPLAY_TRIGGERED = "REPLAY_TRIGGERED"
    PIPELINE_COMPLETE = "PIPELINE_COMPLETE"
    PIPELINE_ABORTED = "PIPELINE_ABORTED"


@dataclass(frozen=True)
class LedgerEntry:
    order_id: str
    event: EventType
    timestamp: datetime.datetime = field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc)
    )
    details: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "order_id": self.order_id,
            "event": self.event.value,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
        }


class Ledger:
    """
    Thread-safe append-only ledger.

    Usage::

        ledger = Ledger()
        ledger.record(order.id, EventType.SCHEMA_PASS)
        entries = ledger.for_order(order.id)
    """

    def __init__(self) -> None:
        self._entries: list[LedgerEntry] = []

    # ------------------------------------------------------------------ #
    # write                                                                #
    # ------------------------------------------------------------------ #

    def record(
        self,
        order_id: str,
        event: EventType,
        details: dict[str, Any] | None = None,
    ) -> LedgerEntry:
        entry = LedgerEntry(order_id=order_id, event=event, details=details or {})
        self._entries.append(entry)
        return entry

    # ------------------------------------------------------------------ #
    # read                                                                 #
    # ------------------------------------------------------------------ #

    def for_order(self, order_id: str) -> list[LedgerEntry]:
        """Return all entries for a specific order, in insertion order."""
        return [e for e in self._entries if e.order_id == order_id]

    def all_entries(self) -> list[LedgerEntry]:
        """Return a snapshot of all ledger entries."""
        return list(self._entries)

    def as_log(self) -> list[dict[str, Any]]:
        """Serialisable representation of all entries."""
        return [e.as_dict() for e in self._entries]

    def __len__(self) -> int:
        return len(self._entries)
