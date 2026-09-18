# Bug Workflow — contract for `bug-analyst`, `bug-fixer` and the `bug:` commands

> Version: 1.0.0 — 2026-09-18. Binding on `claude\agents\bug-analyst.md`, `claude\agents\bug-fixer.md` and
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
  "results_dir": "<optional; absolute or repo-relative>",
  "default_branch_names": ["main", "master"]
}
```
Paths are relative to the repository root; a sibling repository is reached as `../<repo>`. A configured
path that does not exist is reported, never guessed around.

## 4. Where results go — customer data

Logs, incident tickets, timelines and briefs routinely contain **personal and customer data**
(Constitution Article VIII). Therefore:
- The results folder is, in order: `--out=`, `config.results_dir`, `ai/bug/results/`. The command verifies
  with `git check-ignore` that the folder is **outside any repository or git-ignored**. If it is neither,
  the command stops and asks for another folder — it never edits a `.gitignore` on its own.
- Nothing customer-identifying is ever written to a context file, the pattern file, a commit message, a
  fix report's code comments, or the chat relay beyond what is needed to name a session.
- Pattern entries describe the *mechanism*: no session ids, no customer ids, no names.
- A `--brief` (client-shareable) masks customer identifiers unless the human explicitly says otherwise.
- Never copy a credential out of a log or config file into any output (Article I).

## 5. Run artifacts — `<results>/<incident-or-ts>/`

| File | Written by | Content |
|---|---|---|
| `input-<ts>.md` | command | The bug description as given, the filters, the log folder, which log files matched which component. |
| `analysis-<ts>.md` | `bug-analyst` | Timeline · anomalies · narrative · root cause with confidence · affected components · **Fix proposal** (when located in code) · context-file corrections. Ends with the `bug-analysis` verdict block. |
| `brief-<ts>.md` | `bug-analyst`, only with `--brief` | Short, plain-language, shareable: condensed timeline, what happened, status history, RCA, remediation. |
| `fix-<ts>.md` | `bug-fixer` | What changed and why, build/test evidence, how to verify, proposed pattern entry. Ends with the `bug-fix` verdict block. |

Timeline anomaly markers, fixed: ⚠️ warning or unexpected gap · ❌ error · 🔴 fatal/crash · 🔁 retry/repeat ·
❓ **expected event missing** — naming the event the documented flow says should be there, with the
context-file section that says so.

## 6. Root cause — three honest levels

| Level | Meaning | What may follow |
|---|---|---|
| `CONFIRMED` | The log evidence and the code both show the mechanism end to end; every link is cited. | A fix proposal; after the fix, a pattern entry. |
| `HYPOTHESIS` | Consistent with the evidence, at least one link unverified. Ranked if several. Each names the evidence that would confirm or refute it. | A fix proposal **only** if the change is safe even if the hypothesis is wrong — and it says so. No pattern entry. |
| `INSUFFICIENT EVIDENCE` | Logs missing, filtered, or not covering the window. | A list of exactly what to collect. No proposal. |

A log line's **absence** is evidence only if the log guide confirms that line would have been written at
the configured level in that environment.

## 7. Fix proposal (inside `analysis-<ts>.md`) and its approval

```markdown
## Fix proposal
Root cause: <one sentence> (CONFIRMED | HYPOTHESIS)
Files to modify:
- <repo>/<path>:<lines> — <what will change and why>
Blast radius: <callers · protocol/contract · state model · schema · cross-repository · none>
Will NOT change: <explicit out-of-scope list>
Verification: <how to prove it, incl. a test to add if a test class exists>
```
`/bug:fix` shows this verbatim and asks: **Approve as written** / **Approve with changes** (the human's
text is appended as binding amendments) / **Do not fix**. The fixer gets the proposal plus amendments and
nothing else as its mandate. A cross-repository, schema or public-contract change is never approved
implicitly — the command names it in the question.

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
`NOT RUN` is a legitimate value and is reported as such (Article IV). Independent check of a fix: run the
project's review flow on a different model than fixed (`AGENT-CONDUCT-BASELINE.md` B10).
