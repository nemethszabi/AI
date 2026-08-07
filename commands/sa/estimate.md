---
name: sa:estimate
description: Produce a three-point effort estimate tied to a requirements list and design proposal, via req-estimator.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Agent
  - AskUserQuestion
argument-hint: "<slug from /sa:clarify>"
---

<objective>
`/sa:estimate <slug>` produces a three-point effort estimate from `ai/sa/<slug>/requirements.md` and
`ai/sa/<slug>/architecture.md` via `req-estimator`, writing `ai/sa/<slug>/estimation.md`.
</objective>

<process>
<step name="resolve-slug">
Same resolution as `/sa:design`: explicit argument if it names an existing `ai/sa/<slug>/`, else glob
`ai/sa/*/architecture.md` (exactly one → use it; multiple → ask; none → tell the user to run `/sa:design`
first).
</step>

<step name="dispatch">
Dispatch to `req-estimator` via `Agent`. Give it the resolved slug and project path.
</step>

<step name="relay">
Return the agent's summary (Likely totals, contingency %, must-priority coverage check) and the file path
written.
</step>
</process>

<rules>
- **Thin dispatcher only.** All estimation reasoning happens inside `req-estimator`.
</rules>
