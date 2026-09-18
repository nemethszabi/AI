---
name: pr:fix
description: Fix a pull request's review comments - fetches the open threads, dispatches pr-fixer to apply minimal fixes on the PR's source branch and verify build + tests, then shows the diff and proposed replies and commits, pushes, replies and sets thread statuses only as far as you approve, each as its own question.
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
  - Bash(git -C * add -- *)
  - Bash(date *)
  - PowerShell(git -C * status *)
  - PowerShell(git -C * rev-parse *)
  - PowerShell(git -C * diff *)
  - PowerShell(git -C * fetch *)
  - PowerShell(git -C * add -- *)
  - PowerShell(Get-Date *)
argument-hint: "[project path, optional] <PR number | #number | PR URL> [--threads=<id,id,...>] [--from-review] [--include-resolved] [--model=<name>]"
---

> Version: 1.0.0 — 2026-09-18. Initial (revised after agent-review round 2).

<objective>
`/pr:fix 123` takes the review comments on one pull request and gets them addressed: `pr-fixer` triages
each open thread (fix / answer / decline / needs-human), applies minimal fixes in your working tree on the
PR's source branch, runs the project's build and tests, and drafts a reply per thread. This command then
shows you the diff and the replies, and commits, pushes, replies and sets thread statuses **only as far as
you approve, each as its own question**.

Contract: `~/.claude/dev-framework/PR-WORKFLOW.md`. With `--from-review`, the input is the newest local
`comments-*.json` from `/pr:review` instead of provider threads — fix your own PR before anyone has to
comment on it; nothing is posted in that mode.
</objective>

<process>
Step order: resolve-arguments → load-config → fetch-pr → verify-ground → select-threads → dispatch →
show-result → commit → push → reply → suggest-re-review. A stop at any step ends the run with what exists
reported; nothing later runs.

<step name="resolve-arguments">
Optional leading project path (default: current directory); PR id as number, `#number` or URL (take the id
from `/pullrequest/<id>` or `/pull/<id>`); `--threads=` restricts to those thread ids; `--from-review`;
`--include-resolved` (default: only threads whose status is active/pending); `--model=`. No PR id → ask
once via `AskUserQuestion`. Resolve the project to its top level with `git -C <path> rev-parse
--show-toplevel`. `commit` and `push` are deliberately not pre-approved in `allowed-tools`: after your
approval in the question, the platform's own permission prompt is a second check on the exact command.
</step>

<step name="load-config">
Read `<project>/ai/pr/config.json`. Missing → point to `/pr:init` and stop. If the PR was given as a URL
whose repository differs from `config.repository`, stop and say so.
</step>

