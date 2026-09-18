# Bug Workflow — contract for `bug-analyst`, `bug-fixer` and the `bug:` commands

> Version: 1.0.0 — 2026-09-18 (revised after agent-review round 2). Binding on `claude\agents\bug-analyst.md`, `claude\agents\bug-fixer.md` and
> `claude\commands\bug\*`. Read after `CONSTITUTION.md`. Sibling of `PR-WORKFLOW.md`; same design rule:
> **the agents are generic, a project differs only by data in its own repo.**

From an incident to a fix in two gated steps: **analyze** (logs + a bug description → a unified
cross-component timeline, anomalies, a root-cause statement and, where the cause is located in code, a fix
proposal) and **fix** (the *approved* proposal → a minimal change, built, tested, reported). Generalised
from a project-specific log-analysis prompt that had proven itself on real incidents; what was specific
to that project became §2's data files.

## 1. Division of labour

| Actor | Runs in | May | May never |
|---|---|---|---|
| `/bug:analyze`, `/bug:fix` (commands) | main session | resolve inputs, check where results may be written, ask the human, dispatch, and — after explicit approval — append a pattern entry or commit locally | push; fix without an approved proposal; write results into a tracked folder |
| `bug-analyst` | dispatched, read-only on source and logs | read logs, context and code; write its report files into the run's results folder | edit source, touch git state, decide that a fix goes ahead |
| `bug-fixer` | dispatched | edit source in the working tree per the approved proposal, build, test, write its report | widen the proposal, commit, push, edit context or pattern files |

The approval between the two steps is the point of the split: an agent cannot ask a human
(`AGENT-TEMPLATE-BASELINE.md` §1), so the *proposal* is a file, the *approval* happens in the command, and
the fixer receives only what was approved.

## 2. Project files — `ai/bug/`

```
<repo>/ai/bug/
  config.json      components, log patterns, build/test commands, context + pattern files (§3)   required
  log-guide.md     how to read THIS system's logs: identifiers, correlation, timezone,
                   error-recognition table, what is filtered out of which log                       strongly advised
```
`ai/context/*.md` holds the system knowledge (flows, contracts, playbooks) and is read first by both
agents. The **pattern file** (`config.patterns_file`) is the project's list of *confirmed* diagnosed bugs.

## 3. `config.json`

```json
{
  "schema": "bug-config/1",
  "context_files": ["ai/context/<slug>-context.md"],
  "patterns_file": "ai/context/<slug>-bug-patterns.md",
  "log_guide": "ai/bug/log-guide.md",
  "components": [
    {
      "name": "<short name used in timelines, e.g. API>",
      "repository": ". | ../<sibling repo>",
      "log_file_patterns": ["<glob>"],
      "build_command": "<cmd, run from that repository's root>",
      "test_command": "<cmd or empty>"
    }
  ],
  "results_dir": "<optional; repo-relative, may point outside the repo, e.g. ../<repo>-bug-results>",
  "default_branch_names": ["main", "master"]
}
```
Paths are relative to the repository root; a sibling repository is reached as `../<repo>`. A configured
path that does not exist is reported, never guessed around. `results_dir` is resolved against the
repository root like every other path and may leave the repository (`../<repo>-bug-results`); a committed
config never holds an absolute machine path. Missing `default_branch_names` → `["main", "master"]`.

## 4. Where results go — customer data

Logs, incident tickets, timelines and briefs routinely contain **personal and customer data**
(Constitution Article VIII). Therefore:
- The **results root** is resolved the same way by both commands, in order: `--out=`, then
  `config.results_dir` (resolved against the repository root), then `<repo-parent>/<repo>-bug-results`
  (outside the repository — `/bug:analyze` proposes it and asks once), then `ai/bug/results/` — only when
  the human chose it and has git-ignored it. `/bug:fix` searches for an analysis in that same order. The
  command verifies that the folder is **outside
  any repository, or git-ignored** — `git check-ignore` on the full path of the first file it will write,
  not on the folder, which may not exist yet. If neither holds, it stops and asks for another folder.
- The tooling **never edits a `.gitignore`**. The human adds `ai/bug/results/` (and `ai/pr/results/`)
  there. Where a step needs a *clean tree*, that means no tracked changes and no untracked files outside
  `ai/`: `git status --porcelain -- . ":(exclude)ai/"` is empty.
- Nothing customer-identifying is ever written to a context file, the pattern file, a commit message, a
  fix report's code comments, or the chat relay. Commit messages carry no customer identifiers — no
  incident ticket number tied to a customer, no names, no session ids. The relay names a session by its id
  only — and so does what an agent returns to the command (its summary lines and the verdict `summary:`).
- Pattern entries describe the *mechanism*: no session ids, no customer ids, no names.
- A `--brief` (client-shareable) masks customer identifiers unless the human explicitly says otherwise.
- Never copy a credential out of a log or config file into any output (Article I). A credential found in a
  log is flagged under the analysis's limits by file and key, never by value (Article I.3).

## 5. Run artifacts — `<results>/<incident-or-ts>/`

The command creates the run sub-folder (`Write` creates missing folders) and passes **that sub-folder**,
absolute, to the agents as `results_dir`. Log files that match no component's pattern are searched by the
analyst unless the human chose to ignore them, and listed as searched/unattributed — how to treat them is
asked once and recorded in `input-<ts>.md`.

