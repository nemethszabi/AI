---
name: dev:build
description: Build a whole app from one goal - plans the work with dev-planner, then executes it task by task through dev-scaffolder/dev-backend/dev-frontend, verifies with dev-browser-tester and closes with a cross-model dev-reviewer pass. The autonomous multi-task loop; the human gate is the plan, before any code is written.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Write
  - Edit
  - Bash
  - Agent
  - AskUserQuestion
argument-hint: "[project path] <goal> [--from-spec=<path>] [--model=<name>] [--max-tasks=N] [--yes]"
---

> Version: 1.1.0 — agent-review findings applied, 2026-09-07

<objective>
`/dev:build <goal>` takes one sentence and produces a working app, by owning the loop that `/dev:quick`
deliberately does not: decompose, dispatch, record, verify, review.

This is the orchestration layer, and it lives in a command because it has to. `CONSTITUTION.md` Article
VI.2 forbids an agent from spawning another agent, and `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH: "1"` enforces
it structurally — a "dev-lead" agent is not buildable on this machine. A command runs in the main session,
may hold multiple `Agent` dispatches, and is the only place `AskUserQuestion` exists.

**Autonomous is not unattended.** The loop runs many tasks without asking, but it stops at a plan the human
has not seen, at anything irreversible, and at repeated failure. Those three stops are the design, not
friction to route around.
</objective>

<process>
<step name="resolve-arguments">
Parse `$ARGUMENTS`: a leading path is the target project, the remaining prose is the goal. Flags:

| Flag | Effect |
|---|---|
| `--from-spec=<path>` | Rebuild mode — pass this `ui-spec` to the planner and the scaffolder |
| `--model=<name>` | Model for the closing `dev-reviewer` dispatch (`AGENT-CONDUCT-BASELINE.md` B10) |
| `--max-tasks=N` | Hard ceiling on tasks executed this run; default 20 |
| `--yes` | Skip the plan confirmation gate. Only honour this when the user typed it |

No goal → ask for one with `AskUserQuestion` and stop until answered.
</step>

<step name="preflight">
Decide which of three states the target is in, and take the matching route:

| State | Route |
|---|---|
| Empty folder | Normal. The planner's `T-01` will be the scaffold task |
| Has code **and** `ai/context/*.md` | Normal. Brownfield feature work against an understood project |
| Has code, **no** `ai/context/*.md` | **Stop.** Tell the user to run `/scaffold-context` first. Do not plan against a codebase whose conventions nobody has read — every implementer dispatch would refuse anyway, one at a time, after the plan was already built |

Then check `ai/dev/PLAN.md`. If one exists with unfinished work, ask whether to resume it or re-plan —
**showing the remaining task table**, not just a yes/no question. A plan may have been approved under
`--yes`, or hand-edited since, so resuming is not evidence that anyone ever read it. Never silently
discard an existing plan.

**Before resuming, repair interrupted state.** A task left at `in-progress` means a previous run died
mid-dispatch — no agent is working on it now. Reset every such task to `pending` and say which ones you
reset. Left alone it is stranded: the execute loop only picks up `pending` tasks, so it would be skipped
silently while everything depending on it waits forever.
</step>

<step name="plan">
Dispatch `dev-planner` via `Agent` with the goal, the target path, and the spec path if there is one. It
writes `ai/dev/PLAN.md`.

Relay its `## Blocking questions` to the user with `AskUserQuestion` before going further — they are
questions about what to build, and answering them after the build has started is expensive.
</step>

<step name="gate-the-plan">
**Show the task table and ask for confirmation before executing anything.** This is the human gate of the
whole command: it is the one cheap moment to catch a misread goal, and it costs a minute against a run that
may touch dozens of files.

Present the task list, the count, the critical path, and what the planner put under
`## Out of scope — needs a human`. Offer: proceed / edit the plan first / cancel.

**Point the user at the `Acceptance` column specifically.** Nothing in this pipeline validates that a
task's acceptance check is actually machine-runnable — a row reading "works correctly" or "looks good"
passes every automated step here and only fails much later, when an implementer marks it done on its own
say-so. A human reading this table is the only check that exists for it.

Skip this step **only** when the user passed `--yes`. Do not infer consent from an enthusiastic goal, from
a previous run's approval, or from the plan looking obviously right.
</step>

<step name="execute">
Walk the plan in dependency order. Select each task that is **`pending`**, whose dependencies are all
`done`, and whose area is **not** `verify` — until `--max-tasks` is reached.

Both filters are load-bearing. Selecting on dependencies alone re-dispatches work that is already `done`
as soon as its dependents become eligible; `verify`-area tasks are not implementer work at all and belong
to the dedicated `verify` step below, which dispatches a different agent against a running app.

For each selected task:

1. Set the task's `Status` to `in-progress` in `PLAN.md`.
2. Dispatch the agent its `Area` names: `scaffold` → `dev-scaffolder`, `backend` → `dev-backend`,
   `frontend` → `dev-frontend`. Pass the task ID, its description, its acceptance check, the target path,
   and — for a rebuild — the ui-spec path. The agent reads the project's own state and context itself.
3. Read the returned report. The task is `done` only if the agent ran the acceptance check and it passed.
   An agent reporting completion without having run its build is not a completed task (`PRINCIPLES.md` §5,
   Article IV) — treat it as a failure and say why.
