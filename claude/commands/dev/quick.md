---
name: dev:quick
description: Dispatch one ad-hoc backend/frontend task to dev-backend/dev-frontend for the current (or given) project - no phase ceremony, no project-specific mechanics.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Agent
  - AskUserQuestion
argument-hint: "[project path, optional - defaults to current directory] <task description>"
---

> Version: 1.0.0

<objective>
`/dev:quick <task>` executes one concrete implementation task by dispatching to the generic `dev-backend`
and/or `dev-frontend` agents against the current project. This is the generic form of what a
project-specific dispatcher (like the retired `/cm:dev`) would do when the project has no genuinely
different process to enforce — classify the area, inject context, dispatch, relay.

If a project's process is *not* generic (version-bump discipline, a specific issue-tracker integration,
a mandatory approval gate before implementing), that project should have its own command instead of this
one — see `/scm:fix`/`/scm:req` in net8-migration for the pattern.
</objective>

<process>
<step name="resolve-target">
If the first token of `$ARGUMENTS` looks like a path, that's the target project and the rest is the task
description; otherwise the target is the current working directory and the whole argument is the task.
</step>

<step name="check-initialized">
Check `ai/dev/STATE.md` exists at the target. If not, tell the user to run `/dev:init` first and stop —
`dev-backend`/`dev-frontend` will refuse anyway per `PRINCIPLES.md` §1, so failing fast here saves a wasted
dispatch.
</step>

<step name="classify">
Classify the task as `backend`, `frontend`, or `both` from its content (service/API/data-access/`.cs`-type
signals → backend; page/component/UI/form/`.tsx`-type signals → frontend). If genuinely ambiguous, ask via
`AskUserQuestion` — don't default to "both" just to avoid asking.
</step>

<step name="dispatch">
For each area needed, dispatch via `Agent` to `dev-backend` and/or `dev-frontend`, giving it the task
description and the target project path (the agent reads `ai/dev/`+`ai/context/`+`CLAUDE.md` itself per
its own first action). If both areas are needed and one depends on the other's output (e.g. frontend
consumes a contract backend is changing), dispatch backend first and pass its report to the frontend
dispatch; otherwise dispatch both and note they ran independently.
</step>

<step name="relay">
Return each dispatched agent's report verbatim, prefixed with which agent produced it.
</step>
</process>

<rules>
- **Thin dispatcher only.** No `Edit`/`Write`/`Bash` access — all real work happens inside the dispatched
  agent.
- **Never silently pick a classification when genuinely ambiguous.** Ask once via `AskUserQuestion`.
- **This command carries no project-specific process.** If a project needs one (approval gates, an issue
  tracker, a release discipline), that belongs in that project's own command, not here.
</rules>
