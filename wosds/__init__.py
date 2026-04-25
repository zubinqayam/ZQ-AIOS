"""
WOSDS — Work Order Schema & Dispatch System

Validates incoming work-order payloads against the canonical schema
before any execution or policy evaluation occurs.
"""

from .schema import WorkOrder, validate_work_order

__all__ = ["WorkOrder", "validate_work_order"]
