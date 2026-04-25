"""
Factory — assemble the full control-plane pipeline.
"""

from __future__ import annotations

from alga import ALGAExecutor
from core import Pipeline
from governance import Ledger
from policy import PolicyEngine
from policy.rules import (
    block_error_results,
    block_forbidden_actions,
    require_non_empty_payload,
)


def build_pipeline(ledger: Ledger | None = None) -> tuple[Pipeline, Ledger]:
    """
    Return a ``(pipeline, ledger)`` pair wired with default rules.

    Parameters
    ----------
    ledger :
        Supply an existing Ledger to share across pipelines.
        A fresh Ledger is created when *None* is given.
    """
    ledger = ledger or Ledger()

    policy_engine = PolicyEngine(
        pre_rules=[block_forbidden_actions, require_non_empty_payload],
        post_rules=[block_error_results],
    )

    executor = ALGAExecutor()

    pipeline = Pipeline(
        policy_engine=policy_engine,
        executor=executor,
        ledger=ledger,
    )

    return pipeline, ledger
