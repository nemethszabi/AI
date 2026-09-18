---
name: bug:fix
description: Implement the fix proposal of a /bug:analyze report - shows the proposal, takes your approval or amendments, dispatches bug-fixer for a minimal change with build + tests, then offers (separately) to append the bug-pattern entry and to commit locally. Never pushes.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Agent
  - SendMessage
  - AskUserQuestion
  - Bash(git -C * status *)
  - Bash(git -C * rev-parse *)
  - Bash(git -C * diff *)
  - PowerShell(git -C * status *)
  - PowerShell(git -C * rev-parse *)
  - PowerShell(git -C * diff *)
argument-hint: "[project path, optional] <analysis-<ts>.md path | incident ref | latest> [--model=<name>]"
---

> Version: 1.0.0 — 2026-09-18. Initial.

<objective>
`/bug:fix <analysis file>` takes the `## Fix proposal` from a `bug-analyst` report, gets **your** approval
for it, and has the generic `bug-fixer` implement exactly that: minimal change, build, tests, fix report.
Afterwards it offers — as two separate questions — to append the proposed entry to the project's
bug-patterns file and to commit locally. It never pushes. Contract:
`~/.claude/dev-framework/BUG-WORKFLOW.md`.
</objective>

<process>
<step name="resolve-arguments">
Optional leading project path (default: current directory). The analysis is a file path; or an incident
ref / `latest`, resolved inside the results folder (`config.results_dir`, else `<project>/ai/bug/results`)
to the newest `analysis-*.md`. Not found → say where you looked and stop.
</step>

<step name="read-proposal">
Read the analysis. No `## Fix proposal` block, or verdict `INSUFFICIENT EVIDENCE` → say so and stop; there
is nothing to implement. Show, verbatim: the root-cause line with its level, and the whole proposal block.
If the level is `HYPOTHESIS`, say plainly above the proposal that the cause is not confirmed.
</step>

<step name="approve">
Ask via `AskUserQuestion`: **Approve as written** / **Approve with changes** (collect the changes as free
text — they become binding amendments) / **Do not fix**. If the proposal's blast radius names a schema or
migration change, a public contract, or a second repository, say so **in the question itself** — such a
change is never approved by implication (`BUG-WORKFLOW.md` §7). "Do not fix" → stop.
</step>

<step name="verify-ground">
For each repository the proposal names: `git status --porcelain`, current branch. If the branch is one of
`config.default_branch_names`, or files the proposal will modify have uncommitted changes → stop and tell
the user what to do (create/switch to a work-item branch, commit or set aside their changes). This command
never creates a branch, stashes or switches on its own.
</step>

<step name="dispatch">
Dispatch `bug-fixer` via `Agent` (`model:` if given) with `repo_root`, `analysis_file`, `amendments`
(verbatim or "none"), `results_dir`, `ts`. Parse only the returned `verdict` block (`gate: bug-fix`);
missing/malformed → re-prompt once via `SendMessage`, then report the failure.
</step>

<step name="show-result">
Relay the summary; show `git -C <repo> diff --stat` per touched repository and the path of `fix-<ts>.md`.
Build or tests `FAILED` → say that first and recommend against committing. `## Decisions needed` from the
agent → put each to the user via `AskUserQuestion`; an answer that extends the mandate goes back to the
same fixer via `SendMessage` as a new amendment.
</step>

<step name="pattern-entry">
Only if the fix report contains `## Proposed bug-pattern entry`: show the entry and ask via
`AskUserQuestion` whether to append it to `config.patterns_file` — **Append** / **Append edited** /
**Skip**. Before appending, check the entry for customer, session or personal identifiers and refuse to
append any (`BUG-WORKFLOW.md` §4). This is the one file this command may write, and only by appending.
</step>

<step name="commit">
Ask via `AskUserQuestion`, showing the suggested message: **Leave uncommitted (I'll review the diff)** —
recommended / **Commit locally**. On approval: stage exactly the files the fix report lists, by name, and
commit — no `--no-verify`, no amend. **Never push from this command**; say how the project reviews
changes (e.g. open a PR, then `/pr:review <id> --model=<a different model>`).
</step>
</process>

<rules>
- **No approved proposal, no fix.** The human's approval in this run is the fixer's mandate; nothing from
  an earlier run carries over (Constitution Article VII.2).
- **Never push, force, bypass hooks, stash, switch or discard.**
- **Stage by name**, only files the fix report lists.
- **Thin.** This command edits no source. Its only write is the approved pattern-entry append.
</rules>
