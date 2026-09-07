---
name: sa:audit
description: Cross-artifact validation gate — verifies the engagement's JSON artifacts agree with each other by ID, via req-auditor, and emits one of the two verdicts /sa:package requires. /sa:slop-check emits the other, checking the prose rather than the IDs; a clean audit is not clearance to send.
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Agent
argument-hint: "<slug from /sa:triage> [--model=sonnet|opus|haiku|fable]"
---

> Version: 1.1.0 — minor: added the `--model` per-invocation override and a pointer to the second gate
> (`ARTIFACT-SCHEMAS.md` §5, §9).

<objective>
`/sa:audit <slug> [--model=<model>]` runs `req-auditor` over `ai/sa/<slug>/`'s artifacts, writing a
timestamped report to `ai/sa/<slug>/audit/` that ends with a fenced `sa-verdict` block carrying
`gate: sa-audit` and a content-based `inputs_hash`.

This is **one of the two verdicts `/sa:package` requires** (`sa-framework/ARTIFACT-SCHEMAS.md §5`): this one
checks that the JSON artifacts agree with each other by ID; `/sa:slop-check` checks that the prose a human
will read is true to them. Both must pass on a matching hash — so re-run this after any artifact change, not
just once at the end, and don't mistake a clean audit for a clean document.

`--model` is optional and per-invocation. It matters **least** here of the four review commands, and that is
deliberate rather than an oversight: `req-auditor` is mechanical — set operations and arithmetic over IDs —
and mechanical checks are the least model-sensitive thing in this pipeline (§9). Spend the override on
`/sa:slop-check` and `/sa:estimate-review` first.
</objective>

<process>
<step name="resolve-slug">
Same resolution as `/sa:design`: explicit argument if it names an existing `ai/sa/<slug>/`, else glob
`ai/sa/*/engagement.json` (exactly one → use it; multiple → ask; none → tell the user to run `/sa:triage`
first). Parse `--model=<value>` out of `$ARGUMENTS` wherever it appears; valid values are `sonnet`, `opus`,
`haiku`, `fable`. Reject any other value rather than silently ignoring it.
</step>

<step name="dispatch">
Dispatch to `req-auditor` via `Agent`. Give it the resolved slug and project path. If `--model` was set,
pass it as the `Agent` dispatch's `model` parameter — per-invocation only; `req-auditor.md`'s own frontmatter
stays unpinned (`ARTIFACT-SCHEMAS.md §9`).
</step>

<step name="update-state">
Update `ai/sa/<slug>/STATE.md`: phase `audit`, last command `/sa:audit`, and set `Next` to — first match
wins — the specific command that fixes the first blocking finding on a `BLOCKED` verdict, else
`/sa:slop-check` if no fresh passing `sa-slop` verdict exists, else `/sa:package`. Append to phase history.

`/sa:package` is never the `Next` on a passing audit alone: it takes two verdicts, and naming it after one
of them is how a half-gated deliverable gets built.
</step>

<step name="relay">
Return the verdict, the blocking/advisory/waived counts, every blocking finding one line each, which model
ran the audit, and the report path. On `BLOCKED`, name the command that produces each fix — the point of the
gate is to tell the human what to run next, not merely that something is wrong.

On a passing verdict with no fresh `sa-slop` verdict, say plainly that packaging still needs
`/sa:slop-check <slug>` and that a clean audit says nothing about the prose: an offer whose every ID
resolves can still quote a figure no artifact contains.
</step>
</process>

<rules>
- **Thin dispatcher only.** All checking happens inside `req-auditor`.
- **Never re-interpret the verdict.** Relay it as issued — a gate a dispatcher can soften is not a gate
  (`CONSTITUTION.md` Article III).
- **Never present a passing audit as clearance to package.** It is one of two required verdicts
  (`ARTIFACT-SCHEMAS.md §5`).
- **Model override is per-invocation only** — never written into `req-auditor.md`'s frontmatter.
</rules>
