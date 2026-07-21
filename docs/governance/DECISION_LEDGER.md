# Decision Ledger — ZQ Workstation

**Artifact class:** Append-only governance register (mandated by v1.1-H §5)
**Scope:** Canonical history of accepted operational decisions. Decisions are never edited or deleted — status changes are recorded as new entries that supersede prior ones.
**Governing rule:** Resolves contradictions by *decision, not deletion* (H-4.4). Both the active and superseded decisions remain permanently recorded.
**Last updated:** 2026-07-21 (UTC)

---

## Schema

| Field | Type | Description |
|---|---|---|
| Decision ID | String (unique) | Identifier, format `DEC-YYYY-NNN` |
| Timestamp | ISO-8601 UTC | When the decision was recorded |
| Folder | String | Owning folder (default: ZQ Workstation) |
| Subfolder | String | Scoped subfolder, if any |
| Source Chats | List of Chat References | Transcripts supporting the decision |
| Current Decision | Text | The active decision statement |
| Previous Decision | Text / Decision ID | The superseded decision, if any |
| Rationale | Text | Why this decision governs |
| Approval | String | Approving authority (human or authorized agent workflow) |
| Status | Enum | `Active` / `Superseded` |

## Entries

| Decision ID | Timestamp (UTC) | Folder | Subfolder | Source Chats | Current Decision | Previous Decision | Rationale | Approval | Status |
|---|---|---|---|---|---|---|---|---|---|
| DEC-2026-001 | 2026-07-21 | ZQ Workstation | — | Issue #17 | Adopt append-only MAPCORE folder discussion protocol v1.1 as the workspace documentation standard | — | Prevents context loss; establishes register-driven incremental review | Zubin Qayam | Active |
| DEC-2026-002 | 2026-07-21 | ZQ Workstation | — | ZQ QAQC Test Suite 2026-07-21 | Hardening requirements live in a separate normative supplement (v1.1-H), implementations in a separate guide (v1.1-I); protocol v1.1 stays stable | — | Keeps the core protocol stable while implementation technologies evolve independently | Zubin Qayam | Active |
| DEC-2026-003 | 2026-07-21 | ZQ Workstation | — | QA/QC critique 2026-07-21 | Technology choices (e.g. SQLite WAL) are implementation profiles, not protocol mandates; protocol specifies guarantees only | — | Any stack satisfying transactional/atomic/concurrency requirements is conformant | Zubin Qayam | Active |
