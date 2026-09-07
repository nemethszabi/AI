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

## `copilot\` branch (full `sa:` pipeline since 2026-09-07)

**Same pattern as the Claude side, and `check-sync.ps1` has covered it since 2026-09-05**: it reports
`MISSING`/`STALE`/`EXTRA` for `~\.copilot\` against `copilot\agents\`, `copilot\skills\`,
`copilot\commands\`, the shared `skills\`/`dev-framework\`/`sa-framework\`, and the doctrine files. Drift
detection is automatic; promotion stays a deliberate `Copy-Item` step, run from `copilot\README.md`'s
Rollout block.

Three things about this branch that the Claude side has no equivalent of:

- **The blanket `skills\*` copy pulls in what must not be there.** `framework-review` dispatches
  `framework-strategist`, which is Claude-side only, so the `Remove-Item` line immediately after the copy
  is load-bearing — not tidy-up. `check-sync.ps1`'s `$copilotNotPorted` keeps it from being reported
  `MISSING` and "fixed" back into existence, which is exactly what happened on 2026-09-07 before the list
  existed.
- **`document-data\` is deliberately not rolled out here.** It feeds `/sa:package`, which is where binding
  deliverables should be built anyway. Copying it would put brand templates at a root nothing reads.
- **Claude↔Copilot parity is not checked by anything.** `check-sync.ps1` compares *staged versus live per
  tool*; it has no notion of whether `copilot\agents\req-estimator.agent.md` still matches
  `claude\agents\req-estimator.md`. **When you change a Claude `req-*` agent materially, change its
  sibling too** — the conformance checklist in `sa-framework\PIPELINE.md §5` is what to walk, and a
  periodic `/framework-review` is currently the only mechanism that would catch the drift.

## What is shared, and therefore what one edit changes twice

`CONSTITUTION.md`, both `*-BASELINE.md` files at the root, `dev-framework\`, `sa-framework\` (including
`PIPELINE.md`) and the root `skills\` are **one set of files copied to both tools' roots**. Editing any of
them changes behaviour on both sides at the next rollout — which is the point, but it means a change that
looks Claude-shaped can land on Copilot too. The test before editing a shared file: *would this sentence
still be true if the other tool did not exist?* If not, it belongs in a branch.

## What this deliberately does *not* do

No mechanism here keeps `claude\` and `copilot\` **content** in parity with each other (e.g. flagging "a
new agent was added to `claude\agents\` with no Copilot counterpart"). That's a different kind of check —
tracking a porting backlog, not staged-vs-live drift — and would be premature to build while the Copilot
side is intentionally empty by scope decision (`copilot\README.md`). If/when a real port starts, revisit
this file to decide whether that backlog needs its own tracking, rather than building it speculatively now.
