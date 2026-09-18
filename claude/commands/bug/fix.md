---
name: bug:fix
description: Implement the fix proposal of a /bug:analyze report - shows the proposal, takes your approval or amendments, dispatches bug-fixer for a minimal change with build + tests, then offers (separately) to append the bug-pattern entry and to commit locally. Never pushes.
allowed-tools:
  - Read
  - Edit
  - Grep
  - Glob
  - Agent
  - SendMessage
  - AskUserQuestion
  - Bash(git -C * status *)
  - Bash(git -C * rev-parse *)
  - Bash(git -C * diff *)
  - Bash(git -C * check-ignore *)
  - Bash(git -C * add *)
  - Bash(git -C * commit *)
  - Bash(date *)
  - PowerShell(git -C * status *)
  - PowerShell(git -C * rev-parse *)
  - PowerShell(git -C * diff *)
  - PowerShell(git -C * check-ignore *)
  - PowerShell(git -C * add *)
  - PowerShell(git -C * commit *)
  - PowerShell(Get-Date *)
disallowed-tools:
  - Write
  - NotebookEdit
argument-hint: "[project path, optional] <analysis-<ts>.md path | incident ref | latest> [--out=<folder>] [--model=<name>]"
---

> Version: 1.0.0 — 2026-09-18. Initial (revised after agent-review round 2).

<objective>
`/bug:fix <analysis file>` takes the `## Fix proposal` from a `bug-analyst` report, gets **your** approval
for it, and has the generic `bug-fixer` implement exactly that: minimal change, build, tests, fix report.
Afterwards it offers — as two separate questions — to append the proposed entry to the project's
bug-patterns file and to commit locally. It never pushes. Contract:
`~/.claude/dev-framework/BUG-WORKFLOW.md`.
</objective>

<process>
<step name="resolve-arguments">
Optional leading project path (default: current directory). The analysis: a file path, an incident ref,
or `latest`. `--out=<folder>` names the results root to search (the one `/bug:analyze --out` wrote to);
`--model=`. `ts` = now as `YYYYMMDD-HHMM`, local time, from `date +%Y%m%d-%H%M`
(Bash) or `Get-Date -Format yyyyMMdd-HHmm` (PowerShell) — one per run, used for `fix-<ts>.md`.
</step>

<step name="load-config">
Read `<project>/ai/bug/config.json`. Missing → point to `/bug:help` (project setup) and stop.
`default_branch_names` absent → `["main", "master"]`.
</step>

<step name="resolve-analysis">
A file path is used as given. Otherwise search the results root in the `BUG-WORKFLOW.md` §4 order —
`--out`, else `config.results_dir` resolved against `<project>`, else `<repo-parent>/<repo>-bug-results`,
else `<project>/ai/bug/results` (the first that exists) — recursively: an incident ref → the
newest `analysis-*.md` under the sub-folder of that name; `latest` → the newest `analysis-*.md` anywhere
under the root, "newest" by the `<ts>` in its file name, not by file time — an `-r<N>` revision is newer
than its base. Not found → say where you
looked and stop.

`results_dir` = the folder the analysis is in, absolute. Re-check it as `/bug:analyze` did
(`BUG-WORKFLOW.md` §4): `git check-ignore` on the full path of `<results_dir>/fix-<ts>.md`, or no
repository above it. Tracked and not ignored → stop and ask for another folder.
</step>

<step name="read-proposal">
Read the analysis. No `## Fix proposal` block, or verdict `INSUFFICIENT EVIDENCE` → say so and stop; there
is nothing to implement. Show, verbatim: the root-cause line with its level, and the whole proposal block.
If the level is `HYPOTHESIS`, say plainly above the proposal that the cause is not confirmed, and show its
`Safe if the hypothesis is wrong:` line; absent → warn that the analysis breaks `BUG-WORKFLOW.md` §6–§7
and recommend **Do not fix** until the analyst states it.

Map each `Files to modify` entry to a component: its leading path segment(s) must equal a
`components[].repository` value exactly (`./…`, `../<sibling repo>/…`, §7); the local repository path is
that value resolved against `<project>`. An entry that matches no component → say so and stop.
</step>

<step name="approve">
Ask via `AskUserQuestion`: **Approve as written** / **Approve with changes** (collect the changes as free
text — they become binding amendments) / **Do not fix**. If the proposal's blast radius names a schema or
migration change, a public contract, or a second repository, say so **in the question itself** — such a
change is never approved by implication (`BUG-WORKFLOW.md` §7). "Do not fix" → stop.
</step>

