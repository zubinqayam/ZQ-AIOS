# Retrieval Metrics — ZQ Workstation

**Artifact class:** Append-only operational telemetry register (mandated by v1.1-H §5)
**Scope:** Continuous measurement of Folder Review Engine retrieval performance — supports tuning, capacity planning, and grounding-coverage audits.
**Last updated:** 2026-07-21 (UTC)

---

## Metrics Schema

| Metric | Type | Description | Target / Alert Threshold |
|---|---|---|---|
| Candidate threads identified | Integer | Threads passing register filtering (Step 2) | — |
| Threads actually read | Integer | Threads whose evidence entered the context window (Step 3) | Should equal candidates after scoring; a persistent gap signals budget pressure |
| Tokens consumed | Integer | Total tokens for the review cycle | Alert on sustained growth trend |
| Retrieval latency | ms | End-to-end Step 1→3 duration | Alert > 30 s (FM 6.5) |
| Chunk count | Integer | Streamed segments loaded via line-offset chunking | — |
| Confidence score | 0.0–1.0 | Engine self-assessment of answer grounding | Alert < 0.7 |
| Grounding coverage | % | Share of synthesized claims carrying a citation pointer to raw transcript lines | Must be 100% (H-2.1); any ungrounded claim is a protocol violation |

## Recording Rules

- One entry per review cycle, appended with UTC timestamp.
- Entries are telemetry — never edit; corrections are new entries referencing the original.
- Weekly rollup: trend review against thresholds feeds the incremental review workflow.

## Entries

| Timestamp (UTC) | Folder | Subfolder | Candidates | Threads Read | Tokens | Latency (ms) | Chunks | Confidence | Grounding Coverage | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-07-21 | ZQ Workstation | — | — | — | — | — | — | — | — | Register initialized; telemetry begins with first v1.1-I deployment |
