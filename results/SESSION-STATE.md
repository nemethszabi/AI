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
  decided and documented in that session's plan file, not yet built.

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