4. Append the agent's report to `ai/dev/BUILD-LOG.md` (create it if absent) and set the task's final
   `Status` in `PLAN.md`.
5. Route anything under the report's `## Handoffs` — if it belongs to a planned task, note it there; if it
   is genuinely new work, add it to the plan's `## Deferred` section rather than executing it. **Never
   silently expand the run beyond the approved plan** (Article V).

6. **Evaluate the stop conditions below before selecting the next task.** They are checked after every
   task, not once at the end of the walk — a separate step in this document only because they are a list,
   not because they run later.

**In `PLAN.md` you write the `Status` column and append to `## Deferred`; nothing else, and the implementer
agents never write the file at all** (`PRINCIPLES.md` §9). One writer avoids two dispatches racing it.

On a task failure: re-dispatch **once**, passing the failure output so the agent is not rediscovering it.
If it fails again, mark the task `blocked`, record why in `BUILD-LOG.md`, and continue with tasks that do
not depend on it.
</step>

<step name="stop-conditions">
Halt the loop and report — do not push through — on any of:

- **Two consecutive tasks blocked**, or any task blocked twice. Repeated failure usually means the plan is
  wrong, and continuing turns one bad assumption into fifteen files.
- **`--max-tasks` reached.** Report what is left and how to resume.
- **A task turning out to need something irreversible or outward-facing** — a push, a deploy, a shared or
  production database, a cloud resource, a spend. Stop and ask. The planner was told to keep these out of
  the task list, so encountering one means reality diverged from the plan (Articles II and VII).
- **A blocked task that everything remaining depends on.** Continuing produces nothing.

A halt is a normal outcome with a partial result, not a failure to hide. Report exactly which tasks are
`done`, which are `blocked`, and what the app can currently do.
</step>

<step name="verify">
Once the plan's `verify` task is reachable and the app builds, dispatch `dev-browser-tester` against the
running app with the end-to-end flow the plan named. Start the app first if it is not running, and stop it
afterwards.

Record its verdict block. A `FAIL` here does not silently become a fix — it is reported, and any resulting
work is a new task, not an unplanned edit.
</step>

<step name="review">
Dispatch `dev-reviewer` over the run's changes, **with an explicit `model` override different from the one
that produced the code** (`AGENT-CONDUCT-BASELINE.md` B10, `PRINCIPLES.md` §10). Use `--model` if given.

If no override was given, dispatch anyway and say so in the relay: "review ran on the session model;
consider re-running with `--model=<other>` before trusting it." A reviewer sharing the author's model
shares the author's blind spots, which is precisely the correlated-error case that makes an autonomous run
worth reviewing at all.

**Always report which model actually ran the review.**
</step>

<step name="relay">
Report in the shape below. Keep it short — the detail is in `PLAN.md` and `BUILD-LOG.md`, both of which
survive the session.

```markdown
## /dev:build — <goal> — <date>
**Plan:** N tasks (`ai/dev/PLAN.md`)
**Executed:** N done, N blocked, N pending
**Build:** <real result of the last build>
**Browser verify:** PASS | FAIL | not reached — <one line>
**Review:** <verdict> — ran on <model>
**Blocked:** <task ID and one-line reason, each>
**Needs a human:** <the plan's out-of-scope items, plus anything the run hit>
**Next:** <the single most useful next command>
```
</step>
</process>

<rules>
- **You never edit source or application files yourself.** `Write` and `Edit` are for `ai/dev/PLAN.md` and
  `ai/dev/BUILD-LOG.md` only; every code change flows through a dispatched `dev-*` agent. The tool grant
  does not enforce this — it is unrestricted — so it is a rule you keep, not a wall you hit
  (`AGENT-TEMPLATE-BASELINE.md` §1a; a `PreToolUse` hook scoping both tools to `ai/dev/*.md` is the
  structural fix if this ever runs unattended for real).
- **`Bash` is for starting and stopping the app around the `verify` step**, using the project's own
  documented run command. Not git state changes, not deletion, not deploys — those are Article II's
  territory and the root's guard hook is the backstop, not the first line of defence.
- **The plan gate is not optional without `--yes`.** Executing an unreviewed plan is how a misread goal
  becomes forty files.
- **Never execute a task the approved plan does not contain.** New work discovered mid-run goes to
  `## Deferred`, and the user decides (Article V). An autonomous loop that widens its own scope is the
  specific failure mode this command has to be trusted not to have.
- **Never perform an irreversible or outward-facing action, and never dispatch an agent to.** No push, no
  deploy, no cloud resource, no shared/production database, no spend — stop and ask, every time, regardless
  of any earlier approval in the same session (Article VII).
- **Only this command writes `PLAN.md`'s `Status` column.** Implementer agents report; the orchestrator
  records.
- **A task is `done` only against a real acceptance check.** An agent's own assurance is not evidence
  (Article IV).
- **Never weaken an acceptance check, skip a test, or narrow a task to make the loop progress**
  (Article III). A task that cannot pass its check is `blocked`, and blocked is a legitimate outcome.
- **Report partial results honestly.** "Nine of fourteen tasks done, three blocked on X" is the deliverable
  when that is what happened.
</rules>
