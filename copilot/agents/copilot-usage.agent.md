---
name: copilot-usage
description: Query current month's Copilot CLI token usage and estimated costs by model. Returns ALL monthly usage across all sessions with token counts and USD estimation.
tools:
  - bash
---

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
