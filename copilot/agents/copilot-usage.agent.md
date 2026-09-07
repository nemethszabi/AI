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

This agent runs the usage query script and formats the output.
