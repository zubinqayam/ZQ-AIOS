"""
Core — Governed Execution Pipeline and Control Plane.

Assembles WOSDS schema validation, dual-gate policy enforcement, ALGA
execution, and governance ledger recording into a single pipeline.

Also exposes the EventBus (queue-based processing with DLQ + retry),
schema enforcement helpers, and the high-level System orchestrator.
"""

from .event_bus import EventBus, EventEnvelope
from .pipeline import Pipeline, PipelineResult
from .schemas import SchemaValidationError, WorkOrder, enforce
from .system import System

__all__ = [
    "EventBus",
    "EventEnvelope",
    "Pipeline",
    "PipelineResult",
    "SchemaValidationError",
    "WorkOrder",
    "enforce",
    "System",
]
