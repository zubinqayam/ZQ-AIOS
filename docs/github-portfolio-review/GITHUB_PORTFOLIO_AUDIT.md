# GitHub Portfolio Audit

Central review plan for the Zubin Qayam / ZQ Labs GitHub portfolio.

## Review Standard

This is a planning assessment, not a security audit or a claim that any repository is production-ready. Visibility, implementation maturity, test status, and confidentiality must be verified in each repository before public promotion. Use the following classifications:

- **A — LinkedIn-ready:** understandable, safe to show, and sufficiently documented for a public technical audience.
- **B — Improve before public:** potentially relevant, but needs documentation, safety review, or claim calibration.
- **C — Keep private:** contains or may contain sensitive, unfinished, or access-restricted material.
- **D — Archive / de-emphasize:** low current portfolio value or superseded by a stronger project.
- **E — Fork / learning / reference only:** useful technically, but not presented as a primary authored product.

## Repository Assessment

| Repository | Visibility if known | Current purpose | Professional relevance | README quality | Confidentiality risk | Claim risk | Recommended action | LinkedIn suitability | Priority | Next Copilot task |
|---|---|---|---|---|---|---|---|---|---|---|
| [zubinqayam/Zubin-Qayam](https://github.com/zubinqayam/Zubin-Qayam) | Not verified in this workspace | Profile-level identity and portfolio presentation | High if it clearly explains focus and selected work | Not reviewed here | Medium until reviewed | Medium | B — Improve before public; review profile README and links | Potentially high after review | P0 | Audit profile README, links, pinned projects, and public claims |
| [zubinqayam/zq-portfolio](https://github.com/zubinqayam/zq-portfolio) | Public clone resolved | Personal portfolio site or presentation layer | High for visual portfolio storytelling | Requires repository review | Medium until scanned | Medium | B — Improve before public; document scope and demo boundaries | High after safety and claim review | P0 | Improve README, add verified run instructions, and scan public assets |
| [zubinqayam/ZQ-AIOS](https://github.com/zubinqayam/ZQ-AIOS) | Public clone resolved | Central AI, workflow, policy, and operations workspace | High as the coordinating research repository | Added by this package | High until content and history are scanned | High if concepts are stated as deployed systems | B — Improve before public; keep claims research-oriented | Medium to high after cleanup | P0 | Complete safety scan and document verified architecture |
| [zubinqayam/zq-master-bridge](https://github.com/zubinqayam/zq-master-bridge) | Public clone resolved | Integration or orchestration bridge | Medium to high if interfaces and boundaries are clear | Requires repository review | Medium to high until scanned | Medium | B — Improve before public; clarify integrations and demo data | Medium after review | P1 | Inventory integrations, secrets, and supported workflows |
| [zubinqayam/ZQAutoNXG-V1](https://github.com/zubinqayam/ZQAutoNXG-V1) | Public clone resolved | Automation and workflow system | High technical relevance | Requires repository review | High until scanned | High without tested evidence | B — Improve before public; fix invalid path in WSL/Linux and calibrate claims | Medium after remediation | P1 | Rename the Windows-invalid tracked path, then document status and tests |
| [zubinqayam/ZQ_Taskbox](https://github.com/zubinqayam/ZQ_Taskbox) | Public clone resolved | Taskbox or task orchestration workspace | High if the workflow is demonstrable | Requires repository review | High until scanned | High if “autonomous” claims are unsupported | B — Improve before public; remove sensitive examples and explain boundaries | Medium to high after review | P1 | Add a safe quickstart, status label, and task-flow example |
| [zubinqayam/ZQ-AIOS-CoreLoop](https://github.com/zubinqayam/ZQ-AIOS-CoreLoop) | Public clone resolved | Core loop or foundational AIOS component | High for technical depth | Requires repository review | Medium to high until scanned | High without benchmarks or tests | B — Improve before public; document scope and evidence | Medium after review | P1 | Explain the core loop, verification, and known limitations |
| [zubinqayam/ZQ_OPS_Brain-v2](https://github.com/zubinqayam/ZQ_OPS_Brain-v2) | Public clone resolved | Operations intelligence or coordination concept | High if framed as a prototype | Requires repository review | High until scanned | High around healthcare or operational claims | B — Improve before public; use demo data and explicit limitations | Medium after review | P1 | Add prototype status, safety notes, and sanitized examples |
| [zubinqayam/ZQ-LEAPXO-SKILL-ENGINE](https://github.com/zubinqayam/ZQ-LEAPXO-SKILL-ENGINE) | Public clone resolved | Skill or capability engine | Medium to high for AI tooling audiences | Requires repository review | Medium until scanned | Medium to high without reproducible examples | B — Improve before public; publish a focused technical overview | Medium after review | P2 | Add architecture, example inputs/outputs, and verification status |
| [zubinqayam/INNM-WOSDS](https://github.com/zubinqayam/INNM-WOSDS) | 404 from public/unauthenticated access | Unavailable or access-restricted workspace | Unknown | Unknown | Unknown and potentially high | Unknown | **C — Keep private / unavailable in this public workspace** | Not suitable for current LinkedIn batch | P0 | Confirm ownership and confidentiality privately before any promotion |

## ZQAutoNXG-V1 Checkout Remediation

The repository contains a Windows-invalid tracked path:

```text
.github/instructions/*.instructions.md
```

Windows cannot materialize a filename containing the literal `*` character. The recommended fix is to use WSL/Linux to rename it to one of:

```text
.github/instructions/zqautonxg.instructions.md
.github/instructions/default.instructions.md
```

Do not attempt risky Windows checkout repair from this task.

## Limitations

- This workspace confirms clone resolution, not repository visibility settings, branch protection, deployment health, or production readiness.
- `INNM-WOSDS` was not available through public unauthenticated GitHub access and is intentionally excluded from the public batch.
- A repository can contain sensitive material in history, issues, releases, Actions logs, or external links even when its current working tree looks clean.
- Every repository needs its own README, dependency, secret, and claim review before LinkedIn promotion.