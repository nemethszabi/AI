---
name: sa:design-detail
description: Turn a reviewed High-Level Design into a Low-Level Design — per-component interfaces, data model, key flows, deployment detail — via req-detailer.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Agent
  - AskUserQuestion
argument-hint: "<slug from /sa:clarify>"
---

> Version: 1.1.1

<objective>
`/sa:design-detail <slug>` produces a Low-Level Design from `ai/sa/<slug>/architecture.md` (the HLD) via
`req-detailer`, writing `ai/sa/<slug>/detailed-design.md`, then generates any diagrams the LLD calls for via
`mermaid-diagram-maker`. Normally the step after `/sa:design` and `/sa:review` — detail what was already
reviewed, not what's still shaky.
</objective>

<process>
<step name="resolve-slug">
Same resolution as `/sa:design`, but require `architecture.md` specifically (not just
`requirements.md`): if `$ARGUMENTS` names an existing `ai/sa/<slug>/architecture.md`, use it. Otherwise
glob `ai/sa/*/architecture.md`: exactly one match → use it; more than one → ask via `AskUserQuestion` which
topic; none → tell the user to run `/sa:design` first.
</step>

<step name="check-review">
If `ai/sa/<slug>/review.md` doesn't exist yet, proceed anyway but mention in the final relay that running
`/sa:review` first is recommended — this command doesn't block on it, since the review step is
deliberately non-gating in this pipeline.
</step>

<step name="dispatch">
Dispatch to `req-detailer` via `Agent`. Give it the resolved slug and project path.
</step>

<step name="generate-diagrams">
Dispatch to `mermaid-diagram-maker` via `Agent`: give it the `Diagrams` section of the
`detailed-design.md` just written and instruct it to write output to `ai/sa/<slug>/diagrams/` — the same
folder the HLD's own diagrams already live in — using the exact filenames the LLD already references. Skip
this step if the `Diagrams` section says none are warranted beyond the HLD's own diagrams.
</step>

<step name="relay">
Return `req-detailer`'s summary (components detailed, any Open Question that could invalidate the HLD) and
`mermaid-diagram-maker`'s summary (diagram file paths, if any were generated), and the file path written.
</step>
</process>

<rules>
- **Thin dispatcher only.** All design reasoning happens inside `req-detailer`; all diagram drawing happens
  inside `mermaid-diagram-maker`.
</rules>
