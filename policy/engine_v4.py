"""
Policy Engine v4 — dual-gate policy enforcement for the ZQ-AIOS control plane.

This module exposes the v4 policy engine interface.  The implementation is
provided by :mod:`policy.engine`; this module re-exports the public API and
adds version metadata so that the rest of the system can import from a stable
``policy.engine_v4`` path.

Gates
-----
PRE_POLICY   Evaluated *before* execution.  Blocks the order if any rule
             returns DENY.  A blocked order is never executed.

POST_POLICY  Evaluated *after* execution.  Can reject a result that was
             produced but violates governance rules.

Each gate accepts a list of :class:`PolicyRule` callables.  Rules return a
:class:`PolicyDecision` (ALLOW / DENY) plus an optional reason string.

Version: 4
"""

from __future__ import annotations

# Re-export the full public API from the canonical implementation.
from policy.engine import (
    PolicyDecision,
    PolicyEngine,
    PolicyRule,
    PolicyViolationError,
)

#: Version identifier for this policy engine interface.
ENGINE_VERSION: int = 4

__all__ = [
    "PolicyDecision",
    "PolicyEngine",
    "PolicyRule",
    "PolicyViolationError",
    "ENGINE_VERSION",
]
