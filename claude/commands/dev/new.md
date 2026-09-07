---
name: dev:new
description: Scaffold a new .NET demo/prototype app from an empty folder - dispatches dev-scaffolder to produce a building, running vertical slice plus the ai/context/ and ai/dev/ files the rest of the dev-* family requires.
allowed-tools:
  - Read
  - Glob
  - Agent
  - AskUserQuestion
argument-hint: "[target path, optional - defaults to current directory] <what the app should be> [--ui-spec=<path>]"
---

> Version: 1.1.0 — agent-review findings applied, 2026-09-07

<objective>
`/dev:new <description>` turns an empty folder into a running skeleton by dispatching `dev-scaffolder`.
It is the entry point the `dev:` namespace was missing: `/dev:init` writes state files for a project that
already exists, and `dev-backend`/`dev-frontend` refuse to run until a project's conventions are readable —
so before this command there was no way to get from an empty directory to a first dispatch.

Use it on its own for a one-shot skeleton. `/dev:build` calls the same agent as its first step when it
needs one, so there is no need to run both.
</objective>

<process>
<step name="resolve-target">
If the first token of `$ARGUMENTS` looks like a path, that is the target folder and the rest is the app
description; otherwise the target is the current working directory and the whole argument is the
description. `--ui-spec=<path>` selects rebuild mode and is resolved out of the argument string wherever it
appears — it is a real user-facing flag here, not only something `/dev:build` passes internally. If no
description is given at all, ask for one with `AskUserQuestion` — the agent cannot scaffold from a folder
name.
</step>

<step name="preflight">
Glob the target for `**/*.sln`, `**/*.csproj` and `**/package.json`. If anything matches, stop here and
point at `/scaffold-context` then `/dev:init`. Do not offer to scaffold alongside existing code.

This is a **fast-path subset of `dev-scaffolder`'s own OCCUPIED check, not a replacement for it** — the
agent's check is authoritative, recursive, and also covers a populated `src/`. The point of duplicating it
here is to save a dispatch on the common case, so a future edit that tightens the agent's condition need
not be mirrored here; one that *loosens* it must be.
</step>

<step name="dispatch">
Dispatch `dev-scaffolder` via `Agent` with the target path, the app description, and the `--ui-spec` path if
one was given (rebuild mode). The agent reads the stack profile, the constitution and the `dev-*` protocol
itself.
</step>

<step name="relay">
Return the agent's report. Surface the stack-decision table and the real verification output — the build,
test and serve results are the whole claim that the skeleton works, so do not summarise them away.

If the report carries `## Blocking questions`, put them to the user now with `AskUserQuestion`. The agent
had no way to ask, and an unanswered question dies in the transcript otherwise.

Then name the next step: `/dev:build` to continue into feature work against the new skeleton, or
`/dev:quick` for a single task.
</step>
</process>

<rules>
- **Thin dispatcher only.** No `Write`/`Edit`/`Bash` — all real work happens inside the dispatched agent.
- **Never scaffold into an occupied folder**, and never ask the agent to. The preflight check is the point
  of this command's existence, not a formality.
- **Always relay the verification output verbatim.** A scaffold reported as working without a real
  `dotnet build` result is exactly the failure Article IV exists to prevent.
</rules>
