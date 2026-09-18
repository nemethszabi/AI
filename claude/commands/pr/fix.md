---
name: pr:fix
description: Fix a pull request's review comments - fetches the open threads, dispatches pr-fixer to apply minimal fixes on the PR's source branch and verify build + tests, then shows the diff and proposed replies and commits, pushes and replies only as far as you approve.
allowed-tools:
  - Read
  - Write
  - Grep
  - Glob
  - Agent
  - SendMessage
  - AskUserQuestion
  - Bash(git -C * status *)
  - Bash(git -C * rev-parse *)
  - Bash(git -C * diff *)
  - Bash(git -C * fetch *)
  - PowerShell(git -C * status *)
  - PowerShell(git -C * rev-parse *)
  - PowerShell(git -C * diff *)
  - PowerShell(git -C * fetch *)
argument-hint: "[project path, optional] <PR number | #number | PR URL> [--threads=<id,id,...>] [--from-review] [--include-resolved] [--model=<name>]"
---

> Version: 1.0.0 — 2026-09-18. Initial.

<objective>
`/pr:fix 28548` takes the review comments on one pull request and gets them addressed: `pr-fixer` triages
each open thread (fix / answer / decline / needs-human), applies minimal fixes in your working tree on the
PR's source branch, runs the project's build and tests, and drafts a reply per thread. This command then
shows you the diff and the replies, and commits, pushes, replies and sets thread statuses **only as far as
you approve, each as its own decision**.

Contract: `~/.claude/dev-framework/PR-WORKFLOW.md`. With `--from-review`, the input is the newest local
`comments-*.json` from `/pr:review` instead of provider threads — fix your own PR before anyone has to
comment on it; nothing is posted in that mode.
</objective>

<process>
<step name="resolve-arguments">
Optional leading project path (default: current directory); PR id as number, `#number` or URL;
`--threads=` restricts to those thread ids; `--from-review`; `--include-resolved` (default: only threads
whose status is active/pending); `--model=`.
</step>

<step name="load-config">
Read `<project>/ai/pr/config.json`. Missing → point to `/pr:init` and stop.
</step>

<step name="fetch-pr">
Via `mcp__<config.mcp_server>__*`: the PR and its threads. Note `source_branch` and the provider's head
SHA. In `--from-review` mode the threads are still fetched (so a fix does not collide with a human's open
thread) but the findings come from the newest `results/PR-<id>/comments-*.json`.
</step>

<step name="verify-ground">
All must hold, else STOP and tell the user exactly what to do — this command never stashes, switches,
pulls or discards on its own:
- `git -C <project> status --porcelain` is empty;
- current branch equals `source_branch`;
- after `git -C <project> fetch origin <source_branch>`, local `HEAD` equals `origin/<source_branch>`
  (behind → the user pulls; ahead → say so and ask whether to continue on the unpushed commits).
If the PR's author is not the current provider user, say so once and ask whether to proceed — fixing
someone else's branch is legitimate when asked for, and surprising when not.
</step>

<step name="select-threads">
Compact the threads per `PR-WORKFLOW.md` §4 into `threads-<ts>.json`, dropping system threads and marking
which are in scope (`--threads`, status filter). Show the in-scope list — thread id, file:line, author,
first line — and if there are more than ten, ask via `AskUserQuestion` whether to take all or a subset.
Zero in scope → say so and stop. Write `pr-<ts>.json` too.
</step>

<step name="dispatch">
Dispatch `pr-fixer` via `Agent` (with `model:` if given), passing the absolute paths and values its
`<inputs>` table names: `repo_root`, `source_branch`, `head_sha`, `results_dir`, `ts`, `pr_file`,
`findings_file`, optional `requirement_file` (newest `requirement-*.md` in the PR's results folder, if
any) and `only`. Parse only the returned fenced `verdict` block (`gate: pr-fix`); missing/malformed →
re-prompt once via `SendMessage`, then report failure and continue to `show-result` with what exists.
</step>

<step name="show-result">
Relay the agent's summary. Then show `git -C <project> diff --stat` and the per-thread table from
`replies-<ts>.json`: thread · action · proposed reply · proposed status. Put every `declined` and
`needs-human` thread to the user via `AskUserQuestion` (accept the fixer's position / ask the fixer to
implement it anyway, via `SendMessage` / leave for me). Build or tests `FAILED` → say so first, above
everything else, and recommend against committing.
</step>

<step name="commit-and-push">
Ask via `AskUserQuestion`, as one question with the suggested commit message shown: **Leave uncommitted
(I'll review the diff myself)** — the recommended default / **Commit locally** / **Commit and push**.
On approval only: stage exactly the files the fix report lists (never `git add -A`), commit with the
approved message following the project's `fix-guidelines.md`, and push with a plain `git push` — never
`--force`, never `--no-verify` (Articles II, III). A rejected push is reported, not worked around.
</step>

<step name="reply">
Skip entirely in `--from-review` mode. Replies that claim "fixed" are only offered once the fix is pushed
— a reply pointing at code the reviewer cannot see yet is a false statement. Ask via `AskUserQuestion`:
**Post all replies** / **Let me pick or edit** / **Post nothing**. For each approved reply: reply on its
thread via the provider, then set the thread status only if `proposed_status` is non-null **and** the
user approved status changes. Write `posted-<ts>.json`. Never touch a thread that was not in scope.
</step>

<step name="suggest-re-review">
End with one line: re-run `/pr:review <id> --model=<a different model than fixed>` to check the fixes
cold.
</step>
</process>

<rules>
- **Three separate approvals — commit, push, reply — never bundled, never remembered** (Article VII.2).
- **Never force, never bypass hooks, never stash/switch/reset/discard.** If the ground isn't right, stop.
- **Stage by name.** Only files the fix report lists; anything else in the tree is not this command's.
- **Thin.** The fixing happens in the agent; this command does not edit source itself.
- **Never resolve a thread the user did not approve resolving**, and never another person's thread that was
  out of scope.
</rules>
