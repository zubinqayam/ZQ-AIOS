"""
Policy Engine — dual-gate policy evaluation.

Gates
-----
PRE_POLICY   Evaluated before execution.  Blocks the order if any rule
             returns DENY.  A blocked order is logged but never executed.

POST_POLICY  Evaluated after execution.   Can reject / quarantine a
             result that was produced but violates governance rules.

Each gate is a list of PolicyRule callables.  Rules return a
PolicyDecision (ALLOW / DENY) plus an optional reason string.
"""

from .engine import PolicyDecision, PolicyEngine, PolicyRule, PolicyViolationError

__all__ = [
    "PolicyDecision",
    "PolicyEngine",
    "PolicyRule",
    "PolicyViolationError",
]
