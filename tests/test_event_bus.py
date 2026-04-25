"""
Tests for core.event_bus — queue-based event processing with DLQ and retry.

Validation checklist covered:
  ✅ Valid event processed successfully
  ❌ Invalid event rejected (schema failure → immediate DLQ)
  ☠️  Failed events go to DLQ after max retries
  🔴  Permanent failures (policy) → immediate DLQ without retry
"""

from __future__ import annotations

import pytest

from alga import ALGAExecutor
from core.event_bus import EventBus, EventEnvelope
from core import Pipeline
from governance import Ledger
from integration import build_pipeline
from policy import PolicyEngine
from policy.rules import block_error_results, block_forbidden_actions, require_non_empty_payload
from wosds.schema import WorkOrder


def _make_bus(max_retries: int = 3) -> tuple[EventBus, Ledger]:
    """Return a fresh (EventBus, Ledger) pair wired with default rules."""
    pipeline, ledger = build_pipeline()
    bus = EventBus(pipeline, max_retries=max_retries)
    return bus, ledger


class TestEventBusValidFlow:
    def test_valid_order_is_processed_successfully(self):
        bus, _ = _make_bus()
        order = WorkOrder.new(action="ping", payload={"k": 1})
        bus.submit(order)
        results = bus.process_all()

        assert len(results) == 1
        assert results[0].success is True

    def test_queue_is_empty_after_process_all(self):
        bus, _ = _make_bus()
        bus.submit(WorkOrder.new(action="ping", payload={"k": 1}))
        bus.submit(WorkOrder.new(action="echo", payload={"msg": "hi"}))
        bus.process_all()

        assert bus.queue_size() == 0

    def test_multiple_valid_orders_all_succeed(self):
        bus, _ = _make_bus()
        for _ in range(5):
            bus.submit(WorkOrder.new(action="ping", payload={"k": 1}))
        results = bus.process_all()

        assert len(results) == 5
        assert all(r.success for r in results)

    def test_process_next_returns_none_when_empty(self):
        bus, _ = _make_bus()
        assert bus.process_next() is None

    def test_process_next_processes_one_at_a_time(self):
        bus, _ = _make_bus()
        bus.submit(WorkOrder.new(action="ping", payload={"k": 1}))
        bus.submit(WorkOrder.new(action="ping", payload={"k": 2}))

        result = bus.process_next()
        assert result is not None
        assert bus.queue_size() == 1


class TestEventBusSchemaRejection:
    def test_schema_failure_goes_to_dlq_immediately(self):
        bus, _ = _make_bus(max_retries=3)
        # Empty action triggers SchemaValidationError
        order = WorkOrder(id="bad-schema", action="", payload={"k": 1})
        bus.submit(order)
        results = bus.process_all()

        # DLQ must contain the failed envelope
        assert bus.dlq_size() == 1
        dlq_envelope = bus.dlq()[0]
        assert dlq_envelope.order.id == "bad-schema"

    def test_schema_failure_does_not_retry(self):
        """Schema failures are permanent — only one processing attempt expected."""
        bus, _ = _make_bus(max_retries=3)
        order = WorkOrder(id="no-retry", action="", payload={"k": 1})
        bus.submit(order)
        bus.process_all()

        # Only one attempt — no retry for schema failures
        assert bus.dlq()[0].attempt == 1


class TestEventBusDLQ:
    def test_transient_failures_retry_then_go_to_dlq(self):
        """Post-policy failures exhaust retries and land in the DLQ."""
        ledger = Ledger()
        executor = ALGAExecutor()
        executor.register("bad_op", lambda o: {"error": "execution error"})
        policy_engine = PolicyEngine(
            pre_rules=[block_forbidden_actions, require_non_empty_payload],
            post_rules=[block_error_results],
        )
        pipeline = Pipeline(policy_engine=policy_engine, executor=executor, ledger=ledger)

        bus = EventBus(pipeline, max_retries=2)
        order = WorkOrder.new(action="bad_op", payload={"k": 1}, replay=False)
        bus.submit(order)

        # Drain: process_all keeps processing retries until the queue is empty
        results = bus.process_all()

        # All results (including retry results) are collected
        assert len(results) == 2  # 2 attempts (max_retries=2)
        assert bus.dlq_size() == 1

    def test_dlq_snapshot_returns_copy(self):
        bus, _ = _make_bus()
        order = WorkOrder(id="dlq-copy-test", action="", payload={})
        bus.submit(order)
        bus.process_all()

        snapshot = bus.dlq()
        snapshot.clear()
        # Original DLQ must be unaffected
        assert bus.dlq_size() == 1

    def test_pre_policy_failure_goes_to_dlq_immediately(self):
        """Pre-policy denials are permanent — no retry."""
        bus, _ = _make_bus(max_retries=3)
        order = WorkOrder.new(action="delete_all", payload={"k": 1})
        bus.submit(order)
        bus.process_all()

        assert bus.dlq_size() == 1
        assert bus.dlq()[0].attempt == 1

    def test_dlq_size_reflects_failed_events(self):
        bus, _ = _make_bus()
        # Submit 3 schema-invalid orders
        for i in range(3):
            bus.submit(WorkOrder(id=f"bad-{i}", action="", payload={"k": i}))
        bus.process_all()

        assert bus.dlq_size() == 3


class TestEventBusEventEnvelope:
    def test_envelope_tracks_last_error(self):
        ledger = Ledger()
        executor = ALGAExecutor()
        executor.register("fail_op", lambda o: {"error": "deliberate"})
        policy_engine = PolicyEngine(
            pre_rules=[require_non_empty_payload],
            post_rules=[block_error_results],
        )
        pipeline = Pipeline(policy_engine=policy_engine, executor=executor, ledger=ledger)
        bus = EventBus(pipeline, max_retries=1)

        order = WorkOrder.new(action="fail_op", payload={"k": 1}, replay=False)
        bus.submit(order)
        bus.process_all()

        envelope = bus.dlq()[0]
        assert envelope.last_error is not None
