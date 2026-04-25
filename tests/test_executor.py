"""
Tests for ALGA executor edge and fallback behaviors.
"""

from alga import ALGAExecutor
from wosds.schema import WorkOrder


def _order(action: str, payload: dict | None = None) -> WorkOrder:
    return WorkOrder.new(action=action, payload=payload if payload is not None else {"k": 1})


class TestALGAExecutor:
    def test_unknown_action_uses_default_handler(self):
        executor = ALGAExecutor()
        result = executor.execute(_order("unregistered_action"))

        assert result["status"] == "unsupported"
        assert result["action"] == "unregistered_action"
        assert "No handler registered" in result["message"]

    def test_compute_unknown_op_returns_error(self):
        executor = ALGAExecutor()
        result = executor.execute(_order("compute", {"a": 1, "b": 2, "op": "div"}))

        assert result["status"] == "error"
        assert "unknown op 'div'" in result["error"]
