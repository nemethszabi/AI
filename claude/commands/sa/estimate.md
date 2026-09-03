---
name: sa:estimate
description: Produce a three-point effort estimate tied to requirements, design and risk register, via req-estimator.
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

> Version: 2.0.0

<objective>
`/sa:estimate <slug>` produces a three-point effort estimate from `ai/sa/<slug>/`'s `requirements.json`,
`architecture.json` and `risk-register.json` via `req-estimator`, writing `estimation.json` and the
rendered `estimation.md`.

Effort only. Cost appears only if a rate card is configured, and even then as an input to a pricing
decision rather than as a price — see `sa-framework/ESTIMATION-METHOD.md §5`.
</objective>

<process>
<step name="resolve-slug">
Same resolution as `/sa:design`: explicit argument if it names an existing `ai/sa/<slug>/`, else glob
`ai/sa/*/requirements.json` (exactly one → use it; multiple → ask; none → tell the user to run
`/sa:clarify` first).
</step>

<step name="check-preconditions">
Read `lane` from `engagement.json`. `requirements.json` is always required. `architecture.json` is
required on every lane except `rom` — if it's missing elsewhere, stop and say `/sa:design` produces it.

If `risk-register.json` is absent on `offer-sow` or `full-design`, say so before dispatching: contingency
will be derived without a register and will be weaker for it. Recommend `/sa:risk` first, and let the user
decide rather than discovering it in the output.
</step>

<step name="dispatch">
Dispatch to `req-estimator` via `Agent`. Give it the resolved slug and project path.
</step>

<step name="update-state">
Update `ai/sa/<slug>/STATE.md` in the canonical shape from `sa-framework/ARTIFACT-SCHEMAS.md §6`: phase
`estimate`, last command `/sa:estimate`, next `/sa:estimate-review` (or `/sa:offer` on the `rom` lane).
Append to phase history; never rewrite prior lines.
</step>

<step name="relay">
Return the agent's summary — models estimated and their Likely totals, the contingency percentage and
where it came from, the must-coverage check, `not_estimated` count, and whether a rate card was found —
plus the file paths written.
</step>
</process>

<rules>
- **Thin dispatcher only.** All estimation reasoning happens inside `req-estimator`; never restate a
  factor, band or threshold from `ESTIMATION-METHOD.md` here.
- **Never present the output as a price.** If the agent reports effort-only, relay it that way.
- **Never commit.** Writing artifacts is this pipeline's job; committing them is the human's.
</rules>
