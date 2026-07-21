# MAPCORE Folder Protocol — v1.1

**Status:** Active specification
**Implements:** Issue #17 — Append-only update request: MAPCORE / folder discussion register for ZQ Workstation
**Scope:** Repository / workspace documentation requirement only. This protocol defines no runtime logic changes to the ZQ-AIOS control plane.
**Last updated:** 2026-07-21 (UTC)

---

## 1. Purpose

This document is the formal protocol for how knowledge, discussions, and documentation are organized, registered, and reviewed inside the **ZQ Workstation** folder system. It establishes:

1. An **append-only documentation policy** for all protocol artifacts.
2. A **MAPCORE register** that tracks every chat, folder, and subfolder.
3. A **folder → subfolder architecture** with scoped knowledge accumulation.
4. An **incremental review workflow** driven by the register.

## 2. Append-Only Documentation Policy

All documentation governed by this protocol is **append-only**:

- **No deletion.** Previous versions and prior documentation are never overwritten or removed. Every earlier section remains intact for reference.
- **Additions only.** New content is added either at the bottom of the existing document or as a new, clearly marked version section (e.g. `v1.1`, `v1.2`).
- **Timestamp on every update.** Each update carries an explicit UTC timestamp and a version marker.
- **Version chain.** A new version section must reference the version it supersedes, preserving a readable history chain.

## 3. Folder → Subfolder Architecture

**ZQ Workstation** is the main folder system — the top-level container for all workspace knowledge. Tools and topics live inside it as subfolders.

```
ZQ Workstation (main folder)
   ├── INNM-WOSDS            (subfolder — tool/topic)
   ├── ZQ Conference Room    (subfolder — tool/topic)
   └── ...                   (additional subfolders as created)
```

### 3.1 Folder-level knowledge accumulation

Each folder accumulates its own knowledge over time. All discussions, decisions, and documents belonging to a folder are preserved **in full inside that folder** — nothing is stripped out as the workspace grows.

### 3.2 Subfolder-level scoped knowledge

Each subfolder maintains **scoped knowledge**: context limited to its own tool or topic. A subfolder's register entries and history are visible within the parent folder, but its detailed knowledge stays scoped to the subfolder, keeping the parent register navigable.

### 3.3 Moving a chat into a subfolder

A chat's details may be moved (in whole or in part) into a subfolder **without deleting the original chat**. The original remains in place; the subfolder receives a copy or extract with a register entry recording the move (source folder, target subfolder, timestamp).

## 4. MAPCORE Register

The **MAPCORE register** is the master index of all chats, folders, and subfolders in the ZQ Workstation. Every entry records:

| Field | Description |
|---|---|
| `timestamp` | UTC date-time of the register entry |
| `topic` | Short title of the discussion or artifact |
| `folder` | Parent folder (default: ZQ Workstation) |
| `subfolder` | Subfolder, if scoped (e.g. INNM-WOSDS, ZQ Conference Room); empty if folder-level |
| `review_status` | One of: `pending`, `in-review`, `reviewed`, `superseded` |
| `version` | Document/protocol version the entry belongs to |
| `notes` | Optional one-line context (moves, merges, references) |

### 4.1 Register rules

- Entries are **append-only** — status changes are recorded by adding a new entry that supersedes the old one, never by editing history.
- Every chat, folder, and subfolder must have at least one register entry.
- Register entries are the trigger for the review workflow (Section 5).

## 5. Incremental Review Workflow

Reviews are performed **incrementally, based on the register**, not by re-reading the entire workspace:

1. **Scan** the MAPCORE register for entries with `review_status = pending`.
2. **Review** each pending item in register order (oldest timestamp first).
3. **Record** the outcome as a new register entry with an updated status (`reviewed` or `in-review`) and a fresh timestamp.
4. **Supersede** — when a document section is replaced by a newer version, add an entry marking the old version `superseded` and pointing to the new one.

This keeps review effort proportional to what changed since the last review cycle.

