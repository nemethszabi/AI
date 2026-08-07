# Setup — one-time install + troubleshooting

This repo is staging/distribution only — nothing here is live in Claude Code until copied to `~\.claude\`.
See `README.md`'s Rollout section for the copy commands. This file covers **verifying** the install and
the specific problems worth knowing about before you hit them.

## Install

```powershell
# from this repo's root
Copy-Item agents\*.md    "$env:USERPROFILE\.claude\agents\"   -Force
Copy-Item commands\*     "$env:USERPROFILE\.claude\commands\" -Recurse -Force
Copy-Item *-BASELINE.md  "$env:USERPROFILE\.claude\"          -Force
Copy-Item CONSTITUTION.md "$env:USERPROFILE\.claude\"         -Force
Copy-Item dev-framework  "$env:USERPROFILE\.claude\" -Recurse -Force
```

Then merge `CLAUDE.md` into `~\.claude\CLAUDE.md` **by hand** — don't blind-copy with `-Force`, a real
global `CLAUDE.md` may already carry personal notes this would clobber.

## Verify

1. **Start a brand-new Claude Code session** (agent/command lists load at session start — see the
   restart gotcha below, this isn't optional).
2. Run `/sa:help` — should print the `sa:` namespace reference, not an error.
3. In any project with `ai/dev/STATE.md` already scaffolded, run `/dev:status` — should print that
   project's phase/gates, not "not initialized." In a project without one yet, run `/dev:init` and confirm
   it creates `ai/dev/STATE.md` + `config.json`.
4. If a project has its own namespace (e.g. `/scm:help` in net8-migration), run it and confirm it prints
   that project's command reference.

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

## What this repo does not attempt

Unlike the reference framework this was adapted from
(`d:\_GEOMANT_GIT\agentic-dev-framework\docs\SETUP.md`), there is currently no Copilot/Codex install path
and no multi-tool support tier — everything here assumes Claude Code only. Revisit only if that stops being
true; adding it speculatively now would be building for a need that doesn't exist yet.
