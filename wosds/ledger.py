"""
WOSDS File-backed Ledger — append-only JSONL persistence.

LEDGER_FILE is the canonical path where every LedgerEntry is flushed as a
JSON line after it is recorded in memory.

Survivability fixes
-------------------
Fix 1 — directory creation:
    The ``wosds/`` directory is created on first use if it does not exist,
    preventing a ``FileNotFoundError`` on fresh checkouts and CI runners.

Fix 2 — missing-file replay:
    ``replay()`` returns an empty list when the ledger file has not yet been
    created, rather than raising ``FileNotFoundError``.
"""

from __future__ import annotations

import json
import os
from typing import Any

LEDGER_FILE: str = "wosds/ledger.jsonl"


def _ensure_dir() -> None:
    """Create the directory that contains LEDGER_FILE if it does not exist."""
    directory = os.path.dirname(LEDGER_FILE)
    if directory:
        os.makedirs(directory, exist_ok=True)


def append(entry: dict[str, Any]) -> None:
    """
    Append *entry* as a JSON line to LEDGER_FILE.

    The directory is created automatically on first call (Fix 1).
    """
    _ensure_dir()
    with open(LEDGER_FILE, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, default=str) + "\n")


def replay() -> list[dict[str, Any]]:
    """
    Read all entries from LEDGER_FILE and return them as a list of dicts.

    Returns an empty list if the file does not yet exist (Fix 2),
    rather than raising ``FileNotFoundError``.
    """
    if not os.path.exists(LEDGER_FILE):
        return []

    entries: list[dict[str, Any]] = []
    with open(LEDGER_FILE, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries
