---
name: pr:review
description: Review a pull request - fetches the PR and its threads from the project's configured provider, prepares a PR-head checkout, dispatches pr-reviewer (cold, on a model you choose), then shows the proposed line comments and posts only what you approve.
allowed-tools:
  - Read
  - Write
  - Grep
  - Glob
  - Agent
  - SendMessage
  - AskUserQuestion
  - Bash(git -C * fetch *)
  - Bash(git -C * worktree *)
  - Bash(git -C * rev-parse *)
  - Bash(git -C * merge-base *)
  - Bash(git -C * diff *)
  - Bash(git -C * show *)
  - PowerShell(git -C * fetch *)
  - PowerShell(git -C * worktree *)
  - PowerShell(git -C * rev-parse *)
  - PowerShell(git -C * merge-base *)
  - PowerShell(git -C * diff *)
  - PowerShell(git -C * show *)
  - Bash(date *)
  - PowerShell(Get-Date *)
argument-hint: "[project path, optional] <PR number | #number | PR URL> [--req=<file.md> | --req=\"free text\"] [--model=<name>] [--no-post] [--only-report]"
---

> Version: 1.0.0 — 2026-09-18. Initial (revised after agent-review round 2).

<objective>
`/pr:review 123` produces, for one pull request: a detailed review report and a list of short,
line-anchored comments under `<project>/ai/pr/results/PR-<id>/`, via the generic `pr-reviewer` agent — and
then, only after you have read the list and approved it, posts those comments to the PR.

Contract for every file and rule used here: `~/.claude/dev-framework/PR-WORKFLOW.md`. This command owns
what the agent structurally cannot do: talk to the PR provider, prepare the checkout, ask you, and post.
</objective>

<process>
Step order, in every mode: resolve-arguments → load-config → fetch-pr → prepare-checkout → write-inputs →
dispatch → relay → propose-comments → post → **cleanup-checkout, always last** — never before `relay` has
been shown when the run reaches `relay`, also with `--no-post` / `--only-report`; on an earlier stop after
the checkout exists, it runs immediately.

<step name="resolve-arguments">
From `$ARGUMENTS`: an optional leading project path (default: current directory); the PR as a number,
`#number`, or a PR URL (take the id from `/pullrequest/<id>` or `/pull/<id>`); `--req=` (a path if it
resolves to an existing file, otherwise free text); `--model=`; `--no-post` (the comment list is written,
checked and printed, but posting is never offered); `--only-report` (no comment list at all — the reviewer
is told so in the dispatch). No PR id → ask once via `AskUserQuestion`, don't guess. Resolve the project
to its top level with `git -C <path> rev-parse --show-toplevel`, so a run from a subfolder finds `ai/pr/`.
</step>

<step name="load-config">
Read `<project>/ai/pr/config.json`. Missing → tell the user to run `/pr:init` and stop. If the PR was
given as a URL whose repository differs from `config.repository`, stop and say so — reviewing the wrong
repo's checkout against another repo's PR produces confident nonsense.
</step>

<step name="fetch-pr">
Using the MCP server named in `config.mcp_server` (tools `mcp__<mcp_server>__*`; load their schemas via
`ToolSearch` if deferred): get the PR, its comment threads, its check/policy status, and each linked work
item (ids the provider returns, plus ids the description names after "Closes"/"Fixes"/"AB#"). If the
server is not available in this session, stop and say which server name `config.json` expects.

Note source/target branch (strip a leading `refs/heads/`) and the PR's head SHA. A PR that is completed or abandoned → say so and ask
whether to continue.
</step>

<step name="prepare-checkout">
`git -C <project> fetch origin <source> <target>` (remote-tracking refs only). Resolve
`head_sha = origin/<source>` — if it differs from the head SHA the provider reported, fetch again once;
if it still differs, report both SHAs and stop. `base_sha = git merge-base origin/<target> origin/<source>`.

Create the throwaway checkout **outside the repo**:
`git -C <project> worktree add --detach <scratch>/<repository>-PR-<id> <head_sha>`, where `<scratch>` is
the session scratchpad directory if one is listed, else the system temp directory. If that path already
exists from an interrupted run, remove it with `git worktree remove --force` first — it is this command's
own throwaway, nothing else lives there. The user's working tree and current branch are never touched.
</step>

<step name="write-inputs">
`ts` = now as `YYYYMMDD-HHMM`, from `date +%Y%m%d-%H%M` (Bash) or `Get-Date -Format yyyyMMdd-HHmm`
(PowerShell) — no other shell call. `Write` creates missing folders; never `mkdir`. Under
`<project>/ai/pr/results/PR-<id>/` write:
- `pr-<ts>.json` — **compacted** per `PR-WORKFLOW.md` §4 (no avatar/identity URLs, no `_links`), with
  `base_sha`/`head_sha`.
- `threads-<ts>.json` — exactly the §4 shape `[{thread_id, status, file, line, comments:[{id, author,
  date, body}]}]`, mapped field by field: thread id → `thread_id`; thread status → `status`; the thread
  context's file path → `file` (§6 form: leading `/`, forward slashes) and its right-file start line →
  `line` (both `null` for a general thread); per comment: comment id → `id`, author display name →
  `author`, published date → `date`, content → `body`. Drop system threads (policy, ref-update and vote
  notices, comment type `system`) and system comments inside a kept thread. No other keys.
- `requirement-<ts>.md` per §5: the `--req` file or text first, under its own heading with its origin;
  then PR title + description; then each work item's title, description and acceptance criteria. State at
  the top which sources were used.
