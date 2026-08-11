---
name: dev:help
description: Static reference for the dev: command namespace. No live analysis, no project context read.
allowed-tools: []
---

> Version: 1.0.0

<reference>
# `dev:` commands — generic, cross-project dev pipeline

Global — works in any project. See `~/.claude/dev-framework/DESIGN.md` for why this is deliberately
lighter than a full wave/gate pipeline, and `~/.claude/docs/USAGE.md` for the full cross-repo command map
(project-specific namespaces like `scm:`/`merge:` live in their own repos, not here).

| Command | Purpose |
|---|---|
| `/dev:init [path]` | Scaffold `ai/dev/STATE.md` + `config.json` for a project that doesn't have them yet. |
| `/dev:status [path]` | Report a project's current `ai/dev/` state — phase, gates, blockers. |
| `/dev:quick <task>` | Dispatch one ad-hoc task to `dev-backend`/`dev-frontend` — no phase ceremony. |

## Shared conventions
- Every `dev-*` agent requires `ai/dev/STATE.md`/`config.json` to exist first — run `/dev:init` before the
  first dispatch on a new project.
- No gates are wired as blocking anywhere in this namespace. Review is on-demand
  (a project's own `:review` command, e.g. `/scm:review`), never automatic after a `/dev:quick` dispatch.
- If a project's process genuinely differs from generic dispatch (approval gates, an issue-tracker
  integration, a release discipline), it gets its own project-specific command instead of using
  `/dev:quick` — see `net8-migration`'s `/scm:*` namespace for the pattern.

This command performs no live analysis — it only prints the reference above.
</reference>
