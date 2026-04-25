"""
Tests for WOSDS schema validation.
"""

import pytest

from wosds.schema import SchemaValidationError, WorkOrder, validate_work_order


class TestWorkOrderFactory:
    def test_new_creates_valid_order(self):
        order = WorkOrder.new(action="ping", payload={"key": "value"})
        assert order.action == "ping"
        assert order.payload == {"key": "value"}
        assert isinstance(order.id, str) and order.id
        assert order.replay is False
        assert order.metadata == {}

    def test_new_accepts_custom_id(self):
        order = WorkOrder.new(action="ping", payload={"k": 1}, order_id="abc-123")
        assert order.id == "abc-123"

    def test_new_replay_flag(self):
        order = WorkOrder.new(action="echo", payload={"x": 1}, replay=True)
        assert order.replay is True


class TestSchemaValidation:
    def test_valid_order_passes(self):
        order = WorkOrder.new(action="echo", payload={"msg": "hello"})
        validate_work_order(order)  # must not raise

    def test_empty_id_fails(self):
        order = WorkOrder(id="", action="ping", payload={"a": 1})
        with pytest.raises(SchemaValidationError, match="'id'"):
            validate_work_order(order)

    def test_empty_action_fails(self):
        order = WorkOrder(id="x", action="  ", payload={"a": 1})
        with pytest.raises(SchemaValidationError, match="'action'"):
            validate_work_order(order)

    def test_non_dict_payload_fails(self):
        order = WorkOrder(id="x", action="ping", payload="bad")  # type: ignore[arg-type]
        with pytest.raises(SchemaValidationError, match="'payload'"):
            validate_work_order(order)

    def test_non_dict_metadata_fails(self):
        order = WorkOrder(id="x", action="ping", payload={}, metadata="bad")  # type: ignore[arg-type]
        with pytest.raises(SchemaValidationError, match="'metadata'"):
            validate_work_order(order)

    def test_non_bool_replay_fails(self):
        order = WorkOrder(id="x", action="ping", payload={"k": 1}, replay="yes")  # type: ignore[arg-type]
        with pytest.raises(SchemaValidationError, match="'replay'"):
            validate_work_order(order)
