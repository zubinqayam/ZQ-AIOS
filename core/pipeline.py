"""
Governed Execution Pipeline.

Flow
----
1.  Schema validation   (WOSDS)
2.  Pre-policy gate     (Policy Engine — PRE_POLICY)
3.  Execution           (ALGA)
4.  Post-policy gate    (Policy Engine — POST_POLICY)
5.  Ledger recording    (Governance)

Each stage is recorded in the ledger regardless of outcome.
A failed stage aborts the pipeline and records PIPELINE_ABORTED.
A successful end-to-end run records PIPELINE_COMPLETE.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from alga import ALGAExecutor
from governance import EventType, Ledger
from policy import PolicyEngine, PolicyViolationError
from wosds.schema import SchemaValidationError, WorkOrder, validate_work_order

logger = logging.getLogger(__name__)


@dataclass
class PipelineResult:
    """Value returned by Pipeline.run()."""

    order_id: str
    success: bool
    result: dict[str, Any] | None = None
    error: str | None = None
    stage: str | None = None  # stage where failure occurred (if any)

    def as_dict(self) -> dict[str, Any]:
        return {
            "order_id": self.order_id,
            "success": self.success,
            "result": self.result,
            "error": self.error,
            "stage": self.stage,
        }


class Pipeline:
    """
    Governed execution pipeline.

    Parameters
    ----------
    policy_engine : PolicyEngine
        Pre- and post-policy rules to enforce.
    executor : ALGAExecutor
        ALGA execution engine.
    ledger : Ledger
        Governance ledger to record events into.
    """

    def __init__(
        self,
        policy_engine: PolicyEngine,
        executor: ALGAExecutor,
        ledger: Ledger,
    ) -> None:
        self._policy = policy_engine
        self._executor = executor
        self._ledger = ledger

    # ------------------------------------------------------------------ #
    # public API                                                           #
    # ------------------------------------------------------------------ #

    def run(self, order: WorkOrder) -> PipelineResult:
        """
        Execute *order* through the full governed pipeline.

        Always returns a PipelineResult — never raises.
        """
        oid = order.id
        logger.info("Pipeline START  order=%s action=%s", oid, order.action)

        # 1 — Schema validation
        try:
            validate_work_order(order)
            self._ledger.record(oid, EventType.SCHEMA_PASS)
        except SchemaValidationError as exc:
            self._ledger.record(oid, EventType.SCHEMA_FAIL, {"error": str(exc)})
            self._ledger.record(oid, EventType.PIPELINE_ABORTED, {"stage": "schema"})
            logger.warning("Pipeline ABORTED (schema) order=%s: %s", oid, exc)
            return PipelineResult(oid, success=False, error=str(exc), stage="schema")

        # 2 — Pre-policy gate
        try:
            self._policy.enforce_pre(order)
            self._ledger.record(oid, EventType.PRE_POLICY_ALLOW)
        except PolicyViolationError as exc:
            self._ledger.record(
                oid, EventType.PRE_POLICY_DENY, {"reason": exc.reason}
            )
            self._ledger.record(
                oid, EventType.PIPELINE_ABORTED, {"stage": "pre_policy"}
            )
            logger.warning("Pipeline ABORTED (pre_policy) order=%s: %s", oid, exc)
            return PipelineResult(
                oid, success=False, error=str(exc), stage="pre_policy"
            )

        # 3 — Execution
        self._ledger.record(oid, EventType.EXECUTION_START)
        result = self._executor.execute(order)
        self._ledger.record(oid, EventType.EXECUTION_COMPLETE, {"result": result})

        # 4 — Post-policy gate
        try:
            self._policy.enforce_post(order, result)
            self._ledger.record(oid, EventType.POST_POLICY_ALLOW)
        except PolicyViolationError as exc:
            self._ledger.record(
                oid, EventType.POST_POLICY_DENY, {"reason": exc.reason}
            )
            self._ledger.record(
                oid, EventType.PIPELINE_ABORTED, {"stage": "post_policy"}
            )
            logger.warning("Pipeline ABORTED (post_policy) order=%s: %s", oid, exc)
            return PipelineResult(
                oid, success=False, error=str(exc), stage="post_policy"
            )

        # 5 — Complete
        self._ledger.record(oid, EventType.PIPELINE_COMPLETE)
        logger.info("Pipeline COMPLETE order=%s", oid)
        return PipelineResult(oid, success=True, result=result)
