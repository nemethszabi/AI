# dev-framework — Design & Rationale

Companion to `PRINCIPLES.md` (the *how* — binding operational protocol every `dev-*` agent follows).
This file is the *why* and the *what's intentionally not built yet* — read it when deciding whether to
extend this family, not at runtime by any agent.

## Why this exists, and why it's lighter than the reference framework's

`d:\_GEOMANT_GIT\agentic-dev-framework\dev-framework\DESIGN.md` designs a full delivery pipeline:
role-specialist agents routed by an `area` tag, contract-first wave execution (dev-api/dev-db fix the
interface in Wave 0, backend/frontend build in parallel against it in Wave 1), mandatory QA/review/security
gates per phase, and an SA-to-dev bridge carrying REQ-IDs from a won presales engagement straight into a
roadmap. That's the right shape for team delivery work with enough volume and enough people touching the
same files concurrently that wave ordering and gates earn their overhead.

At this repo's actual scale — one person, a handful of projects, tasks dispatched one at a time — that
overhead doesn't pay for itself yet. So this family adopted only two ideas from the reference framework:

1. **Role-specialist generic agents** (`dev-backend`, `dev-frontend`, `dev-reviewer`, `dev-browser-tester`,
   and since 2026-09-07 `dev-scaffolder`, `dev-planner`, `dev-ui-analyst`) — one agent per role, reused
   verbatim across every project, stack facts pulled from the target project's own `ai/context/*.md` at the
   start of every run, never hardcoded into the agent.
2. **A shared operational protocol** (`PRINCIPLES.md`) so independently-dispatched agents behave
   predictably — load state first, stay in their lane, treat contracts as read-only unless they own them,
   one report format.

A third was adopted later, on 2026-09-07, once the trigger below actually fired: **flat task decomposition**
(`PLAN.md`) with a command-level execution loop — deliberately without the reference framework's phase
folders, wave ordering, or blocking gates.

Everything else the reference framework builds on top of those two ideas — wave ordering, mandatory gates,
`PLAN.md`/`SUMMARY.md` phase folders, the SA→dev REQ-ID bridge — is a deliberate non-goal for now (see
below), not an oversight.

## State layout — `ai/dev/` (canonical schema)

Two files per project, written once by `/dev:init` (or by `dev-scaffolder` on a greenfield project) and
read by every `dev-*` agent's first action — plus two more that exist only on plan-driven runs:

```
<project-root>/
└── ai/
    └── dev/
        ├── STATE.md      # human-readable: phase, source of truth, decisions, blockers
        ├── config.json   # machine-readable: gates, pointers, build command
        ├── PLAN.md       # plan-driven runs only: the ordered task list (dev-planner writes it)
        └── BUILD-LOG.md  # plan-driven runs only: append-only per-task reports (/dev:build writes it)
```

`PLAN.md` and `BUILD-LOG.md` are **absent by default and that is a valid state** — a project driven only by
`/dev:quick` never grows either. No agent may treat their absence as an error; ownership rules for both are
in `PRINCIPLES.md` §9.

**`STATE.md`** — four sections, always in this order:
```markdown
# Dev State — <Project>

## Phase
<what's true right now — e.g. "onboarding complete, no task/wave structure yet">

## Source of truth
<where project knowledge/architecture/branch facts live — usually points at ai/context/*.md>

## Decisions
<durable decisions worth not relitigating, e.g. "no wave/gate machinery adopted">

## Blockers
<or "None">
```

**`config.json`** — core fields every `dev-*` agent may rely on; add project-specific keys freely beyond
these, but don't omit or rename the core ones (drift here is exactly the kind of thing that makes a
generic agent silently do the wrong thing on one project and not another):

```json
{
  "project": "<name>",
  "primary_branch": "<branch>",
  "gates": { "qa": false, "review": false, "security": false },
  "context_doc": "ai/context/<primary file>.md",
  "contracts_path": "<real path, or \"N/A - <reason>\">",
  "build_command": "<command, or \"N/A - <reason>\">",
  "notes": "<free text — current scope, what's deliberately deferred>"
}
```

