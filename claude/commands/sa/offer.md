---
name: sa:offer
description: Compose a client-facing solution offer from an engagement's completed artifacts, via req-offer.
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
`/sa:offer <slug>` composes a client-facing solution offer from `ai/sa/<slug>/`'s completed artifacts via
`req-offer`, writing `offer.json` and the rendered `offer.md`. This produces the offer's **content**;
`/sa:package offer` turns it into the actual DOCX.
</objective>

<process>
<step name="resolve-slug">
Same resolution as `/sa:design`: explicit argument if it names an existing `ai/sa/<slug>/`, else glob
`ai/sa/*/engagement.json` (exactly one → use it; multiple → ask; none → tell the user to run `/sa:triage`
first).
</step>

<step name="check-preconditions">
`engagement.json` and `requirements.json` are required — stop and name whichever is missing.

Then read `lane` from `engagement.json` and report which of the lane's expected inputs are absent before
dispatching: on `offer-sow`, that's `architecture.json`, `risk-register.json` and `estimation.json`. An
offer can still be composed without them, but the human should choose that knowingly rather than discover
it in the output — say what will be missing and let them proceed or stop.
</step>

<step name="dispatch">
Dispatch to `req-offer` via `Agent`. Give it the resolved slug and project path.
</step>

<step name="update-state">
Update `ai/sa/<slug>/STATE.md`: phase `offer`, last command `/sa:offer`, next `/sa:audit`. Append to phase
history.
</step>

<step name="relay">
Return the agent's summary — commercial basis and why, headline effort or range, scope and exclusion
counts, the `must`-coverage check, client dependencies raised — plus the file paths written. Then remind
the user that `/sa:audit` must pass before `/sa:package` will build a deliverable.
</step>
</process>

<rules>
- **Thin dispatcher only.** All composition and commercial reasoning happens inside `req-offer`.
- **Never commit.** Writing artifacts is this pipeline's job; committing them is the human's.
</rules>
