"""
Tests for demonstration entrypoint scenarios.
"""

from __future__ import annotations

import main as demo_main


class TestMainScenarios:
    def test_all_scenarios_return_expected_pass_booleans(self):
        assert demo_main.scenario_1_valid_flow() is True
        assert demo_main.scenario_2_schema_failure() is True
        assert demo_main.scenario_3_pre_policy_block() is True
        assert demo_main.scenario_4_post_policy_block() is True
        assert demo_main.scenario_5_replay() is True

    def test_main_returns_nonzero_when_any_scenario_fails(self, monkeypatch):
        monkeypatch.setattr(demo_main, "scenario_1_valid_flow", lambda: True)
        monkeypatch.setattr(demo_main, "scenario_2_schema_failure", lambda: True)
        monkeypatch.setattr(demo_main, "scenario_3_pre_policy_block", lambda: False)
        monkeypatch.setattr(demo_main, "scenario_4_post_policy_block", lambda: True)
        monkeypatch.setattr(demo_main, "scenario_5_replay", lambda: True)

        assert demo_main.main() == 1
