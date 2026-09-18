---
name: bug:help
description: Static reference for the bug: command namespace. No live analysis, no project context read.
allowed-tools: []
---

> Version: 1.0.0 — 2026-09-18. Initial (revised after agent-review round 2).

<reference>
# `bug:` commands — generic incident analysis and minimal fix

Global — works in any project that has `ai/bug/config.json`. Contract and rationale:
`~/.claude/dev-framework/BUG-WORKFLOW.md`.

| Command | Purpose |
|---|---|
| `/bug:analyze [path] --logs=<folder> [--desc=<file\|"text">]` | Logs + description → unified cross-component timeline, anomalies, root cause (CONFIRMED / HYPOTHESIS / INSUFFICIENT EVIDENCE), and a fix proposal when the cause is located in code. Via `bug-analyst`. Changes nothing. |
| `/bug:fix [path] <analysis file \| incident ref \| latest>` | Shows the proposal → **you approve or amend** → `bug-fixer` makes the minimal change, builds, tests → offers to append the bug-pattern entry (only for a `CONFIRMED` cause and a `FIXED` result) and to commit locally, once per repository (separate questions). Never pushes. |
| `/bug:help` | This reference. |

`[path]` is the project repository; optional — default is the current directory.

## `/bug:analyze` options
| Option | Effect |
|---|---|
| `--logs=<folder>` | Required. All files matching the project's component log patterns are considered. |
| `--desc=<file>` / `--desc="text"` | Ticket text, symptom, stack trace, log excerpt — any language. Asked for if absent. |
| `--user=` `--id=` `--date=` `--incident=` | Filters: user/agent name(s), session or correlation id(s), one date, a reference used for naming. |
| `--brief` | Also write a one-page, plain-language, client-shareable brief (customer identifiers masked). |
| `--out=<folder>` | Results folder. Must be outside any git repository or git-ignored — logs and timelines carry customer data. Without it and without `config.results_dir`, the command proposes `<repo-parent>/<repo>-bug-results` and asks once. |
| `--model=<name>` | Model for the analyst. |

## `/bug:fix` options
| Option | Effect |
|---|---|
| `latest` | The newest `analysis-*.md` (by the timestamp in its name; an `-r<N>` revision is newer) anywhere under the results root — searched in the same order `/bug:analyze` uses: `--out`, `config.results_dir`, `<repo-parent>/<repo>-bug-results`, `ai/bug/results`. |
| `--out=<folder>` | Search this results root first — use it when the analysis was written with `/bug:analyze --out`. |
| `--model=<name>` | Model for the fixer. Review the fix on a different one. |

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
  "results_dir": "../MyApp-bug-results",
  "default_branch_names": ["main", "master"]
}
```
`results_dir` is resolved against the repository root and should point **outside** it, as above — never an
absolute machine path in a committed config. If you keep results inside instead, git-ignore them first;
the tooling never edits `.gitignore`. The two lines to add there by hand:
```
ai/bug/results/
ai/pr/results/
```
`log-guide.md` — what only this project knows about its logs: identifier fields per component and how they
correlate, timezone and clock notes, which lines are filtered out of which log in which environment, and
an error-recognition table (what you see → where to look first).
Create the `patterns_file` yourself (a heading is enough) — `/bug:fix` only appends to it, never creates it.
`default_branch_names` must list **every** branch the fixer may never work on (e.g. `staging`, `develop`);
missing → `["main", "master"]` only.
No `ai/context/` yet → `/scaffold-context` first.

## Safety model
- Analysis is read-only. A fix needs your approval of a written proposal, in that run.
- Schema, public-contract and cross-repository changes are named in the approval question, never implied.
- The fixer refuses a default branch and refuses to overwrite your uncommitted changes; nothing is
  stashed, switched or pushed.
- Results never go into a tracked folder; pattern entries carry the mechanism only, no identifiers, and are
  offered only for a `CONFIRMED` root cause whose fix came back `FIXED`.
- `HYPOTHESIS` is not rounded up to a root cause — in the report or in a client brief.

## Relation to `pr:`
`/bug:*` goes from an incident to a change in your working tree; `/pr:*` reviews and fixes pull requests.
A pattern confirmed by `/bug:fix` becomes a review check for `/pr:review` only if the patterns file is also
listed in `ai/pr/config.json` → `context_files`.

This command performs no live analysis — it only prints the reference above.
</reference>