| File | Written by | Content |
|---|---|---|
| `input-<ts>.md` | command | The bug description as given, the filters, the log folder, which log files matched which component, the unmatched files and how the human said to treat them. |
| `analysis-<ts>.md` | `bug-analyst` | Timeline · anomalies · narrative · root cause with confidence · affected components · **Fix proposal** (when located in code) · context-file corrections. Ends with the `bug-analysis` verdict block. |
| `brief-<ts>.md` | `bug-analyst`, only with `--brief` | Short, plain-language, shareable: condensed timeline, what happened, status history (where the system has one), RCA, remediation. |
| `fix-<ts>.md` | `bug-fixer` | What changed and why, build/test evidence, how to verify, proposed pattern entry (only for a `CONFIRMED` cause and a `FIXED` verdict). Written on every exit, including a stop. Ends with the `bug-fix` verdict block. |

A `SendMessage` follow-up that changes an agent's result writes `<name>-<ts>-r<N>.md` (same `<ts>`, never
overwriting, as `PR-WORKFLOW.md` §4), names it on the reply's `Files:`/`File:` line and re-emits the
verdict; the commands read the latest.

Timeline anomaly markers, fixed: ⚠️ warning or unexpected gap · ❌ error · 🔴 fatal/crash · 🔁 retry/repeat ·
❓ **expected event missing** — naming the event the documented flow says should be there, with the
context-file section that says so.

## 6. Root cause — three honest levels

| Level | Meaning | What may follow |
|---|---|---|
| `CONFIRMED` | The log evidence and the code both show the mechanism end to end; every link is cited. | A fix proposal; after a `FIXED` fix, a pattern entry. |
| `HYPOTHESIS` | Consistent with the evidence, at least one link unverified. Ranked if several. Each names the evidence that would confirm or refute it. | A fix proposal **only** if the change is safe even if the hypothesis is wrong — and it says so on the proposal's `Safe if the hypothesis is wrong:` line. No pattern entry. |
| `INSUFFICIENT EVIDENCE` | Logs missing, filtered, or not covering the window. | A list of exactly what to collect. No proposal. |

A log line's **absence** is evidence only if the log guide confirms that line would have been written at
the configured level in that environment.

## 7. Fix proposal (inside `analysis-<ts>.md`) and its approval

```markdown
## Fix proposal
Root cause: <one sentence> (CONFIRMED | HYPOTHESIS)
Files to modify:
- <component.repository exactly as in config.json>/<path>:<lines> — <what will change and why>
Blast radius: <callers · protocol/contract · state model · schema · cross-repository · none>
Will NOT change: <explicit out-of-scope list>
Verification: <how to prove it, incl. a test to add if a test class exists>
Safe if the hypothesis is wrong: <why — required when the level is HYPOTHESIS; omit for CONFIRMED>
```
`/bug:fix` shows this verbatim and asks: **Approve as written** / **Approve with changes** (the human's
text is appended as binding amendments) / **Do not fix**. The fixer gets the proposal plus amendments and
nothing else as its mandate. A cross-repository, schema or public-contract change is never approved
implicitly — the command names it in the question.

A file entry starts with the component's `repository` value exactly as `config.json` writes it —
`./Src/X.cs:40-52`, `../<sibling repo>/Src/Y.cs:10-18` — so the command maps it to a component by exact
match; an entry that matches no component stops `/bug:fix`.

**An amendment given after dispatch is a new approval.** An answer to the fixer's `## Decisions needed` or
`## Blocking questions` that adds a file, a repository, a schema/migration change or a public-contract
change is put to the human in its own question, naming that change. Before it is sent, the command runs
its ground check on every repository not checked yet. On such a follow-up the tree is expected dirty with
exactly the files the previous fix report lists; any other change → stop.

## 8. Verdicts

```verdict
gate: bug-analysis
verdict: CONFIRMED | HYPOTHESIS | INSUFFICIENT EVIDENCE
fix_proposal: yes | no
components: <comma list>
summary: <one line>
```
```verdict
gate: bug-fix
verdict: FIXED | PARTIALLY FIXED | BLOCKED
build: SUCCESS | FAILED | NOT RUN
tests: PASSED | FAILED | NOT RUN
summary: <one line>
```
An analyst run that stopped before analysing (a missing input) returns only `## Blocking questions` and
no verdict block; the command treats that as a valid return and puts the questions to the human, not as
a malformed one. Only a return with neither triggers the re-prompt.

`build` and `tests` aggregate across components, worst first: `FAILED` > `NOT RUN` > `SUCCESS`/`PASSED`. A
`NOT RUN` only because a component's `test_command` is empty does not count; the fix report lists every
component separately.

`bug-fix` verdict, derived, not felt:
- `FIXED` — the approved change is fully applied, build `SUCCESS` and tests `PASSED` (or `NOT RUN` only
  because no `test_command` is configured).
- `PARTIALLY FIXED` — something changed, but the change is incomplete (a gap reported under
  `## Decisions needed`), or build/tests `FAILED`, or build `NOT RUN` for toolchain reasons.
- `BLOCKED` — nothing changed: stopped at verify-ground, the defect is no longer present as described, an
  input is missing, or the approved change is not coherent on its own. The block is still emitted, with
  `build`/`tests` `NOT RUN`.

`NOT RUN` is a legitimate value and is reported as such (Article IV). Independent check of a fix: run the
project's review flow on a different model than fixed (`AGENT-CONDUCT-BASELINE.md` B10).
