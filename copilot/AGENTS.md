Pointers only — the actual rules live in the files below, not here. Same spirit as `..\claude\CLAUDE.md`:
kept thin so it stays readable, never inline the doctrine itself in this file.

## Shared doctrine (applies to every AI tool on this machine, this one included)
- Hard rules: read `~/.copilot/CONSTITUTION.md` first, every session — overrides everything else.
- Agent conduct reference: `~/.copilot/AGENT-CONDUCT-BASELINE.md`
- Design principles reference: `~/.copilot/DESIGN-PRINCIPLES-BASELINE.md`
- Agent/skill file-shape reference (Copilot-specific): `~/.copilot/AGENT-TEMPLATE-BASELINE.md`

## `dev-*` agent family
- Every `dev-*` agent follows `~/.copilot/dev-framework/PRINCIPLES.md`.
- Why it's shaped this way, the `ai/dev/` state schema, and non-goals: `~/.copilot/dev-framework/DESIGN.md`.

## `req-*` agent family / `sa:` pipeline (requirement → offer) — **live here since 2026-09-07**
- **Run it via the `sa-pipeline` skill** — that is this tool's command layer (19 steps in one file), not a
  set of slash commands. It tells you which agent each step dispatches and what it must do before and after.
- Binding contracts, shared byte-for-byte with the Claude side and **cited, never restated**:
  `~/.copilot/sa-framework/PIPELINE.md` (sequence, preconditions, gate rules, conformance),
  `ARTIFACT-SCHEMAS.md` (artifact shape), `ESTIMATION-METHOD.md` (how numbers are derived).
- Standing divergences for the whole family: `~/.copilot/PORT-NOTES.md`. **Read it once before running any
  step** — six of them, and two change what you can rely on.
- Agents dispatch with `@agent-name`. The pipeline dispatches **fifteen** of them — thirteen `req-*` plus
  `doc-briefer` and `mermaid-diagram-maker`; seventeen `.agent.md` files are live at this root in total. See
  `d:\_AI_GIT\copilot\agents\README.md` for the inventory and what is deliberately absent.

## Session handoffs
- Context getting large, or stopping for the day: the **`handoff` skill** — `/handoff`, then `/clear`, then
  `/handoff resume <file>`; `/handoff list`, `/handoff close`. Contract: `~/.copilot/dev-framework/HANDOFF.md`.
- Files live in `<project>/ai/handoff/` and are the same files Claude Code's `/handoff` writes — either tool
  resumes the other's.

## Framework edits
- Change agents, skills, doctrine or hooks in `d:\_AI_GIT` (staged), **never only here at `~/.copilot`**.
  The `framework-change-flag` hook reminds once per session; finishing the change (docs, rollout,
  commit+push, backup) is `/doc-sync` in Claude Code — Copilot has no equivalent by decision.

## Two things this tool cannot do, and must not pretend to
- **Packaging cannot refuse.** The two-verdict gate is checked and reported here, but nothing stops a
  session told to continue. It is an **advisory check, never a gate**. Run packaging in Claude Code for
  anything commercially binding (`PORT-NOTES.md` D6).
- **Read-only cannot be enforced structurally** — no `disallowedTools`, no scoped tool grants. Read-only
  roles get `write` without `shell`, and the rest is a written rule (`PORT-NOTES.md` D2).

## Rules that bind every agent here, `sa:` or not
Two `AGENT-CONDUCT-BASELINE.md` sections added 2026-09-07 are **general agent conduct**, not `sa:`-pipeline
mechanics, so they apply to any work on this tool — including ad-hoc work with no agent file at all:
- **Section D — groundedness & slop.** Every factual claim is sourced, derived, assumed, or declared absent;
  there is no fifth kind. A *specific* unsourced detail (a version number, a percentage, a named capability)
  is the dangerous case, because specificity reads as evidence. Never invent content to complete a table,
  a section, or a list.
- **B10 — cross-model review.** An independent review runs on a different model than produced the work.
  Here that means `/model` **before** dispatching a checking agent — selection is session-level, not
  per-dispatch — and switching back afterwards. Same rule, same honest caveat: sibling models share
  training lineage, so this reduces correlated error rather than delivering independence.

## Getting started
- Repo source of truth (staged, not live): `d:\_AI_GIT\copilot\README.md`.
- Claude Code carries the full-fidelity version of this framework — `d:\_AI_GIT\claude\README.md` — if a
  question can't be answered from what's staged here.

Project-specific facts and rules live in each project's own `ai/context/` and `.github/` — never here.