`contracts_path` and `build_command` should point at a project's **real, already-existing** source of
truth (a contracts project, a documented build step) rather than a duplicated file under `ai/dev/` — this
mirrors `PRINCIPLES.md`'s own amendment note. `gates` are all `false` by default; nothing in this repo
currently sets one `true` anywhere — see non-goals.

Two further fields, added 2026-09-07 and read by `PRINCIPLES.md` §8:

```json
{
  "mode": "greenfield | brownfield",
  "stack_profile": "dev-framework/STACK-DOTNET.md"
}
```

`mode` defaults to `brownfield` when absent — the safe reading, since greenfield mode is what relaxes
convention-matching and scope. Only `dev-scaffolder` sets `greenfield`, and only on a project it created.

### `PLAN.md` — schema

Written by `dev-planner`; `Status` maintained by the orchestrating command; read-only to implementers
(`PRINCIPLES.md` §9). Status vocabulary: `pending` | `in-progress` | `done` | `blocked` | `skipped`.

```markdown
# Build Plan — <Project>

**Goal:** <one sentence>          **Source:** <the ask, plus any spec it derived from>
**Stack:** <resolved, and from where>   **Created:** <date> by dev-planner
**Status vocabulary:** `pending` | `in-progress` | `done` | `blocked` | `skipped`

## Scope note
## Tasks
| ID | Area | Task | Depends on | Acceptance | Status |
| T-01 | scaffold \| backend \| frontend \| verify | <what> | T-nn or — | <runnable check> | pending |
## Out of scope — needs a human
## Deferred
## Blocking questions
## Revisions
```

Two properties carry most of the weight. **One area per task**, because the orchestrator dispatches one
agent per row and cannot split one. **A machine-runnable acceptance check per task**, because an
autonomous loop with no external check marks tasks done on the implementer's own say-so — which is the
whole failure this schema exists to prevent.

## Deliberate non-goals (for now)

- **No `ai/dev/phases/NN-slug/` folders, and no wave ordering.** Task decomposition now exists as a flat,
  dependency-ordered `PLAN.md` (see above, adopted 2026-09-07); what stays unbuilt is the *phase folder*
  structure and the contract-first wave execution model the reference framework uses. A flat list with a
  `Depends on` column covers a demo app's ordering needs without the ceremony.
- **No mandatory QA/review/security gates.** `dev-reviewer` exists and is genuinely useful, and
  `/dev:build` now dispatches it automatically at the end of a run — but its verdict still **blocks
  nothing**. It is a report, not a gate. Nothing in this family refuses to proceed on a review verdict the
  way `/sa:package` refuses on `/sa:audit`'s.
- **No `dev-api`/`dev-db` contract-ownership split.** A single `dev-backend` covers services, data access,
  and integration work. Trigger #2 below has still not fired: `/dev:build` executes tasks sequentially, so
  two dispatches never touch the same interface concurrently. **Revisit the moment the orchestrator starts
  running tasks in parallel** — that is exactly the condition, and the plan schema already marks which
  tasks could parallelise.
- **No SA→dev REQ-ID bridge.** The `req-*` (SA/REQ-CR) pipeline and this `dev-*` family don't hand off
  IDs to each other. `ai/sa/<slug>/` and `ai/dev/` are separate, unconnected state directories.

## Amendment trigger — when to revisit this

Not on a schedule, and not just because the reference framework has more. Revisit adding wave ordering
and/or mandatory gates specifically when either becomes true on a real project:

1. A single project's backlog of dispatched tasks grows past what you can track by memory or a quick
   `/dev:status` glance — that's the signal task decomposition (`PLAN.md`) would actually pay for itself.
2. Two dispatches could plausibly touch the same file/interface in the same window — that's the signal a
   contract-ownership split or a review gate stops being optional.

Until one of those is actually true on a real project, adding the heavier machinery would be building for
a hypothetical, which `DESIGN-PRINCIPLES-BASELINE.md` #10 already argues against.

