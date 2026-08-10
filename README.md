# AI — Generic Claude Code Agents & Commands

Staging and distribution source for generic, project-agnostic Claude Code agents, commands, and
doctrine baseline files. Files here are drafted, reviewed manually, then copied into
`~\.claude\agents\`, `~\.claude\commands\`, and `~\.claude\` respectively — nothing here is live/active
in Claude Code until that copy step happens.

Project-specific agents, commands, and context belong in each project's own repo (its own `.claude\` and
`ai\context\`), never here — see `DESIGN-PRINCIPLES-BASELINE.md`'s and `AGENT-CONDUCT-BASELINE.md`'s own
"how to use" sections for how generic and project-specific artifacts connect.

**Exclusion**: nothing from `d:\WORK\Private\Költségvetés\` may appear in this repo's content, ever — that
project's material never informs, and is never cited by, anything drafted here.

---

## Repository layout

| Path | What it is |
|---|---|
| `CLAUDE.md` | Thin, always-loaded pointer block — merge into `~\.claude\CLAUDE.md` manually (never blind-overwrite; you may already have personal notes there). Points at the doctrine files below, doesn't inline them. |
| `CONSTITUTION.md` | **Binding**, global hard rules (secrets, destructive actions, gates, scope, tool permissions). Every generic agent reads this first. Not a checklist like the two below — this one is live doctrine. |
| `DESIGN-PRINCIPLES-BASELINE.md` | Checklist for drafting a **project's own** `ai/context/design-principles.md` — code/architecture principles (layering, DI, DTOs, isolation boundaries). Not itself binding on any project. |
| `AGENT-CONDUCT-BASELINE.md` | Checklist for drafting a **new agent's own** `<rules>` section — how an agent should behave while working (executor discipline), while reviewing others' work (reviewer discipline), or while using persistent memory (memory conduct). Not code-architecture rules — see the table in this file for the distinction. |
| `AGENT-TEMPLATE-BASELINE.md` | Checklist for a new agent/command's **file structure** — frontmatter fields, section skeleton, tone. Governs shape, not behavior — pairs with `AGENT-CONDUCT-BASELINE.md`, doesn't replace it. |
| `dev-framework\PRINCIPLES.md` | **Binding** shared protocol for the `dev-*` role-specialist agent family (state loading, lane discipline, contract discipline, commit/report format, blocked protocol). Scoped to that one family — not global like `CONSTITUTION.md`, not a checklist like the `*-BASELINE.md` files. |
| `dev-framework\DESIGN.md` | Rationale for the `dev-*` family — why it's deliberately lighter than the reference framework's full wave/gate pipeline, the canonical `ai/dev/` state-file schema, explicit non-goals, and the trigger condition for revisiting them. Read when deciding whether to extend this family, not at runtime. |
| `agents\` | Generic agent definitions, one file per agent, copied to `~\.claude\agents\` |
| `skills\` | Generic skill definitions (`skills\<name>\SKILL.md`, one folder per skill), copied to `~\.claude\skills\`. The canonical form for new reusable, `/name`-invocable work going forward — see `commands\agent-builder.md`'s `classify` step for when to use this instead of `commands\`. |
| `commands\` | Generic slash-command definitions, copied to `~\.claude\commands\` — a legacy path Claude Code still runs but isn't developing further; new work should default to `skills\` instead. |
| `docs\` | Reference documentation that stays in this repo (not copied to `~\.claude\`) — `GETTING-STARTED.md` (first-time walkthrough for someone new to agentic work), `SETUP.md` (install/verify/troubleshoot), and `USAGE.md` (cross-repo "which entry point when" map, since commands now span four different project repos). |

## Current inventory

| Agent | Purpose |
|---|---|
| `agents\solution-analyst.md` | Reads an unfamiliar solution/repo and drafts a first-pass `ai/context/<slug>-context.md` for human review. CREATE/UPDATE mode-aware. Generic across stacks and solution types. Dry-run tested 2026-08-07 (CREATE mode) against `d:\_GEOMANT_GIT\CampaignManager` — held up on a real, messy repo. UPDATE mode still untested. |
| `agents\dev-backend.md` | Backend implementation specialist — generic across stacks. Bound by `dev-framework\PRINCIPLES.md`. Reads a project's `CLAUDE.md`/`ai/context/*.md`/`ai/dev/*` for everything project-specific. |
| `agents\dev-frontend.md` | Frontend implementation specialist — generic across stacks. Same shape/binding as `dev-backend.md`. |
| `agents\dev-reviewer.md` | Independent, read-only code reviewer — generic across stacks. Cold `git diff` read, fixed review dimensions (concrete checks come from the target project's own `ai/context/*.md`), ends with an `AGENT-CONDUCT-BASELINE.md` B7 verdict block. No `Edit`. |
| `agents\dev-browser-tester.md` | Browser-driven smoke-test specialist — generic across web projects. Drives a running app via the `playwright` MCP: navigate, log in, execute a scenario, screenshot, watch console errors, PASS/FAIL report. Never fixes anything; no `Edit`. |
| `agents\req-analyst.md` | Clarifies a free-form requirement/change request into a structured, reviewable requirements list (`REQ-ID`/priority/status/source). Narrative markdown, no formal gates. Generic across domains. |
| `agents\req-architect.md` | Design/architecture proposal from a clarified requirements list — approach, alternatives, components, risks. Named `req-architect`, not `solution-architect`, to avoid colliding with domain-specific agents of that name in other frameworks. |
| `agents\req-estimator.md` | Three-point effort estimate from requirements + design. Never invents a rate card — effort-only if none found. Named `req-estimator`, not `project-estimator`, same collision-avoidance reason. |
| `agents\mermaid-diagram-maker.md` | Writes `.mmd` diagrams (architecture/sequence/flowchart/class/state/deployment/ER) and renders `.png` via `mmdc`. Generic, `memory: user` for cross-project styling conventions only — never project-specific component/service names. Adapted from `agentic-dev-framework`, not copy-pasted: fixed a memory-boundary violation in the source (it told the agent to save component/service names globally) and added a no-silent-overwrite rule. |
| `agents\agent-reviewer.md` | Independent, read-only reviewer for a drafted/edited agent, skill, command, or one-time prompt — the meta-level counterpart to `dev-reviewer` (reviews customization artifacts, not application code). Reads cold, never the drafting session's own reasoning. Ends with an `AGENT-CONDUCT-BASELINE.md` B7 verdict block. No `Edit` beyond narrow, unambiguous mechanical fixes. Added 2026-08-10 specifically because `agent-builder`'s own self-check isn't independent (same session checking its own work) — closes that gap. |

| Skill | Purpose |
|---|---|
| `skills\prompt-builder\SKILL.md` | Drafts a new one-time/occasional-use prompt (`ai/prompts/<topic>/`) with proper context-loading, optional runtime parameters, and an approval gate if the task has real blast radius. Lighter-weight than `agent-builder` — no tool grant, no scope classification, no self-check machinery — and checks first whether the request is genuinely one-time rather than a recurring need in disguise, redirecting to `agent-builder` if not. First entry in this repo's `skills\` folder (2026-08-10). |
| `skills\review-agent\SKILL.md` | Thin dispatcher to `agent-reviewer` — invoke after `agent-builder`/`prompt-builder` produces something, or before trusting/copying anything to global. |

| Command | Purpose |
|---|---|
| `commands\agent-builder.md` | `/agent-builder` — interactively drafts new agents/skills/legacy-commands per this repo's conventions (classifies agent-vs-skill-vs-command and generic-vs-project, executor-vs-reviewer; consults `CONSTITUTION.md`/both baselines; applies naming/placement/body-style rules including the Skill no-XML-tags constraint; self-checks tag balance). Deliberately a command, not an agent — see rationale below. |
| `commands\scaffold-context.md` | `/scaffold-context [path]` — thin dispatcher to `solution-analyst` |
| `commands\diagram.md` | `/diagram [what to diagram]` — thin dispatcher to `mermaid-diagram-maker` |
| `commands\sa\clarify.md`, `design.md`, `estimate.md`, `doc.md`, `help.md` | `/sa:*` — lightweight, generic REQ/CR pipeline (clarify → design → estimate → doc), no formal gates. Dispatches to `req-analyst`/`req-architect`/`req-estimator`; `doc` consolidates directly. Artifacts slugged per-topic under `ai/sa/<slug>/` so repeated use doesn't collide. |
| `commands\dev\init.md`, `status.md`, `quick.md`, `help.md` | `/dev:*` — generic, cross-project scaffold/status/dispatch for the `ai/dev/` convention. `/dev:quick` is the generic form of a project dispatcher for projects with no process of their own to enforce (see the `/cm:dev` retirement note below). |

---

## When authoring a new agent, skill, or command

Prefer running `/agent-builder` over applying this section by hand — it implements the same rules
interactively and stays current as they evolve; this section is the reference, not the primary workflow.

1. Walk `AGENT-TEMPLATE-BASELINE.md` first — frontmatter fields, section skeleton, tone — before writing
   a line of the agent/command itself, so structure doesn't drift file to file. For a skill, the
   equivalent conventions (no XML tags, `description`-as-trigger, folder shape) live directly in
   `commands\agent-builder.md`'s own `draft` step — no separate `SKILL-BASELINE.md` yet (see that file's
   `consult-conventions` step for the threshold on when one would get created).
2. If it touches how a **target codebase** should be structured → walk `DESIGN-PRINCIPLES-BASELINE.md`
   against the project (informed by `solution-analyst`'s "Conventions Observed" output, if available) to
   produce that project's `ai/context/design-principles.md`.
3. Walk `AGENT-CONDUCT-BASELINE.md` — Executor section for an agent that does work, Reviewer section for
   an agent that checks others' work, Memory section (§C) if it sets `memory: user` — and write the
   relevant instances directly into the new agent's own `<rules>`/`<memory>` section.
4. Decide **generic vs. project-specific** before deciding where the file lives: does the agent's own
   text contain a fact that only makes sense inside one repo (an absolute path, an org name, a stack
   fact), or a *process* that genuinely differs per project (an approval gate, an issue-tracker
   integration, a release discipline)? If yes, it belongs in that project's own `.claude\`, not here. See
   `d:\WORK\AI\results\claude-prompting-system-review.md §10` for the full decision rule and naming
   conventions (§13) — not duplicated in this repo to avoid the two drifting out of sync. Concretely: SCM's
   `/scm:fix` earns its project-specific home (Azure DevOps org rule, version-bump discipline — real
   process differences); a thin dispatcher with **no** such differences doesn't — CampaignManager's
   `/cm:dev` was exactly this mistake, retired 2026-08-07 in favor of the generic `/dev:quick` once it
   became clear it carried no CampaignManager-specific logic at all. When in doubt, ask "does this
   command's own `<process>` contain anything that wouldn't apply verbatim to a different project?" — if
   no, it belongs here as a generic command, not there as a bespoke one.
5. If the agent/command is a **gate or reviewer** (produces a PASS/FAIL-style verdict another command or
   human must act on), follow `AGENT-CONDUCT-BASELINE.md` B7/B9 for the verdict-block and freshness-hash
   conventions — don't invent a new verdict shape per agent.
6. Once a command namespace (a `commands\<prefix>\` folder) accumulates more than a handful of commands,
   add a `<prefix>:help` command whose only job is to print a static reference of that namespace — no
   live analysis, no project context, just the reference (mirrors the sample framework's
   `commands/sa/help.md`). Not needed yet at one command; noted here so it isn't forgotten once
   `commands\` grows.
7. Any agent named `dev-*` reads `dev-framework\PRINCIPLES.md` first (after `CONSTITUTION.md`) — that's
   where the family's shared operational rules live; don't restate them in the agent's own `<rules>`.

## Rollout

1. Draft under `agents\`, `skills\`, or `commands\` here.
2. Manual review.
3. Copy to global:
   ```powershell
   # Pre-create destination folders first — Copy-Item with -Recurse onto a not-yet-existing destination
   # can silently mis-create it as a copy of the *first* source item's contents instead of a proper
   # container (hit this for real on 2026-08-10 with skills\ — left a stray SKILL.md sitting loose in
   # ~\.claude\skills\ instead of in its own subfolder). Always ensure the target exists as a real
   # directory first, every time, not just the first time a new subfolder type appears.
   New-Item -ItemType Directory -Path "$env:USERPROFILE\.claude\agents"   -Force | Out-Null
   New-Item -ItemType Directory -Path "$env:USERPROFILE\.claude\skills"   -Force | Out-Null
   New-Item -ItemType Directory -Path "$env:USERPROFILE\.claude\commands" -Force | Out-Null

   Copy-Item agents\*.md  "$env:USERPROFILE\.claude\agents\"   -Force
   Copy-Item skills\*     "$env:USERPROFILE\.claude\skills\"   -Recurse -Force
   Copy-Item commands\*   "$env:USERPROFILE\.claude\commands\" -Recurse -Force
   Copy-Item *-BASELINE.md  "$env:USERPROFILE\.claude\"          -Force
   Copy-Item CONSTITUTION.md "$env:USERPROFILE\.claude\"         -Force
   Copy-Item dev-framework  "$env:USERPROFILE\.claude\" -Recurse -Force
   ```
4. Merge `CLAUDE.md` into `~\.claude\CLAUDE.md` by hand (create it if missing) — do **not** blind-copy
   with `-Force`, since a real global `CLAUDE.md` may already carry personal notes this would clobber.
5. After any future edit here, re-run step 3 (and re-check step 4) so `~\.claude\` picks up the change —
   this repo is the source of truth, `~\.claude\` is a copy of it, not the other way around.
6. Run `powershell -File _scripts\check-sync.ps1` to confirm — reports anything staged here that's
   missing or stale in `~\.claude\`. This caught a real gap on 2026-08-10 (the `skills\*` copy step
   didn't exist in step 3 until that day, so nothing had ever reached `~\.claude\skills\`) — run it after
   every rollout, not just when something seems off.

**One-time setup**: run `powershell -File _scripts\install-hooks.ps1` once (and again after a fresh
clone, or after pulling a change to `_scripts\hooks\`) — installs a `post-commit` hook that auto-runs
step 6 after every commit, so drift surfaces immediately instead of whenever someone remembers to check.
Informational only: it never blocks a commit and never auto-copies to `~\.claude\` — step 3 stays a
deliberate, explicit action.
