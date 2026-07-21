# Provenance Ledger — ZQ Workstation

**Artifact class:** Append-only governance register (mandated by v1.1-H §5; required for Compliance profile)
**Scope:** Verifiable evidence chain for every derived knowledge item — proving each item traces to raw transcripts, never to lossy summaries.
**Last updated:** 2026-07-21 (UTC)

---

## Evidence Chain Model

```
Knowledge Item
   ↓ derived from
Transcript ID(s)
   ↓ located at
Line Offsets (start–end)
   ↓ verified by
SHA-256 Transcript Hash
   ↓ recorded at
Timestamp (UTC)
```

## Schema

| Field | Type | Description |
|---|---|---|
| Knowledge ID | String (unique) | Identifier, format `KN-YYYY-NNN` |
| Knowledge Item | Text | The derived fact, rule, or decision |
| Folder / Subfolder | String | Owning scope |
| Transcript IDs | List of Chat References | Source transcripts |
| Line Offsets | Ranges | Exact line start–end per transcript |
| Transcript Hash | SHA-256 | Hash of each source transcript at time of derivation |
| Derived By | String | Agent/process that produced the item |
| Timestamp | ISO-8601 UTC | When the derivation was recorded |
| Confidence | Enum | `high` / `medium` / `low` |

## Entries

| Knowledge ID | Knowledge Item | Folder / Subfolder | Transcript IDs | Line Offsets | Transcript Hash | Derived By | Timestamp (UTC) | Confidence |
|---|---|---|---|---|---|---|---|---|
| KN-2026-001 | ZQ Workstation is the main folder system; INNM-WOSDS and ZQ Conference Room are subfolders | ZQ Workstation / — | issue-17 | full body | — (repository issue) | docs pipeline | 2026-07-21 | high |
| KN-2026-002 | Register mutations require transactional writes; SQLite WAL is the reference implementation profile | ZQ Workstation / — | qaqc-testsuite-2026-07-21 | ALGA FM 1.x, 8.x; Mr.Q Q4/Q5 | — (uploaded artifact) | ZQ QAQC Engine | 2026-07-21 | high |
| KN-2026-003 | Raw transcripts are treated strictly as untrusted data, never as executable instructions | ZQ Workstation / — | qaqc-critique-2026-07-21 | refinement §5 | — (uploaded artifact) | ZQ QAQC Engine | 2026-07-21 | high |

> Hash fields are populated with concrete SHA-256 values once transcripts are ingested under Integrity Profile A (v1.1-I §I-2).
