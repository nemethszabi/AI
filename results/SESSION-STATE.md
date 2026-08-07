# Session State — hand-off for a fresh session

Written 2026-08-07 to bring a new Claude Code session up to speed on this repo without replaying the
conversation that built it. Read this first if picking up work here cold.

---

## What this repo is

`d:\_AI_GIT\` — staging and distribution source for **generic, project-agnostic** Claude Code agents,
commands, and doctrine files. Nothing here is live in Claude Code until copied to `~\.claude\`. Nothing
project-specific belongs here — see the placement rule below.

## Current inventory

| File | Type | Status |
|---|---|---|
| `CLAUDE.md` | Doctrine — thin pointer | User-authored. Deliberately minimal: points at `CONSTITUTION.md`, both baselines; never inlines doctrine itself. |
| `CONSTITUTION.md` | Doctrine — binding, runtime-read | User-authored. 8 Articles: secrets, destructive/irreversible actions, no bypassing gates, truthfulness, scope boundary, least-privilege tooling, human approval for high-blast-radius work, data/privacy. Overrides everything else if conflicting. |
| `AGENT-CONDUCT-BASELINE.md` | Doctrine — drafting reference | Executor conduct (A1-A9) + Reviewer/auditor conduct (B1-B9, user-extended with concrete mechanisms: B7 verdict-block format, B8 waiver-entry format, B9 content-hash gate freshness — pulled from `agentic-dev-framework\commands\sa\audit-deliverable.md`). Reference-only, not runtime-read by agents (see rationale below) — except `CONSTITUTION.md`, which is runtime-read. |
| `DESIGN-PRINCIPLES-BASELINE.md` | Doctrine — drafting reference | 14 code-architecture principles, synthesized from `scm-context.md §22` and `design-architect.md`. For drafting a *project's own* `ai/context/design-principles.md` — not itself binding anywhere. |
| `README.md` | Meta | Repo layout, rollout/copy steps, "when authoring a new agent" pointer sequence. |
| `agents\solution-analyst.md` | Agent | Reads an unfamiliar solution/repo, drafts `ai/context/<slug>-context.md`. CREATE/UPDATE mode-aware (multi-candidate ambiguity handled). First action reads `~\.claude\CONSTITUTION.md` if present. Tools: `Read, Grep, Glob, Bash, Write, AskUserQuestion` — deliberately no `Edit`, no `Task`. |
| `commands\scaffold-context.md` | Command | `/scaffold-context [path]` — thin dispatcher to `solution-analyst`. |
| `commands\agent-builder.md` | Command | `/agent-builder` — interactively drafts new agents/commands per this repo's conventions (classifies generic-vs-project, executor-vs-reviewer; consults `CONSTITUTION.md`/both baselines; applies naming/placement/body-style rules; self-checks tag balance). Deliberately a command, not an agent — see rationale below. |
| `dev-framework\PRINCIPLES.md` | Doctrine | Added in a separate thread (2026-08-07): binding shared protocol for the `dev-*` family. State-file root amended same day from `.dev\` (reference framework's convention) to `ai\dev\`, to group with the already-established `ai\context\`/`ai\prompts\`/`ai\reports\` convention rather than adding a new top-level dot-folder. `contracts\`/`ARCHITECTURE.md` clarified to point at a project's real, pre-existing sources of truth instead of being duplicated under `ai\dev\` when those already exist. |
| `agents\dev-backend.md`, `agents\dev-frontend.md` | Agent | First two role-specialist `dev-*` agents. Generic, stack-agnostic; read `CONSTITUTION.md` → `dev-framework\PRINCIPLES.md` → the target project's `CLAUDE.md`/`ai\context\*.md`/`ai\dev\*` for everything project-specific. Drafted 2026-08-07 for the CampaignManager slice (see below); not yet copied anywhere, not yet live-tested end to end (only tag-balance-checked). |
| `agents\dev-reviewer.md` | Agent | Read-only reviewer, generic. Fixed `<review_dimensions>` (8, ranked); concrete checks per dimension come from the target project's own `ai/context/*.md` — none baked in here. Ends with a B7 verdict block. Tools: `Read, Bash, Grep, Glob, Write` — no `Edit`. Drafted 2026-08-07 for the net8-migration (SCM) slice; not yet live-tested. |
| `agents\dev-browser-tester.md` | Agent | Browser smoke-test specialist, generic, via the `playwright` MCP. Never fixes anything (no `Edit`, no `Task`/`Agent`) — a verification role only. Drafted 2026-08-07 for the SCM slice's `/scm:test`; not yet live-tested. |

## Git state

3 commits on `main`, up to date with `origin/main` (`https://github.com/nemethszabi/AI.git`).
`agents\solution-analyst.md` has uncommitted local changes (the `CONSTITUTION.md` read wiring). Every
other file above except `commands\scaffold-context.md` is untracked. **No commit has been requested —
don't commit unless asked.**

---

## Load-bearing design decisions (don't relitigate these without reason)

1. **Generic vs. project-specific placement rule**: does the file's own text contain a fact that only
   makes sense in one repo (absolute path, org name, stack fact, build command)? Yes → belongs in that
   project's own `.claude\`, never here. No → belongs here, copied to `~\.claude\`.
2. **Three-tier doctrine, not one file**:
   - `CONSTITUTION.md` — binding, runtime-read (agents check it first if present).
   - `AGENT-CONDUCT-BASELINE.md` / `DESIGN-PRINCIPLES-BASELINE.md` — drafting references, consulted when
     *authoring* something, not read at runtime by the thing itself. Revisit only once enough agents
     exist that manual consistency becomes real risk.
3. **`agent-builder` is a command, not an agent** — subagents run in an isolated context and report back
   once; prompt-drafting needs iteration (plan → draft → review → fix), which an isolated single-shot
   agent can't do without losing the conversation. Commands stay inline in the current session.
4. **XML tags vs. Markdown headers**: Markdown by default. XML only when a prompt's body needs to embed
   an example Markdown output block (e.g. `solution-analyst`'s `output_template`) — avoids the outer/inner
   heading collision. State the choice explicitly when drafting, don't pick silently.
5. **Frontmatter key differs by file type**: agents use `tools:` (comma list). Commands use
   `allowed-tools:` (YAML list). Not interchangeable.
6. **Naming**: kebab-case. Generic agent/command → `<role>.md`/`<verb>.md`, no project prefix. Project
   agent/command → `<project-prefix>-<role>.md`, lives in that project's own `.claude\`.
7. **Költségvetés exclusion**: nothing from `d:\WORK\Private\Költségvetés\` may appear in this repo's
   content, ever — audited clean as of 2026-08-07 (full grep across every `.md` file, zero hits). Keep it
   that way; re-audit if anything gets copy-pasted from that project into a draft here.
8. **Copy-to-global is deferred, on purpose** — user will request it explicitly once everything here is
   finished, not per-file. Don't copy anything to `~\.claude\` without being asked.

## Known gotchas — don't get fooled by these again

- **The `Read` tool's line-numbered display has shown a phantom duplicate closing tag** (e.g. an extra
  `</output>` that doesn't exist in the actual file) on at least two separate occasions this session.
  **Verify XML tag balance with `grep -c '<tag>'` / `grep -c '</tag>'` counts, never by eyeballing `Read`
  output.**
- **`grep -c` itself can false-positive** if a tag name is mentioned in backtick-quoted prose (e.g. a
  sentence referencing `` `<process>` `` as a name, not using it structurally). If a count looks
  unbalanced, check the actual matched lines before concluding there's a real defect.

## Outstanding / not yet done

- **`solution-analyst` CREATE mode now dry-run tested** (2026-08-07, against
  `d:\_GEOMANT_GIT\CampaignManager` on its `staging` branch) — see the CampaignManager section below.
  **UPDATE mode still untested** — `net8-migration` (real `scm-context.md` + `migration-context.md` pair,
  exercises the multi-candidate ambiguity fix) remains the planned target.
- **`dev-backend.md`/`dev-frontend.md` drafted but not live-tested end to end** — only checked for
  frontmatter/section-skeleton compliance and XML tag balance. Real execution requires either a project-
  local or global `.claude\agents\` copy (session-scoped agent discovery isn't hot-reloaded), or the same
  "inline the role into a `general-purpose` agent call" technique used for `solution-analyst`'s dry run.
- **Nothing copied to `~\.claude\` yet.**
- **Untracked files not committed.**
- **No `README.md` line yet stating the Költségvetés-exclusion rule explicitly** — was offered, not yet
  added; worth doing so a fresh session doesn't have to be told again.

## CampaignManager slice (2026-08-07)

First "generic global agent + project context + thin project-specific command" pass, built end-to-end
against a real project per the approved plan in that session:
- `d:\_GEOMANT_GIT\CampaignManager` was stale on `master` (~15k lines behind `origin/staging`, missing
  `docs/ARCHITECTURE.md`/`ROADMAP.md`/ADRs entirely) — user checked out `staging` directly.
- `solution-analyst` dry-run produced `ai/context/campaignmanager-context.md` there; confirmed the
  EnsureCreated-vs-EF-migrations drift (ADR-0004) and an unresolved live conflict between
  `docs/ARCHITECTURE.md` and `docs/ROADMAP.md` over which components are actually done vs. stubbed.
- `ai/dev/STATE.md` + `ai/dev/config.json` scaffolded in CampaignManager itself (gates all `false`, no
  wave/task orchestration adopted — `dev-backend`/`dev-frontend` run standalone).
- `dev-backend.md`/`dev-frontend.md` drafted here in `_AI_GIT` (see inventory table above).
- `d:\_GEOMANT_GIT\CampaignManager\.claude\commands\cm\dev.md` (`/cm:dev`) drafted directly in that
  project's own repo — thin dispatcher, classifies backend/frontend/both, injects project context,
  relays the dispatched agent's report verbatim. Not listed in this repo's own README, per the
  generic/project-specific placement rule.
- **Roadmap for the remaining three project needs** (net8-migration SCM dev-fix/devops conversion,
  scm-stm-merge's read-only analysis agents as a justified project-specific-agent exception, and a
  lightweight `req-analyst`/`solution-architect`/`project-estimator` SA pipeline with no gates) was
  decided and documented in that session's plan file. The first of these (net8-migration) was built next
  — see below.

## net8-migration (SCM) slice (2026-08-07)

Second slice, same conversation. Converted the hand-rolled `ai/prompts/scm-dev-fix/` (FIX/REQ/TEST/REVIEW
modes, v1.4.0) and `ai/prompts/scm-devops/` (ASK/CHANGE modes, v1.0.0) prompt collections into generic
`dev-*` agents + six thin, SCM-specific `/scm:*` commands. Originals left in place, not deleted.

- Two new generic agents added here (see inventory table above): `dev-reviewer.md`, `dev-browser-tester.md`
  — the third new role decided conversationally with the user (`dev-browser-tester`, deliberately not
  named `dev-qa` to avoid colliding with the reference framework's broader dual-mode `dev-qa` role if
  that's ever adopted later).
- `ai/dev/STATE.md` + `ai/dev/config.json` scaffolded directly in `d:\_SCM_GIT\net8-migration` (gates all
  `false`; monolith, so `contracts_path` is explicitly N/A rather than forced into a microservice shape).
- Two new project-specific context files added directly in that repo (not here — pure project fact, not
  mode-specific mechanics): `ai/context/scm-quick-reference.md` (namespace map, session abstractions, DI
  chain, file-path resolution, error recognition, version-bump project map, and the code-review checklist
  mapped onto `dev-reviewer`'s 8 generic dimensions) and `ai/context/scm-devops-quick-reference.md`
  (hosting environment snapshot, known-issues table, symptom recognition table — `IIS-PRODUCTION-CONFIG.md`
  remains authoritative over both).
- Six commands drafted directly in `d:\_SCM_GIT\net8-migration\.claude\commands\scm\`: `fix.md`, `req.md`,
  `review.md`, `devops-ask.md`, `devops-change.md`, `test.md`, plus `help.md` (static reference, per the
  namespace-help convention — six commands is "more than a handful").
- **Design decisions worth remembering if this pattern gets extended to another project:**
  - `devops-ask` and `devops-change` were kept as two separate commands, not merged, specifically so
    ASK's read-only guarantee is enforced by the tool grant itself (no `Agent`/`Write`-to-existing-file/
    `Edit` at all) rather than by instruction alone — matches `AGENT-CONDUCT-BASELINE.md` A6/B1.
  - `req.md`/`devops-change.md` implement the phased-approval gate (Understand → Design → Plan → approve →
    Implement → Report) as **two sequential `Agent` dispatches within one command invocation**, with the
    command itself doing the human approval step via `AskUserQuestion` in between — not a second command
    invocation, since a command runs inline in the current conversation and can pause for input, unlike an
    isolated single-shot subagent.
  - ADO/version-bump/commit-message/never-commit mechanics live in the commands, not in `dev-backend` —
    keeps that agent reusable on non-SCM, non-Azure-DevOps projects.
  - `scm-refactor`, `design-architect`, `new-ui-design-upgrade`, `performance-review`,
    `repository-query-review` prompt folders exist in that repo too but were explicitly out of scope for
    this pass.
- **Not yet done**: none of the six new commands or two new agents have been live-tested end to end (same
  "session-scoped agent discovery isn't hot-reloaded" constraint as the CampaignManager slice).

## scm-stm-merge slice (2026-08-07)

Third slice, same conversation — the roadmap's one deliberate exception to "generic agent + thin command."
**Nothing was added to `_AI_GIT` for this slice** — every artifact lives entirely in
`d:\_SCM_GIT\scm-stm-merge`, because the reasoning content (STM↔SCM entity/enum collision mapping,
ServiceType/TournamentType alignment, SSO-bridge removal inventory) is one-time domain knowledge for this
single merge effort, not a reusable role. This entry exists purely so the decision and its outcome aren't
lost from this repo's own continuity log.

- Converted the never-yet-run `ai/prompts/scm-stm-merge-analysis/` prompt collection (v2.0.0, 4 analysis
  phases + orchestrator) into 4 project-specific read-only agents in
  `scm-stm-merge\.claude\agents\`: `stm-merge-requirements-analyst`, `stm-merge-db-analyst` (has the
  `mcp__scm-db__*`/`mcp__stm-db__*` MCP tool grants), `stm-merge-functional-analyst`,
  `stm-merge-code-analyst`. None have `Edit` — pure planning system, no agent here ever implements code.
- 5 commands in `scm-stm-merge\.claude\commands\merge\`: `requirements.md`, `db.md`, `functional.md`,
  `code.md` (one per phase, each independently runnable), plus `full-analysis.md` (orchestrator — fixed
  order, mid-run checkpoints, writes a consolidated executive summary) and `help.md`.
- `ai/merge/STATE.md` scaffolded (not `ai/dev/` — these aren't part of the `dev-*` family) tracking which
  of the 4 phases have run.
- **Confirmed via user discussion, worth remembering if this exception pattern recurs elsewhere:** even
  when full project-specific agents are justified, still build *both* an orchestrator and individual
  per-phase entry points if the original system had both — report-chaining already makes each phase
  independently re-runnable, so only building the orchestrator would be a real regression in flexibility
  for no savings (each phase command is just "dispatch + relay," near-zero marginal cost).

## SA / REQ-CR pipeline slice (2026-08-07)

Fourth and final roadmap slice, same conversation. Global, generic (per user choice: lightweight, no
gates) — the recurring "analyze a new REQ/CR, produce a design and an estimate, generate documentation"
need, decoupled from any single project.

- Three new generic agents added here (see inventory table above): `req-analyst.md`, `req-architect.md`,
  `req-estimator.md`. **Deliberately renamed from the roadmap's original `solution-architect`/
  `project-estimator`** — both names collide with domain-specific (CCaaS/Buzzeasy) agents of the same name
  already used in `agentic-dev-framework`; renaming now avoids a forced rename later if both frameworks'
  agents ever get installed to `~/.claude/` together. Same reasoning already applied once before to
  `dev-browser-tester` (vs. the framework's broader `dev-qa`).
- Five commands added here in `commands\sa\`: `clarify.md`, `design.md`, `estimate.md`, `doc.md` (no agent
  dispatch — consolidation is squarely a command's own job), `help.md`.
- **Artifacts are slugged per-topic** (`ai/sa/<slug>/requirements.md`/`architecture.md`/`estimation.md`/
  `package.md`), not a single fixed path — this pipeline is explicitly meant to be run repeatedly over time
  on different REQ/CRs within the same project, so a fixed path would let one overwrite another.
  `/sa:design`/`/sa:estimate`/`/sa:doc` resolve the slug from an explicit argument or by globbing
  `ai/sa/*/` and asking if ambiguous.
- No `ai/sa/STATE.md` — each slug's folder is self-contained (unlike `ai/dev/`/`ai/merge/`, there's no
  cross-cutting "current phase" to track across a single project; multiple independent REQ/CRs can be
  in-flight at once).
- `req-estimator` never invents a rate card: looks for `ai/sa/rates.yaml`/`ai/context/rates.yaml` then
  `~/.claude/estimation-data/rates.yaml`; if none found, produces effort-only output and says so explicitly
  (Constitution Article IV — truthfulness).
- **Fixed a latent bug in this repo's own `README.md` rollout instructions while here**: the
  `Copy-Item commands\*.md ... -Force` step (no `-Recurse`) would have silently skipped the new
  `commands\sa\` subfolder (and `commands\cm\`/`commands\scm\`/`commands\merge\` in the project repos,
  though those were never meant to be copied from here anyway). Changed to
  `Copy-Item commands\* ... -Recurse -Force`.
- **Not yet done**: none of the three new agents or five new commands have been live-tested end to end
  (same constraint as every prior slice this session).

This closes out all four roadmap items from this session's original architecture plan (CampaignManager,
net8-migration, scm-stm-merge, SA/REQ-CR). Nothing has been copied to `~/.claude/` yet — still deferred
until explicitly requested.

## docs/ + dev-framework/DESIGN.md + commands/dev/ slice (2026-08-07)

Fifth slice, same conversation, prompted by re-examining `agentic-dev-framework`'s `docs\`,
`dev-framework\DESIGN.md`, and `commands\dev\`/`commands\sa\` separation now that the four roadmap slices
existed to compare against.

- **`dev-framework\DESIGN.md`** (new) — consolidates reasoning that was previously scattered across this
  file's own slice write-ups and an ephemeral plan file: why this `dev-*` family is deliberately lighter
  than the reference framework's wave/gate pipeline, the **canonical `ai/dev/` schema**
  (`STATE.md`'s 4 fixed sections; `config.json`'s core field set), explicit non-goals, and a concrete
  amendment trigger (backlog too big to track by memory, or two dispatches that could plausibly touch the
  same file) rather than "revisit eventually."
- **`docs\SETUP.md`** and **`docs\USAGE.md`** (new, stay in this repo — not copied to `~/.claude\`).
  SETUP's troubleshooting section captures the "agent/command lists aren't hot-reloaded mid-session" gotcha
  that had previously only been noted inline, once per slice, in this very file. USAGE is the cross-repo
  "which entry point when" map — genuinely necessary now that commands span four different repos
  (CampaignManager, net8-migration, scm-stm-merge, plus this repo's own globals).
- **`commands\dev\` namespace** (new): `init.md`, `status.md`, `quick.md`, `help.md` — the `ai/dev/`
  scaffolding step that had been hand-written identically for both CampaignManager and net8-migration is
  now a reusable command instead of manual repetition for a third project.
- **`/cm:dev` retired** (CampaignManager) in favor of the new generic `/dev:quick` — on review, `/cm:dev`
  never actually contained any CampaignManager-specific logic (unlike `/scm:fix`'s real Azure DevOps/
  version-bump mechanics), so building it as a project-specific command in the first place was the wrong
  call. `README.md`'s "generic vs. project-specific" guidance (item 4) now states the test explicitly:
  "does this command's own `<process>` contain anything that wouldn't apply verbatim to a different
  project?" CampaignManager's `ai/dev/config.json` updated to add the missing `build_command` core field
  and to stop referencing the retired command.
- **Not yet done**: none of the 4 new commands or `/dev:quick`'s generalized dispatch have been
  live-tested end to end (same constraint as every prior slice).

## Related material outside this repo

- `d:\WORK\AI\results\claude-prompting-system-review.md` — the original deep-dive: naming conventions
  (§13), generic/specific decision rule (§10), folder-structure guideline (§14). This repo is the
  implementation of that document's recommendations.
- `d:\WORK\AI\results\solution-analyst-readiness-check-20260807.md` — an earlier, narrower status report;
  this file supersedes it for overall repo state, but it has more detail on the specific
  `solution-analyst` review pass.
- `d:\_GEOMANT_GIT\agentic-dev-framework\` — the reference framework everything here is modeled on:
  `agents\dev-lead.md`, `dev-reviewer.md`, `solution-architect.md`, `sa-slop-detector.md`,
  `sa-completeness-auditor.md`; `commands\dev\init.md`, `build.md`; `commands\sa\ingest.md`,
  `audit-deliverable.md`; `CONSTITUTION.md`; `dev-framework\PRINCIPLES.md`, `DESIGN.md`. Consult these
  directly for precedent before inventing a new pattern from scratch.
- `d:\_SCM_GIT\net8-migration\` — real project used as the other grounding source (`ai\context\
  scm-context.md`, `ai\prompts\design-architect\design-architect.md`) and as the planned test target for
  `solution-analyst`'s UPDATE mode.
