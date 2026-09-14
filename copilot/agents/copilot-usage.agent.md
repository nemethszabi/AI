---
name: copilot-usage
description: Query current month's Copilot CLI token usage and estimated costs by model. Returns ALL monthly usage across all sessions with token counts and USD estimation.
tools:
  - shell
---

> Corrected 2026-09-07: `tools: bash` → `shell`. The tool name was verified against Copilot CLI v1.0.82
> during the `sa:` pipeline port — `~/.copilot/permissions-config.json` records approval kinds as `write`
> and `commands`, and every working `.agent.md` here declares `shell`. `bash` was a Claude-side name that
> predates the ports; this agent would have had no shell grant at all. Flagged as unresolved in
> `d:\WORK\AI\knowledge-base\command-inventory.md` since 2026-09-07 — that note can now be closed.

# Copilot Usage Query Agent

Query and display your complete current month's Copilot CLI usage (all sessions, all tokens, estimated cost by model).

## Usage

Invoke from Copilot CLI:
```
@copilot-usage
```

Returns:
- Total input tokens (all sessions, current month)
- Total output tokens (all sessions, current month)  
- Cost breakdown by model
- Estimated USD cost

## Implementation

Run exactly this, adding `-Month <n> -Year <yyyy>` only if the user asked for a different month:

```
& 'd:\_AI_GIT\copilot\scripts\Get-CopilotUsage.ps1'
```

It is a thin wrapper over the cross-tool toolkit `d:\_AI_GIT\_scripts\usage\` (needs Python 3 on `PATH`)
and prints a Markdown report. Relay its figures as printed. Never compute cost yourself or apply a price
table from memory. Say that the costs are estimates, not invoices.

> 2026-09-14: named the script explicitly. The body previously said only "runs the usage query script",
> and the scripts that name used to reach (`simple-usage.ps1`, `Get-CopilotUsage-Fixed.ps1`) queried a
> non-existent table with outdated pricing; both are deleted.
