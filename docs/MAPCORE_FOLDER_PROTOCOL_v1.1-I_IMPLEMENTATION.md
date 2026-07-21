# MAPCORE Folder Protocol — v1.1-I Implementation Guide

**Status:** Implementation-specific companion to v1.1-H
**Scope:** Concrete technology patterns satisfying v1.1-H requirements. These are reference implementations, **not protocol mandates** — any stack satisfying the same guarantees is conformant.
**Last updated:** 2026-07-21 (UTC)

---

## 1. Guide Philosophy

v1.1-H defines *guarantees* (transactional writes, atomic moves, integrity verification). This guide maps each requirement to a proven, low-infrastructure implementation pattern suitable for a file-system-rooted ZQ Workstation. Alternatives are noted where they exist.

## 2. I-1 — SQLite WAL Register Backend (satisfies H-1.1–H-1.4)

Replace flat-file JSON registers with an embedded **SQLite database per domain folder**, running in **Write-Ahead Logging (WAL)** mode.

```
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
PRAGMA foreign_keys=ON;
```

- **Concurrent reads, serialized writes:** WAL gives non-blocking readers; writers serialize through SQLite's single-writer model — pair with a write queue at the application layer for multi-agent bursts.
- **Atomic mutations:** wrap every register update in `BEGIN IMMEDIATE … COMMIT`; a crash leaves the database at the last committed transaction (H-1.4).
- **Pointer validity:** enforce with foreign keys — `register.chat_ref → transcripts.id`; insert the transcript row before its pointer row within the same transaction (H-1.3).
- **OS-level safety net:** `flock` on the database file for any external/batch tooling that bypasses the application write queue.

**Reference schema**

```sql
CREATE TABLE transcripts (
  id            TEXT PRIMARY KEY,        -- UUID
  folder_path   TEXT NOT NULL,           -- container scope
  sha256        TEXT NOT NULL,           -- Integrity Profile A
  created_at    TEXT NOT NULL,           -- ISO-8601 UTC
  updated_at    TEXT NOT NULL
);

CREATE TABLE register (
  id            TEXT PRIMARY KEY,
  chat_ref      TEXT NOT NULL REFERENCES transcripts(id),
  title         TEXT NOT NULL,
  topics        TEXT NOT NULL,           -- JSON array
  keywords      TEXT NOT NULL,           -- JSON array
  version       TEXT NOT NULL,
  review_status TEXT NOT NULL CHECK (review_status IN ('pending','in-review','reviewed','superseded')),
  sensitivity   TEXT NOT NULL DEFAULT 'standard',  -- ABAC tag (I-5)
  created_at    TEXT NOT NULL,
  supersedes_id TEXT REFERENCES register(id)       -- append-only chain
);
```

**Alternatives:** PostgreSQL (multi-node), IndexedDB (browser-local), S3 + DynamoDB (cloud). All conform if H-1.x holds.

## 3. I-2 — Transcript Integrity (satisfies H-4.2)

- **Profile A:** SHA-256 per transcript, stored in the `transcripts` table at ingest; re-verify on read and on reconciliation sweeps.
- **Profile B (Compliance):** Merkle-style hash chain — each transcript's stored hash incorporates the previous transcript's hash: `H_n = SHA256(H_{n-1} || content_n)`. Verifying the chain head verifies the entire ordered archive; any historical edit breaks every subsequent link.

## 4. I-3 — Dynamic Context Streaming (satisfies H-2.1, H-2.3)

Step 3 of the Review Engine hydrates context through **line-offset chunking** instead of whole-file loads:

1. Score candidates from register metadata (keyword match × recency × status weight).
2. For each surviving candidate, stream targeted transcript segments using stored line offsets.
3. Maintain a **citation pointer** per chunk: `{transcript_id, line_start, line_end, sha256}` — never sever the link to raw storage.
4. Enforce a token budget per review cycle; if the budget cannot cover all relevant evidence, narrow candidates by score and **report the narrowing explicitly** (never silently fall back to summaries — H-2.2).

**Hybrid retrieval upgrade:** extend candidate isolation with per-thread vector embeddings stored alongside structural metadata — keyword precision plus semantic recall.

