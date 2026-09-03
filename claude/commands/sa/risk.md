---
name: sa:risk
description: Produce a scored risk register and compliance register for an engagement, via req-risk-officer.
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Agent
  - AskUserQuestion
argument-hint: "<slug from /sa:triage>"
---

> Version: 1.0.0

<objective>
`/sa:risk <slug>` produces a scored risk register and compliance register from `ai/sa/<slug>/`'s
requirements and architecture via `req-risk-officer`, writing `risk-register.json` and the rendered
`risk-register.md`. Its `contingency_recommendation` is the input `/sa:estimate` consumes — run this
before estimating, not after.
</objective>

<process>
<step name="resolve-slug">
Same resolution as `/sa:design`: explicit argument if it names an existing `ai/sa/<slug>/`, else glob
`ai/sa/*/architecture.json` (exactly one → use it; multiple → ask; none → tell the user to run
`/sa:design` first).
</step>

<step name="check-preconditions">
`architecture.json` is required except on the `rom` lane (read `lane` from `engagement.json`). If it's
missing on any other lane, stop and say which command produces it. On `rom`, proceed from
`requirements.json` alone and tell the user the register will be provisional.
</step>

<step name="dispatch">
Dispatch to `req-risk-officer` via `Agent`. Give it the resolved slug and project path.
</step>

<step name="update-state">
Update `ai/sa/<slug>/STATE.md`: phase `risk`, last command `/sa:risk`, next `/sa:estimate`. Append to
phase history.
</step>

<step name="relay">
Return the agent's summary — risk counts by derived severity, compliance obligations and how many are
blocking, the recommended contingency percentage, and how many risks are not priced in — plus the file
paths written.
</step>
</process>

<rules>
- **Thin dispatcher only.** All scoring, derivation and treatment reasoning happens inside
  `req-risk-officer`.
- **Never commit.** Writing artifacts is this pipeline's job; committing them is the human's.
</rules>
