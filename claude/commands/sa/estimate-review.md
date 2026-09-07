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
argument-hint: "<slug from /sa:estimate> [--model=sonnet|opus|haiku|fable]"
---

> Version: 1.1.0 — minor: added the `--model` per-invocation override and the cross-model reminder
> (`ARTIFACT-SCHEMAS.md` §9 / `AGENT-CONDUCT-BASELINE.md` B10).

<objective>
`/sa:estimate-review [slug] [--model=<model>]` critiques `ai/sa/<slug>/estimation.json` against the binding
method in `sa-framework/ESTIMATION-METHOD.md` via `req-estimate-critic`, writing
`ai/sa/<slug>/estimate-review.json` and `ai/sa/<slug>/estimate-review.md`. Run it after `/sa:estimate` and
before `/sa:offer` or `/sa:package` — an optimistic spread or an unpriced risk is far cheaper to fix
before it reaches a client-facing document than after. Advisory only: nothing here blocks the next step.

`--model` is optional and per-invocation, and this is **one of the two commands where it matters most**
(`ARTIFACT-SCHEMAS.md §9`). The critic reads cold — never the estimator's reasoning — but by default it
reads on the estimator's *model*, and an estimate that felt right to produce will feel right to review. A
different model is what makes "independent" mean something beyond not having seen the working.
</objective>

<process>
<step name="resolve-slug">
Same resolution as `/sa:estimate`: explicit argument if it names an existing `ai/sa/<slug>/`, else glob
`ai/sa/*/estimation.json` (exactly one → use it; multiple → ask via `AskUserQuestion` which topic; none →
tell the user to run `/sa:estimate` first).

Parse `--model=<value>` out of `$ARGUMENTS` wherever it appears; valid values are `sonnet`, `opus`, `haiku`,
`fable`. Reject any other value and ask for a correction rather than silently ignoring it.
</step>

<step name="check-preconditions">
Confirm `ai/sa/<slug>/estimation.json` exists. If it does not, stop with:

`No estimation.json in ai/sa/<slug>/ — run /sa:estimate first. There is nothing to review.`

If `ai/sa/<slug>/estimation.md` exists but `estimation.json` does not, say so explicitly — the critic reads
the JSON, and a rendered Markdown estimate alone means the estimate predates the `ARTIFACT-SCHEMAS.md`
dual-output rule and must be re-run through `/sa:estimate`. Do not dispatch in either case.
</step>

<step name="dispatch">
Dispatch to `req-estimate-critic` via `Agent`. Give it the resolved slug and project path. If `--model` was
set, pass it as the `Agent` dispatch's `model` parameter — this overrides nothing permanently and
`req-estimate-critic.md`'s own frontmatter stays unpinned, per `ARTIFACT-SCHEMAS.md §9`.
</step>

<step name="update-state">
Update `ai/sa/<slug>/STATE.md` in the canonical shape defined in `sa-framework/ARTIFACT-SCHEMAS.md §6`:
phase `estimate-review`, last command `/sa:estimate-review`, next `/sa:offer` — or `/sa:estimate` if the
recommended adjustments are being accepted. Append to phase history; never rewrite prior lines.
</step>

<step name="relay">
Return the agent's summary (finding count by severity, stated-vs-adjusted Likely totals and contingency %,
lifecycle-gap count, any dimension left unchecked), **which model actually ran the critique**, and both file
paths written. State that this is advisory — nothing here blocks `/sa:offer` or `/sa:package`; the
recommended adjustments are the human's and the estimator's to accept or reject.

If `--model` was not given, add one line:

```
Critique ran on the session model — the same one that produced the estimate.
Re-run with --model=<a different one> before this number reaches a client.
```

Never describe a cross-model pass as "independently verified" — sibling models share training lineage and
therefore share blind spots. It reduces correlated error; it is not a second estimator.
</step>
</process>

<rules>
- **Thin dispatcher only.** All critique reasoning happens inside `req-estimate-critic`; never restate a
  threshold or a band from `ESTIMATION-METHOD.md` here.
- **Never edit `estimation.json` on the critic's recommendation.** Accepting an adjustment means re-running
  `/sa:estimate`, so the estimator owns its own artifact and the revision history stays honest.
- **Model override is per-invocation only.** Never write a `model:` line into `req-estimate-critic.md`'s own
  frontmatter as a side effect of someone using `--model` once — pinning a reviewer's model makes it wrong
  the moment the estimator's model changes (`ARTIFACT-SCHEMAS.md §9`).
- **Always report which model ran.** A same-model critique is worth less than a cross-model one, and the
  reader is entitled to know which they got.
</rules>
