# `copilot\agents\` — Copilot CLI agent ports

`.agent.md` twins of `..\..\claude\agents\*.md`. Each is a **sibling, not a copy**: it names its Claude
original and version in its own body, and marks every deliberate divergence `[Copilot]`.

**When a Claude original changes materially, its port needs the same change.** Nothing automated enforces
that — `_scripts\check-sync.ps1` compares staged-vs-live per tool, not Claude-vs-Copilot parity.

Standing divergences that apply to the whole `req-*` family live once in `..\PORT-NOTES.md`, not repeated
per file. Conformance target: `..\..\sa-framework\PIPELINE.md §5`.

## Inventory

| Agent | Role | Ported |
|---|---|---|
| `agent-reviewer` | Independent review of a drafted agent/skill/prompt against doctrine | 2026-09-07 |
| `copilot-usage` | Copilot CLI token/cost usage reporting — **Copilot-only, no Claude sibling** | earlier |
| `doc-briefer` | Comprehension brief of an inbound document, then Q&A from the source | 2026-09-07 |
| `mermaid-diagram-maker` | Diagrams from a defined architecture — `.mmd` + `.png` | 2026-09-07 |
| `req-ingestor` | Extract inbound Excel/Word/PDF/text to citable Markdown | 2026-09-07 |
| `req-analyst` | Requirements list with `REQ-` ids, priority, status, source | 2026-09-07 |
| `req-screener` | Bid/no-bid feasibility verdict + a non-quotable effort band | 2026-09-07 |
| `req-architect` | High-Level Design with traceability | 2026-09-07 |
| `req-reviewer` | Design review — severity-rated findings, no verdict | 2026-09-07 |
| `req-detailer` | Low-Level Design (`full-design` lane only) | 2026-09-07 |
| `req-risk-officer` | Scored risk + compliance registers, contingency recommendation | 2026-09-07 |
| `req-estimator` | Three-point AI-assisted effort estimate | 2026-09-07 |
| `req-estimate-critic` | Independent estimate critique — advisory | 2026-09-07 |
| `req-offer` | Client-facing offer content | 2026-09-07 |
| `req-auditor` | Cross-artifact ID integrity — emits `gate: sa-audit` | 2026-09-07 |
| `req-slop-detector` | Prose integrity — emits `gate: sa-slop` | 2026-09-07 |
| `req-onepager` | Dense single-page management document | 2026-09-07 |

The command layer that drives these is **`..\skills\sa-pipeline\SKILL.md`**, not a set of command files —
see that file's own note on why (`~/.copilot/commands/` has no documented discovery behaviour).

## Not ported, deliberately

The `dev-*` family (`dev-backend`, `dev-frontend`, `dev-reviewer`, `dev-browser-tester`),
`solution-analyst`, `framework-strategist`, and `public-figure-researcher`. Claude Code remains the default
tool for implementation work, and `framework-strategist` reviews the framework from the Claude side by
design. Recorded here so a future review reads the absence as intent, not drift.
