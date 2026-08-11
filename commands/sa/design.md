---
name: sa:design
description: Turn a clarified requirements list into a design/architecture proposal, via req-architect.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Agent
  - AskUserQuestion
argument-hint: "<slug from /sa:clarify>"
---

> Version: 1.0.0

<objective>
`/sa:design <slug>` produces a design/architecture proposal from `ai/sa/<slug>/requirements.md` via
`req-architect`, writing `ai/sa/<slug>/architecture.md`.
</objective>

<process>
<step name="resolve-slug">
If `$ARGUMENTS` names an existing `ai/sa/<slug>/requirements.md`, use it. Otherwise glob
`ai/sa/*/requirements.md`: exactly one match → use it; more than one → ask via `AskUserQuestion` which
topic; none → tell the user to run `/sa:clarify` first.
</step>

<step name="dispatch">
Dispatch to `req-architect` via `Agent`. Give it the resolved slug and project path.
</step>

<step name="relay">
Return the agent's summary (chosen approach, component count, any unaddressed `must`-priority requirement)
and the file path written.
</step>
</process>

<rules>
- **Thin dispatcher only.** All design reasoning happens inside `req-architect`.
</rules>
