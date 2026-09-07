# Copilot CLI — agent/skill file-shape reference

The `copilot\` branch's mirror of `..\claude\AGENT-TEMPLATE-BASELINE.md` — documents the **file shapes**
Copilot CLI actually reads. Governs shape, not behavior; pairs with the shared `..\AGENT-CONDUCT-BASELINE.md`
for conduct, the same split as the Claude side.

**Provenance**: verified against `copilot --version` (**v1.0.82**), `copilot --help`,
`copilot help commands`, `copilot help config` and the live `~/.copilot/` tree on **2026-09-07**, during the
`sa:` pipeline port. The 2026-09-03 scaffold recorded much of this as unverified guesswork; the rows below
now distinguish **verified** from **still unverified**, because a table that doesn't say which is which is
the reason a port gets built on an assumption.

---

## `.agent.md` — custom agents

- **Location** — `~/.copilot/agents/` (global) or `.github/agents/` (repo-scoped). **Verified**: 17 agents
  live at the global path and are selectable.
- **Frontmatter** — `name`, `description`, `tools` (YAML list), `model` (optional). **Verified**: the
  ported family uses exactly this.
- **Body** — plain Markdown headings. **Not** Claude's XML-tag sections. A Claude agent's
  `<role>`/`<process>`/`<rules>` *content* ports largely as-is; the tags become `# Role`, `# Process`,
  `# Rules`.
- **Dispatch** — `@agent-name` from an orchestrating session; `/agent [name]` selects one interactively;
  `/fleet` enables parallel subagent execution. **Verified** in `copilot help commands`.

### Tool names — verified

`~/.copilot/permissions-config.json` records approvals by **kind**, and the two kinds observed in the live
file are `write` and `commands`. In `.agent.md` frontmatter these are written:

| Claude tool | Copilot equivalent | Status |
|---|---|---|
| `Read`, `Grep`, `Glob` | *(implicit — no grant needed; every agent can read and search)* | Verified by the working ports |
| `Write` / `Edit` | `write` | **Verified** |
| `Bash` | `shell` | **Verified** |
| `Agent` (subagent dispatch) | `@agent-name` / `/fleet` | **Verified** |
| `AskUserQuestion` | **No equivalent, and none needed** | **Verified** — see below |
| MCP tools (`mcp__*`) | `~/.copilot/mcp-config.json` | **Verified** — `azure-devops-geomant` configured and enabled |

`AskUserQuestion`'s absence is not a gap to work around: a dispatched agent cannot ask on *either* tool
(on Claude the tool exists but is unavailable inside a subagent). The contract is identical — proceed on
the least-committal reading, record the question in the artifact, repeat blocking ones under
`## Blocking questions`, and let the dispatching layer raise them. See `PORT-NOTES.md` D4.

### Fields Copilot does NOT have — and what each costs

The Claude side's `AGENT-TEMPLATE-BASELINE.md` §1a builds real enforcement out of frontmatter fields. Most
have no Copilot equivalent, so a rule that is *structural* there is *instructional* here. Say so in the
agent rather than letting the reader assume parity:

| Claude field | Copilot | What is lost |
|---|---|---|
| `disallowedTools` | **absent** | A read-only agent's promise cannot be enforced by a deny-list. Mitigation: grant `write` only, no `shell`, and state the rule. See `PORT-NOTES.md` D2. |
| Scoped tool grants (`Bash(git hash-object:*)`) | **absent** | `shell` is all-or-nothing. `req-auditor` is the live casualty — its narrowing is a written rule here, not a grant. |
| `effort` | **absent** | No per-agent reasoning-depth control. |
| `memory` | **absent** | No cross-session agent memory; state conventions in the artifact instead. |
| `model` per-dispatch | frontmatter `model` exists, but selection is **session-level** (`/model`) | The cross-model review rule (`ARTIFACT-SCHEMAS.md §9`) is satisfied by switching the session before dispatching. `PORT-NOTES.md` D5. |
| `permissionMode`, `maxTurns`, `hooks`, `isolation` | **absent** | No per-agent circuit-breakers or lifecycle hooks. |

## `SKILL.md` — skills

- **Open, cross-tool standard** (agentskills.io). Claude Code and Copilot CLI both read it natively; each
  ignores frontmatter extras it doesn't recognize. **Verified** — five shared skill folders are live at
  `~/.copilot/skills/` and work unmodified.
- **Location** — `~/.copilot/skills/<name>/SKILL.md` (global) or `.github/skills/`. **Verified.**
- **Frontmatter** — `name`, `description`. No `tools:`/`allowed-tools:` in the open spec, so a skill carries
  no enforced tool allowlist on either tool.
- **Managed via** `/skills`. **Verified** in `copilot help commands`.

## `commands\` — **still unverified, and treat it as unsupported**

`~/.copilot/commands/*.md` appears in **no** `copilot --help`, `copilot help commands` or
`copilot help config` output as of v1.0.82. One file (`usage.md`) was staged there in the 2026-09-03
scaffold on the assumption it worked; that assumption has never been confirmed, and the built-in `/usage`
command would shadow it regardless.

**Do not build on this mechanism.** The `sa:` pipeline's command layer is a skill
(`copilot\skills\sa-pipeline\SKILL.md`) for exactly this reason — nineteen step files on an unverified
discovery path would produce a pipeline that silently does not exist. If custom commands are later
confirmed, splitting that skill is mechanical.

## Always-loaded instructions

`~/.copilot/AGENTS.md` is Copilot CLI's analog of `CLAUDE.md` — the thin, always-loaded pointer file.
`COPILOT_CUSTOM_INSTRUCTIONS_DIRS` (set to `%USERPROFILE%\.copilot` on 2026-09-03) governs which
directories are read; the exact multi-file discovery behaviour **has still not been observed working
end to end** and is worth a real check next time Copilot CLI is used for substantive work.

---

## Porting checklist

Walk this when bringing a Claude agent across. Conformance target for the `sa:` family:
`..\sa-framework\PIPELINE.md §5`.

1. **Frontmatter** — `name`, `description`, `tools` (minimum the role needs; `write` only for read-only
   roles). Drop every field from the "does not have" table above.
2. **Tags → headings** — `<role>` → `# Role`, and so on.
3. **Paths** — `~/.claude/` → `~/.copilot/` throughout. Engagement artifacts (`ai/sa/<slug>/`) stay put:
   they are project-scoped and shared between tools.
4. **Header block** — name the Claude original, its version, and the port date. State that they are
   siblings, not a copy and its cache.
5. **Mark `[Copilot]` divergences inline**, but only those specific to that agent — the family-wide ones
   live once in `PORT-NOTES.md`.
6. **Re-check what the frontmatter used to enforce.** Every `disallowedTools`, scoped grant, `effort` or
   `memory` line on the Claude side is a promise that now needs a written rule and an honest note that it
   is weaker.
7. **Record the port** in `agents\README.md`'s inventory and in `README.md`'s status section.
