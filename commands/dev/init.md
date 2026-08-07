---
name: dev:init
description: Scaffold ai/dev/STATE.md + config.json for a project so dev-backend/dev-frontend/dev-reviewer can be dispatched against it.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Write
  - Bash
  - AskUserQuestion
argument-hint: "[path, optional - defaults to current directory]"
---

<objective>
`/dev:init [path]` scaffolds `ai/dev/STATE.md` + `ai/dev/config.json` for a project, following the
canonical schema in `~/.claude/dev-framework/DESIGN.md`. This is mechanical, reusable scaffolding — the
same two files, the same shape, every project — not a per-project bespoke step.
</objective>

<process>
<step name="resolve-target">
Target = `$ARGUMENTS` if given, else the current working directory. If `ai/dev/STATE.md` already exists
there, stop and say so — point to `/dev:status` instead of overwriting.
</step>

<step name="gather-facts">
Read `CLAUDE.md` and `ai/context/*.md` if present, for a one-line stack/project summary and to find the
project's primary knowledge file (for `context_doc`). Detect the current git branch via `Bash` for
`primary_branch`. Look for an obvious contracts location (a `*.Contracts`/`contracts`-named project or
folder, an OpenAPI/AsyncAPI file) for `contracts_path`; if none is obviously identifiable, use
`"N/A - <short reason>"` rather than guessing. Look for an obvious build command (a `.csproj`,
`package.json` script, etc.) for `build_command`; same fallback rule if unclear.
- If no `ai/context/*.md` exists at all, say so in the output and suggest running `/scaffold-context`
  first — proceed anyway if the human wants to, don't hard-block.
- Ask via `AskUserQuestion` only for something genuinely undeterminable from the repo (e.g. which of
  several plausible contracts locations is the real one) — don't ask about things you can reasonably
  detect or mark N/A.
</step>

<step name="write-state">
Write `ai/dev/STATE.md`:
```markdown
# Dev State — <Project>

## Phase
Just initialized — no task/wave structure yet.

## Source of truth
<context_doc path, and any other ai/context/*.md files found>

## Decisions
No wave/gate machinery adopted. dev-backend/dev-frontend run standalone via /dev:quick (or a
project-specific command, if one exists).

## Blockers
None.
```
</step>

<step name="write-config">
Write `ai/dev/config.json` per the canonical schema (`project`, `primary_branch`, `gates` all `false`,
`context_doc`, `contracts_path`, `build_command`, `notes`) — add project-specific keys only if something
genuinely doesn't fit the core fields; don't invent extra structure speculatively.
</step>

<step name="relay">
Report what was written and what was detected vs. defaulted-to-N/A, so the human can correct anything
guessed wrong.
</step>
</process>

<rules>
- **Never overwrite an existing `ai/dev/STATE.md`.** If one exists, this command's job is done — point to
  `/dev:status`.
- **Never invent a contracts path or build command.** Mark `N/A` with a reason rather than guessing.
- **Follow the canonical schema in `dev-framework/DESIGN.md` exactly** — don't drift the shape per project.
</rules>
