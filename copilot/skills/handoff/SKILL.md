---
name: handoff
description: Write, resume, list or close a session handoff in the project's ai/handoff/ — the same files Claude Code's /handoff writes, so work can move between the two tools. Use when context is getting large, before stopping for the day, or to pick up and clean up an earlier handoff. Triggers on "/handoff", "write a handoff", "handoff resume", "resume the handoff", "list handoffs", "close handoff".
---

> Version: 1.0.0 — Copilot CLI sibling of `claude\commands\handoff.md` v2.1.0, ported 2026-09-14.

# Handoff

**Read `~/.copilot/dev-framework/HANDOFF.md` first and follow it.** It is the binding, tool-agnostic
contract — location and name, the file structure, the `Status` lifecycle, the deletion rule, conformance —
shared byte-for-byte with Claude Code. This file carries only what is Copilot-specific. A handoff written by
either tool is resumed and closed by the other.

## Mode

Take the first word after `/handoff` (or after "handoff") in the human's prompt:

| Words | Mode | Contract |
|---|---|---|
| nothing, or a free-text note | **write** | `HANDOFF.md` §2–§3; the note goes verbatim under `## Also carry over` |
| `resume [file]` | **resume** | §4 |
| `list` | **list** | §4 |
| `close [file]` | **close** | §5 |

If the prompt is ambiguous between write and resume, ask — a wrong write only adds a file, but a wrong
resume starts work on the wrong task.

## Copilot-specific mechanics

- **[Copilot] Time.** Take the date and time from session context if present; otherwise one read-only
  `Get-Date -Format "yyyyMMdd-HHmm"`. If neither is available, drop `-HHMM` as the contract allows.
- **[Copilot] Finding files.** List `{root}/ai/handoff/handoff-*.md` and read only the title and `Status` row
  of each for list and resume selection — never whole files just to choose one.
- **[Copilot] Git position.** `git -C {root} rev-parse --abbrev-ref HEAD` and
  `git -C {root} rev-parse --short HEAD`. Skip outside a git repo.
- **[Copilot] Asking the human.** Copilot CLI has no structured question tool (`PORT-NOTES.md` D4). Ask in
  plain text, list the choices numbered, and **wait for the reply** — do not continue in the same turn:

  ```
  <file name> is handled. Delete it?
    1. Delete — the handoff and: <each path under "Delete when done", or "nothing else">
    2. Delete handoff only
    3. Keep — mark it closed and leave it
  ```

  Only an explicit `1`/`2` (or the words "delete"/"delete handoff only") deletes. Anything else, including
  no answer, is **Keep**.
- **[Copilot] Deleting.** One file per command, absolute path, inside the project root only:
  `Remove-Item -LiteralPath "{absolute path}"`. Never `-Recurse`, never a wildcard. Report each removal.
- **[Copilot] After write.** Print exactly:

  ```
  Handoff written: <absolute path>

  Next session (Copilot CLI or Claude Code):
    /handoff resume <absolute path>

  Now: /clear (or /new).

  May need updating: <project state file>   <- only when it applies
  ```

  `/compact` and `/resume {session}` are Copilot's own alternatives, but neither leaves a file another tool
  or person can read — that is why this skill exists.

## Rules

- The contract in `HANDOFF.md` wins over anything here; a conflict is a bug in this file.
- Compose from context. No repo re-reads, no `@agent` dispatch, no fresh analysis.
- Never overwrite a handoff; only resume and close edit it, and only its `Status` row.
- Never touch `STATE.md` or any framework artifact.
- No secrets, tokens or credentials in the file.
