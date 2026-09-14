# `copilot\skills\` — Copilot-only skills

Cross-tool skills live in the shared `..\..\skills\` (the open `SKILL.md` standard both Claude Code and
Copilot CLI read natively). This folder holds only what is genuinely Copilot-specific.

| Skill | Why it is Copilot-only |
|---|---|
| `sa-pipeline\SKILL.md` | The command layer for the `sa:` pipeline. On the Claude side that layer is 19 slash commands under `..\..\claude\commands\sa\`; here it is one skill, because `~/.copilot/commands/` has **no documented discovery behaviour** (absent from every `copilot --help` / `help commands` / `help config` output as of v1.0.82, re-checked unchanged at v1.0.83 on 2026-09-14) and building 19 step files on an unverified mechanism would produce a pipeline that silently does not exist. The file itself records this. Dispatch syntax, session-level model switching, and the two places this tool cannot match the Claude side are all Copilot-specific, so it could not be shared even if the mechanism matched. |
| `handoff\SKILL.md` | Copilot sibling of Claude's `/handoff` command (2026-09-14). The contract is shared — `..\..\dev-framework\HANDOFF.md` — so handoff files move between tools; this skill holds only the Copilot mechanics (plain-text numbered question instead of `AskUserQuestion`, `Remove-Item -LiteralPath`, `Get-Date` fallback). Copilot-only as a file because Claude's side is a legacy command with `AskUserQuestion`, and a shared skill of the same name would collide with it there. |

**What `sa-pipeline` deliberately does *not* contain**: the pipeline contract itself. Preconditions,
dispatch targets, artifacts, state transitions and the gate rules live once in
`..\..\sa-framework\PIPELINE.md`, shared byte-for-byte with the Claude side and cited rather than restated.
That file exists precisely because this port would otherwise have doubled 19 files of duplicated contract
into 38.

Shared skills currently rolled out here: `doc-brief`, `office-doc-builder`, `office-doc-reader`,
`prompt-builder`, `review-agent`. `framework-review` is deliberately **not** rolled out — it dispatches
`framework-strategist`, which is Claude-side only, so it would produce a command that dispatches an agent
that does not exist. `_scripts\check-sync.ps1` carries that exclusion in `$copilotNotPorted`.
