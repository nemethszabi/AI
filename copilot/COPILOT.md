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

It wraps the cross-tool toolkit `d:\_AI_GIT\_scripts\usage\` and needs Python 3 on `PATH`. Add
`-Plan enterprise` if the seat is Enterprise. Display the results as printed:
- AI credits and USD used, the seat's included credits, usage above them, company cost
- Month-end projection and GitHub's quota line
- Breakdown by model, by initiator and by session

These are Copilot's own recorded charges, not estimates. Since 2026-06-01, Business and Enterprise bill in
AI Credits at API token rates. The one caveat: usage above the seat's share is billed only once the org-wide
pool runs out, which the report cannot see. Never mention premium requests or multipliers; that billing is
retired. (Rewritten 2026-09-14 to drop `simple-usage.ps1`; updated 2026-09-15 for AI Credits billing.)

This should be treated as a standard command that always returns the same format of data.
