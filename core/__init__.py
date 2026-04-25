"""
Core — Governed Execution Pipeline.

Assembles WOSDS schema validation, dual-gate policy enforcement, ALGA
execution, and governance ledger recording into a single pipeline.
"""

from .pipeline import Pipeline, PipelineResult

__all__ = ["Pipeline", "PipelineResult"]
