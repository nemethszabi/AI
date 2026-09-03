# Copilot CLI — agent/skill file-shape reference

The `copilot\` branch's mirror of `..\claude\AGENT-TEMPLATE-BASELINE.md` — documents the **file shapes**
Copilot CLI actually reads, so a future port of a Claude agent/skill has a concrete target instead of
guesswork. Governs shape, not behavior — pairs with the shared `..\AGENT-CONDUCT-BASELINE.md` for conduct,
same split as the Claude side.

**Provenance**: verified against `copilot --help`, `copilot help commands`, `copilot help config`, and
public docs during the design session that produced this scaffold (2026-09-03). Re-verify against a
current `copilot --help`/`copilot mcp --help` before relying on anything below past a few months old —
Copilot CLI has moved fast (the "no subagents" belief this repo held before 2026-09 was already stale by
the time it was checked).

## `.agent.md` — custom agents

- **Location**: `~/.copilot/agents/` (global/personal — the direct analog of `~\.claude\agents\`) or
  `.github/agents/` (repo-scoped, analog of a project's own `.claude\agents\`).
- **Frontmatter**: YAML — `name`, `description`, `tools` (list), `model` (optional). Structurally close to
  Claude Code's own agent frontmatter.
- **Body**: Markdown prose describing role/process/rules — a Claude agent's `<role>`/`<process>`/`<rules>`
  content is largely reusable text for a port, not a rewrite, modulo the tag-vs-heading convention (Copilot
  agents are plain Markdown headings, not Claude's XML-tag sections).
- **Dispatch**: an orchestrating Copilot session calls out to a named custom agent via `@agent-name` (or
  `/fleet` for multi-agent orchestration) as an isolated subagent — the rough equivalent of Claude's `Agent`
  tool.

## `SKILL.md` — skills

- **Open, cross-tool standard** (agentskills.io), not Copilot-specific — Claude Code and Copilot CLI both
  read it natively. A `SKILL.md` written for one works in the other essentially unmodified; each tool
  ignores frontmatter extras it doesn't recognize.
- **Location**: `~/.copilot/skills/` (global) or `.github/skills/` (repo-scoped) — confirm the exact
  personal-scope path against current `copilot help` output before first use; early research also surfaced
  `.agents/skills/` as a possible alternate, unconfirmed as of this writing.
- **Frontmatter**: `name`, `description`, `license` — no `tools:`/`allowed-tools:` field in the open spec
  itself (unlike a Claude Code *command*'s `allowed-tools:`), so a skill carries no enforced tool-allowlist
  on either tool.

## Claude tool name → Copilot tool name mapping

**Unverified — confirm each row against a current `copilot --help`/`copilot mcp --help` before authoring
anything that depends on it.** Recorded here as a starting point, not a settled fact:

| Claude tool | Copilot CLI equivalent (best known, unconfirmed) |
|---|---|
| `Read` | Copilot's built-in file-read capability |
| `Write` / `Edit` | Copilot's built-in file-write/edit capability |
| `Bash` | Copilot's shell/terminal execution capability |
| `Grep` / `Glob` | Copilot's built-in search/file-listing capability |
| `AskUserQuestion` | No confirmed direct equivalent — Copilot's interactive-mode prompting may or may not expose this to a dispatched agent; verify before porting any agent that relies on it |
| `Agent` (subagent dispatch) | `@agent-name` / `/fleet` |
| MCP tools (`mcp__*`) | Configured via `~/.copilot/mcp-config.json` — Copilot CLI supports MCP natively, same protocol as Claude Code |

## Why this file exists, and why it's this thin

Per the standing scope decision (`..\README.md`, `copilot\README.md`): the Copilot branch is a
**doctrine-only scaffold** right now — no `req-*`/`sa:` agent has actually been ported. This file exists so
that *if and when* a port is approved, the frontmatter shapes and tool mapping don't need to be
re-researched from scratch — not because a port is imminent.
