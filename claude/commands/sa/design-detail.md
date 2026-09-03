---
name: sa:design-detail
description: Turn a reviewed High-Level Design into a Low-Level Design — per-component interfaces, data model, key flows, deployment detail — via req-detailer. Writes detailed-design.json plus a rendered detailed-design.md. Full-design lane only; stops without dispatching on rom and offer-sow.
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Agent
  - AskUserQuestion
argument-hint: "<slug from /sa:clarify>"
---

> Version: 2.0.0

<objective>
`/sa:design-detail <slug>` produces a Low-Level Design from `ai/sa/<slug>/architecture.json` (the HLD) via
`req-detailer`, writing `ai/sa/<slug>/detailed-design.json` and the rendered `detailed-design.md`, then
generates any diagrams the LLD calls for via `mermaid-diagram-maker`. Normally the step after `/sa:design`
and `/sa:review` — detail what was already reviewed, not what's still shaky.

**`full-design` lane only.** On `rom` and `offer-sow` this command stops without dispatching.
</objective>

<process>
<step name="resolve-slug">
Same resolution as `/sa:design`, but require `architecture.json` specifically (not just
`requirements.json`): if `$ARGUMENTS` names an existing `ai/sa/<slug>/architecture.json`, use it. Otherwise
glob `ai/sa/*/architecture.json`: exactly one match → use it; more than one → ask via `AskUserQuestion` which
topic; none → tell the user to run `/sa:design` first.
</step>

<step name="check-lane">
Read `lane` from `ai/sa/<slug>/engagement.json`. If it is not `full-design`, stop here — do not dispatch,
do not touch `STATE.md` — and say exactly this:

```
Lane is <lane>. An LLD is a full-design deliverable only, so /sa:design-detail does nothing here.
Run /sa:triage <slug> to move the engagement to full-design if an LLD is genuinely wanted.
Otherwise the next step on the <lane> lane is <the Next command in ai/sa/<slug>/STATE.md>.
```

If `engagement.json` is missing, stop and tell the user to run `/sa:triage` first rather than assuming a
lane — an LLD is the most expensive pass in this pipeline and the wrong one to run on a guess.
</step>

<step name="check-review">
If `ai/sa/<slug>/review.json` doesn't exist yet, proceed anyway but mention in the final relay that running
`/sa:review` first is recommended — this command doesn't block on it, since design review is deliberately
non-gating in this pipeline (`/sa:audit` is the gate).
</step>

<step name="dispatch">
Dispatch to `req-detailer` via `Agent`. Give it the resolved slug and project path.
</step>

<step name="generate-diagrams">
Dispatch to `mermaid-diagram-maker` via `Agent`: give it the `Diagrams` section of the rendered
`detailed-design.md` just written and instruct it to write output to `ai/sa/<slug>/diagrams/` — the same
folder the HLD's own diagrams already live in — using the exact filenames the LLD already references. Skip
this step if the `Diagrams` section says none are warranted beyond the HLD's own diagrams.
</step>

<step name="update-state">
Update `ai/sa/<slug>/STATE.md` in the canonical shape from `sa-framework/ARTIFACT-SCHEMAS.md §6`. Set
`Phase` to `design-detail`, `Last command` to `/sa:design-detail`, `Last update` to the current ISO 8601
UTC timestamp, and `Next` to exactly one command — the first of these whose artifact is still missing:
`/sa:risk` (no `risk-register.json`), then `/sa:estimate` (no `estimation.json`), otherwise `/sa:audit`.
Append one line to `## Phase history`:

```
- <YYYY-MM-DD HH:MM UTC> — design-detail — LLD written (<n> components detailed)
```

Append only. Never rewrite or drop a prior history line, and never leave `Next` naming two commands.
</step>

<step name="relay">
Return `req-detailer`'s summary (`C-` IDs detailed and any left out of scope, any open question that could
invalidate the HLD) and `mermaid-diagram-maker`'s summary (diagram file paths, if any were generated), plus
both file paths written and the `Next` command you wrote into `STATE.md`.
</step>
</process>

<rules>
- **Thin dispatcher only.** All design reasoning happens inside `req-detailer`; all diagram drawing happens
  inside `mermaid-diagram-maker`.
- **`full-design` lane only.** Stop on any other lane rather than producing an LLD nobody's deliverables
  include. `/sa:triage` is what changes a lane, not this command.
- **Never commit.** Writing artifacts is this pipeline's job; committing them is the human's.
</rules>
