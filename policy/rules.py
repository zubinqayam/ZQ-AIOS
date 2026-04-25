"""
Built-in policy rules.

These are the default rules registered on the PolicyEngine.
Additional rules can be injected at construction time.
"""

from __future__ import annotations

from typing import Any

from policy.engine import PolicyDecision
from wosds.schema import WorkOrder

# ------------------------------------------------------------------ #
# Pre-policy rules                                                     #
# ------------------------------------------------------------------ #

BLOCKED_ACTIONS: frozenset[str] = frozenset(
    {
        "delete_all",
        "shutdown",
        "override_governance",
    }
)


def block_forbidden_actions(
    order: WorkOrder,
    result: dict[str, Any] | None = None,
) -> tuple[PolicyDecision, str]:
    """Deny any order whose action is on the hard-blocked list."""
    if order.action in BLOCKED_ACTIONS:
        return PolicyDecision.DENY, f"action '{order.action}' is forbidden"
    return PolicyDecision.ALLOW, ""


def require_non_empty_payload(
    order: WorkOrder,
    result: dict[str, Any] | None = None,
) -> tuple[PolicyDecision, str]:
    """Deny orders with an empty payload (nothing to execute)."""
    if not order.payload:
        return PolicyDecision.DENY, "payload must not be empty"
    return PolicyDecision.ALLOW, ""


# ------------------------------------------------------------------ #
# Post-policy rules                                                    #
# ------------------------------------------------------------------ #


def block_error_results(
    order: WorkOrder,
    result: dict[str, Any] | None = None,
) -> tuple[PolicyDecision, str]:
    """
    Deny acceptance of a result that carries a top-level 'error' key
    unless the order is a replay (replays surface errors intentionally).
    """
    if result and result.get("error") and not order.replay:
        return PolicyDecision.DENY, f"execution returned error: {result['error']}"
    return PolicyDecision.ALLOW, ""
