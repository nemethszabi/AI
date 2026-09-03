# `copilot/` — GitHub Copilot CLI branch (doctrine-only scaffold)

The Copilot CLI branch of `_AI_GIT`, sibling to `..\claude\`. **Currently a doctrine-only scaffold**: the
shared doctrine (`..\CONSTITUTION.md`, both remaining baselines, `..\dev-framework\`, `..\sa-framework\`,
`..\skills\`) is made legible to Copilot CLI via the files here, but no `req-*`/`sa:` agent has actually
been ported — `agents\` and `skills\` below are empty stubs. That's a deliberate, separate scope decision
(you're using Claude Code as the default/preferred tool today), not an oversight.

## Repository layout

| Path | What it is |
|---|---|
| `README.md` | This file — human-facing documentation of the branch. |
| `AGENTS.md` | **Machine-facing** — the file Copilot CLI itself reads as its always-loaded pointer, merged into `~/.copilot/AGENTS.md`. Same spirit as `..\claude\CLAUDE.md`, distinct purpose from this README. |
| `AGENT-TEMPLATE-BASELINE.md` | `.agent.md`/`SKILL.md` frontmatter shapes, install locations, and a Claude-tool-name → Copilot-tool-name mapping table — the reference for porting a Claude agent later. |
| `agents\` | Empty — stub `README.md` only. Would hold `.agent.md` twins of `..\claude\agents\*.md` if a port is ever approved. |
| `skills\` | Empty — stub `README.md` only. `..\skills\` (shared, root-level) already covers cross-tool skills; anything here would be Copilot-only. |

## Why doctrine-only, for now

Copilot CLI (`copilot`, v1.0.64+, standalone winget package) is a genuinely agentic CLI with real subagent
dispatch (`/fleet` + `@agent-name`) and native support for the open `SKILL.md` standard — so a full port is
possible in principle, not blocked by a tooling gap. It's deliberately not done yet because:

- Claude Code is, and will stay, the default/preferred tool for this pipeline.
- Porting the `/sa:*` pipeline (12 `req-*`-family agents, JSON artifact schemas, PERT estimation math, the
  `/sa:audit` blocking gate) is real, non-trivial work with an ongoing maintenance cost — every future edit
  to a Claude `req-*` agent would need a matching Copilot edit, or the two drift.
- `/sa:audit` as a **hard blocking gate** has no Copilot equivalent — Copilot has no "refuse to run without
  a fresh PASS" mechanism, so it would become a manual-discipline convention, a real capability loss.

Revisit this once there's a concrete near-term case for running actual `/sa:*` steps through Copilot, not
speculatively.

## Rollout — approved and run 2026-09-03

The steps below mirror `..\docs\SETUP.md`'s "Install — GitHub Copilot CLI" section exactly, so you land on
the same information starting from either file.

**Status**: approved and run 2026-09-03. `~/.copilot/` already existed as Copilot CLI's own live runtime
state (`session-store.db`, `config.json`, `servers/`, etc. — confirmed empty/no pre-existing doctrine
before copying, so this was a clean additive copy, nothing clobbered) — the doctrine files and
`copilot\AGENTS.md` now sit alongside that runtime state. Two pieces are **not** done yet:
- **`COPILOT_CUSTOM_INSTRUCTIONS_DIRS`** — blocked by the permission classifier as a permanent
  shell-environment change that hadn't been separately confirmed (this file's own "unverified, check at
  install time" flag turned out to matter). Needs an explicit go-ahead before it's set.
- **MCP server wiring** — not attempted yet. `~/.copilot/servers/` exists and is empty; the exact file
  shape Copilot CLI expects there (vs. a single `mcp-config.json`, as first assumed) wasn't confirmed
  before this scaffold was built, so this needs a quick check against current `copilot mcp --help` output
  before wiring anything in.

- **Destination**: `~/.copilot/` (global/personal). Confirmed: `COPILOT_HOME` is the direct analog of
  Claude Code's `CLAUDE_CONFIG_DIR` — so if a second Copilot identity is ever added, the same
  `copilot-work`/`copilot-personal` PowerShell-function-per-identity pattern already used for Claude drops
  in unchanged. Today there's one Copilot login, so one destination.
  ```powershell
  # Run from the repo root. Pre-create destinations first, same reasoning as the Claude rollout.
  $copilotDest = "$env:USERPROFILE\.copilot"
  New-Item -ItemType Directory -Path "$copilotDest\agents" -Force | Out-Null
  New-Item -ItemType Directory -Path "$copilotDest\skills" -Force | Out-Null

  Copy-Item copilot\agents\*.agent.md   "$copilotDest\agents\" -Force -ErrorAction SilentlyContinue
  Copy-Item copilot\skills\*            "$copilotDest\skills\" -Recurse -Force -ErrorAction SilentlyContinue
  Copy-Item skills\*                    "$copilotDest\skills\" -Recurse -Force
  Copy-Item AGENT-CONDUCT-BASELINE.md, DESIGN-PRINCIPLES-BASELINE.md   "$copilotDest\" -Force
  Copy-Item copilot\AGENT-TEMPLATE-BASELINE.md   "$copilotDest\" -Force
  Copy-Item CONSTITUTION.md             "$copilotDest\" -Force
  Copy-Item dev-framework               "$copilotDest\" -Recurse -Force
  Copy-Item sa-framework                "$copilotDest\" -Recurse -Force
  ```
- **Done** — merged `copilot\AGENTS.md` into `~/.copilot/AGENTS.md` (no pre-existing file there, so this
  was a plain copy, not an actual merge).
- **Not yet done — needs a separate go-ahead**: set `COPILOT_CUSTOM_INSTRUCTIONS_DIRS` (user env var) to
  include `~/.copilot/` so the doctrine is visible regardless of which project you're in. Copilot's
  custom-instructions loading is scoped to git root / cwd / this env var — there's no single
  always-loaded global file the way `~\.claude\CLAUDE.md` works — and the exact multi-file-per-dir
  discovery behavior still hasn't been independently confirmed beyond the CLI's own `--help` text. Blocked
  by the permission classifier on 2026-09-03 as a permanent environment change; run
  `setx COPILOT_CUSTOM_INSTRUCTIONS_DIRS "$env:USERPROFILE\.copilot"` yourself, or approve it explicitly.
- **Not yet done**: wire the same MCP servers already configured for Claude Code (Azure DevOps ×2,
  Playwright, draw.io, sequential-thinking, filesystem) into Copilot's MCP config. `~/.copilot/servers/`
  exists and is empty; confirm its expected file shape against current `copilot mcp --help` before wiring
  anything in — this doc originally assumed a single `~/.copilot/mcp-config.json`, unconfirmed. Genuine
  shared capability, not just a doc convention, since Copilot CLI supports MCP natively.
