# PR Workflow — contract for `pr-reviewer`, `pr-fixer` and the `pr:` commands

> Version: 1.0.0 — 2026-09-18 (revised after agent-review, before first rollout). Binding on `claude\agents\pr-reviewer.md`, `claude\agents\pr-fixer.md` and
> `claude\commands\pr\*`. Read after `CONSTITUTION.md`.

Generic across projects, stacks and PR providers. Everything a single project knows — its provider
connection, its comment tone, its hot-spots, its build commands, its thread-resolution etiquette — lives in
that project's own `ai/pr/` folder as **data**. No project gets its own copy of an agent or a command
unless its *process* genuinely differs (`claude\README.md`, authoring rule 4).

---

## 1. Division of labour

The split follows `CONSTITUTION.md` Articles VI and VII. Only part of it is structural — see the
consequences below for which part:

| Actor | Runs in | May | May never |
|---|---|---|---|
| `/pr:review`, `/pr:fix` (commands) | main session | call the PR provider (MCP), `git fetch`, add/remove a scratch worktree, ask the human, and — **after explicit approval, every time** — post comments, reply, set thread status, commit, push | post, commit or push without that approval; vote on a PR |
| `pr-reviewer` (agent) | dispatched, cold | read the PR head checkout, the diff, the project context; write files under the run's results folder | call the PR provider, edit source, touch git state, post anything |
| `pr-fixer` (agent) | dispatched | edit source in the working tree on the PR source branch, build, test, write its report | call the PR provider, commit, push, reply to a thread, change a thread's status |

Consequences worth stating once:
- **Neither agent holds a PR-provider MCP tool** — that part is structural. The agents are
  provider-agnostic because the command hands them plain files (§4). Swapping Azure DevOps for GitHub
  changes `config.json` and the command's provider calls, never an agent.
- **The agents' git and write limits are instruction-bound, not enforced.** Both hold `Bash` (the fixer
  must build; the reviewer reads git history), and `Bash` could run `git commit`, `git push` or a network
  call, and `Write` has no path limit. Until per-agent `PreToolUse` hooks exist, the "never" column for the
  agents is a rule they follow, not a wall — say so wherever it is described, never "enforced by tool
  grant".
- **A comment on a colleague's PR is outward-facing shared state.** The reviewer *proposes*
  `comments-*.json`; a human reads the list and approves what is posted. Approval is per run, never
  standing (Article VII.2).
- **The tooling never votes.** The review verdict is advice to the human reviewer of record.

## 2. Project files — `ai/pr/`

```
<repo>/ai/pr/
  config.json              provider connection + paths (§3)                     required
  review-guidelines.md     what to check here, comment voice, severity use      optional, strongly advised
  fix-guidelines.md        build/test commands, commit + reply + status rules   optional, strongly advised
  results/PR-<id>/         one folder per PR, every run appends (§4)            written by the tooling
```

`ai/context/*.md` stays where the rest of the framework expects it and is read by both agents; `ai/pr/`
holds only what is specific to reviewing and fixing PRs. Whether `ai/pr/results/` is committed is the
project's choice — it contains review prose about colleagues' code, so the default in `/pr:init` is to
suggest a `.gitignore` entry and let the human decide.

## 3. `config.json`

```json
{
  "schema": "pr-config/1",
  "provider": "azure-devops",
  "mcp_server": "<name of the MCP server as configured on this machine, e.g. azure-devops-acme>",
  "organization": "<org>",
  "project": "<project name>",
  "repository": "<repository name>",
  "default_target_branch": "<branch, informational>",
  "context_files": ["ai/context/<slug>-context.md"],
  "related_repositories": [
    { "name": "<sibling repo>", "relation": "<one line>", "context_files": ["<path or sibling-relative path>"] }
  ],
  "review": { "max_inline_comments": 15, "post_summary_comment": true, "build_in_review": false },
  "fix":    { "build_command": "<cmd>", "test_command": "<cmd>" }
}
```

- `mcp_server` is a **name, never a credential**. The server itself is configured per user (`claude mcp
  add --scope user …`) with that user's own token; nothing under `ai/pr/` may contain one (Article I).
- `review.build_in_review: true` makes the reviewer run `fix.build_command` / `fix.test_command` on the
  PR author's code — MSBuild targets, test code and scripts executing with the reviewer's environment,
  including any provider token held in an environment variable. Enable it only where every PR author is
  trusted.
- `context_files` and `related_repositories[].context_files` are read by both agents before anything
  else. Paths are relative to the repository root and are **always resolved against `repo_root`**, never
  against the scratch checkout (§10), where a sibling-relative path does not exist; a related repository's files are normally reached as a
  sibling clone (`../<repo>/ai/context/…`), so no machine-specific absolute path is committed. A path that
  does not exist — a colleague may not have the sibling cloned — is reported, not guessed around.
- Unknown keys are ignored; a missing optional key takes the default shown above.

## 4. Run artifacts — `ai/pr/results/PR-<id>/`