### Trigger #1 fired — 2026-09-07

Recorded here rather than quietly acted on, because the point of writing a trigger down is that it gets
checked rather than reinterpreted.

The use case that fired it was not a growing backlog on an existing project but a new one: **building demo
and prototype apps from a one-line ask, and rebuilding apps from their UI**. That produces 8–20 dispatched
tasks from a single prompt, which is trigger #1's condition arriving all at once instead of accumulating.

What that revealed was a harder blocker than the missing plan. The family **could not start a project at
all**: `dev-backend` and `dev-frontend` resolve every stack fact from `ai/context/*.md` and refuse to guess
when it is absent, `solution-analyst` only reads solutions that already exist, and `/dev:init` writes state
files but no code. An empty folder was a dead end in every direction — a gap invisible for as long as the
family was only ever pointed at repos that already existed.

Four things were added, and one deliberately was not:

| Added | Why |
|---|---|
| `dev-scaffolder` | Creates the skeleton **and** the `ai/context/`+`ai/dev/` files the others require. The precondition was the gap |
| `dev-planner` + `PLAN.md` | Trigger #1's answer, kept flat rather than phase-foldered |
| `dev-ui-analyst` + `ui-spec` | The rebuild-from-UI half, which had no coverage at all — `dev-browser-tester` verifies and cannot describe |
| `/dev:build` | The loop. A **command**, because Article VI.2 and `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH: "1"` make a "dev-lead" agent structurally impossible |
| *Not* added: edits to `dev-backend`/`dev-frontend` | Their greenfield refusal was correct behaviour reached through a missing precondition. `dev-scaffolder` satisfies it, so both agents work on greenfield projects unchanged |

`STACK-DOTNET.md` came with them: a family that resolves stack facts by reading a context file needs a
default for the case where no context file exists yet, or every generated app is a different stack.


## Current command surface

| Command | Scope | Purpose |
|---|---|---|
| `/dev:init [path]` | Global | Scaffold `ai/dev/STATE.md` + `config.json` for a project that doesn't have them yet. |
| `/dev:status [path]` | Global | Read and report a project's current `ai/dev/` state in a consistent format. |
| `/dev:quick <task>` | Global | Dispatch one task to `dev-backend`/`dev-frontend` for the current (or given) project — no phase ceremony. |
| `/dev:new <description>` | Global | Empty folder → running skeleton + context/state files, via `dev-scaffolder`. Added 2026-09-07. |
| `/dev:deconstruct <inputs>` | Global | Existing app's UI → `ui-spec`, via `dev-ui-analyst`. Added 2026-09-07. |
| `/dev:build <goal>` | Global | The multi-task loop: plan → gate → execute → verify → cross-model review. Added 2026-09-07. |
| `/dev:help` | Global | Static reference for this namespace. |

These three are **commands, not skills**, which departs from `claude-prompting-kb.md` §2's "default to
Skill for anything new". Two reasons, both specific rather than habitual. They extend an existing command
namespace whose `/dev:help` table and cross-references would otherwise be split across two artifact forms
for no user-visible gain. And `/dev:build` in particular must be **explicitly invoked only** — a skill's
auto-triggering on description match is an anti-feature for a command that dispatches agents to write code
across dozens of files. Prefer a skill for the next genuinely standalone thing; the namespace-coherence
argument does not generalise beyond `dev:`.
| `/scm:fix`, `/scm:req`, `/scm:review`, `/scm:devops-ask`, `/scm:devops-change`, `/scm:test` | Project (net8-migration) | Own SCM-specific mechanics (Azure DevOps org rule, version-bump, never-commit) on top of the same generic agents. |

`/cm:dev` (CampaignManager) was retired 2026-08-07 in favor of `/dev:quick` once it became clear it carried
no CampaignManager-specific mechanics at all — a case where a project-specific command had been built where
a generic one belonged. If a future project-specific `dev-*` dispatcher turns out to have no real
project-specific logic either, prefer `/dev:quick` over a bespoke command.
