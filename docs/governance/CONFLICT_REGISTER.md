# Conflict Register — ZQ Workstation

**Artifact class:** Append-only governance register (mandated by v1.1-H §5)
**Scope:** Explicit record of contradictions between raw transcripts or between index and source. Contradictions are **recorded and governed, never resolved by deleting or overwriting history** (H-4.4).
**Last updated:** 2026-07-21 (UTC)

---

## Schema

| Field | Type | Description |
|---|---|---|
| Conflict ID | String (unique) | Identifier, format `CON-YYYY-NNN` |
| Detected At | ISO-8601 UTC | When the conflict was detected |
| Detected By | String | Review Engine / reconciliation daemon / human |
| Conflicting Transcripts | List of Chat References | The transcripts (or register entries) in contradiction |
| Transcript Timestamps | List of ISO-8601 | Chronological context for each side |
| Affected Knowledge | Knowledge ID(s) / text | What the conflict concerns |
| Resolution | Text | The governing decision (links to Decision Ledger) |
| Authority | String | Who/what approved the resolution |
| Status | Enum | `open` / `resolved` / `monitoring` |

## Resolution Precedence (per H-4.4)

1. Both conflicting transcripts remain fully preserved — always.
2. Default: temporal precedence — the newer transcript governs active operational context.
3. Override: an explicit authorized decision (recorded in the Decision Ledger) may establish the older statement as governing, with rationale. Temporal precedence alone is not proof of correctness.
4. The Knowledge Model records: active decision, superseded decision, rationale, approving authority.

## Entries

| Conflict ID | Detected At | Detected By | Conflicting Transcripts | Transcript Timestamps | Affected Knowledge | Resolution | Authority | Status |
|---|---|---|---|---|---|---|---|---|
| CON-2026-001 | 2026-07-21 | QA/QC critique | v1.1 protocol §5 (\"read complete discussions\") vs QA streaming recommendation | 2026-07-21 / 2026-07-21 | Step 3 evidence-loading semantics | Resolved by H-2.1: all relevant evidence must be reviewed before synthesis; evidence may be streamed in chunks provided no relevant section is omitted and citation links to raw source are preserved | Zubin Qayam | resolved |
| CON-2026-002 | 2026-07-21 | QA/QC critique | Mr.Q A3 (\"newest transcript wins\") vs critique (newer can be incorrect) | 2026-07-21 / 2026-07-21 | Contradiction-resolution precedence | Resolved by H-4.4: temporal precedence is the default only; explicit authorized override with recorded rationale governs; history is never replaced | Zubin Qayam | resolved |