<step name="fetch-pr">
Via `mcp__<config.mcp_server>__*` (load schemas via `ToolSearch` if deferred): the PR and its threads. If
the server is not available in this session, stop and say which server name `config.json` expects. Note
`source_branch` (strip a leading `refs/heads/`) and the provider's head SHA. A PR that is completed or
abandoned → say so and stop; there is no branch to push fixes to that anyone will merge. In `--from-review` mode the threads are still fetched
(so a fix does not collide with a human's open thread) but the findings come from the newest
`results/PR-<id>/comments-*.json` by the timestamp in its name — `-r<N>` revisions count as newer.
</step>

<step name="verify-ground">
All must hold, else STOP and tell the user exactly what to do — this command never stashes, switches,
pulls or discards on its own:
- the tree is clean per `PR-WORKFLOW.md` §10: `git -C <project> status --porcelain -- . ":(exclude)ai/"`
  prints nothing;
- current branch (`git -C <project> rev-parse --abbrev-ref HEAD`) equals `source_branch` — `HEAD` (a
  detached checkout) is a stop;
- after `git -C <project> fetch origin <source_branch>`, local `HEAD` equals `origin/<source_branch>`
  (behind → the user pulls; ahead → say so and ask whether to continue on the unpushed commits);
- in `--from-review` mode, the review's `head_sha` equals local `HEAD` — otherwise its line numbers point
  at other code; the user re-runs `/pr:review` first.
Record `head_sha = git -C <project> rev-parse HEAD` for the dispatch. If the PR's author is not the current
provider user, say so once and ask whether to proceed — fixing someone else's branch is legitimate when
asked for, and surprising when not.
</step>

<step name="select-threads">
`ts` = now as `YYYYMMDD-HHMM`, from `date +%Y%m%d-%H%M` (Bash) or `Get-Date -Format yyyyMMdd-HHmm`
(PowerShell). `Write` creates missing folders; never `mkdir`. Under `<project>/ai/pr/results/PR-<id>/`
write `pr-<ts>.json` (compacted, §4) and `threads-<ts>.json` in exactly the §4 shape, mapped as
`/pr:review`'s `write-inputs` step maps it: thread id → `thread_id`; status → `status`; the thread
context's file path → `file` (leading `/`, forward slashes) and right-file start line → `line` (`null` for a
general thread); per comment: id → `id`, author display name → `author`, published date → `date`, content →
`body`; system threads and system comments dropped; no other keys. Decide the in-scope set — it travels to
the fixer as `only`, not as a key in the file: provider threads filtered by `--threads` and the status
filter; in `--from-review` mode instead the comments of the newest `comments-*.json` (restricted by
`--threads=` given as `C-NN` ids), with the provider threads as context only.

Read every earlier `posted-*.json` in the PR's folder: a thread this tooling already replied to is shown as
such, so the user does not answer it twice.

Show the in-scope list — thread id, file:line, author, first line — and if there are more than ten, ask via
`AskUserQuestion` whether to take all or a subset. Zero in scope → say so and stop (in `--from-review`
mode: zero comments, not zero provider threads).
</step>

