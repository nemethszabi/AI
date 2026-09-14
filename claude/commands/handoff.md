---
name: handoff
description: Writes, resumes, lists and cleans up session handoffs in the project's ai/handoff/ — one naming convention and structure in every project and both tools. Use when the context guard warns, before stopping for the day, or to pick up and close a previous handoff.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Bash
  - AskUserQuestion
argument-hint: "[resume [file] | list | close [file] | anything extra to carry over]"
---

> Version: 2.1.0 — 2026-09-14: the contract (name, structure, lifecycle, deletion rule) moved to the shared
> `dev-framework/HANDOFF.md` so Copilot CLI's `handoff` skill implements the same one; no behaviour change.

<objective>
`/handoff` ends a session deliberately instead of letting it grow, and makes the next session pick it up and
clean it away. Four modes, chosen by the first word of `$ARGUMENTS`:

| Invocation | Mode |
|---|---|
| `/handoff [note]` | **write** — `<root>/ai/handoff/handoff-<YYYYMMDD-HHMM>-<slug>.md` from what this session already knows |
| `/handoff resume [file]` | **resume** — load a handoff, mark it resumed, continue; ask to delete it once handled |
| `/handoff list` | **list** — open handoffs in this project |
| `/handoff close [file]` | **close** — the approval-gated deletion on its own |

**The binding contract is `~/.claude/dev-framework/HANDOFF.md`** — read it before any mode. Location and
name (§2), the file structure (§3), the `Status` lifecycle (§4), the deletion rule (§5) and conformance (§6)
live there, shared byte-for-byte with Copilot CLI's `handoff` skill, so a handoff written in either tool is
resumed and closed in the other. This file carries only the Claude Code mechanics.
</objective>

<process>
<step name="load-contract">
All modes. `Read` `~/.claude/dev-framework/HANDOFF.md` (under a profile: `$CLAUDE_CONFIG_DIR/dev-framework/
HANDOFF.md`). Resolve the project root as its §2 describes.
</step>

<step name="write" condition="no mode word, or only a free-text note">
Follow §2–§3. Claude mechanics:
- Date/time from this session's context — no clock shell-out; unknown time of day → drop `-HHMM`.
- `Glob` `<root>/ai/handoff/` before naming; create the folder if absent.
- Git position: `git -C <root> rev-parse --abbrev-ref HEAD` and `git -C <root> rev-parse --short HEAD`.
- `$ARGUMENTS` goes verbatim under `## Also carry over`.
- If this session began with `/handoff resume <older file>` and it is still on disk, run `close` for it first.

Print this and nothing else:
```
Handoff written: <absolute path>

Next session (Claude Code or Copilot CLI):
  /handoff resume <absolute path>

Now: /clear (or start a new session).

May need updating: <project state file>   <- only when it applies
```
</step>

<step name="resume" condition="first word is resume">
Follow §4. Claude mechanics: `Glob` `<root>/ai/handoff/handoff-*.md` and read only each file's `Status` row to
select; several `open` → `AskUserQuestion` with the newest four. Set the `Status` row with `Edit`. End the
five-line summary with: `When this is handled I'll ask to delete <file name> — say "close handoff" any time.`
The §4 standing obligation to close holds for the rest of this session.
</step>

<step name="list" condition="first word is list">
Follow §4 (list). `Glob` for the files; read only title and `Status` rows.
</step>

<step name="close" condition="first word is close, or triggered by resume/write">
Follow §5. Claude mechanics: ask via `AskUserQuestion` with the three options **Delete** / **Delete handoff
only** / **Keep**, listing the `## Delete when done` paths in the question text. Delete each file with
`rm -- "<absolute path>"`. Without an explicit delete choice, nothing is deleted.
</step>
</process>

<rules>
- **`HANDOFF.md` is the contract**; a conflict between it and this file is a bug here.
- **Compose from context, never re-derive.** No repo re-reads, no agent dispatch, no fresh analysis.
- **Never overwrite a handoff**; only `resume`/`close` edit its `Status` row.
- **Deletion only after an explicit `AskUserQuestion` choice**, one file at a time, never recursive.
- **Never touch `STATE.md` or any framework artifact.** Point at them instead.
- **No secrets in the file.**
</rules>