`<ts>` is `YYYYMMDD-HHMM`, local time, one per run. Nothing is overwritten; a PR's folder is its history.

| File | Written by | Content |
|---|---|---|
| `pr-<ts>.json` | command | Compact PR snapshot: id, title, author, source/target branch, base + head SHA, description, linked work-item ids, policy/check status. **Never the raw provider payload** — it is mostly avatar URLs. |
| `threads-<ts>.json` | command | Existing comment threads, compacted: `[{thread_id, status, file, line, comments:[{id, author, date, body}]}]`. System threads (policy updates, ref updates, votes) are dropped. |
| `requirement-<ts>.md` | command | What the change is supposed to do, with provenance (§5). |
| `review-<ts>.md` | `pr-reviewer` | The detailed review report — the deep-analysis record. |
| `comments-<ts>.json` | `pr-reviewer` | Proposed PR comments (§6). |
| `fix-<ts>.md` | `pr-fixer` | What was changed per thread, build/test evidence, what was deliberately not changed. |
| `replies-<ts>.json` | `pr-fixer` | Proposed thread replies and statuses (§7). |
| `posted-<ts>.json` | command | What was actually posted after approval: comment/reply id → provider thread id. The dedupe record for the next run. |

**Revisions within a run.** When a `SendMessage` follow-up changes a finding, a comment or the verdict,
the agent writes the revised pair as `review-<ts>-r<N>.md` / `comments-<ts>-r<N>.json` (N = 1, 2, …;
the same for `fix-`/`replies-`), keeps `<ts>` so the command's `pr-`/`threads-`/`requirement-<ts>` files
still pair with it, and names the new paths on the `Files:` line of its reply, followed by a re-emitted
verdict block. The command always reads the paths from the agent's **latest** `Files:` line and the latest
verdict block — never the file names it predicted at dispatch.

## 5. The requirement input

A review measures a change against what it was *supposed* to do. `/pr:review` resolves that in this order
and writes every source it used into `requirement-<ts>.md` under its own heading:

1. `--req=<path>` — a Markdown/text file. Copied in verbatim.
2. `--req="<free text>"` — copied in verbatim.
3. Always appended, clearly separated: the PR's own title + description, and the title, description and
   acceptance criteria of each linked work item the provider returns.

With no `--req`, (3) alone is the requirement and the file says so — a review against the author's own
description can confirm the code matches the description, not that the description matches the need.
The reviewer reports that limitation in its summary instead of hiding it.

## 6. `comments-<ts>.json`

```json
{
  "schema": "pr-comments/1",
  "pr": 123, "head_sha": "<sha reviewed>", "model": "<model that ran, if known>",
  "summary_comment": "<markdown, <= 12 lines, or null>",
  "comments": [
    {
      "id": "C-01",
      "severity": "blocker | major | minor | nit | question",
      "file": "/path/from/repo/root.cs",
      "line": 42,
      "body": "<the comment text, WITHOUT a severity tag — the command adds that>",
      "finding": "F-03",
      "existing_thread": null
    }
  ]
}
```

Rules, binding on the reviewer and checked by the command before it shows the list:
- **`file`** is repo-relative with a leading `/` and forward slashes on every OS — never a drive letter,
  never a backslash, never the scratch-checkout path.
- **`line` is a line number in the file at `head_sha`**, and that line is inside a changed hunk or within
  three lines of one.
- **Anchorable is not the same as caused.** A finding the PR *causes* but that has no changed line to sit
  on — a requirement not met, a consumer in an unchanged file left un-updated, a model change with no
  migration, a paired change in a related repository that is missing — **counts toward the verdict**
  like any other. It goes in `summary_comment` (and in the report), not in `comments[]`. Only a defect
  that already existed in unchanged code before this PR is a *pre-existing issue*: reported separately,
  never counted, never commented on.
- **`body` carries no severity tag.** The command prefixes it at posting time in the format the
  project's `review-guidelines.md` prescribes (absent a rule: `**[severity]** `), and shows the user the
  prefixed text — what is approved is exactly what is posted. A body that already starts with a tag is
  not tagged again.
- **`summary_comment`** is written by the reviewer every run, following the project's
  `review-guidelines.md` where it describes one: the verdict in words, the PR-caused findings that have no
  inline anchor, and anything the guidelines route only to the summary. `null` only when there is
  genuinely nothing to say beyond the inline comments.
- **`body` is short**: one to three sentences, plain words, says what is wrong and what to do instead; at
  most one small code suggestion. No severity essay, no praise padding, no restating the diff. The depth
  lives in `review-<ts>.md` under the matching `finding` id.
- **One comment per defect.** The same defect in five places is one comment at the first place, naming
  the others.