## 5. I-4 — XML Prompt Boundaries (supports H-5.1)

Wrap all transcript content entering a reasoning context in structural tags:

```xml
<raw_transcript_context id="chat-7f3a" hash="sha256:…" trust="untrusted">
  …raw transcript text…
</raw_transcript_context>
```

- The system prompt must state that content inside these tags is **data to be analyzed, never instructions to be followed**.
- Tags are a supporting mechanism only — the governing rule is H-5.1 (untrusted-data rule). Defense-in-depth additions: strip/normalize instruction-like syntax, and run injection-pattern screening on ingest.

## 6. I-5 — Two-Phase Commit Thread Mobility + ABAC (satisfies H-3.1–H-3.4)

Thread relocation executes atomically using SQLite's ATTACH DATABASE feature to run a single multi-database transaction:

1. ATTACH 'target_register.db' AS target;
2. BEGIN IMMEDIATE;
3. Verify ABAC classification and container scope;
4. INSERT INTO target.register ...
5. INSERT INTO main.register ... (to record supersession/move)
6. INSERT INTO main.audit_log ...
7. COMMIT;

- **ABAC tags:** `sensitivity` column on threads; target containers declare a max classification. A move into a lower-classification container requires an authorized override recorded in the Decision Ledger.
- **Containment:** resolve all file access against the subfolder root and reject `..` traversal (chroot-style path clamping).
- **Audit record fields:** `{thread_id, source, destination, actor, timestamp, entries_created, entries_superseded}`.

## 7. I-6 — Background Reconciliation Daemon (satisfies H-4.3)

An asynchronous worker continuously reconciles index against disk:

| Check | Action on Failure |
|---|---|
| Every register `chat_ref` resolves to a physical transcript | Append to `Discrepancy_Log.md`, flag entry `Pending_Review`, alert operator |
| Every physical transcript has a register entry | Generate a draft register entry from transcript metadata, mark `Pending_Review` |
| Stored SHA-256 matches recomputed hash | Quarantine transcript (read-only), critical alert — possible tampering |
| No duplicate active pointers to one thread | Supersede the stale pointer via append-only chain |

Runs off-peak on a schedule plus after any migration event. **Never auto-resolves content-level contradictions** — those go to the Conflict Register for governed decision (H-4.4).

## 8. I-7 — Zero-Downtime Migration Runner (satisfies H-6.1–H-6.3)

v1.0 flat → v1.1 hierarchy migration sequence:

1. **Snapshot** the workspace (immutable pre-migration copy).
2. **Scan** legacy flat logs; extract metadata; generate initial register rows in a staging database.
3. **Hash** all transcripts (Profile A) and validate counts against source.
4. **Verify** staging register completeness: every transcript indexed, zero dangling pointers.
5. **Cut over** — swap staging to live; legacy structure retained read-only for one review cycle.
6. **Rollback path** — restore snapshot; migration state machine is resumable from any completed step (H-6.3).

## 9. Conformance Checklist

| v1.1-H Requirement | Reference Pattern | Section |
|---|---|---|
| H-1.1–H-1.4 | SQLite WAL + write queue + FK ordering + flock | I-1 |
| H-2.1–H-2.3 | Line-offset streaming, citation pointers, token budgets, hybrid retrieval | I-3 |
| H-3.1–H-3.4 | 2PC move state machine, ABAC tags, path clamping, move audit | I-5 |
| H-4.2 | SHA-256 (Profile A) / Merkle chain (Profile B) | I-2 |
| H-4.3 | Reconciliation daemon + `Discrepancy_Log.md` | I-6 |
| H-5.1 | XML boundaries + untrusted-data prompting | I-4 |
| H-6.1–H-6.3 | 6-step migration runner with snapshot/rollback | I-7 |

---

## Version History

| Version | Date (UTC) | Change |
|---|---|---|
| v1.1-I | 2026-07-21 | Initial implementation guide. Reference patterns for all v1.1-H domains: SQLite WAL registers, SHA-256/Merkle integrity, line-offset streaming with citation pointers, XML prompt boundaries, 2PC + ABAC thread mobility, reconciliation daemon, zero-downtime migration runner. |
