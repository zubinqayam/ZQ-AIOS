"""
ZQ-AIOS Phase 5 — Control Plane
================================

Demonstration entry point.  Runs five representative scenarios through
the governed execution pipeline and prints a structured summary.

Scenarios
---------
  1. ✅ Valid flow            — ping action succeeds end-to-end
  2. ❌ Schema failure        — malformed work order rejected at schema gate
  3. 🔴 Pre-policy block      — forbidden action blocked before execution
  4. 🔴 Post-policy block     — execution result rejected after execution
  5. 🔁 Replay works          — error result accepted when replay=True
"""

from __future__ import annotations

import json
import logging
import sys

from alga import ALGAExecutor
from core import Pipeline
from governance import EventType, Ledger
from integration import build_pipeline
from policy import PolicyEngine
from policy.rules import block_error_results, block_forbidden_actions, require_non_empty_payload
from wosds.schema import WorkOrder

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("main")

SEPARATOR = "─" * 60


def _print_result(label: str, result, ledger: Ledger) -> None:
    status = "✅ PASS" if result.success else f"❌ FAIL (stage={result.stage})"
    print(f"\n{SEPARATOR}")
    print(f"  {label}")
    print(f"  Status : {status}")
    if result.result:
        print(f"  Result : {json.dumps(result.result)}")
    if result.error:
        print(f"  Error  : {result.error}")
    entries = ledger.for_order(result.order_id)
    print(f"  Ledger : {[e.event.value for e in entries]}")
    print(SEPARATOR)


def scenario_1_valid_flow() -> bool:
    print("\n🔹 Scenario 1 — Valid flow (ping)")
    pipeline, ledger = build_pipeline()
    order = WorkOrder.new(action="ping", payload={"source": "main.py"})
    result = pipeline.run(order)
    _print_result("Scenario 1 — Valid flow", result, ledger)
    return result.success


def scenario_2_schema_failure() -> bool:
    print("\n🔹 Scenario 2 — Schema failure (empty action)")
    pipeline, ledger = build_pipeline()
    order = WorkOrder(id="schema-fail-demo", action="", payload={"k": 1})
    result = pipeline.run(order)
    _print_result("Scenario 2 — Schema failure", result, ledger)
    return not result.success  # expected failure → test passes when success=False


def scenario_3_pre_policy_block() -> bool:
    print("\n🔹 Scenario 3 — Pre-policy block (delete_all)")
    pipeline, ledger = build_pipeline()
    order = WorkOrder.new(action="delete_all", payload={"target": "everything"})
    result = pipeline.run(order)
    _print_result("Scenario 3 — Pre-policy block", result, ledger)
    return not result.success


def scenario_4_post_policy_block() -> bool:
    print("\n🔹 Scenario 4 — Post-policy block (bad_op returns error)")
    ledger = Ledger()
    executor = ALGAExecutor()
    executor.register("bad_op", lambda o: {"error": "simulated execution error"})
    policy_engine = PolicyEngine(
        pre_rules=[block_forbidden_actions, require_non_empty_payload],
        post_rules=[block_error_results],
    )
    pipeline = Pipeline(policy_engine=policy_engine, executor=executor, ledger=ledger)

    order = WorkOrder.new(action="bad_op", payload={"trigger": "error"}, replay=False)
    result = pipeline.run(order)
    _print_result("Scenario 4 — Post-policy block", result, ledger)
    return not result.success


def scenario_5_replay() -> bool:
    print("\n🔹 Scenario 5 — Replay works (error result allowed with replay=True)")
    ledger = Ledger()
    executor = ALGAExecutor()
    executor.register("bad_op", lambda o: {"error": "surface error for replay"})
    policy_engine = PolicyEngine(
        pre_rules=[block_forbidden_actions, require_non_empty_payload],
        post_rules=[block_error_results],
    )
    pipeline = Pipeline(policy_engine=policy_engine, executor=executor, ledger=ledger)

    order = WorkOrder.new(action="bad_op", payload={"trigger": "error"}, replay=True)
    ledger.record(order.id, EventType.REPLAY_TRIGGERED, {"initiated_by": "main.py"})
    result = pipeline.run(order)
    _print_result("Scenario 5 — Replay", result, ledger)
    return result.success


def main() -> int:
    print("\n╔══════════════════════════════════════════════════════╗")
    print("║   ZQ-AIOS  Phase 5 — Control Plane Demonstration    ║")
    print("╚══════════════════════════════════════════════════════╝")

    scenarios = [
        scenario_1_valid_flow,
        scenario_2_schema_failure,
        scenario_3_pre_policy_block,
        scenario_4_post_policy_block,
        scenario_5_replay,
    ]

    passed = 0
    for fn in scenarios:
        if fn():
            passed += 1

    total = len(scenarios)
    print(f"\n{'═' * 60}")
    print(f"  Result: {passed}/{total} scenarios passed")
    print(f"{'═' * 60}\n")

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
