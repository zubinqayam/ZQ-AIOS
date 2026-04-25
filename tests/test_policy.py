"""
Tests for the Policy Engine and built-in rules.
"""

import pytest

from policy import PolicyDecision, PolicyEngine, PolicyViolationError
from policy.rules import (
    block_error_results,
    block_forbidden_actions,
    require_non_empty_payload,
)
from wosds.schema import WorkOrder


def _order(action: str = "ping", payload: dict | None = None, replay: bool = False):
    return WorkOrder.new(action=action, payload=payload if payload is not None else {"k": 1}, replay=replay)


class TestBuiltInPreRules:
    def test_allow_normal_action(self):
        decision, _ = block_forbidden_actions(_order("ping"))
        assert decision is PolicyDecision.ALLOW

    def test_deny_forbidden_action(self):
        decision, reason = block_forbidden_actions(_order("delete_all"))
        assert decision is PolicyDecision.DENY
        assert "forbidden" in reason

    def test_allow_non_empty_payload(self):
        decision, _ = require_non_empty_payload(_order(payload={"k": 1}))
        assert decision is PolicyDecision.ALLOW

    def test_deny_empty_payload(self):
        decision, reason = require_non_empty_payload(_order(payload={}))
        assert decision is PolicyDecision.DENY
        assert "empty" in reason


class TestBuiltInPostRules:
    def test_allow_ok_result(self):
        order = _order()
        decision, _ = block_error_results(order, result={"status": "ok"})
        assert decision is PolicyDecision.ALLOW

    def test_deny_error_result_non_replay(self):
        order = _order(replay=False)
        decision, reason = block_error_results(order, result={"error": "oops"})
        assert decision is PolicyDecision.DENY
        assert "error" in reason

    def test_allow_error_result_when_replay(self):
        order = _order(replay=True)
        decision, _ = block_error_results(order, result={"error": "oops"})
        assert decision is PolicyDecision.ALLOW


class TestPolicyEngine:
    def test_pre_policy_passes(self):
        engine = PolicyEngine(pre_rules=[block_forbidden_actions])
        engine.enforce_pre(_order("ping"))  # must not raise

    def test_pre_policy_blocks(self):
        engine = PolicyEngine(pre_rules=[block_forbidden_actions])
        with pytest.raises(PolicyViolationError) as exc_info:
            engine.enforce_pre(_order("shutdown"))
        assert exc_info.value.gate == "PRE_POLICY"

    def test_post_policy_passes(self):
        engine = PolicyEngine(post_rules=[block_error_results])
        engine.enforce_post(_order(), {"status": "ok"})  # must not raise

    def test_post_policy_blocks(self):
        engine = PolicyEngine(post_rules=[block_error_results])
        with pytest.raises(PolicyViolationError) as exc_info:
            engine.enforce_post(_order(replay=False), {"error": "bad"})
        assert exc_info.value.gate == "POST_POLICY"
