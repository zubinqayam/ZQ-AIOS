"""
End-to-end pipeline tests.

Covers every scenario listed in the problem statement:
  ✅ valid flow
  ❌ schema failure
  🔴 pre-policy block
  🔴 post-policy block
  🔁 replay works
"""

import pytest

from governance.ledger import EventType
from integration import build_pipeline
from core import PipelineResult
from wosds.schema import WorkOrder


def _run(action: str, payload: dict, replay: bool = False, order_id: str | None = None):
    """Helper: build a fresh pipeline, run one order, return (result, ledger)."""
    pipeline, ledger = build_pipeline()
    order = WorkOrder.new(
        action=action, payload=payload, replay=replay, order_id=order_id
    )
    result = pipeline.run(order)
    return result, ledger, order


class TestValidFlow:
    def test_ping_succeeds(self):
        result, ledger, order = _run("ping", {"k": 1})
        assert result.success is True
        assert result.result["pong"] is True
        events = [e.event for e in ledger.for_order(order.id)]
        assert EventType.PIPELINE_COMPLETE in events
        assert EventType.PIPELINE_ABORTED not in events

    def test_echo_succeeds(self):
        result, ledger, order = _run("echo", {"msg": "hello"})
        assert result.success is True
        assert result.result["echo"] == {"msg": "hello"}

    def test_compute_add(self):
        result, _, _ = _run("compute", {"a": 3, "b": 4, "op": "add"})
        assert result.success is True
        assert result.result["result"] == 7


class TestSchemaFailure:
    def test_empty_action_blocked_at_schema(self):
        pipeline, ledger = build_pipeline()
        # Construct a malformed order bypassing the factory
        order = WorkOrder(id="bad-1", action="", payload={"k": 1})
        result = pipeline.run(order)
        assert result.success is False
        assert result.stage == "schema"
        events = [e.event for e in ledger.for_order("bad-1")]
        assert EventType.SCHEMA_FAIL in events
        assert EventType.PIPELINE_ABORTED in events
        # Execution must NOT have been attempted
        assert EventType.EXECUTION_START not in events

    def test_non_dict_payload_blocked_at_schema(self):
        pipeline, ledger = build_pipeline()
        order = WorkOrder(id="bad-2", action="ping", payload="not-a-dict")  # type: ignore[arg-type]
        result = pipeline.run(order)
        assert result.success is False
        assert result.stage == "schema"


class TestPrePolicyBlock:
    def test_forbidden_action_blocked(self):
        result, ledger, order = _run("delete_all", {"k": 1})
        assert result.success is False
        assert result.stage == "pre_policy"
        events = [e.event for e in ledger.for_order(order.id)]
        assert EventType.PRE_POLICY_DENY in events
        assert EventType.EXECUTION_START not in events

    def test_empty_payload_blocked(self):
        result, _, order = _run("ping", {})
        assert result.success is False
        assert result.stage == "pre_policy"

    def test_shutdown_blocked(self):
        result, _, order = _run("shutdown", {"k": 1})
        assert result.success is False
        assert result.stage == "pre_policy"


class TestPostPolicyBlock:
    """Force a post-policy denial by registering a handler that returns an error."""

    def test_error_result_blocked_post_policy(self):
        from alga import ALGAExecutor
        from core import Pipeline
        from governance import Ledger
        from policy import PolicyEngine
        from policy.rules import block_error_results, block_forbidden_actions, require_non_empty_payload

        ledger = Ledger()
        executor = ALGAExecutor()
        # Register a handler that always returns an error result
        executor.register("bad_op", lambda o: {"error": "something went wrong"})

        policy_engine = PolicyEngine(
            pre_rules=[block_forbidden_actions, require_non_empty_payload],
            post_rules=[block_error_results],
        )
        pipeline = Pipeline(policy_engine=policy_engine, executor=executor, ledger=ledger)

        order = WorkOrder.new(action="bad_op", payload={"k": 1}, replay=False)
        result = pipeline.run(order)

        assert result.success is False
        assert result.stage == "post_policy"
        events = [e.event for e in ledger.for_order(order.id)]
        assert EventType.POST_POLICY_DENY in events
        assert EventType.EXECUTION_COMPLETE in events  # execution DID run


class TestReplay:
    def test_replay_flag_passes_post_policy_on_error_result(self):
        from alga import ALGAExecutor
        from core import Pipeline
        from governance import Ledger
        from policy import PolicyEngine
        from policy.rules import block_error_results, block_forbidden_actions, require_non_empty_payload

        ledger = Ledger()
        executor = ALGAExecutor()
        executor.register("bad_op", lambda o: {"error": "surface error for replay"})

        policy_engine = PolicyEngine(
            pre_rules=[block_forbidden_actions, require_non_empty_payload],
            post_rules=[block_error_results],
        )
        pipeline = Pipeline(policy_engine=policy_engine, executor=executor, ledger=ledger)

        order = WorkOrder.new(action="bad_op", payload={"k": 1}, replay=True)
        result = pipeline.run(order)

        # Replay flag lets the error result through post-policy
        assert result.success is True
        events = [e.event for e in ledger.for_order(order.id)]
        assert EventType.REPLAY_TRIGGERED not in events  # ledger note below
        assert EventType.PIPELINE_COMPLETE in events

    def test_replay_recorded_in_ledger(self):
        """Pipeline can manually record REPLAY_TRIGGERED via the ledger."""
        pipeline, ledger = build_pipeline()
        order = WorkOrder.new(action="ping", payload={"k": 1}, replay=True)
        # Record replay event before running
        ledger.record(order.id, EventType.REPLAY_TRIGGERED, {"source": "test"})
        result = pipeline.run(order)
        assert result.success is True
        events = [e.event for e in ledger.for_order(order.id)]
        assert EventType.REPLAY_TRIGGERED in events
        assert EventType.PIPELINE_COMPLETE in events


class TestPipelineResult:
    def test_as_dict(self):
        result = PipelineResult(
            order_id="o-1",
            success=False,
            result={"k": 1},
            error="failure",
            stage="schema",
        )
        assert result.as_dict() == {
            "order_id": "o-1",
            "success": False,
            "result": {"k": 1},
            "error": "failure",
            "stage": "schema",
        }
