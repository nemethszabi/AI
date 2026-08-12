---
name: sa:estimate-review
description: Independently critique an existing estimate against sa-framework/ESTIMATION-METHOD.md, via req-estimate-critic — advisory findings and recommended adjustments, no pass/fail gate.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Agent
  - AskUserQuestion
  - Edit
  - Write
argument-hint: "<slug from /sa:estimate>"
---

> Version: 1.0.0

<objective>
`/sa:estimate-review [slug]` critiques `ai/sa/<slug>/estimation.json` against the binding method in
`sa-framework/ESTIMATION-METHOD.md` via `req-estimate-critic`, writing
`ai/sa/<slug>/estimate-review.json` and `ai/sa/<slug>/estimate-review.md`. Run it after `/sa:estimate` and
before `/sa:offer` or `/sa:package` — an optimistic spread or an unpriced risk is far cheaper to fix
before it reaches a client-facing document than after. Advisory only: nothing here blocks the next step.
</objective>

<process>
<step name="resolve-slug">
Same resolution as `/sa:estimate`: explicit argument if it names an existing `ai/sa/<slug>/`, else glob
`ai/sa/*/estimation.json` (exactly one → use it; multiple → ask via `AskUserQuestion` which topic; none →
tell the user to run `/sa:estimate` first).
</step>

<step name="check-preconditions">
Confirm `ai/sa/<slug>/estimation.json` exists. If it does not, stop with:

`No estimation.json in ai/sa/<slug>/ — run /sa:estimate first. There is nothing to review.`

If `ai/sa/<slug>/estimation.md` exists but `estimation.json` does not, say so explicitly — the critic reads
the JSON, and a rendered Markdown estimate alone means the estimate predates the `ARTIFACT-SCHEMAS.md`
dual-output rule and must be re-run through `/sa:estimate`. Do not dispatch in either case.
</step>

<step name="dispatch">
Dispatch to `req-estimate-critic` via `Agent`. Give it the resolved slug and project path.
</step>

<step name="update-state">
Update `ai/sa/<slug>/STATE.md` in the canonical shape defined in `sa-framework/ARTIFACT-SCHEMAS.md §6`:
phase `estimate-review`, last command `/sa:estimate-review`, next `/sa:offer` — or `/sa:estimate` if the
recommended adjustments are being accepted. Append to phase history; never rewrite prior lines.
</step>

<step name="relay">
Return the agent's summary (finding count by severity, stated-vs-adjusted Likely totals and contingency %,
lifecycle-gap count, any dimension left unchecked) and both file paths written. State that this is advisory
— nothing here blocks `/sa:offer` or `/sa:package`; the recommended adjustments are the human's and the
estimator's to accept or reject.
</step>
</process>

<rules>
- **Thin dispatcher only.** All critique reasoning happens inside `req-estimate-critic`; never restate a
  threshold or a band from `ESTIMATION-METHOD.md` here.
- **Never edit `estimation.json` on the critic's recommendation.** Accepting an adjustment means re-running
  `/sa:estimate`, so the estimator owns its own artifact and the revision history stays honest.
</rules>