## 6. Timestamp and Versioning Rules

- All timestamps are **UTC**, format `YYYY-MM-DD` (add `HH:MM` when same-day ordering matters).
- Protocol versions follow `vMAJOR.MINOR` (this document: **v1.1**).
- A **MINOR** bump = appended content that does not change prior rules.
- A **MAJOR** bump = a rule change; the previous version section must be preserved in full beneath the new one.

## 7. Preservation Guarantee

> All previous documentation — every version, every folder and subfolder history, every register entry — is preserved intact. Updates are expressed only as new appended content. Nothing governed by this protocol may be deleted or rewritten in place.

---

## Addendum A — Hardening & Implementation Documents (2026-07-21)

*Appended per the append-only policy (Section 2). Nothing above is modified.*

Following the ZQ QAQC automated test suite (ALGA / Mr. Q / DRM — 100 failure modes across 10 categories) and its independent QA/QC critique, the protocol documentation now separates into a three-document hierarchy:

| Document | Role |
|---|---|
| `docs/MAPCORE_FOLDER_PROTOCOL_v1.1.md` (this document) | Normative protocol — *what* the workspace requires |
| `docs/MAPCORE_FOLDER_PROTOCOL_v1.1-H_HARDENING.md` | Normative supplement — production-readiness guarantees (failure modes, security, concurrency, integrity, migration, governance profiles) |
| `docs/MAPCORE_FOLDER_PROTOCOL_v1.1-I_IMPLEMENTATION.md` | Implementation guide — reference technologies satisfying v1.1-H (SQLite WAL, Merkle trees, 2PC, ABAC, XML boundaries, streaming retrieval) |

Four append-only governance artifacts are formalized under `docs/governance/`: Decision Ledger, Provenance Ledger, Conflict Register, Retrieval Metrics.

Two clarifications to this protocol's intent, resolved via Conflict Register entries CON-2026-001/002:

1. **Evidence loading.** "Review" of discussions by the engine means *all relevant transcript evidence* must be reviewed before synthesis. Evidence may be loaded incrementally or streamed in chunks, provided no relevant section is omitted and every claim stays traceable to raw source locations. (Normative form: v1.1-H requirement H-2.1.)
2. **Contradiction handling.** Conflicting statements across transcripts are resolved by governed decision — active decision, superseded decision, rationale, approving authority — never by deleting or overwriting history. (Normative form: v1.1-H requirement H-4.4.)

---

## Version History

| Version | Date (UTC) | Change |
|---|---|---|
| v1.1 | 2026-07-21 | Initial formal specification. Converts Issue #17 requirements into protocol form: append-only policy, MAPCORE register, folder → subfolder architecture, incremental review workflow. |
| v1.1 Addendum A | 2026-07-21 | Appended: three-document hierarchy (v1.1 / v1.1-H / v1.1-I), governance artifacts, and two clarifications (evidence loading, contradiction handling). No prior content modified. |

## MAPCORE Register — Seed Entries

| Timestamp (UTC) | Topic | Folder | Subfolder | Review Status | Version | Notes |
|---|---|---|---|---|---|---|
| 2026-07-21 | MAPCORE Folder Protocol v1.1 specification | ZQ Workstation | — | reviewed | v1.1 | Formalizes Issue #17 |
| 2026-07-21 | Issue #17 — append-only update request | ZQ Workstation | — | superseded | v1.1 | Superseded by this protocol document |
| 2026-07-21 | v1.1-H Hardening Specification | ZQ Workstation | — | reviewed | v1.1 Addendum A | From ZQ QAQC test suite (100 FMs) |
| 2026-07-21 | v1.1-I Implementation Guide | ZQ Workstation | — | reviewed | v1.1 Addendum A | Reference tech satisfying v1.1-H |
| 2026-07-21 | Governance artifacts (Decision/Provenance/Conflict/Metrics) | ZQ Workstation | — | reviewed | v1.1 Addendum A | Append-only registers, `docs/governance/` |