<step name="dispatch">
Dispatch `pr-fixer` via `Agent` (with `model:` if given), passing the absolute paths and values its
`<inputs>` table names: `repo_root`, `source_branch`, `head_sha`, `results_dir`, `ts`, `pr_file`,
`findings_file` (`threads-<ts>.json`, or the review's `comments-*.json` in `--from-review` mode), in
`--from-review` mode `threads_file` (`threads-<ts>.json`), optional `requirement_file` (newest
`requirement-*.md` in the PR's results folder, if any) and always `only` = the in-scope ids.

Parse only the returned fenced `verdict` block (`gate: pr-fix`); missing/malformed → re-prompt once via
`SendMessage`. Still none → **no valid verdict**: report it, show the diff in `show-result`, and offer no
commit, push or reply in this run.

If the fixer returned `## Blocking questions`, put them to the user via `AskUserQuestion` and pass the
answers back with `SendMessage`.

After **every** `SendMessage` — blocking questions, a re-prompt, a decision below — re-read the fixer's
latest reply: its `Files:` line names the current `fix-`/`replies-` pair (a follow-up writes `-r<N>`
revisions, §4) and its verdict block is the current verdict. Never use a file name predicted at dispatch.
When the fixer's session is gone, fall back to the latest `fix-<ts>*.md` / `replies-<ts>*.json` — highest
`-r<N>` by numeric N, the unsuffixed file as `r0` (§4) — and the working-tree diff, and say that the
verdict comes from the file, not a live reply.
</step>

<step name="show-result">
First, headlined above everything else: build or tests `FAILED` → say so and recommend against committing;
build or tests `NOT RUN` → say so and that nothing proves the change compiles or passes. Then state which
model ran the fixer (or "session model — no `--model` given"), relay the agent's summary, show
`git -C <project> diff --stat` and the per-thread table from the latest `replies-*.json`: thread · action ·
proposed reply · proposed status.

Put every `declined` and `needs-human` thread to the user via `AskUserQuestion` (accept the fixer's
position / ask the fixer to implement it anyway, via `SendMessage` / leave for me), then re-read as
`dispatch` says and repeat this step from the top — a follow-up can change the build or test result.

`BLOCKED`, or no valid verdict → stop after this step: nothing to commit, push or reply.
</step>

<step name="commit">
Stage list = the union of `files_changed` across the latest `replies-*.json`, plus the files the latest
fix report lists under its changes, each checked against `git -C <project> status --porcelain
--untracked-files=all -- . ":(exclude)ai/"` (so a new file in a new folder is listed by name). Normalise
both sides before comparing: strip the leading `/` from the JSON and report paths, unquote porcelain paths;
stage with the repo-relative form, never the `/`-prefixed one. A listed file that is not in the porcelain output is dropped with a note. A changed file
in the porcelain output that no list names is **shown, never staged silently** — ask via `AskUserQuestion`
per such file: include / leave out.

Ask via `AskUserQuestion`, with the suggested commit message and the stage list shown: **Leave uncommitted
(I'll review the diff myself)** — the recommended default / **Commit locally** / **Commit with an edited
message**. On approval only: `git -C <project> add -- <each file by name>` (never `-A`, never `.`), then
`git -C <project> commit -m "<approved message>"` following the project's `fix-guidelines.md` — never
`--no-verify`, never `--amend`. Show the resulting SHA (`git -C <project> rev-parse --short HEAD`). A failed
commit (a hook, an empty index) is reported and ends the run.
</step>

<step name="push">
Only after a successful commit in this run. Ask via `AskUserQuestion`, naming the SHA and the branch:
**Push `<sha>` to `origin/<source_branch>`** / **Don't push**. On approval only:
`git -C <project> push origin <source_branch>` — never `--force`, never `--no-verify` (Articles II, III).
Confirm with `git -C <project> rev-parse origin/<source_branch>` equal to the commit's SHA. A rejected
push is reported, not worked around.
</step>

<step name="reply">
Skip entirely in `--from-review` mode. Replies whose action is `fixed` are offered only after a push this
run confirmed — a reply pointing at code the reviewer cannot see yet is a false statement; without a
confirmed push, only `answered`/`declined`/`needs-human` replies are offered. Replace `{commit_sha}` in a
reply with the pushed short SHA only then; a reply still holding the placeholder is never posted.

Show each reply exactly as it will be posted. Ask via `AskUserQuestion`: **Post all replies** / **Let me
pick or edit** / **Post nothing**. Then, as a **separate question**, list every non-null
`proposed_status` of the approved replies (thread · current → proposed status, and "(per an unconfirmed
team rule)" where the fix report flags one): **Set all these statuses** / **Let me pick** / **Change no
status**.

For each approved reply: reply on its thread via the provider; then set that thread's status only if the
reply posted successfully and the status question approved it. Write `posted-<ts>.json` (thread id → reply id, status set or not, anything
that failed). Report what was posted and what failed — never retry silently. Never touch a thread that was
not in scope.
</step>

<step name="suggest-re-review">
End with one line: re-run `/pr:review <id> --model=<a different model than fixed>` to check the fixes
cold.
</step>
</process>

<rules>
- **Four separate approvals — commit, push, reply, thread status — never bundled, never remembered**
  (Article VII.2). Push is only ever asked after a commit this run made.
- **Never force, never bypass hooks, never stash/switch/reset/discard.** If the ground isn't right, stop.
- **Stage by name.** Only the files the stage list names, checked against the tree; anything else is shown
  for a decision, never swept in.
- **Every git call names the project**: `git -C <project> …`, and a push names `origin <source_branch>`.
- **No valid verdict, no commit.** A missing or `BLOCKED` verdict ends the run after the diff is shown.
- **Thin.** The fixing happens in the agent; this command does not edit source itself.
- **Never resolve a thread the user did not approve resolving**, and never another person's thread that was
  out of scope.
</rules>
