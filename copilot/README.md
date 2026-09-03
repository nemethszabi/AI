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
- **Done 2026-09-03** — `COPILOT_CUSTOM_INSTRUCTIONS_DIRS` (permanent, user-level) set to
  `%USERPROFILE%\.copilot` via `setx`, approved explicitly. Requires a new terminal to take effect (`setx`
  doesn't affect already-open shells). The exact multi-file-per-dir discovery behavior still hasn't been
  independently observed working end-to-end — worth a real check (open a fresh terminal, run `copilot` from
  outside `_AI_GIT`, confirm it's actually reading the doctrine) next time Copilot CLI is used for real.
- **Partially done 2026-09-03** — confirmed via `copilot mcp --help` that `~/.copilot/mcp-config.json` is
  indeed the right location (the earlier assumption held; `~/.copilot/servers/` was something else, unused
  here). Added `azure-devops-geomant` only (`copilot mcp add azure-devops-geomant --env ... --
  npx -y @tiberriver256/mcp-server-azure-devops`, values read straight from Claude's own
  `azure-devops-geomant` entry — same org URL, PAT, auth method), verified via `copilot mcp get
  azure-devops-geomant` (Status: Enabled). Deliberately **not yet done**: `azure-devops-netsolve`,
  Playwright, draw.io, sequential-thinking, filesystem — scoped down to Geomant only for now, add the rest
  the same way (`copilot mcp add <name> --env KEY=VALUE ... -- <command> [args...]`) when actually needed.
