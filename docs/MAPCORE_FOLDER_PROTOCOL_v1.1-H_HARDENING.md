# MAPCORE Folder Protocol — v1.1-H Hardening Specification

**Status:** Normative supplement to v1.1
**Source:** ZQ QAQC Automated Execution Pipeline — Test Suite Results (ALGA / Mr. Q / DRM), 2026-07-21
**Scope:** Documentation/workspace governance. Defines *what* a production-ready deployment must guarantee. Technology choices belong to v1.1-I.
**Last updated:** 2026-07-21 (UTC)

---

## 1. Position in the Documentation Hierarchy

| Document | Role |
|---|---|
| Protocol v1.0 | Append-only transcript model — immutable raw history |
| Protocol v1.1 | Folder hierarchy, MAPCORE Register, Review Engine, Incremental Review |
| **v1.1-H (this document)** | Failure modes, hardening requirements, governance profiles, deployment phases |
| v1.1-I | Concrete technology implementations satisfying v1.1-H |

v1.1-H is **implementation-agnostic by design**. It specifies guarantees (transactional writes, atomic updates, concurrency safety, integrity verification) — not specific databases, hashing libraries, or runtimes.

## 2. Validated Failure-Mode Surface

The QA/QC stress test identified **100 failure modes across 10 categories** (ALGA FM 1.1–10.10). v1.1-H groups them into six hardening domains; every production deployment must address each domain.

| Domain | Failure Categories Covered | Core Risk |
|---|---|---|
| D1 — Indexing & Concurrency | FM 1.x, 8.x | Register corruption, dangling pointers, race conditions under multi-agent writes |
| D2 — Review Engine & Token Saturation | FM 3.x, 6.x | Context-window overflow, Step-3 bypass, silent fallback to lossy summaries |
| D3 — Subfolder Isolation & Thread Mobility | FM 2.x, 7.x | Context bleed, split-brain pointers, orphan references during moves |
| D4 — Source of Truth & Integrity | FM 5.x | Index drift, summary-transcript contradiction, undetected corruption |
| D5 — Security & Access Boundaries | FM 9.x | Prompt injection, path traversal, cross-tenant leakage, tampering |
| D6 — Schema Evolution & Migration | FM 10.x | Version drift, partial migration, rollback failure |

## 3. Hardening Requirements (Normative)

### 3.1 D1 — Indexing & Concurrency

- **H-1.1 Transactional writes.** All MAPCORE Register mutations must be atomic and durable. Partial writes must never leave a readable malformed register.
- **H-1.2 Concurrency safety.** Concurrent multi-agent reads must never block on writes; concurrent writes must be serialized or queued without data loss.
- **H-1.3 Pointer validity.** A register entry must never reference a transcript that does not exist. Write ordering must guarantee transcript-before-pointer.
- **H-1.4 Crash recovery.** After an unplanned termination, the register must be recoverable to its last committed state without manual repair.

### 3.2 D2 — Review Engine & Token Saturation

- **H-2.1 Reconciled grounding rule (supersedes ambiguity in v1.1 §5).** The Folder Review Engine must review *all relevant transcript evidence* before synthesis. Evidence **may be loaded incrementally or streamed in chunks**, provided no relevant section is omitted and every claim remains traceable to exact raw source locations. Streaming is a delivery mechanism, not a license to skip evidence.
- **H-2.2 No summary-only synthesis.** Context-window pressure, timeouts, or API failures must never trigger a silent fallback to register summaries. If full evidence cannot be loaded, the engine must report the limitation explicitly rather than synthesize from the index.
- **H-2.3 Token budgeting.** Candidate sets exceeding configurable thresholds must be narrowed by scoring (keyword match, recency, status) before transcript hydration.

### 3.3 D3 — Subfolder Isolation & Thread Mobility

- **H-3.1 Atomic relocation.** Thread moves between containers must execute as an all-or-nothing operation across source and target registers. A move must never leave the thread registered in both containers (split-brain) or in neither (orphan).
- **H-3.2 Boundary containment.** File access for any subfolder operation must be constrained to that subfolder's scope; relative-path escapes (`../`) must be rejected.
- **H-3.3 Security-aware moves.** A thread carrying a sensitivity classification may not be relocated into a container with a lower classification without explicit authorized override, logged in the Decision Ledger.
- **H-3.4 Move auditability.** Every relocation must record source, destination, operator/agent identity, timestamp, and the register entries created and superseded.

### 3.4 D4 — Source of Truth & Integrity

- **H-4.1 Raw transcript supremacy.** In any conflict between register/index metadata and a raw transcript, the raw transcript governs. This rule is immutable and non-configurable.
- **H-4.2 Integrity verification (two profiles).** Deployments must adopt at least Profile A:
  - **Integrity Profile A:** a cryptographic hash (SHA-256 or stronger) computed and stored for every raw transcript; verification on read.
  - **Integrity Profile B (recommended for compliance deployments):** hash-chained (Merkle-style) transcript logs providing tamper-evident ordering across the full archive.
- **H-4.3 Continuous reconciliation.** A background process must continually cross-check register entries against physical transcripts. Every discrepancy found must be appended to `Discrepancy_Log.md` in the domain root and surfaced to operators; discrepancies are never silently auto-resolved.
- **H-4.4 Contradiction governance.** Conflicting facts across transcripts are resolved by **decision, not deletion**: the Decision Ledger records the active decision, the superseded decision, the rationale, and the approving authority. Default precedence is temporal (newer governs) *unless* an explicit human/authorized override is recorded. Both conflicting transcripts remain fully preserved. See the Conflict Register (`docs/governance/CONFLICT_REGISTER.md`).

