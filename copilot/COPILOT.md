---
name: Monthly Usage
description: Copilot CLI custom instructions for /monthly- trigger
---

# Custom Instructions for Copilot CLI

## /monthly-usage Command

When the user types `/monthly-usage` or `/monthly`, respond with their current month's Copilot CLI usage statistics.

Execute this command to fetch the data (add `-Month <n> -Year <yyyy>` for another month):
```
! & 'd:\_AI_GIT\copilot\scripts\Get-CopilotUsage.ps1'
```

It wraps the cross-tool toolkit `d:\_AI_GIT\_scripts\usage\` and needs Python 3 on `PATH`. Display the
results in a clear format with:
- Model breakdown
- Token counts (input, output, cache)
- Estimated list-price cost and Copilot's own recorded cost
- Premium units
- Date range covered

Estimates, not invoices — say so. (Rewritten 2026-09-14: this block used to call `simple-usage.ps1`, which
read a non-existent table and priced Opus at $15/$75; that script is deleted.)

This should be treated as a standard command that always returns the same format of data.
