---
name: sa:audit
description: Cross-artifact validation gate — verifies the engagement's artifacts agree with each other and emits the verdict /sa:package requires, via req-auditor.
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Agent
argument-hint: "<slug from /sa:triage>"
---

> Version: 1.0.0

<objective>
`/sa:audit <slug>` runs `req-auditor` over `ai/sa/<slug>/`'s artifacts, writing a timestamped report to
`ai/sa/<slug>/audit/` that ends with a fenced `sa-verdict` block carrying a content-based `inputs_hash`.

`/sa:package` refuses to build a client deliverable without a `PASS` or `PASS-WITH-WAIVERS` from this
command **on a matching hash** — so re-run it after any artifact change, not just once at the end.
</objective>

<process>
<step name="resolve-slug">
Same resolution as `/sa:design`: explicit argument if it names an existing `ai/sa/<slug>/`, else glob
`ai/sa/*/engagement.json` (exactly one → use it; multiple → ask; none → tell the user to run `/sa:triage`
first).
</step>

<step name="dispatch">
Dispatch to `req-auditor` via `Agent`. Give it the resolved slug and project path.
</step>

<step name="update-state">
Update `ai/sa/<slug>/STATE.md`: phase `audit`, last command `/sa:audit`, and set next to `/sa:package` on
a passing verdict, or to the specific command that fixes the first blocking finding on a `BLOCKED` one.
Append to phase history.
</step>

<step name="relay">
Return the verdict, the blocking/advisory/waived counts, every blocking finding one line each, and the
report path. On `BLOCKED`, name the command that produces each fix — the point of the gate is to tell the
human what to run next, not merely that something is wrong.
</step>
</process>

<rules>
- **Thin dispatcher only.** All checking happens inside `req-auditor`.
- **Never re-interpret the verdict.** Relay it as issued — a gate a dispatcher can soften is not a gate
  (`CONSTITUTION.md` Article III).
</rules>
