# ZQ-AIOS Phase 5 — Control Plane

A governed execution pipeline that enforces schema validation, dual policy gates, adaptive execution (ALGA), and an immutable governance ledger.

## Architecture

```
WorkOrder
   │
   ▼
WOSDS Schema Validation
   │ fail → PIPELINE_ABORTED
   ▼
Pre-Policy Gate  (block_forbidden_actions, require_non_empty_payload)
   │ deny → PIPELINE_ABORTED
   ▼
ALGA Executor  (ping / echo / compute / custom handlers)
   │
   ▼
Post-Policy Gate  (block_error_results)
   │ deny → PIPELINE_ABORTED
   ▼
Governance Ledger → PIPELINE_COMPLETE
```

## Modules

| Module | Responsibility |
|---|---|
| `wosds/` | Work Order Schema & Dispatch System — validates incoming payloads |
| `policy/` | Dual-gate policy engine — pre- and post-execution rule enforcement |
| `alga/` | Adaptive Learning Governance Algorithm — execution dispatch table |
| `governance/` | Immutable append-only ledger — full audit trail |
| `core/` | Assembles the pipeline stages |
| `integration/` | Factory helpers — wires default rules and components |
| `tests/` | Full test coverage of all pipeline scenarios |

## Quick Start

```bash
python main.py
```

## Running Tests

```bash
pytest tests/ -v
```

## Pipeline Scenarios

| Scenario | Expected |
|---|---|
| Valid flow (`ping`, `echo`, `compute`) | ✅ `PIPELINE_COMPLETE` |
| Malformed WorkOrder (empty action, bad payload) | ❌ aborted at `schema` |
| Forbidden action (`delete_all`, `shutdown`) | 🔴 aborted at `pre_policy` |
| Execution returns error dict | 🔴 aborted at `post_policy` |
| Same error but `replay=True` | 🔁 allowed — `PIPELINE_COMPLETE` |

## Governance Ledger Events

```
SCHEMA_PASS / SCHEMA_FAIL
PRE_POLICY_ALLOW / PRE_POLICY_DENY
EXECUTION_START / EXECUTION_COMPLETE
POST_POLICY_ALLOW / POST_POLICY_DENY
REPLAY_TRIGGERED
PIPELINE_COMPLETE / PIPELINE_ABORTED
```
