# Setup — one-time install + troubleshooting

This repo is staging/distribution only — nothing here is live in Claude Code until copied to `~\.claude\`.
See `README.md`'s Rollout section for the copy commands. This file covers **verifying** the install and
the specific problems worth knowing about before you hit them.

## Install

This machine has **three independent Claude Code config roots** — the default/legacy location
(`$env:USERPROFILE\.claude\`) and two profiles (`claude-scm`, `claude-nsz`, under `$env:LOCALAPPDATA\`),
each fully redirected via `CLAUDE_CONFIG_DIR` with **no fallback** to the default. Real sessions run under
a profile — installing to only the default silently leaves both real profiles without any of this (this
happened for real on 2026-08-10: `dev-backend` was "not found" in a live session despite being correctly
rolled out to `~\.claude\`). Always install to all three, every time:

```powershell
# from this repo's root — pre-create destination folders first; Copy-Item -Recurse onto a
# not-yet-existing destination can silently mis-create it (see claude\README.md Rollout step 3 for the
# skills\ incident this caused once)
$destinations = @(
    "$env:USERPROFILE\.claude",
    "$env:LOCALAPPDATA\claude-scm",
    "$env:LOCALAPPDATA\claude-nsz"
)
foreach ($dest in $destinations) {
    New-Item -ItemType Directory -Path "$dest\agents"   -Force | Out-Null
    New-Item -ItemType Directory -Path "$dest\skills"   -Force | Out-Null
    New-Item -ItemType Directory -Path "$dest\commands" -Force | Out-Null

    Copy-Item claude\agents\*.md          "$dest\agents\"   -Force
    Copy-Item skills\*                    "$dest\skills\"   -Recurse -Force
    Copy-Item claude\commands\*           "$dest\commands\" -Recurse -Force
    Copy-Item AGENT-CONDUCT-BASELINE.md, DESIGN-PRINCIPLES-BASELINE.md   "$dest\" -Force
    Copy-Item claude\AGENT-TEMPLATE-BASELINE.md   "$dest\" -Force
    Copy-Item CONSTITUTION.md             "$dest\"          -Force
    Copy-Item dev-framework               "$dest\" -Recurse -Force
    Copy-Item sa-framework                "$dest\" -Recurse -Force
}
```

`sa-framework\` is **not optional** — every `req-*` agent reads `ARTIFACT-SCHEMAS.md` and
`ESTIMATION-METHOD.md` at runtime and will misbehave without them, the same way `dev-*` agents depend on
`dev-framework\PRINCIPLES.md`.

Then merge `CLAUDE.md` into **each** destination's own `CLAUDE.md` **by hand** — don't blind-copy with
`-Force`, a real `CLAUDE.md` at any of the three may already carry personal notes this would clobber.

Run `powershell -File _scripts\check-sync.ps1` afterward to confirm all three destinations actually picked
up the change — it reports anything staged here that's missing or stale, per destination. A `post-commit`
hook (installed once via `_scripts\install-hooks.ps1`) runs this automatically after every commit, but the
copy step above stays a deliberate, explicit action, never automatic.

## Verify

1. **Start a brand-new Claude Code session, under the profile you actually use** (`claude --profile scm`
   or `claude --profile nsz` — agent/command lists load at session start, see the restart gotcha below,
   and are per-profile, not shared with the default location).
2. Run `/sa:help` — should print the `sa:` namespace reference (17 commands), not an error.
3. In any project with `ai/dev/STATE.md` already scaffolded, run `/dev:status` — should print that
   project's phase/gates, not "not initialized." In a project without one yet, run `/dev:init` and confirm
   it creates `ai/dev/STATE.md` + `config.json`.
4. If a project has its own namespace (e.g. `/scm:help` in net8-migration), run it and confirm it prints
   that project's command reference.

## Optional: the rate card (for priced offers)

Without one, `/sa:estimate` produces **effort-only** output — deliberately, never an invented number
(`sa-framework\ESTIMATION-METHOD.md §5`). To get cost figures:

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\estimation-data" | Out-Null
Copy-Item estimation-data\rates.yaml.example `
          "$env:USERPROFILE\.claude\estimation-data\rates.yaml"
