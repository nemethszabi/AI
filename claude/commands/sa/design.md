---
name: sa:design
description: Turn a clarified requirements list into a design/architecture proposal, via req-architect.
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Agent
  - AskUserQuestion
argument-hint: "<slug from /sa:clarify> [--model=<name>, optional] [--apply-review[=<severity>], optional — revise the existing HLD against ai/sa/<slug>/review.json's findings at or above <severity> (default: high)]"
---

> Version: 2.0.0

<objective>
`/sa:design <slug>` produces a High-Level Design (HLD) from `ai/sa/<slug>/requirements.json` via
`req-architect`, writing `ai/sa/<slug>/architecture.json` and the rendered `architecture.md`, then generates
the diagrams the HLD calls for via `mermaid-diagram-maker`. For interface/data-model/deployment-level detail
(the LLD), run `/sa:review` against this HLD first, then `/sa:design-detail`.

Pass `--apply-review` to instead revise an existing HLD against its own `ai/sa/<slug>/review.json` findings —
a full rewrite driven by that review's `findings[]`, filtered to the requested severity, not a fresh design.
Re-run `/sa:review` afterward to confirm the fixes landed.
</objective>

<process>
<step name="parse-model-override">
If `$ARGUMENTS` contains `--model=<name>`, extract it and strip it from the remaining arguments before
slug resolution. This is optional — omit it and the dispatch inherits whatever model the calling session
is running under. Reach for it only when the design is genuinely novel or high-stakes (no close precedent
in the codebase, or the cost of a wrong recommendation is high) — not as a default.
</step>

<step name="parse-apply-review-flag">
If `$ARGUMENTS` contains `--apply-review` or `--apply-review=<severity>`, extract it and strip it from the
remaining arguments before slug resolution. `<severity>` is one of `high`, `medium`, `low`
(case-insensitive) — the minimum severity of `review.json` findings to apply; omit the value and it defaults
to `high` only. Optional — omit the flag entirely for a normal fresh/overwrite design run.
</step>

<step name="resolve-slug">
If the remaining `$ARGUMENTS` names an existing `ai/sa/<slug>/requirements.json`, use it. Otherwise glob
`ai/sa/*/requirements.json`: exactly one match → use it; more than one → ask via `AskUserQuestion` which
topic; none → tell the user to run `/sa:clarify` first. If `--apply-review` was passed, also require
`ai/sa/<slug>/review.json` to exist — if it doesn't, tell the user to run `/sa:review` first instead of
dispatching.
</step>

<step name="dispatch">
Dispatch to `req-architect` via `Agent`. Give it the resolved slug and project path. If a model override
was parsed above, pass it as the `Agent` tool's `model` parameter for this dispatch. If `--apply-review` was
parsed, tell it explicitly to run its revision pass against `review.json` at the given severity threshold
rather than producing a fresh design.
</step>

<step name="generate-diagrams">
Dispatch to `mermaid-diagram-maker` via `Agent`: give it the `Diagrams` section of the `architecture.md`
just written (which diagrams it named, and why) and instruct it to write output to
`ai/sa/<slug>/diagrams/` — not its default `docs/diagrams/` — using the exact filenames the HLD already
references, so the paths `architecture.md` points to resolve. Skip this step if the `Diagrams` section says
none are warranted.
</step>

<step name="update-state">
Update `ai/sa/<slug>/STATE.md` in the canonical shape from `sa-framework/ARTIFACT-SCHEMAS.md §6`. Set
`Phase` to `design`, `Last command` to `/sa:design`, `Last update` to the current ISO 8601 UTC timestamp,
and `Next` to exactly one command — `/sa:review` on the `full-design` lane, `/sa:risk` on `offer-sow` (read
`lane` from `engagement.json`). Append one line to `## Phase history`:

```
- <YYYY-MM-DD HH:MM UTC> — design — HLD written (<n> components), <n> diagrams generated
```

Append only. Never rewrite or drop a prior history line, and never leave `Next` naming two commands.
Create `STATE.md` in the canonical shape if it doesn't exist.
</step>

<step name="relay">
Return `req-architect`'s summary (chosen approach, component count, integrations by confidence, any
unaddressed `must`-priority requirement) and `mermaid-diagram-maker`'s summary (diagram file paths), plus
both file paths written for the HLD. If this was an `--apply-review` run, also relay which findings were
applied (by `F-` ID) and any new IDs introduced, and remind the user to re-run `/sa:review`. Otherwise name
the `Next` command you just wrote into `STATE.md`.
</step>
</process>

<rules>
- **Thin dispatcher only.** All design reasoning happens inside `req-architect`; all diagram drawing happens
  inside `mermaid-diagram-maker`.
- **Never commit.** Writing artifacts is this pipeline's job; committing them is the human's.
- **Model override is per-invocation only.** Never write a `model:` line into `req-architect.md`'s own
  frontmatter as a side effect of someone using `--model` once — that would pin a default for every future
  run, which is exactly what this flag is designed to avoid.
</rules>
