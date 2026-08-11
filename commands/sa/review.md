---
name: sa:review
description: Review a design (HLD and/or LLD) against its requirements list, via req-reviewer — narrative findings, no pass/fail gate.
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
`/sa:review <slug>` reviews `ai/sa/<slug>/architecture.md` (and `detailed-design.md` if it exists) against
`ai/sa/<slug>/requirements.md` via `req-reviewer`, writing `ai/sa/<slug>/review.md`. Run this after
`/sa:design` and before `/sa:design-detail` — catching a coverage gap or a shaky alternative in the HLD is
cheaper than catching it after the LLD is built on top of it. Re-run after `/sa:design-detail` too, if you
want the LLD checked against the HLD as well.
</objective>

<process>
<step name="resolve-slug">
Same resolution as `/sa:design`: explicit argument if it names an existing `ai/sa/<slug>/requirements.md`,
else glob `ai/sa/*/requirements.md` (exactly one match → use it; multiple → ask via `AskUserQuestion` which
topic; none → tell the user to run `/sa:clarify` first).
</step>

<step name="dispatch">
Dispatch to `req-reviewer` via `Agent`. Give it the resolved slug and project path.
</step>

<step name="relay">
Return the agent's summary (finding count by severity, REQ-coverage headline) and the file path written.
Remind the user this produces findings for their own disposition, not a gate — nothing here blocks running
`/sa:design-detail` or `/sa:estimate` next; that's a deliberate choice for this decision, not an oversight.
</step>
</process>

<rules>
- **Thin dispatcher only.** All review reasoning happens inside `req-reviewer`.
</rules>
</output>
