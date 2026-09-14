---
name: handoff
description: Writes, resumes, lists and cleans up session handoffs in the project's ai/handoff/ — one naming convention and structure in every project. Use when the context guard warns, before stopping for the day, or to pick up and close a previous handoff.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Bash
  - AskUserQuestion
argument-hint: "[resume [file] | list | close [file] | anything extra to carry over]"
---

> Version: 2.0.0

<objective>
`/handoff` ends a session deliberately instead of letting it grow, and makes the next session pick it up and
clean it away. Four modes, chosen by the first word of `$ARGUMENTS`:

| Invocation | Mode |
|---|---|
| `/handoff [note]` | **write** — `<root>/ai/handoff/handoff-<YYYYMMDD-HHMM>-<slug>.md` from what this session already knows |
| `/handoff resume [file]` | **resume** — load a handoff, mark it resumed, continue; ask to delete it once handled |
| `/handoff list` | **list** — open handoffs in this project |
| `/handoff close [file]` | **close** — the approval-gated deletion on its own |

**One convention, every project** — code repos, SA engagements, the personal folder alike. A handoff never
goes to `results/`, `reports/`, `ai/merge/` or any other folder, and never under another name.

Why it exists: every turn re-sends the whole context, so a session's cost grows roughly with
turns × context — in the 2026-08/09 usage baseline, requests above 150k context were 46% of requests and
67% of spend. A handoff plus `/clear` is the cheap way out, and unlike `/compact` a human chose what
survives, and it is on disk where the next session, another tool, or a colleague can read it.

Distinct from project state. `ai/dev/STATE.md` and `ai/sa/<slug>/STATE.md` are the *project's* durable
state, owned by their frameworks; a handoff is *this session's* baton, and it is temporary by design — once
the next session has absorbed it, it is deleted. This command never rewrites those state files.
</objective>

<process>
<step name="resolve-root">
All modes. Walk up from the working directory to the nearest ancestor containing `ai/`, `CLAUDE.md`, or
`.git`; that is the project root. If none is found, use the working directory and say so in the output.
The handoff folder is `<root>/ai/handoff/`.
</step>

<step name="write" condition="no mode word, or only a free-text note">
**Compose from the conversation already in context.** Do not re-read the repository, re-run analysis, or
dispatch an agent — a handoff that costs a fresh investigation defeats its own purpose. Read a file only
to confirm a specific path or identifier you are about to write down. If the session is too short or too
shallow to have anything worth carrying over, say so and write nothing.

**Name**: `handoff-<YYYYMMDD-HHMM>-<slug>.md` — date/time from this session's context (no clock shell-out;
if the time of day is unknown, drop `-HHMM`), `<slug>` = 2–5 lowercase ASCII words from the session goal,
hyphen-separated, no accents. `Glob` the folder first; never overwrite — append `-2`, `-3` on a clash.
Create the folder if absent.

**Git position** (only if the root is a git repo): `git -C <root> rev-parse --abbrev-ref HEAD` and
`git -C <root> rev-parse --short HEAD`, forward-slash paths.

**Structure** — keep every heading in this order; drop a section only when it would be empty:

```markdown
# Handoff — <project> — <YYYY-MM-DD HH:MM> — <topic>

| | |
|---|---|
| **Status** | open |
| **Project root** | <absolute path> |
| **Branch / HEAD** | <branch> @ <short sha>  (omit row outside git) |
| **Resume with** | `/handoff resume <absolute path of this file>` |
| **Related state** | <ai/dev/STATE.md, ai/sa/<slug>/STATE.md, … or "none"> |

**Session goal:** <one or two sentences>
**Progress:** <in progress | blocked | complete-but-unverified>

## Where things stand
### Verified
<done and checked — how it was checked>
### Assumed / not yet verified
<done or believed true, but not checked>

## Decisions and why
<each decision with the reason and the rejected alternative — the expensive part to rebuild>

## Ruled out
<dead ends already tried, so the next session does not repeat them>

## Open questions
<for the user, or things to check>

## Next step
<the single next action, concrete enough to start on>

## Key paths and commands
<files touched, artifacts written, commands to re-run — absolute paths>

## Delete when done
<temporary files this session created that the resuming session should remove with the handoff — or drop>

## Also carry over
<$ARGUMENTS verbatim, if any>
```

Content rules: real paths, identifiers, ticket numbers and function names rather than descriptions; keep
verified and assumed apart; never copy secrets, tokens or credentials.

**Superseded handoff**: if this session was itself started with `/handoff resume <older file>` and that
file is still on disk, run the `close` step for it before printing the output.

Print this and nothing else:
```
Handoff written: <absolute path>

Next session:
  /handoff resume <absolute path>

Now: /clear (or start a new session).

May need updating: <project state file>   <- only when it applies
```
The last line appears only when the project has its own state file **and** this session changed the work
it describes. Never update that file here.
</step>

<step name="resume" condition="first word is resume">
1. File given → use it. None given → `Glob` `<root>/ai/handoff/handoff-*.md`, read each candidate's
   `Status` row, and keep only `open` ones (never auto-pick a `resumed` or `closed` file); one → use it;
   several → `AskUserQuestion` with the newest four; none → say so and stop.
2. `Read` it in full. Set its `Status` row to `resumed <YYYY-MM-DD>` with `Edit` — nothing else in the file
   changes.
3. Summarise in at most five lines: goal, where it stands, the next step, open questions — then one more
   line for the human: `When this is handled I'll ask to delete <file name> — say "close handoff" any
   time.` Then continue with the next step as the session's task.
4. **Standing instruction for the rest of this session:** when the handoff's next step and open questions
   are handled — or the user says the work is done, or a new `/handoff` is written — run the `close` step
   for this file. Do not wait to be reminded.
</step>

<step name="list" condition="first word is list">
`Glob` `<root>/ai/handoff/handoff-*.md`; read only each file's title and `Status` row. Print a table —
file name, status, date, topic — newest first. Also report, without moving anything, any file named like
a handoff (`*handoff*`, `SESSION-HANDOFF*`, `SESSION-STATE*`) elsewhere under `<root>/ai/`, `<root>/results/`
or `<root>/reports/` as "outside the convention".
</step>

<step name="close" condition="first word is close, or triggered by resume/write">
File given → use it; none → the file resumed in this session; otherwise ask as in `resume`.

Ask via `AskUserQuestion`: *"`<file name>` is handled — delete it?"* listing, in the question text, any
paths under its `## Delete when done`. Options:
- **Delete** — the handoff and the listed temporary files
- **Delete handoff only**
- **Keep** — set `Status` to `closed <YYYY-MM-DD>` and leave the file

On a delete choice: remove each file individually with `rm -- "<absolute path>"` (never a recursive or
wildcard delete); only paths inside the project root. Report exactly what was removed. Without an explicit
choice, nothing is deleted.
</step>
</process>

<rules>
- **One location, one name**: `<root>/ai/handoff/handoff-<YYYYMMDD[-HHMM]>-<slug>.md`, in every project
  (`-HHMM` dropped only when the time of day is unknown).
- **Compose from context, never re-derive.** No repo re-reads, no agent dispatch, no fresh analysis.
- **Never overwrite a handoff**; only `resume`/`close` edit its `Status` row.
- **Deletion only after an explicit `AskUserQuestion` choice**, one file at a time, never recursive.
- **Never touch `STATE.md` or any framework artifact.** Point at them instead.
- **Specific over tidy.** "Fixed the Quartz job-group bug in `SchedulerBootstrapper.cs:142`, tests not yet
  run" beats "made progress on scheduling".
- **No secrets in the file.**
</rules>
