---
name: bug:analyze
description: Analyze an incident or bug from logs - dispatches bug-analyst to build a unified cross-component timeline, mark anomalies, state a root cause at an honest confidence level and, when located in code, write a fix proposal for /bug:fix. Optionally a client-shareable brief.
allowed-tools:
  - Read
  - Write
  - Grep
  - Glob
  - Agent
  - SendMessage
  - AskUserQuestion
  - Bash(git -C * check-ignore *)
  - Bash(git -C * rev-parse *)
  - Bash(date *)
  - PowerShell(git -C * check-ignore *)
  - PowerShell(git -C * rev-parse *)
  - PowerShell(Get-Date *)
disallowed-tools:
  - Edit
  - NotebookEdit
argument-hint: "[project path, optional] --logs=<folder> [--desc=<file> | --desc=\"text\"] [--user=<name,..>] [--id=<session/correlation id,..>] [--date=YYYY-MM-DD] [--incident=<ref>] [--brief] [--out=<folder>] [--model=<name>]"
---

> Version: 1.0.0 — 2026-09-18. Initial (revised after agent-review round 2).

<objective>
`/bug:analyze --logs=<folder> --desc=<ticket.md>` turns an incident's logs and description into
`analysis-<ts>.md` — timeline, anomalies, root cause (CONFIRMED / HYPOTHESIS / INSUFFICIENT EVIDENCE) and,
where the cause is located in code, a fix proposal — via the generic `bug-analyst` agent. Nothing is
changed. Contract: `~/.claude/dev-framework/BUG-WORKFLOW.md`.
</objective>

<process>
<step name="resolve-arguments">
Optional leading project path (default: current directory). `--logs` is required — missing → ask once via
`AskUserQuestion`; given but not an existing folder (check with `Glob`) → say so and stop. `--desc` is a path if it resolves to a file, else free text; absent → ask the user to
paste the description (any language). `--user`, `--id`, `--date`, `--incident` are filters passed through
as given. `--brief`, `--out`, `--model`.

`ts` = now as `YYYYMMDD-HHMM`, local time, from `date +%Y%m%d-%H%M` (Bash) or `Get-Date -Format
yyyyMMdd-HHmm` (PowerShell) — the only shell call besides the granted `git` ones. One `ts` per run.
</step>

<step name="load-config">
Read `<project>/ai/bug/config.json`. Missing → print the minimal `config.json` from `/bug:help` and stop;
do not invent component names or log patterns.
</step>

<step name="resolve-results-dir">
Candidate = `--out`, else `config.results_dir` (resolved against `<project>`; it may point outside the
repository, e.g. `../<repo>-bug-results`). With neither: propose `<repo-parent>/<repo>-bug-results` and
ask once via `AskUserQuestion` (**Use it** / **Other folder** / **`ai/bug/results` — I have git-ignored
it**). Run sub-folder = `<candidate>/<--incident, else ts>`; `results_dir` from here on is that
sub-folder, absolute.

The first file this command writes is `<results_dir>/input-<ts>.md`; that full path must be **outside
any git repository or git-ignored**: `git -C <nearest existing parent> rev-parse --show-toplevel` fails,
or `git -C <that repo> check-ignore <full path of input-<ts>.md>` succeeds — check the file path, not the
folder, which does not exist yet. Inside a repository and not ignored → stop and ask via
`AskUserQuestion` for another folder — logs and timelines carry customer data (`BUG-WORKFLOW.md` §4).
Never edit a `.gitignore` here. No `mkdir`: `Write` creates the missing folders.
</step>

<step name="map-logs">
`Glob` each component's `log_file_patterns` inside `--logs` (recursively). No component matched at all →
show what is in the folder and ask whether to continue. Files matching no component → list them and ask
once via `AskUserQuestion` how to treat them (**Search them too, unattributed** — the default /
**Attribute to a component: …** / **Ignore them**). Write `input-<ts>.md`: the description verbatim, the
filters, the log folder, the component → matched files table including components with no files, the
unmatched files, and the answer on how to treat them.
</step>

<step name="dispatch">
Dispatch `bug-analyst` via `Agent` — `model:` when `--model` was given — with the absolute paths and
values its `<inputs>` table names (`repo_root`, `logs_dir`, `input_file`, `results_dir` — the absolute run
sub-folder, already created — `ts`, `brief`), the model name so the report can record it, and any output
wishes the user expressed (shape, length, language of a brief). Parse only the returned
fenced `verdict` block (`gate: bug-analysis`). A return that carries only `## Blocking questions` and no
verdict block is valid (`BUG-WORKFLOW.md` §8) — go to `relay`'s question path. A return with neither →
re-prompt once via `SendMessage`, then report the failure and keep the files.
</step>

<step name="relay">
Show the agent's summary — with any customer name, phone number, e-mail or message content removed —
the file paths, and the limits it reported. State which model ran; if no
`--model` was given, say it ran on the session model. Name sessions by their id only — no customer
names, phone numbers or message content in the relay (`BUG-WORKFLOW.md` §4). If it returned
`## Blocking questions`, put them to the user via `AskUserQuestion` and send the answers back with
`SendMessage`. When the verdict carries `fix_proposal: yes`, end with the exact next command:
`/bug:fix <project> <analysis file>`. When it is `INSUFFICIENT EVIDENCE`, end with the list of what to
collect. Iterating on a brief's wording is a `SendMessage` to the same analyst, not a re-run; after any
follow-up, the files are those on the analyst's latest `Files:` line (`-r<N>` revisions) and its latest verdict.
</step>
</process>

<rules>
- **Read-only flow.** This command and its agent change no source, no context file, no git state.
- **Results never land in a tracked folder.** Stop and ask rather than write there.
- **Don't paraphrase the description** into `input-<ts>.md` — verbatim, so the analyst reads what the
  reporter wrote.
- **Thin.** No diagnosing in the relay; questions about the analysis go to the analyst via `SendMessage`
  while its session lives, afterwards to `analysis-<ts>.md` and its cited log refs.
</rules>
