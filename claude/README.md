# `claude/` — Claude Code agents & commands

The Claude Code branch of `_AI_GIT`. Staging and distribution source for generic, project-agnostic Claude
Code agents, commands, and its own doctrine baseline file. Files here are drafted, reviewed manually, then
copied into `~\.claude\agents\`, `~\.claude\commands\`, and `~\.claude\` respectively — nothing here is
live/active in Claude Code until that copy step happens. See the repo root `README.md` for the shared
doctrine (`CONSTITUTION.md`, both remaining baselines, `dev-framework\`, `sa-framework\`, `skills\`) that
applies to this branch too but lives one level up.

Project-specific agents, commands, and context belong in each project's own repo (its own `.claude\` and
`ai\context\`), never here — see `DESIGN-PRINCIPLES-BASELINE.md`'s and `AGENT-CONDUCT-BASELINE.md`'s own
"how to use" sections (both at repo root) for how generic and project-specific artifacts connect.

**Exclusion**: nothing from `d:\WORK\Private\Költségvetés\` may appear in this repo's content, ever — that
project's material never informs, and is never cited by, anything drafted here.

---

## Repository layout

| Path | What it is |
|---|---|
| `CLAUDE.md` | Thin, always-loaded pointer block — merge into `~\.claude\CLAUDE.md` manually (never blind-overwrite; you may already have personal notes there). Points at the doctrine files below, doesn't inline them. |
| `AGENT-TEMPLATE-BASELINE.md` | Checklist for a new agent/command's **file structure** — frontmatter fields, section skeleton, tone. Governs shape, not behavior — pairs with `..\AGENT-CONDUCT-BASELINE.md`, doesn't replace it. |
| `agents\` | Generic agent definitions, one file per agent, copied to `~\.claude\agents\` |
| `commands\` | Generic slash-command definitions, copied to `~\.claude\commands\` — a legacy path Claude Code still runs but isn't developing further; new work should default to the shared `..\skills\` instead. |

The shared doctrine one level up — `..\CONSTITUTION.md` (binding), `..\DESIGN-PRINCIPLES-BASELINE.md`,
`..\AGENT-CONDUCT-BASELINE.md`, `..\dev-framework\`, `..\sa-framework\`, `..\skills\`,
`..\estimation-data\`, `..\docs\` — is genuinely tool-agnostic and lives at the repo root; see the root
`README.md` for that table. `skills\` in particular is listed again below for completeness of "what
Claude can invoke", even though the folder itself physically lives at the repo root as shared, cross-tool
content (already the open `SKILL.md` format both Claude Code and Copilot CLI read natively).

## Current inventory

| Agent | Purpose |
|---|---|
| `agents\solution-analyst.md` | Reads an unfamiliar solution/repo and drafts a first-pass `ai/context/<slug>-context.md` for human review. CREATE/UPDATE mode-aware. Generic across stacks and solution types. Dry-run tested 2026-08-07 (CREATE mode) against `d:\_GEOMANT_GIT\CampaignManager` — held up on a real, messy repo. UPDATE mode still untested. |
| `agents\dev-backend.md` | Backend implementation specialist — generic across stacks. Bound by `..\dev-framework\PRINCIPLES.md`. Reads a project's `CLAUDE.md`/`ai/context/*.md`/`ai/dev/*` for everything project-specific. |
| `agents\dev-frontend.md` | Frontend implementation specialist — generic across stacks. Same shape/binding as `dev-backend.md`. |
| `agents\dev-reviewer.md` | Independent, read-only code reviewer — generic across stacks. Cold `git diff` read, fixed review dimensions (concrete checks come from the target project's own `ai/context/*.md`), ends with an `AGENT-CONDUCT-BASELINE.md` B7 verdict block. No `Edit`. No dispatcher command — invoked directly; the caller may pass `model:` on the `Agent` call for a large/high-risk/subtle diff (added 2026-08-11, no frontmatter pin). |
| `agents\dev-browser-tester.md` | Browser-driven smoke-test specialist — generic across web projects. Drives a running app via the `playwright` MCP: navigate, log in, execute a scenario, screenshot, watch console errors, PASS/FAIL report. Never fixes anything; no `Edit`. **Pinned `model: sonnet` + `effort: low`** (Mechanical tier, `d:\WORK\AI\knowledge-base\token-economy.md` §6, 2026-09-12). **v1.3.0, same day — evidence economy**: works from `browser_snapshot` (the accessibility tree — text, and the only one of the two you can act on) and screenshots *outcomes* rather than every step, at `scale: css` with no `fullPage` default. A FAIL always carries an image; a PASS usually needs only the snapshot. Screenshotting every step was the most expensive possible way to reach the same verdict. |
| `agents\dev-scaffolder.md` | Greenfield bootstrap specialist — empty folder + a description → a solution skeleton that actually builds, runs and tests, **plus** the `ai/context/<slug>-context.md` (in `solution-analyst`'s own nine-section shape) and `ai/dev/` files the rest of the family requires. Added 2026-09-07 to close the family's hardest gap: `dev-backend`/`dev-frontend` resolve every stack fact from a context file and refuse to guess, `solution-analyst` only reads solutions that already exist, and `/dev:init` writes state but no code — so an empty folder was a dead end in every direction. Bound by `..\dev-framework\STACK-DOTNET.md` (versions detected via `dotnet --version`, never asserted from memory). **Declines outright on a folder that already holds a solution** — mode-detected, not overridable, since scaffolding over existing work is the one irreversible thing it could do. |
| `agents\dev-planner.md` | Task decomposition specialist — a goal (plus an optional `ui-spec` or requirements list) → `ai/dev/PLAN.md`: vertical-slice tasks, one owning area each, dependency-ordered, every one carrying a **machine-runnable acceptance check**. CREATE/UPDATE mode-aware; never rewrites a `done` task. Irreversible/outward-facing work (deploys, pushes, cloud resources, shared databases, anything costing money) is routed to `## Out of scope — needs a human` rather than into the task list — this agent is where an autonomous loop's blast radius is actually bounded. Plans only: `disallowedTools: Edit, Bash`. Added 2026-09-07. |
| `agents\dev-ui-analyst.md` | UI deconstruction specialist — a running URL, screenshots, a design export and/or a source tree → `ai/context/<slug>-ui-spec.md`: screen/route inventory, component tree, design tokens, states, flows, observable API surface. Four modes (LIVE/STATIC/SOURCE/MIXED) that determine what it may honestly claim, and **every finding marked `measured`/`observed`/`inferred`/`gap`** — because a hex code read from a computed style and one eyeballed from a JPEG are different facts, and a rebuild driven by the second while believing it was the first is wrong in a way nobody can later diagnose. A gap is a valid result; inventing a token to fill a table is not (`AGENT-CONDUCT-BASELINE.md` D2/D3). Read-only and non-mutating on the target, `disallowedTools`-enforced (`Edit`, `Bash`). The rebuild-from-UI capability had **no** coverage before this — `dev-browser-tester` verifies a scenario and structurally cannot describe an interface. Added 2026-09-07. |
| `agents\doc-briefer.md` | Reads an inbound document (docx/xlsx/pdf/md, or already-ingested `inputs/*.extracted.md`) in its own context and produces a comprehension brief for a human about to work on it — section map classified requirement/background/boilerplate, key facts, integration surface with a "specified vs. merely named" call, conspicuous gaps, and where to read closely. Then answers follow-ups from the source with citations. Deliberately **not** requirement-writing — no REQ-IDs, no priorities; that's `req-analyst`. Sits beside the `/sa:*` pipeline, never writes pipeline state, and its `brief.md` is excluded from `inputs_hash`. Added 2026-08-12. |
| `agents\req-screener.md` | Answers the two questions asked *before* anyone decides to bid — "can we do this?" and "roughly what would it cost?" — from a clarified requirements list. Feasibility verdict (`can-do`/`can-do-if`/`probably-not`/`cannot-assess`) with cited blockers, plus a deliberately coarse order-of-magnitude effort band that is **never quotable**. Writes only `screen.md`, advisory non-artifact #2 after `brief.md`. Deliberately **not** a lighter `req-estimator`: no PERT, no K-categories, no contingency, no calibration, no price — their absence is the point (`ESTIMATION-METHOD.md` §8, which also forbids `req-estimator` from anchoring on the band and `req-estimate-critic` from critiquing it). Runs on any lane, because depth-of-pass and lane are independent axes. Added 2026-08-12. |
| `agents\req-ingestor.md` | Mechanically extracts inbound Excel/Word/PDF/text files into `ai/sa/<slug>/inputs/*.extracted.md` for `req-analyst` to cite. No interpretation — that's the next step's job. Uses the `office-doc-reader` skill for `.xlsx`/`.docx`; `.pdf` via the built-in `Read` tool. Added 2026-08-11. **Pinned `model: sonnet` + `effort: low`** (Mechanical tier, `d:\WORK\AI\knowledge-base\token-economy.md` §6, 2026-09-12). |
| `agents\req-analyst.md` | Clarifies a free-form requirement/change request (or already-ingested files) into a structured, reviewable requirements list (`REQ-ID`/priority/status/source). Since v2.0.0 (2026-08-12) writes `requirements.json` (source of truth) plus a rendered `.md`, with `D-` IDs for open questions; the old "stay narrative" rule was retired. Generic across domains. |
| `agents\req-architect.md` | High-Level Design (HLD) from a clarified requirements list — approach with weighed alternatives scored against named decision criteria, components, quality attributes/NFRs, security & compliance posture, system context, data flow, deployment topology, risks, phasing, assumptions/constraints, and a full requirements traceability matrix. Deliberately stays at component level, never LLD-specific values (config, schema fields, exact infra sizing); `req-detailer` is the separate LLD pass. Named `req-architect`, not `solution-architect`, to avoid colliding with domain-specific agents of that name in other frameworks. Accepts an optional model override via `/sa:design <slug> --model=<name>` for a genuinely novel/high-stakes design (added 2026-08-11). Upgraded to this full depth 2026-08-12 (v1.3.0), no frontmatter pin. |
| `agents\req-reviewer.md` | Independent, read-only critique of a design (HLD and/or LLD) against its requirements — severity-rated findings with a coverage count, written as `review.json` + rendered `review.md`, no PASS/BLOCKING gate (a deliberate, explicitly documented divergence from `AGENT-CONDUCT-BASELINE.md` B7 — this pipeline is gate-free by design, unlike the heavier `sa-design-critic` in the reference framework). Also checks quality-attribute/traceability-matrix coverage against `req-architect`'s v1.3.0 output (added 2026-08-12). Named `req-reviewer`, same collision-avoidance reason as the others. Added 2026-08-11. |
| `agents\req-detailer.md` | Low-Level Design (LLD) from a reviewed HLD — per-component interface/contract sketches, data model, key flows, deployment detail, staying consistent with the HLD's Quality Attributes/Security & Compliance/Deployment Topology sections rather than ignoring them (2026-08-12). Never re-litigates the HLD's approach; flags it in Open Questions instead. Added 2026-08-11. |
| `agents\req-estimator.md` | Three-point **AI-assisted** effort estimate from requirements + design + risk register — one delivery model by default (`traditional`/`both` are opt-in, never on `rom`), `must`-only bare-minimum baseline with `should`/`could` sized separately as priced Optional items, stricter bare-minimum discipline on `rom` (v3.0.0, 2026-09-03). v3.4.0 (2026-09-15) applies `ESTIMATION-METHOD.md` v1.5: §9.3 strict sizing controls (written `k_sanity_check`, per-line lifecycle, 30% lifecycle bound, one requirement one home, itemised contingency), no re-estimate-after language, PERT-only summary with `worst` never rendered. Line items cite a `QA-ID` alongside `REQ-ID`/component ID where relevant. Never invents a rate card — effort-only if none found. Named `req-estimator`, not `project-estimator`, same collision-avoidance reason. |
| `agents\mermaid-diagram-maker.md` | Writes `.mmd` diagrams (architecture/sequence/flowchart/class/state/deployment/ER) and renders `.png` via `mmdc`. Generic, `memory: user` for cross-project styling conventions only — never project-specific component/service names. Adapted from `agentic-dev-framework`, not copy-pasted: fixed a memory-boundary violation in the source (it told the agent to save component/service names globally) and added a no-silent-overwrite rule. **Pinned `model: sonnet` + `effort: low`** (Mechanical tier, `d:\WORK\AI\knowledge-base\token-economy.md` §6, 2026-09-12) — the tier's costliest agent on Opus, and a malformed diagram fails loudly at `mmdc` render. **v1.3.0, 2026-09-12 — render loop capped**: measured at 40.3 model requests and 20.8 min per dispatch (against a comparable agent's 17.9 and 5.6) because steps 3-5 formed an uncapped per-diagram write→render→fallback→re-read cycle, with a verify pass that re-read files `mmdc` had already rendered. Now: write all files, render in one pass, **two attempts per diagram maximum**, no read-back. The pin alone would not have fixed this — a cheaper model retrying a failing render could loop *more*. |
| `agents\req-risk-officer.md` | Scored risk register (probability × impact → **derived** severity, treatment, owner, residual) plus a compliance register, and the contingency recommendation `req-estimator` consumes. Enforces that every `assumed`/`unknown` integration produces a risk, and that every `priced_in: false` risk becomes an offer exclusion. Added 2026-08-12. |
| `agents\req-estimate-critic.md` | Estimate-side mirror of `req-reviewer` — quantified optimism-bias and spread heuristics, PERT integrity, K-category sanity, scope-tier discipline (must-only baseline vs. priced optional) and bare-minimum/`rom`-strictness compliance, contingency-band fit, exclusion integrity, the commonly-forgotten lifecycle lines, rollup integrity (dimension 15), and `ESTIMATION-METHOD.md` §9.3's five sizing controls (dimension 16). Advisory only; never blocks packaging. v1.4.0. |
| `agents\req-offer.md` | Composes the client-facing solution offer (`offer.json` + `offer.md`) from completed artifacts. **Composes, never creates** — every scope line traces to another artifact; `should`/`could` requirements are routed to `scope.optional` rather than committed, never to `in_scope` unless explicitly requested; never states a price without a rate card; bound by the groundedness taxonomy (`AGENT-CONDUCT-BASELINE.md` D1–D3); under high uncertainty proposes sequential contracting (Discovery sold on its own), never later phases "re-estimated" (`ESTIMATION-METHOD.md` §4–§5). v1.4.0. |
| `agents\req-auditor.md` | Cross-artifact validation gate — referential integrity, `must` coverage, exclusion integrity, offer traceability, PERT arithmetic, must-only baseline/optional-scope reconciliation, `rom`-lane model restriction, zero-baseline, commitment-gate field, **rollup arithmetic**, locale preservation. Deliberately **mechanical, never editorial**, which is what makes the gate unarguable. Emits `gate: sa-audit` with a content-based `inputs_hash`. **One of two verdicts `/sa:package` requires** — `req-slop-detector` is the other, and this agent's own report now says so, because a reader taking a clean audit as clearance to send is the failure mode that split exists to prevent. Nine blocking checks are unwaivable — including that an offer never quotes the reference-only all-options total. Advisory checks 23 (no re-estimate-after language) and 24 (`worst` rendered) added in v1.4.0 (2026-09-15). `effort: medium` since 2026-09-12 (arithmetic and ID matching, not judgment), deliberately **no** model pin (B10). |
| `agents\agent-reviewer.md` | Independent, read-only reviewer for a drafted/edited agent, skill, command, or one-time prompt — the meta-level counterpart to `dev-reviewer` (reviews customization artifacts, not application code). Reads cold, never the drafting session's own reasoning. Ends with an `AGENT-CONDUCT-BASELINE.md` B7 verdict block. No `Edit` beyond narrow, unambiguous mechanical fixes. Added 2026-08-10 specifically because `agent-builder`'s own self-check isn't independent (same session checking its own work) — closes that gap. |
| `agents\req-slop-detector.md` | **Prose-integrity gate** — the second of the two verdicts `/sa:package` requires, and the exact complement of `req-auditor`: that agent checks whether the JSON artifacts agree with each other by ID, this one checks whether the rendered `.md` and the extracted deliverable text are *true to them*. Four layers, severity split by audience (a defect in `offer.md` blocks; the same defect in `architecture.md` is advisory): **groundedness** (ungrounded quantities, fabricated specifics, invented client facts, `assumed` integrations written as settled fact — `AGENT-CONDUCT-BASELINE.md` D1's four-kinds-of-claim taxonomy is the test), **contradictions** (both sides cited), **slop** (absolute AI-tells plus counted density thresholds — deliberately *not* em-dash density or sentence length, which catch competent human prose), **locale** (a flattened diacritic in the client's own name is blocking). Emits `gate: sa-slop`. Read-only, `disallowedTools`-enforced. Ports the reference framework's `sa-slop-detector`, which was never brought across when `sa-completeness-auditor` became `req-auditor` — leaving the pipeline with an ID gate and no prose gate. Added 2026-09-07. |
| `agents\req-onepager.md` | Composes a dense single A4-landscape page for people who won't read the artifacts — five fixed page types (`summary`, `roadmap`, `estimate`, `timeline`, `architecture`), each driven by a specific artifact set. Self-contained HTML with print CSS, no external font or CDN; `/sa:onepager` renders the PDF via headless Chromium. **Density is the point** — a one-pager that says less than the artifacts has failed at its only job — made safe by three disciplines: every figure cites its artifact line, an untraceable figure is printed as a named gap rather than filled, and the awkward questions ("not included", "what we commit to", "where this slips") are fixed sections rather than left for the meeting. Advisory non-artifact #3; gates nothing, but `/sa:slop-check` scans its output as client-facing text. Added 2026-09-07; v1.1.0 (2026-09-15) reads the stored rollup `pert` and never renders `worst`. |
| `agents\framework-strategist.md` | Whole-**system** reviewer and strategist for the framework itself — the tier above `agent-reviewer`, which checks one artifact. Audits staged-vs-live sync across every config root, doctrine integrity, documentation honesty, placement, and roster coherence; researches what changed in industry/platform practice (every claim carrying a fetched URL + date); reconciles the tracked gap register in `claude-prompting-kb.md §5`; proposes ranked new agentic use cases routed to the correct layer; and produces `framework-review-YYYYMMDD.md` with a three-bucket changelist. **Advisory — gates nothing.** Takes every machine path from `framework-data\scope.yaml` at the config root (same indirection as `req-estimator`'s rate card), so this file stays generic. Hard limits: never promotes to a live config root, never touches git state, never edits a doctrine/agent/skill/command file, never drafts a new artifact (that's `/agent-builder`). Direct edits confined to an allowlist of living knowledge-base files, for facts verified that run. Added 2026-09-05. |

| Skill | Purpose |
|---|---|
| `..\skills\prompt-builder\SKILL.md` | Drafts a new one-time/occasional-use prompt (`ai/prompts/<topic>/`) with proper context-loading, optional runtime parameters, and an approval gate if the task has real blast radius. Lighter-weight than `agent-builder` — no tool grant, no scope classification, no self-check machinery — and checks first whether the request is genuinely one-time rather than a recurring need in disguise, redirecting to `agent-builder` if not. First entry in the shared `..\skills\` folder (2026-08-10). |
| `..\skills\doc-brief\SKILL.md` | Thin dispatcher to `doc-briefer` — invoke when a document needs understanding before anyone acts on it. Paired with `commands\sa\brief.md` (`/sa:brief <slug>`) for the engagement-slug form. Added 2026-08-12. |
| `..\skills\review-agent\SKILL.md` | Thin dispatcher to `agent-reviewer` — invoke after `agent-builder`/`prompt-builder` produces something, or before trusting/copying anything to global. |
| `..\skills\framework-review\SKILL.md` | Thin dispatcher to `framework-strategist` — the periodic health-and-strategy pass over the *whole* framework, as opposed to `review-agent`'s single-artifact check. Takes an optional focus argument (`drift`, `doctrine`, `research`, `ideas`, `parity`); full review is the default. Documents the one-time `framework-data\scope.yaml` setup and the applied/proposed/build split that is the skill's safety model. Added 2026-09-05. |
| `..\skills\office-doc-builder\SKILL.md` | Reusable Excel/Word/PowerPoint formatting helpers (`lib\excel_helpers.py`, `word_helpers.py`, `pptx_helpers.py` — openpyxl/python-docx/python-pptx). A library, not a workflow — other skills with document-generation needs (e.g. `travel-planner`) import from it instead of rewriting styling boilerplate. Added 2026-08-10. |
| `..\skills\office-doc-reader\SKILL.md` | Read-side counterpart to `office-doc-builder` — extracts `.xlsx`/`.docx` content to Markdown (`lib\excel_reader.py`, `word_reader.py`), both importable and CLI-runnable. `.pdf` deliberately out of scope here — the built-in `Read` tool already parses it. Backs `req-ingestor`. Zero-dependency default; escalation path documented in both this skill and `office-doc-builder` points to the optional `document-skills@anthropic-agent-skills` plugin (OCR, legacy `.doc`, patch-editing, charts/pivots — see `..\docs\SETUP.md`) for what neither library does. Added 2026-08-11. |

| Command | Purpose |
|---|---|
| `commands\agent-builder.md` | `/agent-builder` — interactively drafts new agents/skills/legacy-commands per this repo's conventions (classifies agent-vs-skill-vs-command and generic-vs-project, executor-vs-reviewer; consults `..\CONSTITUTION.md`/both baselines; applies naming/placement/body-style rules including the Skill no-XML-tags constraint; self-checks tag balance). Deliberately a command, not an agent — see rationale below. |
| `commands\scaffold-context.md` | `/scaffold-context [path]` — thin dispatcher to `solution-analyst` |
| `commands\diagram.md` | `/diagram [what to diagram]` — thin dispatcher to `mermaid-diagram-maker` |
| `commands\sa\*` (19: `screen`, `triage`, `brief`, `ingest`, `clarify`, `design`, `review`, `design-detail`, `risk`, `estimate`, `estimate-review`, `offer`, `audit`, `slop-check`, `package`, `status`, `doc`, `onepager`, `help`) | `/sa:*` — the generic **requirement→offer** pipeline. Restructured 2026-08-12 from a linear 8-command REQ/CR chain into a **three-lane** model (`rom` / `offer-sow` / `full-design`) chosen at `/sa:triage`, because the old pipeline only ever served *internal* solution design and terminated in an internal `package.md` — nothing produced a client-facing priced document. Every artifact is written twice, `<name>.json` (source of truth) + rendered `<name>.md`, per `..\sa-framework\ARTIFACT-SCHEMAS.md`. Dispatches to fourteen agents (the thirteen `req-*` plus `doc-briefer`); `doc`, `package` and `status` act directly. **One refusal point, two gate inputs** (2026-09-07): `/sa:package` refuses without a fresh `PASS` from **both** `/sa:audit` (`gate: sa-audit`, IDs agree) and `/sa:slop-check` (`gate: sa-slop`, prose is grounded), each verified by content hash, never mtime — everything else (`review`, `estimate-review`) stays advisory. `/sa:doc` (internal consolidation), `/sa:onepager` (internal, one page) and `/sa:offer`→`audit`+`slop-check`→`package` (client-facing) are different documents for different audiences and must not be confused. `design`/`design-detail` also dispatch `mermaid-diagram-maker`. Artifacts slugged per-topic under `ai/sa/<slug>/`; deliverables build into the branded template a document profile resolves (`ARTIFACT-SCHEMAS.md` §8). `design` takes `--model=<name>` and `--apply-review[=<severity>]`; `review`, `estimate-review`, `audit` and `slop-check` all take `--model=<name>` and **should be run on a different model than produced the work** (§9). Full walkthrough: `..\docs\SA-WORKFLOW.md`. |
| `commands\dev\init.md`, `status.md`, `quick.md`, `help.md` | `/dev:*` — generic, cross-project scaffold/status/dispatch for the `ai/dev/` convention. `/dev:quick` is the generic form of a project dispatcher for projects with no process of their own to enforce (see the `/cm:dev` retirement note below). |
| `commands\handoff.md` | `/handoff` (**v2.1.0, 2026-09-14**: contract moved to the shared `..\dev-framework\HANDOFF.md`, which Copilot's `handoff` skill also implements — handoffs now move between tools; v2.0.0 same day: write / `resume` / `list` / `close`, name `handoff-<YYYYMMDD-HHMM>-<slug>.md`, deleted after approval once handled) — ends a session deliberately instead of letting it grow: writes `<project>\ai\handoff\handoff-<YYYYMMDD-HHMM>.md` from what the session **already holds** (no repo re-read, no agent dispatch — a handoff that costs a fresh investigation defeats its own purpose), then prints the one-line prompt that resumes the work after `/clear`. Establishes `ai\handoff\` as a third `ai\` convention alongside `ai\dev\` and `ai\sa\<slug>\`, and deliberately distinct from both: those hold the *project's* durable state, owned by their frameworks, while a handoff is *this session's* baton — what was in flight, what was decided and why, what to do next. Handoffs accumulate as a history and are never overwritten, so a stale one stays as evidence of what was thought when; the command never writes `STATE.md`, only points at it. The command is Claude's implementation; the *files* are cross-tool since v2.1.0 (Copilot sibling: `..\copilot\skills\handoff\SKILL.md`). What stays Claude-only is the context guard and status line that suggest it at the right moment. Added 2026-09-12. |
| `commands\doc-sync.md` | `/doc-sync` — after a framework/prompting change: proposes documentation updates, then behind four separate approvals applies them, rolls out only the changed staged files, commits **and pushes** this repo in one approval (v1.1.0 — never force, never a project repo) and runs the backup. Machine paths from `framework-data\scope.yaml` → `doc_sync`. Suggested by `_scripts\hooks\framework-change-flag.py` (`PostToolUse`, matcher `Edit|Write|MultiEdit|NotebookEdit`). Added 2026-09-14. The same script also runs as a Copilot `postToolUse` hook (`..\copilot\hooks\`), where it points back here — `/doc-sync` itself is deliberately not ported. |
| `commands\dev\new.md`, `deconstruct.md`, `build.md` | `/dev:new` (thin dispatcher to `dev-scaffolder`), `/dev:deconstruct` (thin dispatcher to `dev-ui-analyst`, confirming authorisation before driving a browser at a non-local target), and **`/dev:build`** — the multi-task loop: `dev-planner` → **human gate on the plan** → per-task dispatch to scaffolder/backend/frontend → `dev-browser-tester` → `dev-reviewer` on a `--model` override. Added 2026-09-07. `/dev:build` is a **command rather than an agent** because `..\CONSTITUTION.md` Article VI.2 and `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH: "1"` make a "dev-lead" agent structurally impossible — orchestration only runs in the main session. Its safety model is three stops: an unapproved plan, anything irreversible, and repeated failure (two consecutive blocked tasks). It owns `PLAN.md`'s `Status` column exclusively, so implementer dispatches never race it. |

---

## When authoring a new agent, skill, or command

Prefer running `/agent-builder` over applying this section by hand — it implements the same rules
interactively and stays current as they evolve; this section is the reference, not the primary workflow.

1. Walk `AGENT-TEMPLATE-BASELINE.md` first — frontmatter fields, section skeleton, tone — before writing
   a line of the agent/command itself, so structure doesn't drift file to file. For a skill, the
   equivalent conventions (no XML tags, `description`-as-trigger, folder shape) live directly in
   `commands\agent-builder.md`'s own `draft` step — no separate `SKILL-BASELINE.md` yet (see that file's
   `consult-conventions` step for the threshold on when one would get created).
2. If it touches how a **target codebase** should be structured → walk `..\DESIGN-PRINCIPLES-BASELINE.md`
   against the project (informed by `solution-analyst`'s "Conventions Observed" output, if available) to
   produce that project's `ai/context/design-principles.md`.
3. Walk `..\AGENT-CONDUCT-BASELINE.md` — Executor section for an agent that does work, Reviewer section for
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
   human must act on), follow `..\AGENT-CONDUCT-BASELINE.md` B7/B9 for the verdict-block and
   freshness-hash conventions — don't invent a new verdict shape per agent.
6. Once a command namespace (a `commands\<prefix>\` folder) accumulates more than a handful of commands,
   add a `<prefix>:help` command whose only job is to print a static reference of that namespace — no
   live analysis, no project context, just the reference (mirrors the sample framework's
   `commands/sa/help.md`). `sa:` and `dev:` both have one; keep it updated when a command is added.
7. Any agent named `dev-*` reads `..\dev-framework\PRINCIPLES.md` first (after `..\CONSTITUTION.md`) —
   that's where the family's shared operational rules live; don't restate them in the agent's own
   `<rules>`.

## Rollout

1. Draft under `agents\` or `commands\` here (or the shared `..\skills\` for new reusable work).
2. Manual review.
3. Copy to **every** live config location — not just one. This machine has **three independent Claude
   Code config roots**, discovered the hard way on 2026-08-10 when `dev-backend` was "not found" in a
   real session despite being correctly rolled out to `~\.claude\`: the default/legacy location
   (`$env:USERPROFILE\.claude\`) **and** two profiles (`claude-scm`, `claude-nsz`, under
   `$env:LOCALAPPDATA\`), each fully redirected via `CLAUDE_CONFIG_DIR` and **not** falling back to the
   default. Real sessions run under a profile — rolling out to only the default silently leaves both real
   profiles without any of this.
   ```powershell
   # Run from the repo root (one level up from claude\). Pre-create destination folders first —
   # Copy-Item with -Recurse onto a not-yet-existing destination can silently mis-create it as a copy
   # of the *first* source item's contents instead of a proper container (hit this for real on
   # 2026-08-10 with skills\ — left a stray SKILL.md sitting loose in the destination instead of in its
   # own subfolder). Always ensure the target exists as a real directory first, every time.
   $destinations = @(
       "$env:USERPROFILE\.claude",
       "$env:LOCALAPPDATA\claude-scm",
       "$env:LOCALAPPDATA\claude-nsz"
   )
   foreach ($dest in $destinations) {
       New-Item -ItemType Directory -Path "$dest\agents"   -Force | Out-Null
       New-Item -ItemType Directory -Path "$dest\skills"   -Force | Out-Null
       New-Item -ItemType Directory -Path "$dest\commands" -Force | Out-Null

       Copy-Item claude\agents\*.md          "$dest\agents\"   -Force
       Copy-Item skills\*                    "$dest\skills\"   -Recurse -Force
       Copy-Item claude\commands\*           "$dest\commands\" -Recurse -Force
       Copy-Item AGENT-CONDUCT-BASELINE.md, DESIGN-PRINCIPLES-BASELINE.md   "$dest\" -Force
       Copy-Item claude\AGENT-TEMPLATE-BASELINE.md   "$dest\" -Force
       Copy-Item CONSTITUTION.md             "$dest\"          -Force
       Copy-Item dev-framework               "$dest\" -Recurse -Force
       Copy-Item sa-framework                "$dest\" -Recurse -Force
   }
   ```
   `estimation-data\rates.yaml` is deliberately **not** copied by the loop above — it's commercially
   sensitive and lives only at `~\.claude\estimation-data\rates.yaml`, created once by hand from
   `rates.yaml.example`:
   ```powershell
   New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\estimation-data" | Out-Null
   Copy-Item estimation-data\rates.yaml.example `
             "$env:USERPROFILE\.claude\estimation-data\rates.yaml"   # then edit
   ```

   `document-data\` (brand templates + the profile map `/sa:package` reads, `..\sa-framework\
   ARTIFACT-SCHEMAS.md` §8) is gitignored for the same reason but **does** need to reach every root, since
   any profile can be used from any of them. Unlike the rate card, the repo copy at
   `d:\_AI_GIT\document-data\` is the canonical one — gitignored, but present and backed up with the repo —
   and the three roots are derived from it. **Edit it there, then re-run this loop**; editing a root's copy
   directly means the next rollout overwrites it. It's a separate loop from step 3's only because
   `$destinations` needs re-declaring if you run it on its own:
   ```powershell
   foreach ($dest in $destinations) {
       New-Item -ItemType Directory -Path "$dest\document-data\templates" -Force | Out-Null
       Copy-Item document-data\templates.yaml   "$dest\document-data\" -Force
       Copy-Item document-data\templates\*.docx "$dest\document-data\templates\" -Force
   }
   ```
   Not checked by `check-sync.ps1` — like `estimation-data\` and `framework-data\`, it sits outside the
   compared folders on purpose, so a live-only file isn't reported as `EXTRA` forever. The cost is that
   drift here is invisible to tooling: **if you edit a template or a profile, re-run this loop by hand.**
4. Merge `CLAUDE.md` into **each** destination's own `CLAUDE.md` by hand (create it if missing) — do
   **not** blind-copy with `-Force`, since a real `CLAUDE.md` at any of the three may already carry
   personal notes this would clobber.
5. After any future edit here, re-run step 3 (and re-check step 4) so every destination picks up the
   change — this repo is the source of truth, none of the three destinations are, individually or
   together.
6. Run `powershell -File ..\_scripts\check-sync.ps1` (from `claude\`, or `_scripts\check-sync.ps1` from
   the repo root) to confirm — reports anything staged here that's missing or stale, **per destination**,
   all three checked every run. This caught two real gaps on 2026-08-10: the `skills\*` copy step didn't
   exist in step 3 at first (nothing reached any `skills\` folder), and step 3 only ever targeted the
   default location, silently leaving both real profiles completely empty the entire time — run it after
   every rollout, not just when something seems off, and don't assume "in sync" for one destination means
   any of the others are too.

**One-time setup**: run `powershell -File ..\_scripts\install-hooks.ps1` once (and again after a fresh
clone, or after pulling a change to `..\_scripts\hooks\`) — installs a `post-commit` hook that auto-runs
step 6 after every commit, so drift surfaces immediately instead of whenever someone remembers to check.
Informational only: it never blocks a commit and never auto-copies to `~\.claude\` — step 3 stays a
deliberate, explicit action.

Every hook run also appends its output to `..\_scripts\sync-check.log` (gitignored — runtime state, not
repo content), timestamped and tagged with the commit it ran after — check that file if you want to
confirm the hook actually fired and what it found, rather than relying on having seen it scroll by live
in the terminal.