- **Never duplicate an existing thread.** If `threads-<ts>.json` already raises the point, set
  `existing_thread` to that thread id and the command skips posting it (the report may still say "thread
  #N is still unresolved at `<sha>`").
- `max_inline_comments` caps the list. Over the cap, keep by severity and move the rest to the report —
  forty comments on a PR get none of them read.
- `question` is for genuine uncertainty. A defect phrased as a question to seem polite is still a defect;
  give it its real severity.

What the command does with a comment that fails a check: it is **never offered for posting**. It is
listed separately under "Not postable" with the reason (file missing at head, line out of range, not near
a changed hunk, body over three sentences, duplicate of an existing thread), so the user sees it and can
ask the reviewer to relocate it. Over the `max_inline_comments` or the three-nit cap, the command keeps
the highest severities and lists the rest as not postable. A `head_sha` in the JSON or the verdict block
that differs from the SHA the command dispatched stops the posting step entirely.

Severity, fixed across projects:

| Severity | Meaning | Merge implication |
|---|---|---|
| `blocker` | Wrong behaviour, data loss/corruption, security hole, crash, breaks a contract another component relies on | must be fixed |
| `major` | Likely bug under realistic conditions, resource/lifetime leak, missing handling on a path that will be hit, requirement not met | should be fixed |
| `minor` | Maintainability, unclear naming, missing test for new logic, inconsistent with project convention | fix or answer |
| `nit` | Cosmetic. Used sparingly, never more than three per review | author's choice |
| `question` | Reviewer cannot determine correctness from code + context | needs an answer |

## 7. `replies-<ts>.json`

```json
{
  "schema": "pr-replies/1",
  "pr": 123, "base_sha": "<working-tree HEAD the fixes were applied on>",
  "replies": [
    {
      "thread_id": 4711,
      "action": "fixed | answered | declined | needs-human",
      "reply": "<the reply as it will appear on the thread>",
      "proposed_status": "<provider thread status, or null to leave unchanged>",
      "files_changed": ["/path.cs"]
    }
  ]
}
```

- `fixed` — code changed; the reply says what changed in one or two sentences.
- `answered` — a question or misunderstanding; no code change; the reply is the answer, cited to code.
- `declined` — the fixer believes the comment is wrong or out of scope. **It changes nothing and says
  why**; a human decides. Never silently skipped, never "fixed" against its own judgement to look agreeable.
- `needs-human` — ambiguous, a design decision, or a change whose blast radius exceeds the thread.
- `proposed_status` follows the project's `fix-guidelines.md`. Absent a rule there, it is `null`: whoever
  opened a thread usually owns closing it.

## 8. Verdicts

`pr-reviewer` ends with exactly one fenced block (`AGENT-CONDUCT-BASELINE.md` B7):

```verdict
gate: pr-review
verdict: APPROVE | APPROVE WITH SUGGESTIONS | WAIT FOR AUTHOR | REJECT
head_sha: <sha>
counts: blocker=<n> major=<n> minor=<n> nit=<n> question=<n>
summary: <one line>
```

Derived, not felt: any `blocker` → `REJECT` or `WAIT FOR AUTHOR` (the latter when the fix is small and
obvious); any `major` or open `question` → `WAIT FOR AUTHOR`; only `minor`/`nit` → `APPROVE WITH
SUGGESTIONS`; nothing → `APPROVE`. It gates nothing mechanically — it is what the human reads first.
`counts` are over **findings caused by this PR**, anchored or not (§6) — never over proposed comments, and
never including pre-existing issues. A run that stopped before reviewing (a missing input) returns only
`## Blocking questions` and no verdict block; the command treats that as a valid return, not a malformed
one.

`pr-fixer` ends with:

```verdict
gate: pr-fix
verdict: ALL ADDRESSED | PARTIALLY ADDRESSED | BLOCKED
build: SUCCESS | FAILED | NOT RUN
tests: PASSED | FAILED | NOT RUN
counts: fixed=<n> answered=<n> declined=<n> needs-human=<n>
summary: <one line>
```

`NOT RUN` is a legitimate value and must be reported as such — never rounded up to success (Article IV).

## 9. Cross-model review

`AGENT-CONDUCT-BASELINE.md` B10 applies: `/pr:review` takes `--model=<name>`, passes it on the dispatch,
reports which model ran, and says so plainly when none was given. `pr-reviewer` carries no `model:` pin.
When `/pr:fix` is followed by a re-review of the fixes, run that review on a different model than fixed.

## 10. The PR head checkout

The reviewer must read whole files at the PR's head, not at whatever the developer's working tree
happens to have checked out. The command therefore:

1. `git fetch origin <source> <target>` — updates remote-tracking refs only.
2. `git worktree add --detach <scratch>/<repo>-PR-<id> <head_sha>` — a throwaway checkout outside the
   repo. Line numbers the reviewer sees with `Read` are then exactly the line numbers a PR comment needs.
3. Removes it with `git worktree remove` when the run ends, success or not — **after** posting and after
   any follow-up to the reviewer, never between dispatch and posting: the reviewer's follow-up answers and
   the command's own comment checks both read files at head from that checkout.

The developer's own working tree and branch are never touched by a review. `/pr:fix` is different by
nature: it needs the real working tree on the PR's source branch, clean, and it stops rather than
stashing or switching anything on its own.
