---
name: sa:design
description: Turn a clarified requirements list into a design/architecture proposal, via req-architect.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Agent
  - AskUserQuestion
argument-hint: "<slug from /sa:clarify> [--model <name>, optional] [--apply-review[=<severity>], optional — revise the existing HLD against ai/sa/<slug>/review.md's findings at or above <severity> (default: High)]"
---

> Version: 1.2.0

<objective>
`/sa:design <slug>` produces a High-Level Design (HLD) from `ai/sa/<slug>/requirements.md` via
`req-architect`, writing `ai/sa/<slug>/architecture.md`, then generates the diagrams the HLD calls for via
`mermaid-diagram-maker`. For interface/data-model/deployment-level detail (the LLD), run `/sa:review`
against this HLD first, then `/sa:design-detail`.

Pass `--apply-review` to instead revise an existing HLD against its own `ai/sa/<slug>/review.md` findings —
a full rewrite driven by the review's Findings table (filtered to the requested severity), not a fresh
design. Re-run `/sa:review` afterward to confirm the fixes landed.
</objective>

<process>
<step name="parse-model-override">
If `$ARGUMENTS` contains `--model <name>`, extract it and strip it from the remaining arguments before
slug resolution. This is optional — omit it and the dispatch inherits whatever model the calling session
is running under. Reach for it only when the design is genuinely novel or high-stakes (no close precedent
in the codebase, or the cost of a wrong recommendation is high) — not as a default.
</step>

<step name="parse-apply-review-flag">
If `$ARGUMENTS` contains `--apply-review` or `--apply-review=<severity>`, extract it and strip it from the
remaining arguments before slug resolution. `<severity>` is one of `High`, `Medium`, `Low`
(case-insensitive) — the minimum severity of `review.md` findings to apply; omit the value and it defaults
to `High` only. Optional — omit the flag entirely for a normal fresh/overwrite design run.
</step>

<step name="resolve-slug">
If the remaining `$ARGUMENTS` names an existing `ai/sa/<slug>/requirements.md`, use it. Otherwise glob
`ai/sa/*/requirements.md`: exactly one match → use it; more than one → ask via `AskUserQuestion` which
topic; none → tell the user to run `/sa:clarify` first. If `--apply-review` was passed, also require
`ai/sa/<slug>/review.md` to exist — if it doesn't, tell the user to run `/sa:review` first instead of
dispatching.
</step>

<step name="dispatch">
Dispatch to `req-architect` via `Agent`. Give it the resolved slug and project path. If a model override
was parsed above, pass it as the `Agent` tool's `model` parameter for this dispatch. If `--apply-review` was
parsed, tell it explicitly to run its revision pass against `review.md` at the given severity threshold
rather than producing a fresh design.
</step>

<step name="generate-diagrams">
Dispatch to `mermaid-diagram-maker` via `Agent`: give it the `Diagrams` section of the `architecture.md`
just written (which diagrams it named, and why) and instruct it to write output to
`ai/sa/<slug>/diagrams/` — not its default `docs/diagrams/` — using the exact filenames the HLD already
references, so the paths `architecture.md` points to resolve. Skip this step if the `Diagrams` section says
none are warranted.
</step>

<step name="relay">
Return `req-architect`'s summary (chosen approach, component count, any unaddressed `must`-priority
requirement) and `mermaid-diagram-maker`'s summary (diagram file paths), plus the file path written for
`architecture.md`. If this was an `--apply-review` run, also relay which findings were applied (by number)
and any new IDs introduced, and remind the user to re-run `/sa:review`. Otherwise mention `/sa:review` as
the recommended next step before `/sa:design-detail`.
</step>
</process>

<rules>
- **Thin dispatcher only.** All design reasoning happens inside `req-architect`; all diagram drawing happens
  inside `mermaid-diagram-maker`.
</rules>
