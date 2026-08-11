---
name: dev:status
description: Read and report a project's current ai/dev/ state (phase, gates, blockers, pointers) in a consistent format.
allowed-tools:
  - Read
  - Grep
  - Glob
argument-hint: "[path, optional - defaults to current directory]"
---

> Version: 1.0.0

<objective>
`/dev:status [path]` reads `ai/dev/STATE.md` + `config.json` for a project and reports where things stand,
without requiring a human to open and parse the files themselves.
</objective>

<process>
<step name="resolve-target">
Target = `$ARGUMENTS` if given, else the current working directory.
</step>

<step name="read-state">
Read `ai/dev/STATE.md` and `ai/dev/config.json`. If neither exists, say so plainly and point to
`/dev:init` — don't guess a status for an uninitialized project.
</step>

<step name="report">
Print, in this order: Phase (from STATE.md), Gates (qa/review/security, from config.json — call out any
that are `true`, since none are by default anywhere in this system), Source of truth / context_doc,
Build command, Blockers (from STATE.md — highlight if non-empty), and Decisions worth restating (from
STATE.md).
</step>
</process>

<rules>
- **Read-only.** This command never modifies `ai/dev/` — that's `/dev:init`'s job on first creation, and
  each `dev-*` agent's own job to update after a dispatch per `PRINCIPLES.md` §6.
- **Say plainly when a project isn't initialized** rather than presenting an empty/defaulted status as if
  it were real state.
</rules>
