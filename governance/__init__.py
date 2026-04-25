"""
Governance — immutable ledger and audit layer.

The Ledger records every significant event in the execution pipeline:
schema validation, pre-policy decisions, execution results, and
post-policy decisions.  Entries are append-only and time-stamped.
"""

from .ledger import Ledger, LedgerEntry, EventType

__all__ = ["Ledger", "LedgerEntry", "EventType"]
