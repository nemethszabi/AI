# dev framework — Shared Agent Protocol

Every `dev-*` agent MUST follow this protocol. Read this file first when spawned — before your own
`<role>` instructions, and before touching any file. **Binding**, not a checklist: this is the operational
contract that lets independently-authored specialist agents coordinate through the same state without
stepping on each other.

> **Precedence**: `~/.claude/CONSTITUTION.md` overrides this file if the two ever conflict (secrets,
> destructive actions, gates, scope, tool permissions — those live there, not duplicated here).
> `~/.claude/AGENT-CONDUCT-BASELINE.md` and `AGENT-TEMPLATE-BASELINE.md` govern general conduct and file
> shape respectively — this file is the layer specific to the `dev-*` role-specialist family only.

State-file convention below is `ai/dev/` — grouped under the same `ai/` root as `ai/context/`,
`ai/prompts/`, `ai/reports/` (the convention already used across these projects), rather than a bare
top-level `.dev/` dot-folder as in the reference framework this was adapted from. If a project you're
generating agents for uses yet another convention, change every `ai/dev/` path in this file to match — do
it once, here, not per-agent.

**Standard `ai/` layout** (every project; a folder exists only once something is written to it):

| Folder | Holds |
|---|---|
| `ai/context/` | Living project facts — read by agents, updated in place |
| `ai/design/` | Design documents — `<id>-<slug>-design-YYYYMMDD.md`. **Never** under `reports/` |
| `ai/reports/` | Dated investigation, review and analysis results |
| `ai/handoff/` | Session handoffs — `handoff-YYYYMMDD-HHMM-<slug>.md`, written and deleted by `/handoff` only |
| `ai/dev/`, `ai/sa/<slug>/` | Framework state (§1 here; `sa-framework\ARTIFACT-SCHEMAS.md`) |
| `ai/prompts/`, `ai/scripts/` | Reusable prompts; utility scripts |

A project may add its own folders (e.g. `ai/rollout/`) in its own `ai/README.md`; it may not put designs or
handoffs anywhere else.

---

## 1. Load state before anything

```bash
cat ai/dev/STATE.md 2>/dev/null
cat ai/dev/config.json 2>/dev/null
```

Internalize: current phase/status, accumulated decisions (they constrain you), open blockers. If
`ai/dev/` doesn't exist, stop and report "project not initialized" rather than guessing a starting
state.

## 2. Stay in your lane

Your task carries an `area` tag matching your role. If you discover work belonging to another area, do
**not** do it — record it under `## Handoffs` in your report (area, description, why) and let the
orchestrator route it. Exception: trivially small touches (a handful of lines) needed to keep the
immediate task coherent are fine; disclose them anyway.

## 3. Contracts are law

`ai/dev/contracts/` is the source of truth for every interface between areas — unless the project already
has a real, code-level contracts location (e.g. a dedicated contracts/DTOs project); in that case treat
that as the source of truth and record its path in `ai/dev/config.json` instead of duplicating it under
`ai/dev/contracts/`. Implement against a contract
exactly. If a contract is wrong or insufficient: stop that task, record a `## Contract Issue` in your
report, move to the next independent task. Never silently diverge from a published contract. Only the
area that owns a contract/schema may edit it — every other area treats it as read-only.

## 4. Commit discipline

