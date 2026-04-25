"""
ALGA Engine — execution layer entry point for the ZQ-AIOS control plane.

This module re-exports :class:`~alga.executor.ALGAExecutor` under the
``alga.engine`` path so that the control plane can import the executor from
a stable, semantically named location.

The ALGA (Adaptive Learning Governance Algorithm) executor receives a
schema-validated, pre-policy-approved WorkOrder and produces a result dict.
"""

from __future__ import annotations

from alga.executor import ALGAExecutor

__all__ = ["ALGAExecutor"]
