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

## `req-*` agent family / `sa:` pipeline (requirement → offer)
- Artifact data contract, estimation method: `~/.copilot/sa-framework/ARTIFACT-SCHEMAS.md`,
  `~/.copilot/sa-framework/ESTIMATION-METHOD.md`. Binding wherever a `req-*` agent exists.
- **Current status**: no `req-*`/`sa:` agent has been ported to Copilot CLI yet — doctrine-only tier. See
  `~/.copilot/README.md` (or `d:\_AI_GIT\copilot\README.md`, the staged source) for why, and what porting
  would take.

## Getting started
- Repo source of truth (staged, not live): `d:\_AI_GIT\copilot\README.md`.
- Claude Code carries the full-fidelity version of this framework — `d:\_AI_GIT\claude\README.md` — if a
  question can't be answered from what's staged here.

Project-specific facts and rules live in each project's own `ai/context/` and `.github/` — never here.
