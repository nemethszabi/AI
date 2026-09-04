---
name: Monthly Usage
description: Copilot CLI custom instructions for /monthly- trigger
---

# Custom Instructions for Copilot CLI

## /monthly-usage Command

When the user types `/monthly-usage` or `/monthly`, respond with their current month's Copilot CLI usage statistics.

Execute this command to fetch the data:
```
! & 'd:\_AI_GIT\copilot\scripts\simple-usage.ps1'
```

Then display the results in a clear format with:
- Model breakdown
- Token counts (input + output)
- Estimated USD cost
- Date range covered

This should be treated as a standard command that always returns the same format of data.
