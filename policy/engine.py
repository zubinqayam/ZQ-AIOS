"""
Policy Engine implementation.

PolicyRule protocol
-------------------
A callable that accepts a WorkOrder (and optionally a result dict for
post-policy) and returns a (PolicyDecision, reason) tuple.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Callable, Protocol

from wosds.schema import WorkOrder


class PolicyDecision(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"


class PolicyViolationError(RuntimeError):
    """Raised when a policy gate denies a work order."""

    def __init__(self, gate: str, order_id: str, reason: str) -> None:
        self.gate = gate
        self.order_id = order_id
        self.reason = reason
        super().__init__(f"[{gate}] Order {order_id!r} denied — {reason}")


class PolicyRule(Protocol):
    """A callable that returns (decision, reason)."""

    def __call__(
        self,
        order: WorkOrder,
        result: dict[str, Any] | None = None,
    ) -> tuple[PolicyDecision, str]: ...


class PolicyEngine:
    """
    Holds pre- and post-policy rule lists and enforces them.

    Usage::

        engine = PolicyEngine(pre_rules=[...], post_rules=[...])
        engine.enforce_pre(order)             # before execution
        engine.enforce_post(order, result)    # after execution
    """

    def __init__(
        self,
        pre_rules: list[PolicyRule] | None = None,
        post_rules: list[PolicyRule] | None = None,
    ) -> None:
        self._pre_rules: list[PolicyRule] = pre_rules or []
        self._post_rules: list[PolicyRule] = post_rules or []

    # ------------------------------------------------------------------ #
    # public API                                                           #
    # ------------------------------------------------------------------ #

    def enforce_pre(self, order: WorkOrder) -> None:
        """Run all pre-policy rules; raise PolicyViolationError on first DENY."""
        self._run_gate("PRE_POLICY", order, result=None, rules=self._pre_rules)

    def enforce_post(self, order: WorkOrder, result: dict[str, Any]) -> None:
        """Run all post-policy rules; raise PolicyViolationError on first DENY."""
        self._run_gate("POST_POLICY", order, result=result, rules=self._post_rules)

    # ------------------------------------------------------------------ #
    # internal                                                             #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _run_gate(
        gate: str,
        order: WorkOrder,
        result: dict[str, Any] | None,
        rules: list[PolicyRule],
    ) -> None:
        for rule in rules:
            decision, reason = rule(order, result)
            if decision is PolicyDecision.DENY:
                raise PolicyViolationError(gate, order.id, reason)
