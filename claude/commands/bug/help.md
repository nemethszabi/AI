---
name: bug:help
description: Static reference for the bug: command namespace. No live analysis, no project context read.
allowed-tools: []
---

> Version: 1.0.0 — 2026-09-18. Initial.

<reference>
# `bug:` commands — generic incident analysis and minimal fix

Global — works in any project that has `ai/bug/config.json`. Contract and rationale:
`~/.claude/dev-framework/BUG-WORKFLOW.md`.

| Command | Purpose |
|---|---|
| `/bug:analyze --logs=<folder> [--desc=<file\|"text">]` | Logs + description → unified cross-component timeline, anomalies, root cause (CONFIRMED / HYPOTHESIS / INSUFFICIENT EVIDENCE), and a fix proposal when the cause is located in code. Via `bug-analyst`. Changes nothing. |
| `/bug:fix <analysis file \| incident ref \| latest>` | Shows the proposal → **you approve or amend** → `bug-fixer` makes the minimal change, builds, tests → offers to append the bug-pattern entry and to commit locally (two separate questions). Never pushes. |
| `/bug:help` | This reference. |

## `/bug:analyze` options
| Option | Effect |
|---|---|
| `--logs=<folder>` | Required. All files matching the project's component log patterns are considered. |
| `--desc=<file>` / `--desc="text"` | Ticket text, symptom, stack trace, log excerpt — any language. Asked for if absent. |
| `--user=` `--id=` `--date=` `--incident=` | Filters: user/agent name(s), session or correlation id(s), one date, a reference used for naming. |
| `--brief` | Also write a one-page, plain-language, client-shareable brief (customer identifiers masked). |
| `--out=<folder>` | Results folder. Must be outside any git repository or git-ignored — logs and timelines carry customer data. |
| `--model=<name>` | Model for the analyst. |

## Project setup — `ai/bug/`
Minimal `config.json`:
```json
{
  "schema": "bug-config/1",
  "context_files": ["ai/context/<slug>-context.md"],
  "patterns_file": "ai/context/<slug>-bug-patterns.md",
  "log_guide": "ai/bug/log-guide.md",
  "components": [
    { "name": "API", "repository": ".", "log_file_patterns": ["**/MyApp.Api_*.log"],
      "build_command": "dotnet build MyApp.sln", "test_command": "dotnet test" }
  ],
  "default_branch_names": ["main", "master"]
}
```
`log-guide.md` — what only this project knows about its logs: identifier fields per component and how they
correlate, timezone and clock notes, which lines are filtered out of which log in which environment, and
an error-recognition table (what you see → where to look first).
No `ai/context/` yet → `/scaffold-context` first.

## Safety model
- Analysis is read-only. A fix needs your approval of a written proposal, in that run.
- Schema, public-contract and cross-repository changes are named in the approval question, never implied.
- The fixer refuses a default branch and refuses to overwrite your uncommitted changes; nothing is
  stashed, switched or pushed.
- Results never go into a tracked folder; pattern entries carry the mechanism only, no identifiers.
- `HYPOTHESIS` is not rounded up to a root cause — in the report or in a client brief.

## Relation to `pr:`
`/bug:*` goes from an incident to a change in your working tree; `/pr:*` reviews and fixes pull requests.
A pattern confirmed by `/bug:fix` becomes a review check for `/pr:review` through the shared patterns file.

This command performs no live analysis — it only prints the reference above.
</reference>