</step>

<step name="dispatch">
Dispatch `pr-reviewer` via `Agent` — with `model: <--model>` when given — passing the absolute paths and
values its `<inputs>` table names (`repo_root`, `checkout`, `base_sha`, `head_sha`, `results_dir`, `ts`,
`pr_file`, `threads_file`, `requirement_file`, and `only_report: true` with `--only-report`) and the model
name so the report can record it. Pass
nothing else: no opinion about the PR, no summary of what you saw while fetching it — the read is cold.

Parse only the returned fenced `verdict` block (`gate: pr-review`). A return that carries only
`## Blocking questions` and no verdict block is valid (`PR-WORKFLOW.md` §8) — go to `relay`. Otherwise,
missing or malformed → re-prompt once via `SendMessage`; still missing → report the failure, keep the
files, skip posting.
</step>

<step name="relay">
Check the counts against the report: the number of `### F-NN — <severity>` headings per severity in the
latest `review-*.md` must equal the verdict block's `counts`. A mismatch is shown in the relay, first, with
both numbers — the verdict is derived from counts the report does not substantiate — and the user can ask
the reviewer to reconcile via `SendMessage`.

Show: the verdict line, the counts, the top findings, the limits the agent reported, and the file paths.
State which model ran; if no `--model` was given, add one line: "Review ran on the session model —
for a review you will act on, re-run with `--model=<other>` (`AGENT-CONDUCT-BASELINE.md` B10)."
If the agent returned `## Blocking questions`, put them to the user via `AskUserQuestion` and pass the
answers back with `SendMessage`.

From here on, the review's files are whatever the agent's **latest** reply names on its `Files:` line,
and its verdict is the latest verdict block — a follow-up may have produced `-r<N>` revisions
(`PR-WORKFLOW.md` §4). Never read a file name predicted at dispatch time.
</step>

<step name="propose-comments">
Skip with `--only-report`. Otherwise read the latest `comments-*.json` and check it against
`PR-WORKFLOW.md` §6, using the checkout (still present — it is removed only in `cleanup-checkout`):
- `head_sha` in the JSON and in the verdict block equals the `head_sha` dispatched — otherwise say so and
  stop before posting anything;
- per comment: the file exists at head (strip §6's leading `/` before resolving it under the checkout),
  `line` is within its length, and the line is inside or within three lines of a changed hunk per
  `git -C <project> diff -U0 <base_sha> <head_sha> -- <file>` hunk headers; body three sentences or fewer;
  `existing_thread` is null;
- the list: at most three `nit`, at most `review.max_inline_comments` — over either cap, keep the highest
  severities;
- `summary_comment`: 12 lines or fewer.

A comment that fails is **never offered for posting**: list it under "Not postable" with its reason, so
the user can ask the reviewer to relocate it via `SendMessage`.

Build each postable body exactly as it will be posted: the severity tag in the format the project's
`review-guidelines.md` prescribes (absent a rule: `**[severity]** `), unless the body already starts with
a tag, then the body. Print `C-NN · severity · file:line` and that final text, then the summary comment,
then the "Not postable" list. With `--no-post`, stop there and say posting was not offered. Otherwise ask
via `AskUserQuestion`: **Post all** / **Let me pick** (follow up with the ids to post or drop, or edited
bodies) / **Post nothing**. Default recommendation: none — the user has not read them yet.
</step>

<step name="post">
Skip with `--no-post` or `--only-report`. First re-read the PR from the provider: if its head SHA is no
longer `head_sha`, post nothing, say the PR moved while you were reading, and suggest a re-run — a comment
on `file` + `line` would land on whatever that line now holds. Only what was approved, only now, and exactly the text shown (or as the user edited it) — nothing is
added or reworded after approval. For each approved comment: a new thread on `file` + `line` via the
provider, status `active`. Then the summary comment as a general thread, if approved and
`review.post_summary_comment` is not `false`. Write `posted-<ts>.json` (comment id → provider thread id,
plus anything that failed). Report what was posted and what failed — never retry a failed post silently,
and never post a comment twice: check `posted-*.json` from earlier runs first.

Never vote on the PR, never change the PR's status, reviewers, or another person's thread.
</step>

<step name="cleanup-checkout">
`git -C <project> worktree remove --force <checkout>` — the last step in every mode: after `relay` has
been shown, after posting (or "Post nothing", or the printed list under `--no-post`, or the report alone
under `--only-report`) and after any follow-up to the reviewer. Always run it once the checkout exists:
also on a failed dispatch, an abort, or an early stop. Never before `relay` — the reviewer's follow-ups
and the checks above read the checkout.
</step>
</process>

<rules>
- **Posting is per-run approval, every time** (`CONSTITUTION.md` Article VII). A previous "post all" means
  nothing for this run.
- **The review is cold.** Nothing from this session's own view of the PR goes into the dispatch prompt.
- **Thin.** No reviewing here — if the agent's findings look wrong, ask it via `SendMessage`; do not
  overrule or supplement them in the relay.
- **The scratch worktree is the only git state this command creates, and it always removes it — as
  the last step.** No
  checkout, switch, stash, commit or push — ever — in this command.
- **Never write a credential** into any results file; the provider payload is compacted before it is saved.
- **Follow-ups**: questions about a finding go to the same reviewer via `SendMessage` while its session
  lives; afterwards, re-read the latest `review-*.md` and the cited lines — with the checkout gone, via
  `git -C <project> show <head_sha>:<file>` — rather than re-dispatching.
</rules>
