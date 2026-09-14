---
name: sa:review
description: Review a design (HLD and/or LLD) against its requirements list, via req-reviewer — severity-rated findings with a coverage count, no pass/fail gate here (refusal lives at /sa:package, on the /sa:audit and /sa:slop-check verdicts). Writes review.json plus a rendered review.md. Takes --model; run it on a different model than produced the design.
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Agent
  - AskUserQuestion
argument-hint: "<slug from /sa:clarify> [--model=sonnet|opus|haiku|fable]"
---

> Version: 2.2.0 — minor: relay names `SendMessage` follow-ups to the same reviewer and their fallback
> (`AGENT-TEMPLATE-BASELINE.md` §3). 2.1.0: `--model` guidance rewritten from "stronger model" to
> "different model than produced the design" (`ARTIFACT-SCHEMAS.md` §9), and a reminder added when no
> override was given.

<objective>
`/sa:review <slug> [--model=<model>]` reviews `ai/sa/<slug>/architecture.json` (and `detailed-design.json`
if it exists) against `ai/sa/<slug>/requirements.json` via `req-reviewer`, writing
`ai/sa/<slug>/review.json` and the rendered `review.md`. Run this after `/sa:design` and before
`/sa:design-detail` — catching a coverage gap or a shaky alternative in the HLD is cheaper than catching it
after the LLD is built on top of it. Re-run after `/sa:design-detail` too, if you want the LLD checked
against the HLD as well.

`--model` is optional, opt-in only — omit it and the review runs on whatever model the session is already
using. Review is a judgment-heavy critic role (catching a weak alternatives-considered table, a
disproportionate component, a missed integration risk), which is exactly the case worth overriding for on a
high-stakes or client-facing pass.

**Pick a model different from the one that produced the design, not merely a stronger one**
(`sa-framework/ARTIFACT-SCHEMAS.md §9`, `AGENT-CONDUCT-BASELINE.md` B10). The point is decorrelated error:
the model that found an architectural assumption reasonable enough to write down is the one least likely to
challenge it. If the HLD was written on `opus`, review on `sonnet` — a same-family `opus → opus` pass is the
weakest configuration available, and "stronger model" is not a substitute for "different model".
</objective>

<process>
<step name="resolve-slug">
Same resolution as `/sa:design`: explicit argument if it names an existing `ai/sa/<slug>/requirements.json`,
else glob `ai/sa/*/requirements.json` (exactly one match → use it; multiple → ask via `AskUserQuestion` which
topic; none → tell the user to run `/sa:clarify` first). Parse `--model=<value>` out of `$ARGUMENTS`
wherever it appears; valid values are `sonnet`, `opus`, `haiku`, `fable`. Reject and ask for correction if
some other value is given rather than silently ignoring it.
</step>

<step name="dispatch">
Dispatch to `req-reviewer` via `Agent`. Give it the resolved slug and project path. If `--model` was set,
pass it as the model override on the `Agent` dispatch itself — this overrides `req-reviewer.md`'s own
frontmatter (which stays unset, no pinned default) for this run only, per-invocation, not a lasting change
to the agent.
</step>

<step name="update-state">
Update `ai/sa/<slug>/STATE.md` in the canonical shape from `sa-framework/ARTIFACT-SCHEMAS.md §6`. Set
`Phase` to `review`, `Last command` to `/sa:review`, `Last update` to the current ISO 8601 UTC timestamp,
and `Next` to exactly one command — `/sa:design-detail` on the `full-design` lane, `/sa:risk` on
`offer-sow` (read `lane` from `engagement.json`). Append one line to `## Phase history`:

```
- <YYYY-MM-DD HH:MM UTC> — review — <n> findings (<n> high), <n>/<n> requirements traced
```

Append only. Never rewrite or drop a prior history line, and never leave `Next` naming two commands.
</step>

<step name="relay">
Return the agent's summary (what was in `scope_reviewed` with revisions, finding count by severity, the
coverage headline naming every `must_untraced` REQ-ID), which model actually ran the review (so a
`--model` request is visibly confirmed, not just assumed), and both file paths written. Remind the
user this produces findings for their own disposition, not a gate — nothing here blocks the `Next` command;
refusal in this pipeline happens at `/sa:package`, on the `/sa:audit` and `/sa:slop-check` verdicts, which is
a deliberate split, not an oversight.

If `--model` was not given, add one line:

```
Review ran on the session model — the same one that produced the design.
Re-run with --model=<a different one> before this design underwrites a priced offer.
```

Then add one line: questions about a finding go to that **same** `req-reviewer` via `SendMessage` to the
agent id this dispatch returned. It still holds the design and its reasoning, and it stays on the model
that ran the review, so the cross-model separation holds. Its answers explain findings. Changing one
means re-running `/sa:review`, because `--apply-review` reads only `review.json`. If that agent is gone, the
fallback is `review.json` plus the JSON paths each finding cites, not a fresh dispatch.
</step>
</process>

<rules>
- **Thin dispatcher only.** All review reasoning happens inside `req-reviewer`.
- **Never commit.** Writing artifacts is this pipeline's job; committing them is the human's.
- **Model override is per-invocation only.** Never write a `model:` line into `req-reviewer.md`'s own
  frontmatter as a side effect of someone using `--model` once — that would pin a default for every future
  run, which is exactly what this flag is designed to avoid.
</rules>
