"""
ALGA — Adaptive Learning Governance Algorithm.

Responsible for the *execution* step inside the control plane.
ALGA receives a validated, pre-policy-approved WorkOrder and produces a
result dict.  It also maintains a short in-memory execution history that
can be used by governance and replay subsystems.
"""

from .executor import ALGAExecutor

__all__ = ["ALGAExecutor"]
