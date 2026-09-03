# Updating — how a change here reaches every live tool

What "in sync" means differs by tier, because the three branches (shared root, `claude\`, `copilot\`) are
at genuinely different maturity levels. This file is the map of what's automatic today, what's manual, and
what has no live target yet — read it before assuming a change here is already live somewhere.

## Shared doctrine (`CONSTITUTION.md`, both remaining root baselines, `dev-framework\`, `sa-framework\`,
`skills\`)

One file, read by both tools once rolled out — there is no per-tool copy to keep in sync *within this
repo*. What needs to happen after an edit:

1. Re-run the Claude rollout `Copy-Item` block (`claude\README.md` → Rollout, or `docs\SETUP.md` → Install)
   — copies the changed file to all three Claude config roots.
2. Once the Copilot rollout has been approved and run at least once (see `copilot\README.md` — currently a
   proposal, not yet executed), re-run its `Copy-Item` block too. Until then, there's no live Copilot
   destination to update — nothing to do on that side yet.

## `claude\` branch (agents, commands, `CLAUDE.md`, `AGENT-TEMPLATE-BASELINE.md`)

**Automatic drift detection, manual promotion** — this is the one piece of real automation in the repo:

- `_scripts\install-hooks.ps1` (run once, or again after a fresh clone) installs a `post-commit` git hook
  that runs `_scripts\check-sync.ps1` after every commit and appends the result to
  `_scripts\sync-check.log`. This **detects** drift between what's staged here and what's actually live in
  each of the three Claude config roots (`~\.claude\`, `claude-scm`, `claude-nsz`) — it does not fix it.
- Promotion (actually copying the changed file to the live config roots) stays a **deliberate, manual**
  step every time — the Rollout `Copy-Item` block in `claude\README.md` — by design, so a half-finished
  edit never goes live from an automated commit hook. Run it, then re-run `check-sync.ps1` to confirm.

So: commit → hook fires → log tells you if something drifted → you decide when to actually promote it.
Nothing pushes a change live without that manual step, on purpose.

## `copilot\` branch (currently a doctrine-only scaffold)

**No automatic sync exists here yet, and there is deliberately nothing to sync** — `copilot\agents\` and
`copilot\skills\` hold only stub `README.md` files, and the proposed rollout (`copilot\README.md`) hasn't
been run even once, so there's no live `~\.copilot\` config to drift against. `_scripts\check-sync.ps1`
has a comment marking exactly where a Copilot check would be added:

```
# Copilot side (copilot\agents\, copilot\skills\) is intentionally not checked yet - nothing to sync
# until it holds real files. Add a matching check here once the first Copilot agent/skill is authored.
```

**When this changes** (a `req-*`/`sa:` port is approved and `copilot\agents\`/`copilot\skills\` start
holding real files): extend `check-sync.ps1` with a fourth destination entry for `$env:USERPROFILE\.copilot`
and a matching `Get-FileHashMapRemapped` call for `copilot\agents`/`copilot\skills`, mirroring exactly how
the Claude side already works (see the function's own doc-comment) — at that point the same
"automatic drift detection, manual promotion" pattern above applies to Copilot too, with no new design
needed, just wiring in the destination.

## What this deliberately does *not* do

No mechanism here keeps `claude\` and `copilot\` **content** in parity with each other (e.g. flagging "a
new agent was added to `claude\agents\` with no Copilot counterpart"). That's a different kind of check —
tracking a porting backlog, not staged-vs-live drift — and would be premature to build while the Copilot
side is intentionally empty by scope decision (`copilot\README.md`). If/when a real port starts, revisit
this file to decide whether that backlog needs its own tracking, rather than building it speculatively now.
