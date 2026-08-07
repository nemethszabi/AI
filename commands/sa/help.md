---
name: sa:help
description: Static reference for the sa: command namespace. No live analysis, no project context read.
allowed-tools: []
---

<reference>
# `sa:` commands — lightweight Solution-Architect / REQ-CR pipeline

Global, generic — works in any project (or standalone, with no project at all) for the recurring
"analyze a new requirement/change request, produce a design and an estimate, generate documentation" need.
Deliberately lightweight: no verdict-blocks, no PASS/BLOCKING gates, no critic agents — narrative markdown
output, reviewed by you directly. Add rigor later only if it proves necessary.

| Command | Purpose | Dispatches to |
|---|---|---|
| `/sa:clarify <description>` | Turn a free-form REQ/CR into a structured requirements list. | `req-analyst` |
| `/sa:design <slug>` | Design/architecture proposal from the requirements list. | `req-architect` |
| `/sa:estimate <slug>` | Three-point effort estimate from requirements + design. | `req-estimator` |
| `/sa:doc <slug>` | Consolidate whichever of the above exist into one package document. | none (direct) |

## Shared conventions
- Artifacts are slugged per-topic: `ai/sa/<slug>/requirements.md`, `architecture.md`, `estimation.md`,
  `package.md` — so multiple REQ/CRs analyzed over time in the same project don't collide.
- `req-analyst`/`req-architect`/`req-estimator` are named with a `req-` prefix, not `solution-architect`/
  `project-estimator`, specifically to avoid colliding with domain-specific agents of those names in other
  installed frameworks.
- No formal gates. `req-analyst` marks unclear items `to_clarify` rather than blocking; `req-architect` and
  `req-estimator` note open questions/coverage gaps in their own reports rather than refusing to proceed.
- `req-estimator` never invents a rate card — no rates file found means effort-only output, stated
  explicitly.
- All three agents read the target project's `CLAUDE.md`/`ai/context/*.md` if run inside one, and proceed
  standalone (saying so) if not — this pipeline works before a project even exists yet.

This command performs no live analysis — it only prints the reference above.
</reference>
