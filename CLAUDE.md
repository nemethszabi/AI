# Global Instructions

Pointers only — the actual rules live in the files below, not here. Kept thin on purpose so it stays
readable every session; never inline the doctrine itself in this file.

## Global doctrine
- Hard rules: read `~/.claude/CONSTITUTION.md` first, every session — overrides everything else.
- Agent conduct reference: `~/.claude/AGENT-CONDUCT-BASELINE.md`
- Design principles reference: `~/.claude/DESIGN-PRINCIPLES-BASELINE.md`
- Agent/command file-shape reference: `~/.claude/AGENT-TEMPLATE-BASELINE.md`

## dev-* agent family
- Every `dev-*` agent follows `~/.claude/dev-framework/PRINCIPLES.md`.
- Why it's shaped this way, the `ai/dev/` state schema, and non-goals: `~/.claude/dev-framework/DESIGN.md`.

## req-* agent family / `sa:` pipeline (requirement → offer)
- Artifact data contract (JSON + rendered Markdown, IDs, lanes, the packaging gate):
  `~/.claude/sa-framework/ARTIFACT-SCHEMAS.md`.
- How estimates are derived (PERT, compression factors, contingency, calibration gate, pricing
  separation): `~/.claude/sa-framework/ESTIMATION-METHOD.md`.
- Both are **binding** on every `req-*` agent, read after `CONSTITUTION.md`.
- Workflow walkthrough and design rationale: `d:\_AI_GIT\docs\SA-WORKFLOW.md`. Quick reference: `/sa:help`.

## Getting started / usage reference
- First time using these agents? Read `d:\_AI_GIT\docs\GETTING-STARTED.md`.
- Full "which command for which situation" map: `d:\_AI_GIT\docs\USAGE.md`.
- Install/troubleshooting: `d:\_AI_GIT\docs\SETUP.md`.

Project-specific facts and rules live in each project's own `ai/context/` and `.claude/` — never here.