# then edit it — roles left at `rate: 0` are treated as a placeholder, i.e. still no rate card
```

Lives in `~\.claude\` only, never in this repo — a filled-in card is commercially sensitive and
`.gitignore` excludes it. It is also never reproduced in a client-facing deliverable; only the arithmetic
someone chose to show. A card whose `as_of` is more than ~6 months old is still used, but flagged stale.

Per-engagement or per-project overrides can sit at `ai/sa/rates.yaml` or `ai/context/rates.yaml`; first
hit wins.

## Optional: the `document-skills` plugin (docx/xlsx/pptx/pdf)

Not part of this repo's own install — a separate, optional escalation path for `office-doc-reader`/
`office-doc-builder` (OCR on scanned PDFs, legacy `.doc`, tracked-changes patch-editing, native Excel
charts/pivots, PPTX theme generation). Installed via:

```
claude plugin marketplace add anthropics/skills
claude plugin install document-skills@anthropic-agent-skills --scope user
```

**This is per-profile, same gotcha as the three config roots above.** `claude plugin install --scope user`
writes under that profile's own `$env:LOCALAPPDATA\claude-<profile>\plugins\` (or
`$env:USERPROFILE\.claude\plugins\` for the default) — there is no shared/global plugin location across
the three roots. Installing it once under `claude-nsz` does **not** make it available under `claude-scm`
or the default profile; repeat both commands under each profile you actually use `/sa:ingest` from.
Source-available, not open-source (Anthropic's own README) — a real dependency to trust deliberately, not
a default reach.

## Optional: the `frontend-design` plugin (HTML/CSS work)

Not part of this repo's own agents/commands — a general-purpose Anthropic plugin for producing distinctive,
production-grade frontend UI instead of generic AI-default styling. Relevant any time a task involves
writing or reviewing HTML/CSS (dashboards, landing pages, artifact-based UI mockups). Installed via:

```
claude plugin marketplace add anthropics/claude-plugins-official   # already added on this machine
claude plugin install frontend-design@claude-plugins-official --scope user
```

**Same per-profile gotcha as `document-skills` above** — installed 2026-09-03 on all three config roots
(default, `claude-scm`, `claude-nsz`) since there is no shared/global plugin location across them. Repeat
on any additional profile you set up later.

## Troubleshooting

**A command isn't found (`/dev:status` etc. don't autocomplete or error out).**
Commands must land at `~/.claude/commands/<namespace>/<name>.md` — the *subfolder* is what becomes the
`namespace:` prefix. A file copied to the wrong level (flat in `commands\`, or under the wrong subfolder
name) won't register under the name you expect.

**A newly-added or newly-edited agent/command doesn't seem to exist yet, even though the file is right
there.** Agent and command lists are loaded once, at session start — they are **not hot-reloaded** mid
conversation. This came up in every single slice built this session: drafting `dev-reviewer.md` and trying
to dispatch it in the same session that created it will not work. Restart the session (or open a fresh
one) after copying new/changed files to `~/.claude/`.

**A `dev-*` agent immediately reports "project not initialized" / stops without doing anything.**
Per `dev-framework/PRINCIPLES.md` §1, every `dev-*` agent requires `ai/dev/STATE.md` and `config.json` to
exist in the target project before it will proceed. Run `/dev:init` first.

**A project-specific agent (e.g. `dev-reviewer`, `dev-browser-tester`) needs to be tested before you're
ready to copy it globally.** Two options, in order of preference: (a) if the project already has a
`.claude\agents\` folder of its own, drop a copy there — project-level agents are discovered the same way
global ones are, still subject to the same session-restart rule above; (b) for a one-off dry run without
installing anything anywhere, inline the agent's `<role>`/`<process>`/`<output_template>`/`<rules>` content
directly into a `general-purpose` agent dispatch — this is how `solution-analyst` and the SCM/CampaignManager
`dev-*` agents were first validated in this repo, before any install step.

**Drafting a new agent/command and the XML tags look right but something's off.** The `Read` tool's
line-numbered display has shown a phantom duplicate closing tag on at least two occasions. Verify tag
balance with `grep -c '<tagname[ >]' file` vs. `grep -c '</tagname>' file` — restricted to lines that are
*only* the tag (`^<tagname>$`), since a tag name mentioned in backtick-quoted prose (` `` `<output>` `` `)
will false-positive a plain count. Never conclude a defect from eyeballing `Read` output alone.

## Install — GitHub Copilot CLI

**Approved and run 2026-09-03.** The file copy below has been executed — `~/.copilot/` (Copilot CLI's own
live runtime state; confirmed empty of any pre-existing doctrine first, so this was a clean additive copy)
now carries the doctrine files and `AGENTS.md`. Two pieces remain outstanding, see the callouts below:
`COPILOT_CUSTOM_INSTRUCTIONS_DIRS` (blocked by the permission classifier as a permanent env-var change,
needs explicit approval) and MCP server wiring (not attempted — the destination file shape wasn't
confirmed). Matches `copilot\README.md`'s own rollout section verbatim.

- **Destination**: `~/.copilot/` (global/personal). `COPILOT_HOME` is the direct analog of Claude Code's
  `CLAUDE_CONFIG_DIR` — a future second Copilot identity would follow the same
  `copilot-work`/`copilot-personal` PowerShell-function pattern already used for Claude. Today there's one
  Copilot login, so one destination.
  ```powershell
  # from this repo's root
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
- **Done** — `copilot\AGENTS.md` merged into `~/.copilot/AGENTS.md` (a plain copy, since nothing was there
  before).
- **Done 2026-09-03** — `COPILOT_CUSTOM_INSTRUCTIONS_DIRS` (permanent, user-level) set to
  `%USERPROFILE%\.copilot` via `setx`. Requires a new terminal to take effect. Still worth a real
  end-to-end check next time Copilot CLI is used for real (open a fresh terminal, run `copilot` from
  outside `_AI_GIT`, confirm it's actually reading the doctrine) — the discovery behavior itself was never
  independently observed, only documented from `--help` text.
- **Partially done 2026-09-03** — `~/.copilot/mcp-config.json` confirmed as the right location via
  `copilot mcp --help` (the earlier assumption held). Only `azure-devops-geomant` wired in so far, via
  `copilot mcp add azure-devops-geomant --env KEY=VALUE ... -- npx -y @tiberriver256/mcp-server-azure-devops`
  (values copied from Claude's own config for that server). `azure-devops-netsolve`, Playwright, draw.io,
  sequential-thinking, and filesystem are **not yet wired** — deliberately scoped to Geomant only for now;
  add the rest the same way, one `copilot mcp add` call per server, when actually needed.

**Support tier, current as of 2026-09-03**: Copilot CLI has real subagent dispatch (`/fleet` + `@agent-name`)
and reads the same open `SKILL.md` format Claude Code does, so full parity is possible in principle — but
no `req-*`/`sa:` port exists yet (`copilot\README.md` has the full reasoning). Today, running the steps
above only makes the shared doctrine legible to Copilot; it does not run the `/sa:*`/`/dev:*` pipeline —
there is no Copilot equivalent to dispatch yet.
