# `copilot/` — GitHub Copilot CLI branch

The Copilot CLI branch of `_AI_GIT`, sibling to `..\claude\`. **As of 2026-09-07 this is a full-pipeline
branch, not a doctrine-only scaffold**: the shared doctrine plus 17 agents and the `sa:` pipeline's command
layer are live at `~/.copilot/`.

The design target is *"share the method, separate the mechanics"*: `CONSTITUTION.md`, both baselines and
`..\sa-framework\` are **one set of files copied to two roots** — never forks — while agents and commands
are tool-native siblings, because the two tools' formats and dispatch mechanics are genuinely
incompatible and pretending otherwise produces files that work on neither.

## Repository layout

| Path | What it is |
|---|---|
| `README.md` | This file — human-facing documentation of the branch. |
| `AGENTS.md` | **Machine-facing** — Copilot CLI's always-loaded pointer, merged into `~/.copilot/AGENTS.md`. Same spirit as `..\claude\CLAUDE.md`, distinct purpose from this README. |
| `AGENT-TEMPLATE-BASELINE.md` | `.agent.md`/`SKILL.md` shapes, the **verified** tool-name mapping, the fields Copilot lacks and what each costs, and the porting checklist. Re-verified against v1.0.82 on 2026-09-07. |
| `PORT-NOTES.md` | **Read once.** The six standing divergences that apply to every ported `req-*` agent and to the whole `sa:` pipeline. Not repeated per file — a divergence documented in fourteen places gets corrected in fourteen inconsistent ways. |
| `agents\` | 17 `.agent.md` files. Siblings of `..\claude\agents\*.md`, each naming its original and marking `[Copilot]` divergences. See that folder's `README.md` for the inventory and what is deliberately absent. |
| `skills\` | Copilot-only skills — chiefly `sa-pipeline\SKILL.md`, this branch's command layer, and `handoff\SKILL.md` (2026-09-14). Cross-tool skills live in the shared `..\skills\`. |
| `hooks\` | User-level hook files for `~/.copilot/hooks/` — `framework-change-flag.json` (2026-09-14). See **Hooks** below. |
| `commands\` | One legacy file, kept but **not built on** — see the warning below. |
| `scripts\` | Copilot usage-tracking PowerShell. Repo-side only, not rolled out. |

## What is shared, and what is not

| Layer | Shared? | Why |
|---|---|---|
| `CONSTITUTION.md`, `AGENT-CONDUCT-BASELINE.md`, `DESIGN-PRINCIPLES-BASELINE.md` | **Shared, byte-identical** | Prose doctrine. Both tools' agents read it as-is. |
| `sa-framework\ARTIFACT-SCHEMAS.md`, `ESTIMATION-METHOD.md`, `PIPELINE.md` | **Shared, byte-identical** | The artifact schema, the estimation method, and the pipeline contract are statements about the *work*, not about a tool. `PIPELINE.md` was extracted during this port precisely so 19 command files did not become 38. |
| `skills\` (root) | **Shared** | `SKILL.md` is an open cross-tool standard; both tools read it natively. |
| Agents | **Separate siblings** | XML-tag sections vs Markdown headings; `tools: Read, Write` vs `tools: [write]`; `disallowedTools`/`effort`/`memory` exist on one side only. |
| Command layer | **Separate, and differently shaped** | 19 slash commands on Claude; **one skill** here — see below. |
| `document-data\` | **Not rolled out to this root** | Consumed by `/sa:package`, which is where binding deliverables should be built anyway. `skills\sa-pipeline\SKILL.md` therefore tries `~/.copilot/document-data/templates.yaml` first and **falls back to `d:/_AI_GIT/document-data/templates.yaml`**, saying which it used. That fallback is the live path here — do not "simplify" it away. |

## The command layer is a skill, not commands

`~/.copilot/commands/*.md` has **no documented discovery behaviour** — it appears in no `copilot --help`,
`copilot help commands` or `copilot help config` output as of v1.0.82, and the built-in `/usage` would
shadow the one file staged there in 2026-09-03 regardless. That file predates the check and is kept only so
its removal is a deliberate act rather than a side effect.

So the `sa:` pipeline's 19 steps live in **`skills\sa-pipeline\SKILL.md`**, a documented and verified
mechanism. Nineteen step files built on an unverified discovery path would produce a pipeline that silently
does not exist, which is worse than a differently-shaped one that works. If custom commands are later
confirmed, splitting that skill is mechanical.

## Session handoffs — the same files as Claude Code

`skills\handoff\SKILL.md` (2026-09-14) is the Copilot sibling of Claude's `/handoff` v2.1.0. Both implement
the shared contract `..\dev-framework\HANDOFF.md` — name, structure, `Status` lifecycle, deletion rule — so a
handoff written in one tool is resumed and closed in the other; `ai/handoff/` is project-scoped like
`ai/sa/<slug>/`. Invoke with `/handoff`, `/handoff resume <file>`, `/handoff list`, `/handoff close` in the
prompt. Copilot-side divergences, all marked `[Copilot]` in the skill: plain-text numbered question instead
of `AskUserQuestion` (D4 — silence means *Keep*), `Remove-Item -LiteralPath` instead of `rm`, and `Get-Date`
allowed when the session has no clock.

## Hooks

Copilot CLI loads user-level hooks from `~/.copilot/hooks/*.json` (`{"version": 1, "hooks": {...}}`), and
repo-level ones from `.github/hooks/*.json` **and from inline `hooks` in a repo's `.claude/settings.json`** —
so a project's Claude hooks may already run under Copilot. Source: GitHub's hooks configuration reference
and `copilot help config` (v1.0.83), read 2026-09-14; loading **confirmed live 2026-09-14** — `/env`
lists `postToolUse: 1 hook (sources: ~\.copilot\hooks\framework-change-flag.json)`. The reminder firing on a
real edit has not been seen yet (the script is dry-run tested). The same `/env` check found `doc-briefer`
missing — a YAML frontmatter error, fixed; see `AGENT-TEMPLATE-BASELINE.md` porting checklist item 1.

| Hook file | Event | What it does |
|---|---|---|
| `hooks\framework-change-flag.json` | `postToolUse` | Runs the **same** `..\_scripts\hooks\framework-change-flag.py` the Claude roots use. The script detects Copilot's camelCase payload (`toolName`/`toolArgs`/`sessionId`), counts only `edit`/`create`/`write` (Copilot's `view` also carries a path), and injects a one-time `additionalContext` asking to stage the change in `_AI_GIT` and finish with `/doc-sync` **from Claude Code**. Written after 2026-09-12 found ~600 lines of doctrine that had existed only at this root. Dry-run tested with simulated payloads 2026-09-14. |

The hook file names the absolute script path `D:/_AI_GIT/...` — machine-specific by necessity, the same as
the Claude `settings.json` wiring.

## Not ported, deliberately

Recorded so a future review or sync check reads the absence as intent, not drift (the `framework-review`
lesson below):

| Claude-side piece | Why not here |
|---|---|
| `/doc-sync` | Framework upkeep — docs, rollout, commit+push, backup against `_AI_GIT` — is done from Claude Code. The Copilot hook above points there instead of duplicating a four-gate command on an unverified command mechanism. |
| `context_guard.py` (`UserPromptSubmit`) | Reads Claude's transcript format for context size. Copilot's `userPromptSubmitted` payload carries no transcript path, and `/context` is built in. Revisit if Copilot's `statusLine` JSON proves to carry context size. |
| `statusline.py` | Same — Claude transcript/`rate_limits` fields. Copilot has its own `statusLine` setting; not investigated. |
| "Handoff before compaction" (`PreCompact`) | Proposed Claude-side only. On Copilot `preCompact` hook output is ignored, so it could not remind anyone. |
| `dev-*`, `solution-analyst`, `framework-strategist`, `framework-review` | Standing scope decision — see `agents\README.md` and *Skills deliberately not ported* below. |

## The two things this tool genuinely cannot do

Recorded prominently because both were reasons this port was deferred, and neither has gone away — they are
now *handled*, not solved.

1. **The packaging gate cannot refuse.** `/sa:package` on the Claude side refuses to build without two
   fresh passing verdicts. Copilot CLI has no mechanism by which a skill can hard-stop a session told to
   continue. The skill therefore performs every check, prints a prominent **STOP** block on failure, and
   **calls itself an advisory check rather than a gate** — because a gate that looks like a gate and isn't
   produces the confidence of enforcement with none of the substance. **Run packaging in Claude Code for
   anything commercially binding.** (`PORT-NOTES.md` D6, `..\sa-framework\PIPELINE.md §3`.)
2. **Read-only cannot be enforced structurally.** No `disallowedTools`, no scoped grants. Mitigated by
   granting `write` without `shell` to every read-only role, which is the half that *is* enforceable, and
   by stating the rest as rules. `req-auditor` is the sharpest case: its Claude sibling holds a shell grant
   scoped to hashing; here it holds full `shell` and a written narrowing. (`PORT-NOTES.md` D2.)

A third divergence is milder but bites daily: **model selection is session-level**, so the cross-model
review rule (`ARTIFACT-SCHEMAS.md §9`) is satisfied by `/model` *before* dispatching, not by a per-dispatch
parameter. (`PORT-NOTES.md` D5 — which since v1.0.83 also records the per-agent `subagents.agents.<name>`
config setting as a candidate, not-yet-adopted alternative.)

## Why the port happened

The 2026-09-03 scaffold deferred it on three grounds. Two were overtaken:

| Original reason | Status |
|---|---|
| "Claude Code is and will stay the default tool" | **Still true**, and unchanged by this. Copilot now has the same capability; which tool you reach for is a separate question. |
| "Porting is real work with an ongoing maintenance cost — every future edit to a Claude `req-*` agent needs a matching Copilot edit, or the two drift" | **Still true and still unmitigated by tooling.** Reduced, not removed: extracting `PIPELINE.md` moved the most drift-prone content (preconditions, gate rules, state transitions) into one shared file both sides cite. What remains duplicated is each agent's own process prose. |
| "`/sa:audit` as a hard blocking gate has no Copilot equivalent" | **Confirmed true** — and now handled explicitly rather than used as a reason not to start. See above. |

The decisive argument for porting was **engagement portability**: `ai/sa/<slug>/` is project-scoped and
conforms to one shared schema, so an engagement triaged in Claude Code can be clarified in Copilot CLI and
packaged back in Claude Code. That only works if both sides implement the same contract, which is what
`PIPELINE.md §5`'s conformance checklist now defines.

## Rollout

**Status**: doctrine rolled out 2026-09-03; full pipeline rolled out 2026-09-07; `handoff` skill,
`HANDOFF.md` and the `framework-change-flag` hook rolled out 2026-09-14.

```powershell
# Run from the repo root.
$copilotDest = "$env:USERPROFILE\.copilot"
New-Item -ItemType Directory -Path "$copilotDest\agents" -Force | Out-Null
New-Item -ItemType Directory -Path "$copilotDest\skills" -Force | Out-Null
New-Item -ItemType Directory -Path "$copilotDest\hooks"  -Force | Out-Null

Copy-Item copilot\agents\*.agent.md   "$copilotDest\agents\" -Force
Copy-Item copilot\skills\*            "$copilotDest\skills\" -Recurse -Force
Copy-Item copilot\hooks\*.json        "$copilotDest\hooks\"  -Force
Copy-Item skills\*                    "$copilotDest\skills\" -Recurse -Force
# ...then remove the skills deliberately NOT ported (see the table below):
Remove-Item "$copilotDest\skills\framework-review" -Recurse -Force -ErrorAction SilentlyContinue
Copy-Item AGENT-CONDUCT-BASELINE.md, DESIGN-PRINCIPLES-BASELINE.md "$copilotDest\" -Force
Copy-Item copilot\AGENT-TEMPLATE-BASELINE.md, copilot\PORT-NOTES.md, copilot\AGENTS.md "$copilotDest\" -Force
Copy-Item CONSTITUTION.md             "$copilotDest\" -Force
Copy-Item dev-framework               "$copilotDest\" -Recurse -Force
Copy-Item sa-framework                "$copilotDest\" -Recurse -Force
```

`copilot\agents\README.md` and `copilot\scripts\` are repo-side documentation, not part of the rollout;
`check-sync.ps1` excludes them.

**Why `dev-framework\` is copied here when no `dev-*` agent is.** The `dev-*` family and the `/dev:*`
namespace are absent from this root by standing scope decision — that includes `dev-scaffolder`,
`dev-planner` and `dev-ui-analyst`, added Claude-side 2026-09-07, which inherit it. But the *doctrine*
folder is shared, tool-agnostic content and is copied here in full, `STACK-DOTNET.md` included. So the
files sit here describing agents this tool does not have.

That is deliberate, and it is the cheaper of the two errors: `check-sync.ps1` compares the folder
byte-for-byte, so excluding it would report `MISSING` forever and invite exactly the "fix" that broke
`framework-review` on 2026-09-07. Do **not** trim it. If the `dev-*` family is ever ported, the doctrine it
needs is already here.

### Skills deliberately not ported

`skills\*` is a blanket copy, so anything that must *not* land here has to be removed after it — the
`Remove-Item` line above, kept adjacent to the copy so the two never drift apart. `_scripts\check-sync.ps1`
carries the same list in `$copilotNotPorted` and will not report these as `MISSING`.

| Skill | Why not |
|---|---|
| `framework-review` | Thin dispatcher to `framework-strategist`, which is Claude-side only. Copied here it produces a command that dispatches an agent that does not exist. |

Learned the hard way on 2026-09-07: the first run of the new Copilot sync check reported this skill as
`MISSING`, it was rolled out to clear the finding, and that produced exactly the broken command the
2026-09-05 review had recommended avoiding. **A deliberate absence has to be recorded somewhere a tool
reads, or the next tool that notices it will "fix" it.** That lesson is why `agents\README.md` and
`PORT-NOTES.md` both carry explicit not-ported sections.

### Environment and MCP

- **Done 2026-09-03** — `COPILOT_CUSTOM_INSTRUCTIONS_DIRS` set to `%USERPROFILE%\.copilot` via `setx`
  (permanent, user-level; needs a new terminal). **The exact multi-file discovery behaviour still has not
  been observed working end to end** — worth a real check next time Copilot CLI is used for substantive
  work, and doubly so now that 17 agents depend on the doctrine actually being read.
- **Partially done 2026-09-03** — `~/.copilot/mcp-config.json` confirmed as the right location;
  `azure-devops-geomant` added and verified enabled. Deliberately not yet added: `azure-devops-netsolve`,
  Playwright, draw.io, sequential-thinking, filesystem.

## Maintenance — the standing obligation

**When a Claude original changes materially, its Copilot sibling needs the same change.** Nothing automated
enforces this: `check-sync.ps1` compares *staged versus live per tool*, never *Claude versus Copilot
parity*. The conformance checklist in `..\sa-framework\PIPELINE.md §5` is what a periodic
`/framework-review` should walk to catch divergence, and that is currently the only mechanism there is.
