---
name: dev:help
description: Static reference for the dev: command namespace. No live analysis, no project context read.
allowed-tools: []
---

> Version: 1.1.1 — 2026-09-16: stale `net8-migration` pointer → `development`.
> 1.1.0 — added `/dev:new`, `/dev:deconstruct`, `/dev:build` and the greenfield/rebuild routes
> (2026-09-07)

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
| `/dev:new <description>` | Empty folder → a skeleton that builds, runs and tests, plus the `ai/context/`+`ai/dev/` files everything else needs. Via `dev-scaffolder`. |
| `/dev:deconstruct <inputs>` | A running URL, screenshots and/or a source tree → `ai/context/<slug>-ui-spec.md`. Via `dev-ui-analyst`. |
| `/dev:build <goal>` | The whole loop: plan → **human gate** → execute task by task → browser verify → cross-model review. Via `dev-planner` + the implementers. |

## Which one, from where you're standing

| Situation | Start with |
|---|---|
| Empty folder, want an app | `/dev:build "<goal>"` — it scaffolds as task T-01 |
| Empty folder, just want the skeleton | `/dev:new "<description>"` |
| Rebuilding an app you can see or run | `/dev:deconstruct <url\|images\|src>` → then `/dev:build --from-spec=<path>` |
| Existing repo, one task | `/dev:quick <task>` |
| Existing repo, many tasks | `/dev:build "<goal>"` |
| Existing repo, never analysed | `/scaffold-context` first — then any of the above |

## Shared conventions
- Every `dev-*` agent requires `ai/dev/STATE.md`/`config.json` to exist first. `/dev:init` writes them for
  an existing project; `dev-scaffolder` writes them for a new one.
- **`dev-scaffolder` refuses to touch a folder that already contains a solution.** That is
  `solution-analyst`'s job (`/scaffold-context`), and the refusal is not overridable.
- **`/dev:build` gates on the plan, not on the result.** You approve the task list before any code is
  written; `--yes` skips that and should be typed deliberately.
- No gates are wired as blocking anywhere in this namespace. `/dev:build` dispatches `dev-reviewer` at the
  end of a run, but its verdict blocks nothing — it is a report. Nothing here refuses to proceed the way
  `/sa:package` does.
- **Review runs on a different model than the code.** Pass `--model=<name>` to `/dev:build`; where you
  don't, it says so rather than presenting same-model review as independent.
- Nothing in this namespace pushes, deploys, provisions, or touches a shared database. A plan that needs
  one lists it under "needs a human" instead of executing it.
- If a project's process genuinely differs from generic dispatch (approval gates, an issue-tracker
  integration, a release discipline), it gets its own project-specific command instead of using
  `/dev:quick` — see `d:\_SCM_GIT\development`'s `/scm:*` namespace for the pattern (`/svm:*` in
  `d:\_SVM_GIT\dev` is a minimal variant).

This command performs no live analysis — it only prints the reference above.
</reference>