One commit per completed task. Conventional Commits (`feat:`, `fix:`, `chore:`, `test:`, `refactor:`,
`docs:`, plus `infra:` as a project extension if needed). Reference task/requirement IDs in the body when
the project has them. The destructive/bypass rules (`--no-verify`, force-push, amending others' commits)
are `CONSTITUTION.md` Article II — not restated here, just enforced.

## 5. Quality defaults

- TDD when implementing logic: failing test → implement → green → refactor. Skip only for pure
  config/markup tasks.
- Match existing codebase conventions (naming, structure, error handling) — see the project's own
  `ai/context/design-principles.md` if one exists. **Greenfield, or no architecture doc under
  `ai/context/`: follow §8**, which names the real fallback chain. (Until 2026-09-07 this line pointed at
  `ai/dev/ARCHITECTURE.md` — a file that has never been part of `DESIGN.md`'s state schema and that nothing
  in this framework writes. It was inherited from the reference framework and was unfollowable.)
- Deviation rule: if the plan says X but reality demands Y, do the smallest correct Y, document it under
  `## Deviations` in your report with rationale — never silently do something other than what was asked.
- **Diagnose before fixing.** When the task is a bug/defect rather than new-feature work: before changing
  anything, form a root-cause hypothesis grounded only in what you actually read this run — the error/
  stack trace/log excerpt handed to you, plus the affected code. If the project maintains a bug-patterns
  file under `ai/context/*.md` (commonly named `*-bug-patterns.md`), check it first — apply its documented
  fix directly if a pattern matches, rather than re-deriving one from scratch, and append a new entry
  there (following that file's own format) once you've fixed something not yet documented. State a
  confidence level before implementing, using this fixed scale — also the scale to use for a `Confidence`
  line in your own report format, where one exists:
  - **High (85–100%)** — root cause confirmed by reading the actual code, log, or stack trace, and the
    repro is unambiguous. A match in the project's bug-patterns file further confirms this but isn't
    required — a genuinely novel bug can still be High if the evidence itself is conclusive.
  - **Medium (60–84%)** — plausible but not fully confirmed (e.g. no direct repro, or the code reading is
    inferential rather than a confirmed trace through the actual failure).
  - **Low (<60%)** — inferred from limited evidence, best-effort.

  Base the percentage on evidence quality, not how clean the resulting fix looks. If nothing in the
  available evidence supports a hypothesis, say so and ask for more evidence (repro steps, logs) rather
  than implementing a speculative fix. Before touching code, also weigh blast radius: does the fix affect
  other callers of the changed method/endpoint, a public API surface, auth/session, or payment/money
  handling? If so, read whatever project convention doc covers that area first, and flag the exposure
  under `## Notes for gates`.

## 6. Report format

Return your report to the caller in the shape below. **On a plan-driven run** (the project has an
`ai/dev/PLAN.md` — see §9) the orchestrating command also appends it to `ai/dev/BUILD-LOG.md`; you do not
write that file yourself. There is no `phases/NN-slug/SUMMARY.md` in this framework's state schema —
`DESIGN.md` lists phase folders as an explicit non-goal, so the reference framework's per-phase summary
file has no equivalent here and never did.

```markdown
## [agent-name] — [task IDs] — [date]
**Done:** what was built, files touched, commits made
**Deviations:** (or "none")
**Handoffs:** (or "none")
**Contract issues:** (or "none")
**Notes for gates:** anything a reviewer/QA/security gate should scrutinize
```

Then update `ai/dev/STATE.md`'s position/decisions if your work changed them. This is the concrete,
dev-family instance of `AGENT-CONDUCT-BASELINE.md` A8 (consistent report format) — use this template
rather than inventing a new shape per agent.

## 7. Blocked protocol

If truly blocked (missing credential, ambiguous requirement with no safe default, a failing dependency
outside your area): stop, write the blocker to `ai/dev/STATE.md` under `## Blockers`, report it in your
final message. Don't guess on irreversible things — `CONSTITUTION.md` Article VII.

Note what "ask" means for a dispatched agent: `AskUserQuestion` does not exist inside one. Record the
blocker, and repeat the genuinely blocking ones under `## Blocking questions` in your returned report so
the dispatching command — which does run in the main session — can put them to the human
(`AGENT-CONDUCT-BASELINE.md` A7).

## 8. Greenfield mode

Applies when `ai/dev/config.json` sets `"mode": "greenfield"`. It changes three things and nothing else.

**Where conventions come from.** §5 tells you to match the conventions the codebase already uses. On a new
project there are none for the first few tasks. Fall back, in this order: the conventions
`dev-scaffolder` established and recorded in `ai/context/<slug>-context.md` §6; then the stack profile
named in `config.json`'s `stack_profile` (normally `dev-framework/STACK-DOTNET.md`). **Never introduce a
third convention** because you prefer it — an app assembled by four dispatches each following its own
taste is the specific failure this rule prevents.

**Scope, narrowly widened.** Article V's "do only what the task asked" is right for production work and
wrong for greenfield, where a task like "add the orders endpoint" genuinely implies a DTO, a DI
registration, a migration and a test. Within a greenfield project, and only for work a `PLAN.md` task
directly requires, implementing that supporting code is in scope and needs no separate task. Everything
beyond it — a feature nobody asked for, a refactor of another task's output, an "obvious" improvement to
the plan — remains a `## Handoffs` entry. The exemption covers what the approved task implies, never what
you think the project should also have.

**What does not change.** Articles I, II, III, VII and VIII apply identically. Greenfield relaxes
architecture and scope. It relaxes nothing about secrets, destructive actions, quality gates, irreversible
or outward-facing work, or personal data — and "it's only a demo" is not an argument against any of them.

## 9. Plan-driven execution — `ai/dev/PLAN.md`

When a project has an `ai/dev/PLAN.md`, it is the authoritative task list for the current build run. Its
schema, status vocabulary and worked shape live in `DESIGN.md`.

Ownership is strict, because a plan is written by one agent, executed through several, and updated
concurrently with dispatches in flight:

| Who | May |
|---|---|
| `dev-planner` | Create the plan; in UPDATE mode append tasks and re-scope `pending`/`blocked` ones — editing their `Task`/`Depends on`/`Acceptance` cells, never their `Status`. **No field of a `done` task's row may change** |
| The orchestrating command (`/dev:build`) | Write the `Status` column, and append to `## Deferred`. Nothing else in the file. Append reports to `BUILD-LOG.md` |
| Implementer agents (`dev-scaffolder`, `dev-backend`, `dev-frontend`) | **Read it. Never write it.** Report your outcome and let the orchestrator record it |

An implementer that edits `PLAN.md` creates a race with the orchestrator and destroys the run's record of
what actually happened.

Executing against a plan does not lower any bar: a task is `done` only when its stated acceptance check has
actually been run and passed (§5, Article IV), and a task that cannot pass its check is `blocked` — never
narrowed, and never marked done with a caveat.

## 10. Independent review runs on a different model

`AGENT-CONDUCT-BASELINE.md` B10 applies to this family exactly as it does to the `req-*` one: a
`dev-reviewer` dispatch is worth running because its errors are uncorrelated with the implementer's, and
that property is lost when both run on the same model. A reviewer sharing the author's model shares the
author's blind spots — and a plausible-looking mistake is precisely what the model that made it is least
likely to flag.

So a command dispatching `dev-reviewer` passes an explicit `model` override different from the one that
produced the code, exposes it as `--model=<name>`, and **reports which model actually ran**. Where no
override was given, say so in the relay rather than letting same-model review pass as independent. Never
pin a `model:` into `dev-reviewer`'s own frontmatter — that makes it wrong whenever the implementer's model
changes.

---

**Amendment procedure**: edit this file directly; the git commit message is the change rationale. Takes
effect globally once copied to `~\.claude\dev-framework\PRINCIPLES.md`.

---

**Amendment note (2026-08-07)**: state-file root changed from `.dev/` to `ai/dev/` to keep all
AI-tooling state grouped under the existing `ai/` folder (`ai/context/`, `ai/prompts/`, `ai/reports/`)
instead of adding a new top-level dot-folder. Also clarified that `contracts/` and `ARCHITECTURE.md`
should point at a project's real, pre-existing sources of truth rather than being duplicated under
`ai/dev/` when those already exist in code or in `ai/context/`.

**Amendment note (2026-09-14)**: added the standard `ai/` layout table under the header — `ai/design/` for
design documents (previously mixed into `ai/reports/`) and `ai/handoff/` as the only handoff location,
matching `/handoff` v2.0.0.

**Amendment note (2026-09-07)**: added §8 (greenfield mode), §9 (plan-driven execution and `PLAN.md`
ownership), §10 (cross-model review for this family, mirroring `AGENT-CONDUCT-BASELINE.md` B10), and the
`AskUserQuestion` clarification in §7. Also fixed **two latent defects, both inherited verbatim from the reference framework and both
unfollowable since the day they were written**. §5 told an agent on a greenfield project to "follow
`ai/dev/ARCHITECTURE.md`" — a file that has never been in `DESIGN.md`'s state schema and that nothing here
writes; it now defers to §8, which names the real fallback chain. And §6 instructed every `dev-*`
agent to "append your section to the phase's `SUMMARY.md`", a file that has never existed in this
framework — `DESIGN.md` lists phase folders as an explicit non-goal, so the instruction was inherited
verbatim from the reference framework and was unfollowable from the day it was written. Reports now return
to the caller, and `BUILD-LOG.md` (orchestrator-written) is the durable record on plan-driven runs. These
changes accompany `dev-scaffolder`/`dev-planner`/`dev-ui-analyst` and `/dev:build`; the trigger that
justified them is recorded in `DESIGN.md`.

**Amendment note (2026-08-14)**: added the "Diagnose before fixing" quality default (§5), generalizing
discipline that had been living ad hoc inside `net8-migration`'s `/scm:fix` command (confidence bands,
bug-patterns-first, blast-radius check) — `ReaFlow`'s older, pre-agent monolithic fix prompt had
independently reinvented a weaker version of the same thing, which is the drift this closes. Centralized
here rather than duplicated into `dev-backend.md`/`dev-frontend.md` directly, since both already say
"follow PRINCIPLES.md's rules, don't restate them" and inherit this automatically. Bug-fixing commands
(e.g. `/scm:fix`) still own whatever's structurally project-only — DB/log access, issue-tracker
integration, version-bump mechanics — since the dispatched agent's tool grant can't reach those anyway.
