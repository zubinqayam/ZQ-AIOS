"""
Integration — factory helpers.

Provides a ready-to-use Pipeline pre-wired with the default rule sets
and a shared Ledger instance.  Import `build_pipeline` to get started
without assembling every component manually.
"""

from .factory import build_pipeline

__all__ = ["build_pipeline"]
