"""
Event Bus — queue-based event processing with Dead Letter Queue (DLQ) and retry.

Processing flow for each submitted WorkOrder:
    submit(order) → schema validation → pre-policy gate → ALGA execution
                  → post-policy gate → ledger recording

Retry & DLQ behaviour
---------------------
* Schema failures and pre-policy denials are permanent — the order is moved
  to the DLQ immediately without retrying (retrying would produce the same
  outcome).
* All other failures (post-policy, execution errors) are retried up to
  ``max_retries`` times before being moved to the DLQ.

Usage::

    bus = EventBus(pipeline, max_retries=3)
    bus.submit(order)
    results = bus.process_all()
    failed = bus.dlq()
"""

from __future__ import annotations

import logging
import queue
from dataclasses import dataclass, field
from typing import Any

from core.pipeline import Pipeline, PipelineResult
from wosds.schema import WorkOrder

logger = logging.getLogger(__name__)

# Stages that are permanent failures — no retry benefit.
_PERMANENT_FAILURE_STAGES = frozenset({"schema", "pre_policy"})


@dataclass
class EventEnvelope:
    """Wraps a WorkOrder for queue-based processing."""

    order: WorkOrder
    attempt: int = 0
    last_error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class EventBus:
    """
    Queue-backed event bus that drives work orders through the governed pipeline.

    Parameters
    ----------
    pipeline :
        The governed execution pipeline to dispatch orders through.
    max_retries :
        Maximum number of processing attempts before an order is sent to the
        Dead Letter Queue.  Default is 3.
    """

    def __init__(self, pipeline: Pipeline, max_retries: int = 3) -> None:
        self._pipeline = pipeline
        self._max_retries = max_retries
        self._queue: queue.Queue[EventEnvelope] = queue.Queue()
        self._dlq: list[EventEnvelope] = []

    # ------------------------------------------------------------------ #
    # public API                                                           #
    # ------------------------------------------------------------------ #

    def submit(self, order: WorkOrder) -> None:
        """Enqueue *order* for governed processing."""
        logger.debug("EventBus: enqueued order=%s action=%s", order.id, order.action)
        self._queue.put(EventEnvelope(order=order))

    def process_next(self) -> PipelineResult | None:
        """
        Dequeue and process the next event.

        Returns ``None`` when the queue is empty.
        """
        try:
            envelope = self._queue.get_nowait()
        except queue.Empty:
            return None
        return self._dispatch(envelope)

    def process_all(self) -> list[PipelineResult]:
        """Drain the queue, processing every pending event. Returns all results."""
        results: list[PipelineResult] = []
        while not self._queue.empty():
            result = self.process_next()
            if result is not None:
                results.append(result)
        return results

    def dlq(self) -> list[EventEnvelope]:
        """Return a snapshot of the Dead Letter Queue."""
        return list(self._dlq)

    def dlq_size(self) -> int:
        """Return the number of events currently in the DLQ."""
        return len(self._dlq)

    def queue_size(self) -> int:
        """Return the number of events currently in the main queue."""
        return self._queue.qsize()

    # ------------------------------------------------------------------ #
    # internal                                                             #
    # ------------------------------------------------------------------ #

    def _dispatch(self, envelope: EventEnvelope) -> PipelineResult:
        """Run one processing attempt for *envelope*."""
        envelope.attempt += 1
        order = envelope.order

        logger.debug(
            "EventBus: processing order=%s attempt=%d/%d",
            order.id,
            envelope.attempt,
            self._max_retries,
        )

        result = self._pipeline.run(order)

        if result.success:
            logger.debug("EventBus: order=%s succeeded", order.id)
            return result

        # Failure path — decide retry vs DLQ.
        envelope.last_error = result.error

        if result.stage in _PERMANENT_FAILURE_STAGES:
            # Permanent failure — no retry benefit.
            logger.warning(
                "EventBus: DLQ (permanent failure stage=%s) order=%s: %s",
                result.stage,
                order.id,
                result.error,
            )
            self._dlq.append(envelope)
            return result

        if envelope.attempt < self._max_retries:
            logger.warning(
                "EventBus: retry %d/%d for order=%s: %s",
                envelope.attempt,
                self._max_retries,
                order.id,
                result.error,
            )
            self._queue.put(envelope)
            return result

        # Exhausted retries.
        logger.error(
            "EventBus: DLQ (retries exhausted after %d attempts) order=%s: %s",
            envelope.attempt,
            order.id,
            result.error,
        )
        self._dlq.append(envelope)
        return result
