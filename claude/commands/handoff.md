---
name: handoff
description: Writes this session's handoff to the project's ai/handoff/ and prints the prompt that resumes it in a fresh session. Use when the context guard warns, or before stopping for the day.
allowed-tools:
  - Read
  - Write
  - Grep
  - Glob
argument-hint: "[anything extra to carry over, optional]"
---

> Version: 1.0.0

<objective>
`/handoff` ends a session deliberately instead of letting it grow. It writes
`<project>/ai/handoff/handoff-<YYYYMMDD-HHMM>.md` from the knowledge **this session already holds**, then
prints the one-line prompt that resumes the work in a new session.

Why it exists: every turn re-sends the whole context, so a session's cost grows roughly with
turns × context — in the 2026-08/09 usage baseline, requests above 150k context were 46% of requests and
67% of spend. A handoff plus `/clear` is the cheap way out, and
unlike `/compact` it is lossless in the way that matters: a human chose what survives, and it is on disk
where the next session, another tool, or a colleague can read it.

Distinct from the state files it sits beside. `ai/dev/STATE.md` and `ai/sa/<slug>/STATE.md` are the
*project's* durable state, owned by their frameworks; a handoff is *this session's* baton — what was in
flight, what was decided and why, what to do next. This command never rewrites those files.
</objective>

<process>
<step name="resolve-target">
Walk up from the working directory to the nearest ancestor containing `ai/`, `CLAUDE.md`, or `.git`; that
is the project root. If none is found, use the working directory and say so in the output.

Write to `<root>/ai/handoff/`, creating it if absent. Filename: `handoff-<YYYYMMDD-HHMM>.md`, built from
the date already in this session's context — do not shell out for a clock. If the time of day is not
established in context, use `handoff-<YYYYMMDD>.md`.

Never overwrite an existing handoff: `Glob` `<root>/ai/handoff/handoff-*.md` first and, if the name is
already taken, append `-2` (then `-3`, and so on).
</step>

<step name="gather">
Compose **from the conversation already in context**. Do not re-read the repository, re-run analysis, or
dispatch an agent to reconstruct anything — a handoff that costs a fresh investigation defeats its own
purpose. Read a file only to confirm a specific path or identifier you are about to write down.

If the session is too short or too shallow to have anything worth carrying over, say so and write nothing.
</step>

<step name="write">
Write this structure, dropping any section that would be empty rather than padding it:

```markdown
# Handoff — <project> — <YYYY-MM-DD HH:MM>

**Session goal:** <one or two sentences>
**Status:** <in progress | blocked | complete-but-unverified>

## Where things stand
<what is done, what is half-done, what was verified vs assumed>

## Decisions and why
<each decision with the reason and the alternative rejected — the reasoning is the part that is expensive
to rebuild>

## Ruled out
<dead ends already tried, so the next session does not repeat them>

## Open questions
<questions for the user, or things to check>

## Next step
<the single next action, concrete enough to start on>

## Key paths and commands
<files touched, artifacts written, commands to re-run — absolute paths>
```

Rules for the content: name real paths, identifiers, ticket numbers and function names rather than
describing them; separate what was verified from what was assumed; never copy secrets, tokens or
credentials into the file. Append anything the user passed in `$ARGUMENTS` under a `## Also carry over`
section.
</step>

<step name="output">
Print this and nothing else:

```
Handoff written: <absolute path>

Next session:
  Read <absolute path> and continue.

Now: /clear (or start a new session).

May need updating: <project state file>   <- final line, only when it applies
```

The last line appears only when the project has its own state file (`ai/dev/STATE.md`,
`ai/sa/<slug>/STATE.md`) **and** this session changed the work that file describes — it lets the user
decide whether to update it. Omit the line entirely otherwise. Never update that file here.
</step>
</process>

<rules>
- **Compose from context, never re-derive.** No repo re-reads, no agent dispatch, no fresh analysis.
- **Never overwrite a handoff.** They are a history; a stale one is still evidence of what was thought when.
- **Never touch `STATE.md` or any framework artifact.** Point at them instead.
- **Specific over tidy.** "Fixed the Quartz job-group bug in `SchedulerBootstrapper.cs:142`, tests not yet
  run" beats "made progress on scheduling".
- **No secrets in the file.**
</rules>
