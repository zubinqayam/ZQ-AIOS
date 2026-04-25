"""
System Orchestrator — high-level entry point for the ZQ-AIOS control plane.

This module assembles and exposes the complete governed processing system:

    Event → Schema → Policy (PRE) → ALGA → Policy (POST) → Ledger

It wires together the EventBus, Pipeline, and governance Ledger so that
callers only need to instantiate a :class:`System` and call
:meth:`System.process`.

Usage::

    system = System()
    system.process(order)

    # Or submit many and process in bulk:
    system.submit(order_1)
    system.submit(order_2)
    results = system.drain()
"""

from __future__ import annotations

import logging
from typing import Any

from core.event_bus import EventBus, EventEnvelope
from core.pipeline import Pipeline, PipelineResult
from governance import Ledger
from integration.factory import build_pipeline

logger = logging.getLogger(__name__)


class System:
    """
    High-level system orchestrator for the ZQ-AIOS control plane.

    Wraps an EventBus (which wraps a Pipeline) so that the caller only
    needs to deal with WorkOrders and PipelineResults.

    Parameters
    ----------
    ledger :
        Shared ledger; a fresh one is created when *None* is given.
    max_retries :
        Retry budget for transient failures before an order is sent to
        the Dead Letter Queue.
    """

    def __init__(
        self,
        ledger: Ledger | None = None,
        max_retries: int = 3,
    ) -> None:
        self._pipeline, self._ledger = build_pipeline(ledger)
        self._bus = EventBus(self._pipeline, max_retries=max_retries)
        logger.info("System initialised (max_retries=%d)", max_retries)

    # ------------------------------------------------------------------ #
    # public API                                                           #
    # ------------------------------------------------------------------ #

    @property
    def ledger(self) -> Ledger:
        """The governance ledger shared across all pipeline runs."""
        return self._ledger

    @property
    def pipeline(self) -> Pipeline:
        """The underlying governed pipeline."""
        return self._pipeline

    @property
    def bus(self) -> EventBus:
        """The underlying event bus."""
        return self._bus

    def submit(self, order: Any) -> None:
        """Enqueue *order* for governed processing."""
        self._bus.submit(order)

    def process(self, order: Any) -> PipelineResult:
        """
        Submit *order* and process it immediately.

        This is a convenience wrapper for single-order scenarios.
        """
        self._bus.submit(order)
        result = self._bus.process_next()
        # process_next is guaranteed to return a result here because we
        # just submitted exactly one order.
        assert result is not None, (
            "process_next returned None immediately after submitting one order — "
            "this indicates an internal EventBus consistency error."
        )
        return result

    def drain(self) -> list[PipelineResult]:
        """Process all enqueued orders and return the results."""
        return self._bus.process_all()

    def dlq(self) -> list[EventEnvelope]:
        """Return the Dead Letter Queue snapshot."""
        return self._bus.dlq()

    def summary(self) -> dict[str, Any]:
        """Return a brief operational summary of the system."""
        return {
            "queue_size": self._bus.queue_size(),
            "dlq_size": self._bus.dlq_size(),
            "ledger_entries": len(self._ledger),
        }
