"""
Tests for file-backed WOSDS ledger helpers.
"""

from __future__ import annotations

import json

import wosds.ledger as file_ledger


class TestWOSDSFileLedger:
    def test_append_creates_directory_and_file_and_replay_reads_back(
        self, tmp_path, monkeypatch
    ):
        ledger_path = tmp_path / "nested" / "ledger.jsonl"
        monkeypatch.setattr(file_ledger, "LEDGER_FILE", str(ledger_path))

        entry = {"event": "SCHEMA_PASS", "details": {"k": 1}}
        file_ledger.append(entry)

        assert ledger_path.exists()
        assert file_ledger.replay() == [entry]

    def test_replay_returns_empty_when_missing_file(self, tmp_path, monkeypatch):
        missing_path = tmp_path / "nope" / "ledger.jsonl"
        monkeypatch.setattr(file_ledger, "LEDGER_FILE", str(missing_path))

        assert file_ledger.replay() == []

    def test_replay_skips_blank_lines(self, tmp_path, monkeypatch):
        ledger_path = tmp_path / "ledger.jsonl"
        monkeypatch.setattr(file_ledger, "LEDGER_FILE", str(ledger_path))
        ledger_path.write_text(
            json.dumps({"event": "A"}) + "\n\n" + json.dumps({"event": "B"}) + "\n",
            encoding="utf-8",
        )

        assert file_ledger.replay() == [{"event": "A"}, {"event": "B"}]