<step name="verify-ground">
For each repository the proposal names: `git -C <repo> status --porcelain -- . ":(exclude)ai/"` and
`git -C <repo> rev-parse --abbrev-ref HEAD`. A detached `HEAD` (the call prints `HEAD`), a branch in
`default_branch_names`, or uncommitted changes in files the proposal will modify → stop and tell the user
what to do (create/switch to a work-item branch, commit or set aside their changes). Other changes are
listed and left alone. Keep each repository's porcelain output as the **baseline** for `show-result`
and `commit`. This command never creates a branch, stashes or switches on its own.
</step>

<step name="dispatch">
Dispatch `bug-fixer` via `Agent` (`model:` if given) with `repo_root`, `analysis_file`, `amendments`
(verbatim or "none"), `results_dir` (as resolved in `resolve-analysis`, absolute), `ts`. Parse only the returned
`verdict` block (`gate: bug-fix`); missing/malformed → re-prompt once via `SendMessage`, then report the
failure. After any `SendMessage` follow-up, use the fix report named on the agent's latest `File:` line
(`fix-<ts>-r<N>.md`) and its latest verdict block; with the session gone, the newest `fix-<ts>*.md`.
</step>

<step name="show-result">
First, headlined above everything else: build or tests `FAILED` → say so and recommend against
committing; build or tests `NOT RUN` → say so and that nothing proves the change compiles or passes.
Then relay the summary and state which model ran (the session model when no `--model` was given); show,
per touched repository, `git -C <repo> diff --stat` and `git -C <repo> status --porcelain
--untracked-files=all -- . ":(exclude)ai/"` (new and untracked files included), and the path of the fix
report. Compare what changed since the `verify-ground` baseline with the files the fix report lists and
show every difference either way.

`## Blocking questions` and `## Decisions needed` from the agent → put each to the user via
`AskUserQuestion`. An answer that adds a file, a repository, a schema/migration change or a public-contract
change is a new approval (`BUG-WORKFLOW.md` §7): name that change in its own question, and run
`verify-ground` for any repository not checked yet before sending it. The answers go back to the same
fixer via `SendMessage` as binding amendments; then return to the top of `show-result` with the fix
report on the agent's latest `File:` line and its latest verdict.
</step>

<step name="pattern-entry">
Only if the fix report contains `## Proposed bug-pattern entry` **and** the analysis level is `CONFIRMED`,
the verdict is `FIXED`, and neither build nor tests is `FAILED`: show the entry and ask via
`AskUserQuestion` whether to append it to `config.patterns_file` — **Append** / **Append edited** /
**Skip**. Before appending, check the entry for customer, session or personal identifiers and refuse to
append any (`BUG-WORKFLOW.md` §4). Append with `Edit`, anchored on the file's current last lines — this is
the one file this command may write, and only by appending; a missing file is not created — show the
entry for the user to add. Before appending, `git -C <project> diff --quiet -- <patterns_file>`: already
modified → after the append offer only **Leave it for a separate commit**; otherwise ask whether the
patterns file goes into the commit below (**Include** / **Leave it for a separate commit**). It is staged
only in the repository that contains it.
</step>

<step name="commit">
Skip when the verdict is `BLOCKED` — nothing to commit. Otherwise screen the suggested message first:
it follows `ai/pr/fix-guidelines.md` where present, and carries no customer, session or incident-ticket
identifier (`BUG-WORKFLOW.md` §4) — strip any before showing it. A changed file the fix report does not
list (the `show-result` comparison) is **never staged silently** — ask per file: include / leave out.
Ask via `AskUserQuestion`, showing the message and the stage list: **Leave uncommitted (I'll review the
diff)** — recommended / **Commit locally**. On approval, once per repository: `git -C <repo> add -- <files
the fix report lists for that repo, plus any the user included>` (plus the patterns file, in its own
repository, if the user included it), then `git -C <repo> commit -m '<message>'` — single-quoted, exactly
the message shown, no added trailer — no `--no-verify`, no amend.
Report each commit's SHA. **Never push from this command**; say how the project reviews changes (e.g.
open a PR, then `/pr:review <id> --model=<a different model>` — which checks the pattern only if the
patterns file is in `ai/pr/config.json` → `context_files`).
</step>
</process>

<rules>
- **No approved proposal, no fix.** The human's approval in this run is the fixer's mandate; nothing from
  an earlier run carries over (Constitution Article VII.2).
- **Never push, force, bypass hooks, stash, switch or discard.**
- **Stage by name**, only files the fix report lists or the user included file by file.
- **Thin.** This command edits no source. Its only write is the approved pattern-entry append; no `mkdir`,
  no other file.
</rules>
