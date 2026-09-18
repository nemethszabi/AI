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
  - PowerShell(git -C * check-ignore *)
  - PowerShell(git -C * rev-parse *)
argument-hint: "[project path, optional] --logs=<folder> [--desc=<file> | --desc=\"text\"] [--user=<name,..>] [--id=<session/correlation id,..>] [--date=YYYY-MM-DD] [--incident=<ref>] [--brief] [--out=<folder>] [--model=<name>]"
---

> Version: 1.0.0 — 2026-09-18. Initial.

<objective>
`/bug:analyze --logs=<folder> --desc=<ticket.md>` turns an incident's logs and description into
`analysis-<ts>.md` — timeline, anomalies, root cause (CONFIRMED / HYPOTHESIS / INSUFFICIENT EVIDENCE) and,
where the cause is located in code, a fix proposal — via the generic `bug-analyst` agent. Nothing is
changed. Contract: `~/.claude/dev-framework/BUG-WORKFLOW.md`.
</objective>

<process>
<step name="resolve-arguments">
Optional leading project path (default: current directory). `--logs` is required — missing → ask once via
`AskUserQuestion`. `--desc` is a path if it resolves to a file, else free text; absent → ask the user to
paste the description (any language). `--user`, `--id`, `--date`, `--incident` are filters passed through
as given. `--brief`, `--out`, `--model`.
</step>

<step name="load-config">
Read `<project>/ai/bug/config.json`. Missing → print the minimal `config.json` from `/bug:help` and stop;
do not invent component names or log patterns.
</step>

<step name="resolve-results-dir">
Candidate = `--out`, else `config.results_dir`, else `<project>/ai/bug/results`. Sub-folder =
`--incident` if given, else `<ts>` (`YYYYMMDD-HHMM`). The candidate must be **outside any git repository
or git-ignored**: `git -C <candidate's nearest existing parent> rev-parse --show-toplevel` fails, or
`git -C <that repo> check-ignore <candidate>` succeeds. If it is inside a repository and not ignored:
stop and ask via `AskUserQuestion` for another folder — logs and timelines carry customer data
(`BUG-WORKFLOW.md` §4). Never edit a `.gitignore` here.
</step>

<step name="map-logs">
`Glob` each component's `log_file_patterns` inside `--logs` (recursively). Write `input-<ts>.md`: the
description verbatim, the filters, the log folder, and the component → matched files table, including
components with no files and files matching no component. No component matched at all → show what is in
the folder and ask whether to continue.
</step>

<step name="dispatch">
Dispatch `bug-analyst` via `Agent` — `model:` when `--model` was given — with the absolute paths and
values its `<inputs>` table names (`repo_root`, `logs_dir`, `input_file`, `results_dir`, `ts`, `brief`)
and any output wishes the user expressed (shape, length, language of a brief). Parse only the returned
fenced `verdict` block (`gate: bug-analysis`); missing/malformed → re-prompt once via `SendMessage`, then
report the failure and keep the files.
</step>

<step name="relay">
Show the agent's summary, the file paths, and the limits it reported. If it returned
`## Blocking questions`, put them to the user via `AskUserQuestion` and send the answers back with
`SendMessage`. When the verdict carries `fix_proposal: yes`, end with the exact next command:
`/bug:fix <project> <analysis file>`. When it is `INSUFFICIENT EVIDENCE`, end with the list of what to
collect. Iterating on a brief's wording is a `SendMessage` to the same analyst, not a re-run.
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
