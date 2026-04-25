"""
Tests for the Governance Ledger.
"""

from governance.ledger import EventType, Ledger


class TestLedger:
    def setup_method(self):
        self.ledger = Ledger()

    def test_record_and_retrieve(self):
        self.ledger.record("order-1", EventType.SCHEMA_PASS)
        entries = self.ledger.for_order("order-1")
        assert len(entries) == 1
        assert entries[0].event is EventType.SCHEMA_PASS

    def test_multiple_events_same_order(self):
        for event in [
            EventType.SCHEMA_PASS,
            EventType.PRE_POLICY_ALLOW,
            EventType.EXECUTION_START,
            EventType.EXECUTION_COMPLETE,
            EventType.POST_POLICY_ALLOW,
            EventType.PIPELINE_COMPLETE,
        ]:
            self.ledger.record("order-2", event)
        entries = self.ledger.for_order("order-2")
        assert len(entries) == 6
        assert entries[-1].event is EventType.PIPELINE_COMPLETE

    def test_isolation_between_orders(self):
        self.ledger.record("order-A", EventType.SCHEMA_PASS)
        self.ledger.record("order-B", EventType.SCHEMA_FAIL)
        assert len(self.ledger.for_order("order-A")) == 1
        assert len(self.ledger.for_order("order-B")) == 1

    def test_as_log_is_serialisable(self):
        self.ledger.record("order-X", EventType.PIPELINE_COMPLETE, {"key": "val"})
        log = self.ledger.as_log()
        assert isinstance(log, list)
        entry = log[0]
        assert entry["event"] == "PIPELINE_COMPLETE"
        assert entry["details"] == {"key": "val"}
        assert "timestamp" in entry

    def test_len(self):
        assert len(self.ledger) == 0
        self.ledger.record("o", EventType.SCHEMA_PASS)
        assert len(self.ledger) == 1
