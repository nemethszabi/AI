---
name: copilot-monthly
description: Get current month's Copilot CLI usage (tokens + cost). Invoke with @copilot-monthly
license: MIT
---

# Monthly Copilot Usage

Get your complete current month's Copilot CLI usage across all sessions.

## Usage

In Copilot CLI, type:
```
@copilot-monthly
```

## What it Returns

- Total tokens used (input + output)
- Cost breakdown by model
- Estimated USD total
- All sessions in current month

## Data Source

Queries `~/.copilot/session-store.db` and runs the usage analysis script to aggregate all monthly sessions.
