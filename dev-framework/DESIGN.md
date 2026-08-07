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

1. **Role-specialist generic agents** (`dev-backend`, `dev-frontend`, `dev-reviewer`, `dev-browser-tester`)
   — one agent per role, reused verbatim across every project, stack facts pulled from the target
   project's own `ai/context/*.md` at the start of every run, never hardcoded into the agent.
2. **A shared operational protocol** (`PRINCIPLES.md`) so independently-dispatched agents behave
   predictably — load state first, stay in their lane, treat contracts as read-only unless they own them,
   one report format.

Everything else the reference framework builds on top of those two ideas — wave ordering, mandatory gates,
`PLAN.md`/`SUMMARY.md` phase folders, the SA→dev REQ-ID bridge — is a deliberate non-goal for now (see
below), not an oversight.

## State layout — `ai/dev/` (canonical schema)

Two files per project, written once by `/dev:init` and read by every `dev-*` agent's first action:

```
<project-root>/
└── ai/
    └── dev/
        ├── STATE.md      # human-readable: phase, source of truth, decisions, blockers
        └── config.json   # machine-readable: gates, pointers, build command
```

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

## Deliberate non-goals (for now)

- **No `ai/dev/phases/NN-slug/` folders.** No `PLAN.md` (task decomposition), no `SUMMARY.md` (per-task
  build log), no wave ordering. Tasks are dispatched one at a time via `/dev:quick` or a project-specific
  command; there's no multi-task plan to decompose yet.
- **No mandatory QA/review/security gates.** `dev-reviewer` exists and is genuinely useful, but nothing
  currently *requires* a green review before calling a task done — it's invoked on demand
  (`/scm:review`, or a future generic `/dev:review`), not wired as a blocking step after every
  `dev-backend`/`dev-frontend` dispatch.
- **No `dev-api`/`dev-db` contract-ownership split.** A single `dev-backend` covers services, data access,
  and integration work; splitting contract ownership into its own role only matters once two agents could
  plausibly touch the same interface at the same time, which isn't happening at current task volume.
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

## Current command surface

| Command | Scope | Purpose |
|---|---|---|
| `/dev:init [path]` | Global | Scaffold `ai/dev/STATE.md` + `config.json` for a project that doesn't have them yet. |
| `/dev:status [path]` | Global | Read and report a project's current `ai/dev/` state in a consistent format. |
| `/dev:quick <task>` | Global | Dispatch one task to `dev-backend`/`dev-frontend` for the current (or given) project — no phase ceremony. |
| `/dev:help` | Global | Static reference for this namespace. |
| `/scm:fix`, `/scm:req`, `/scm:review`, `/scm:devops-ask`, `/scm:devops-change`, `/scm:test` | Project (net8-migration) | Own SCM-specific mechanics (Azure DevOps org rule, version-bump, never-commit) on top of the same generic agents. |

`/cm:dev` (CampaignManager) was retired 2026-08-07 in favor of `/dev:quick` once it became clear it carried
no CampaignManager-specific mechanics at all — a case where a project-specific command had been built where
a generic one belonged. If a future project-specific `dev-*` dispatcher turns out to have no real
project-specific logic either, prefer `/dev:quick` over a bespoke command.
