# AI — Generic Claude Code Agents & Commands

Staging and distribution source for generic, project-agnostic Claude Code agents, commands, and
doctrine baseline files. Files here are drafted, reviewed manually, then copied into
`~\.claude\agents\`, `~\.claude\commands\`, and `~\.claude\` respectively — nothing here is live/active
in Claude Code until that copy step happens.

Project-specific agents, commands, and context belong in each project's own repo (its own `.claude\` and
`ai\context\`), never here — see `DESIGN-PRINCIPLES-BASELINE.md`'s and `AGENT-CONDUCT-BASELINE.md`'s own
"how to use" sections for how generic and project-specific artifacts connect.

---

## Repository layout

| Path | What it is |
|---|---|
| `CLAUDE.md` | Thin, always-loaded pointer block — merge into `~\.claude\CLAUDE.md` manually (never blind-overwrite; you may already have personal notes there). Points at the doctrine files below, doesn't inline them. |
| `CONSTITUTION.md` | **Binding**, global hard rules (secrets, destructive actions, gates, scope, tool permissions). Every generic agent reads this first. Not a checklist like the two below — this one is live doctrine. |
| `DESIGN-PRINCIPLES-BASELINE.md` | Checklist for drafting a **project's own** `ai/context/design-principles.md` — code/architecture principles (layering, DI, DTOs, isolation boundaries). Not itself binding on any project. |
| `AGENT-CONDUCT-BASELINE.md` | Checklist for drafting a **new agent's own** `<rules>` section — how an agent should behave while working (executor discipline) or while reviewing others' work (reviewer discipline). Not code-architecture rules — see the table in this file for the distinction. |
| `agents\` | Generic agent definitions, one file per agent, copied to `~\.claude\agents\` |
| `commands\` | Generic slash-command definitions, copied to `~\.claude\commands\` |

## Current inventory

| Agent | Purpose |
|---|---|
| `agents\solution-analyst.md` | Reads an unfamiliar solution/repo and drafts a first-pass `ai/context/<slug>-context.md` for human review. CREATE/UPDATE mode-aware. Generic across stacks and solution types. |

| Command | Purpose |
|---|---|
| `commands\scaffold-context.md` | `/scaffold-context [path]` — thin dispatcher to `solution-analyst` |

---

## When authoring a new agent or command

1. If it touches how a **target codebase** should be structured → walk `DESIGN-PRINCIPLES-BASELINE.md`
   against the project (informed by `solution-analyst`'s "Conventions Observed" output, if available) to
   produce that project's `ai/context/design-principles.md`.
2. Walk `AGENT-CONDUCT-BASELINE.md` — Executor section for an agent that does work, Reviewer section for
   an agent that checks others' work — and write the relevant instances directly into the new agent's
   own `<rules>` section.
3. Decide **generic vs. project-specific** before deciding where the file lives: does the agent's own
   text contain a fact that only makes sense inside one repo (an absolute path, an org name, a stack
   fact)? If yes, it belongs in that project's own `.claude\`, not here. See
   `d:\WORK\AI\results\claude-prompting-system-review.md §10` for the full decision rule and naming
   conventions (§13) — not duplicated in this repo to avoid the two drifting out of sync.
4. If the agent/command is a **gate or reviewer** (produces a PASS/FAIL-style verdict another command or
   human must act on), follow `AGENT-CONDUCT-BASELINE.md` B7/B9 for the verdict-block and freshness-hash
   conventions — don't invent a new verdict shape per agent.
5. Once a command namespace (a `commands\<prefix>\` folder) accumulates more than a handful of commands,
   add a `<prefix>:help` command whose only job is to print a static reference of that namespace — no
   live analysis, no project context, just the reference (mirrors the sample framework's
   `commands/sa/help.md`). Not needed yet at one command; noted here so it isn't forgotten once
   `commands\` grows.

## Rollout

1. Draft under `agents\` or `commands\` here.
2. Manual review.
3. Copy to global:
   ```powershell
   Copy-Item agents\*.md    "$env:USERPROFILE\.claude\agents\"   -Force
   Copy-Item commands\*.md  "$env:USERPROFILE\.claude\commands\" -Force
   Copy-Item *-BASELINE.md  "$env:USERPROFILE\.claude\"          -Force
   Copy-Item CONSTITUTION.md "$env:USERPROFILE\.claude\"         -Force
   ```
4. Merge `CLAUDE.md` into `~\.claude\CLAUDE.md` by hand (create it if missing) — do **not** blind-copy
   with `-Force`, since a real global `CLAUDE.md` may already carry personal notes this would clobber.
5. After any future edit here, re-run step 3 (and re-check step 4) so `~\.claude\` picks up the change —
   this repo is the source of truth, `~\.claude\` is a copy of it, not the other way around.
