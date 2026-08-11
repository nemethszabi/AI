---
name: sa:design
description: Turn a clarified requirements list into a design/architecture proposal, via req-architect.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Agent
  - AskUserQuestion
argument-hint: "<slug from /sa:clarify> [--model <name>, optional — escalate for a genuinely novel/high-stakes design]"
---

> Version: 1.1.0

<objective>
`/sa:design <slug>` produces a High-Level Design (HLD) from `ai/sa/<slug>/requirements.md` via
`req-architect`, writing `ai/sa/<slug>/architecture.md`. For interface/data-model/deployment-level detail
(the LLD), run `/sa:review` against this HLD first, then `/sa:design-detail`.
</objective>

<process>
<step name="parse-model-override">
If `$ARGUMENTS` contains `--model <name>`, extract it and strip it from the remaining arguments before
slug resolution. This is optional — omit it and the dispatch inherits whatever model the calling session
is running under. Reach for it only when the design is genuinely novel or high-stakes (no close precedent
in the codebase, or the cost of a wrong recommendation is high) — not as a default.
</step>

<step name="resolve-slug">
If the remaining `$ARGUMENTS` names an existing `ai/sa/<slug>/requirements.md`, use it. Otherwise glob
`ai/sa/*/requirements.md`: exactly one match → use it; more than one → ask via `AskUserQuestion` which
topic; none → tell the user to run `/sa:clarify` first.
</step>

<step name="dispatch">
Dispatch to `req-architect` via `Agent`. Give it the resolved slug and project path. If a model override
was parsed above, pass it as the `Agent` tool's `model` parameter for this dispatch.
</step>

<step name="relay">
Return the agent's summary (chosen approach, component count, any unaddressed `must`-priority requirement)
and the file path written. Mention `/sa:review` as the recommended next step before `/sa:design-detail`.
</step>
</process>

<rules>
- **Thin dispatcher only.** All design reasoning happens inside `req-architect`.
</rules>
