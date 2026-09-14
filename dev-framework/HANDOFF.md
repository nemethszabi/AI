# Session handoff — shared contract

> Version: 1.0.0 — extracted 2026-09-14 from `claude\commands\handoff.md` v2.0.0 when handoffs were ported
> to Copilot CLI.

**Binding** on every tool's handoff implementation. It defines *the work* — where a handoff lives, what it
contains, how it is resumed and removed. *How a tool does it* (command vs skill, how the human is asked,
which delete command runs) stays in that tool's own file:

| Tool | Implementation | Invocation |
|---|---|---|
| Claude Code | `claude\commands\handoff.md` | `/handoff [resume [file] \| list \| close [file] \| note]` |
| Copilot CLI | `copilot\skills\handoff\SKILL.md` | `/handoff …` in the prompt, same words |

Both read this file rather than restating it — the same "share the method, separate the mechanics" split as
`sa-framework\PIPELINE.md`. The payoff is the same too: a handoff is a project file, so one written in
either tool can be resumed and closed in the other.

---

## 1. Why a handoff exists

Every turn re-sends the whole context, so a session's cost grows roughly with turns × context. A handoff
plus `/clear` ends a session deliberately instead of letting it grow — unlike `/compact`, a human chose what
survives, and it is on disk where the next session, another tool, or a colleague can read it.

A handoff is **this session's baton and temporary by design**. `ai/dev/STATE.md` and `ai/sa/<slug>/STATE.md`
are the *project's* durable state, owned by their frameworks; a handoff never rewrites them, only points at
them.

## 2. Location and name — one convention, every project

- **Root**: walk up from the working directory to the nearest ancestor containing `ai/`, `CLAUDE.md`,
  `AGENTS.md` or `.git`. None found → the working directory, and say so.
- **Folder**: `<root>/ai/handoff/` — never `results/`, `reports/`, `ai/merge/` or anywhere else (standard
  `ai/` layout, `PRINCIPLES.md`).
- **Name**: `handoff-<YYYYMMDD-HHMM>-<slug>.md`. `<slug>` = 2–5 lowercase ASCII words from the session goal,
  hyphen-separated, no accents. `-HHMM` is dropped only when the time of day is unknown.
- **Never overwrite**: on a clash append `-2`, `-3`.

## 3. Writing — compose from context, never re-derive

Compose from the conversation already held. No repository re-read, no re-run analysis, no agent dispatch —
a handoff that costs a fresh investigation defeats its own purpose. Read a file only to confirm a path or
identifier about to be written down. A session too short to carry anything over gets no file, and says so.

Git position (only inside a git repo): current branch and short HEAD, forward-slash paths.

**Structure** — every heading, in this order; a section is dropped only when it would be empty:

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
<the human's extra note verbatim, if any>
```

Content rules: real paths, identifiers, ticket numbers and function names rather than descriptions; verified
and assumed kept apart; **no secrets, tokens or credentials**. "Fixed the Quartz job-group bug in
`SchedulerBootstrapper.cs:142`, tests not yet run" beats "made progress on scheduling".

After writing, the output is: the file path, the exact resume line, the instruction to `/clear` (or start a
new session), and — only when the project has its own state file **and** this session changed the work it
describes — a line naming that file as possibly needing an update. Never update it from here.

## 4. Lifecycle — the `Status` row

| Status | Set by | Meaning |
|---|---|---|
| `open` | write | Not yet picked up. The only value `resume` auto-selects. |
| `resumed <YYYY-MM-DD>` | resume | A session has absorbed it and owns closing it. |
| `closed <YYYY-MM-DD>` | close → *Keep* | Handled, kept on disk as history. |

Only resume and close ever edit a handoff, and only its `Status` row.

- **Resume**: a named file wins; otherwise list `open` handoffs — one → use it, several → ask the human
  (newest four), none → say so and stop. Read it in full, set `resumed <date>`, summarise in at most five
  lines (goal, where it stands, next step, open questions), tell the human it will be offered for deletion
  once handled, then continue with its next step.
- **Standing obligation after resume**: when the next step and open questions are handled — or the human
  says the work is done, or a new handoff is written — run close for that file without being reminded.
- **Superseded**: a session started from a handoff that writes a new one closes the old one first.
- **List**: title, status, date, topic, newest first. Also report — without moving anything — files named
  like a handoff (`*handoff*`, `SESSION-HANDOFF*`, `SESSION-STATE*`) under `<root>/ai/`, `<root>/results/`
  or `<root>/reports/` as "outside the convention".

## 5. Close — deletion only on an explicit choice

Ask the human, naming the file and every path under its `## Delete when done`. Three answers:

- **Delete** — the handoff and the listed temporary files
- **Delete handoff only**
- **Keep** — set `Status` to `closed <YYYY-MM-DD>` and leave the file

Deletion happens only after one of the two delete answers is given explicitly — silence, "ok", or moving on
is *Keep*. Files are removed one at a time by absolute path, never with a recursive or wildcard delete, and
only inside the project root. Report exactly what was removed.

## 6. Conformance — what "the same handoff" means across tools

An implementation conforms when all of these hold:

1. §2 location and name, byte-for-byte the same pattern.
2. §3 structure: every heading in order, the five-row header table, `Status` row first.
3. Compose-from-context: no re-read, no dispatch, no analysis.
4. §4 statuses spelled exactly `open` / `resumed <date>` / `closed <date>`, so either tool's `list` and
   `resume` read the other's files.
5. §5 deletion gated on an explicit answer, one file at a time, inside the root.
6. Never touches `STATE.md` or any framework artifact.

A divergence forced by the tool (no structured question tool, a different delete command) is recorded in the
implementation as `[Copilot]` / `[Claude]`, never by changing this contract.