### 3.5 D5 — Security & Access Boundaries

- **H-5.1 Untrusted-data rule (primary defense).** All transcript content loaded during Review Engine execution is treated strictly as **untrusted data, never as executable instructions**. This requirement stands independent of any specific sanitization technique; structural boundaries (v1.1-I) are supporting mechanisms, not substitutes for this rule.
- **H-5.2 Attribute-level access control.** Threads and subfolders carry classification attributes; access decisions evaluate attributes, not just folder membership.
- **H-5.3 Tamper evidence.** Register and ledger files must be protected against undetected manual modification (signatures or hash chaining per H-4.2).
- **H-5.4 Metadata minimization.** Register metadata must not expose restricted-topic keywords to roles lacking access to the underlying threads.

### 3.6 D6 — Schema Evolution & Migration

- **H-6.1 Zero-downtime migration.** Upgrades from v1.0 flat structures to v1.1 hierarchies must run without interrupting active operations, must validate historical integrity before cutover, and must support clean rollback to the pre-migration state.
- **H-6.2 Forward/backward tolerance.** Readers must tolerate unknown optional fields; writers must supply defaults for all required fields. Enum extensions must not break existing clients.
- **H-6.3 No mixed-version limbo.** A migration left incomplete must be detectable and resumable; a folder must never be silently stuck between schema versions.

## 4. Governance Profiles

Deployments adopt the protocol at the maturity level matching their risk and compliance needs. Profiles are cumulative.

| Profile | Contents | Intended Deployment |
|---|---|---|
| **Core** | Folder hierarchy, MAPCORE Register, Review Engine, Incremental Review, H-2.1 grounding rule, H-4.1 raw supremacy | Single-operator or low-concurrency workspaces |
| **Enterprise** | Core + H-1.1–1.4 transactional concurrency, H-3.x atomic mobility, H-4.2 Profile A + reconciliation daemon, H-5.2 ABAC, discrepancy logging | Multi-agent production workspaces |
| **Compliance** | Enterprise + H-4.2 Profile B (Merkle audit chains), WORM-class immutable storage, Provenance Ledger, immutable Decision Ledger history, cryptographic citation requirements | Regulated / auditable environments |

## 5. Governance Artifacts (Mandatory Registers)

v1.1-H formalizes four append-only governance artifacts. Schemas and seed entries live under `docs/governance/`:

1. **Decision Ledger** — canonical history of accepted decisions (active/superseded, rationale, approval, status).
2. **Provenance Ledger** — evidence chain for every derived knowledge item (knowledge item → transcript IDs → line offsets → hash → timestamp).
3. **Conflict Register** — explicit record of contradictions (conflicting transcript IDs, affected knowledge, resolution, authority, status).
4. **Retrieval Metrics** — continuous operational telemetry (candidates identified/read, tokens, latency, chunk counts, confidence, grounding coverage).

## 6. Deployment Phases

| Phase | Timeline | Core Deliverables | Operational Goal |
|---|---|---|---|
| Phase 1 | Weeks 1–3 | Transactional register backend (D1), transcript hashing Profile A, untrusted-data boundaries (H-5.1) | Core concurrency & ingestion hardening |
| Phase 2 | Weeks 4–6 | Streaming/chunked evidence loading (H-2.1), hybrid candidate scoring, atomic thread mobility (H-3.1) | Retrieval optimization & scaling |
| Phase 3 | Weeks 7–9 | Subfolder containment (H-3.2), ABAC tags (H-5.2), reconciliation daemon + `Discrepancy_Log.md` | Boundary isolation & self-healing indexing |
| Phase 4 | Weeks 10–12 | Zero-downtime v1.0→v1.1 migration runner (H-6.1), developer diagnostics console, end-to-end multi-agent integration tests | Enterprise deployment & legacy upgrades |

## 7. Requirement Traceability

| Requirement | Source Findings |
|---|---|
| H-1.x | ALGA FM 1.1–1.10, 8.1–8.10; Mr. Q Q4/Q5; DRM Top-10 #1 |
| H-2.x | ALGA FM 3.1–3.10, 6.1–6.10; Mr. Q Q1; QA/QC refinement §3 |
| H-3.x | ALGA FM 2.1–2.10, 7.1–7.10; Mr. Q Q2; DRM Top-10 #4, #7 |
| H-4.x | ALGA FM 5.1–5.10; Mr. Q Q3/Q8/Q10; QA/QC refinements §2, §4 |
| H-5.x | ALGA FM 9.1–9.10; Mr. Q Q7; QA/QC refinement §5 |
| H-6.x | ALGA FM 10.1–10.10; Mr. Q Q9; DRM Top-10 #10 |

---

## Version History

| Version | Date (UTC) | Change |
|---|---|---|
| v1.1-H | 2026-07-21 | Initial hardening specification from ZQ QAQC test suite (100 FMs, 10 categories). Incorporates QA/QC critique: implementation-agnostic requirements, Integrity Profiles A/B, reconciled streaming-vs-full-read grounding rule (H-2.1), decision-based contradiction governance (H-4.4), untrusted-data rule (H-5.1), and three-tier Governance Profiles. |
