---
name: sa:help
description: Static reference for the sa: command namespace. No live analysis, no project context read.
allowed-tools: []
---

> Version: 1.0.2

<reference>
# `sa:` commands — lightweight Solution-Architect / REQ-CR pipeline

Global, generic — works in any project (or standalone, with no project at all) for the recurring
"analyze inbound material, produce a design and an estimate, generate documentation" need. Deliberately
lightweight: no verdict-blocks, no PASS/BLOCKING gates, no critic agents — narrative markdown output,
reviewed by you directly. Add rigor later only if it proves necessary.

| Command | Purpose | Dispatches to |
|---|---|---|
| `/sa:ingest <slug> <path...> [--recursive]` | Extract inbound Excel/Word/PDF/text files into readable Markdown. Optional first step, when starting from files rather than prose. Folder scans are one-level-deep by default — `--recursive` opts into walking every subfolder. | `req-ingestor` |
| `/sa:clarify <description>` | Turn a free-form REQ/CR (or already-ingested files) into a structured requirements list. | `req-analyst` |
| `/sa:design <slug> [--model=<name>] [--apply-review[=<severity>]]` | High-Level Design (HLD) — approach, components, NFRs/security/deployment posture, risks, phasing, and a full requirements traceability matrix. `--apply-review` revises against `review.md` findings instead. | `req-architect` |
| `/sa:review <slug> [--model=opus\|sonnet\|haiku\|fable]` | Narrative critique of the design (HLD, and LLD once it exists) against requirements — no gate. `--model` is opt-in per-run; `opus` recommended for a high-stakes/client-facing pass, unset otherwise. | `req-reviewer` |
| `/sa:design-detail <slug>` | Low-Level Design (LLD) — per-component interfaces, data model, key flows, deployment detail. | `req-detailer` |
| `/sa:estimate <slug>` | Three-point effort estimate from requirements + design. | `req-estimator` |
| `/sa:doc <slug>` | Consolidate whichever of the above exist into one package document. | none (direct) |

## The flow

```
[ inbound files, if any ]
        │
        ▼
   /sa:ingest          ← optional — Excel/Word/PDF/text → ai/sa/<slug>/inputs/*.extracted.md
        │
        ▼
   /sa:clarify          ← requirements.md (from ingested inputs and/or free-form description)
        │
        ▼
   /sa:design            ← architecture.md — the HLD
        │
        ▼
   /sa:review             ← review.md — narrative findings, no gate; revise the HLD if warranted
        │
        ▼
   /sa:design-detail        ← detailed-design.md — the LLD
        │
        ▼
   /sa:estimate               ← estimation.md
        │
        ▼
   /sa:doc                      ← package.md — everything consolidated for a stakeholder
```

Every arrow is a suggestion, not an enforced gate — `/sa:estimate` doesn't refuse to run because
`/sa:review` hasn't happened, for instance. Skip a step when the topic doesn't need it (a small CR usually
doesn't need `/sa:ingest` or a separate LLD pass at all).

## Shared conventions
- Artifacts are slugged per-topic: `ai/sa/<slug>/requirements.md`, `architecture.md`, `review.md`,
  `detailed-design.md`, `estimation.md`, `package.md`, `inputs/*.extracted.md` — so multiple REQ/CRs
  analyzed over time in the same project don't collide.
- `req-analyst`/`req-architect`/`req-reviewer`/`req-detailer`/`req-estimator`/`req-ingestor` are named
  with a `req-` prefix, not `solution-architect`/`project-estimator`/`sa-design-critic`, specifically to
  avoid colliding with domain-specific agents of those names in other installed frameworks.
- No formal gates, anywhere in this pipeline. `req-analyst` marks unclear items `to_clarify` rather than
  blocking; `req-architect`, `req-detailer`, and `req-estimator` note open questions/coverage gaps in
  their own reports rather than refusing to proceed; `req-reviewer` produces findings, never a
  PASS/BLOCKING verdict.
- `req-ingestor` is purely mechanical — it never interprets extracted content as a requirement. That
  judgment call belongs to `req-analyst`, one step later, working from what `req-ingestor` wrote.
- `req-estimator` never invents a rate card — no rates file found means effort-only output, stated
  explicitly.
- All agents read the target project's `CLAUDE.md`/`ai/context/*.md` if run inside one, and proceed
  standalone (saying so) if not — this pipeline works before a project even exists yet.
- `.xlsx`/`.xls`/`.docx` extraction uses the `office-doc-reader` skill (`~/.claude/skills/office-doc-reader/`).
  `.pdf` extraction uses Claude's built-in `Read` tool directly — no separate skill needed for that format.

This command performs no live analysis — it only prints the reference above.
</reference>
