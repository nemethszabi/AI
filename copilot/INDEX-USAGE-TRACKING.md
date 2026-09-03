# Copilot CLI Usage Tracking — Complete Index

**Version**: 1.0.0  
**Status**: Production-ready  
**Date**: 2026-09-03

---

## What This Framework Does

Provides **two complementary ways** to query Copilot CLI session usage (tokens + estimated USD cost) for the current calendar month, integrated into the Copilot scaffold.

**Data source**: `~/.copilot/session-store.db` (SQLite, auto-maintained by Copilot CLI)  
**Scope**: Personal/user-level sessions only  
**Pricing**: Public API rates (baked in, verified Sept 2026)

---

## File Map

### Core Files (in this repo, d:\_AI_GIT\copilot\)

| File | Purpose | Type | Size |
|---|---|---|---|
| **USAGE-TRACKING-README.md** | Framework overview, design rationale, integration guide | Framework doc | 8.5 KB |
| **skills/COPILOT-USAGE-QUERY.md** | Interactive skill definition (SKILL.md format) | Skill | 5.6 KB |
| **scripts/Get-CopilotUsage.ps1** | Standalone PowerShell script with export options | Script | 11.3 KB |
| **INDEX-USAGE-TRACKING.md** | This file — quick navigation | Index | - |

### Knowledge Base (d:\WORK\AI\knowledge-base\)

| File | Purpose | Reference |
|---|---|---|
| **copilot-usage-tracking.md** | KB reference: quick start + pricing + troubleshooting | Main KB reference |
| **system-overview.md** (updated) | Global AI system map, now with §1b Copilot CLI section | Updated 2026-09-03 |

---

## Quick Start

### Option 1: Interactive (Easiest)

```powershell
copilot
# Inside CLI:
@copilot-usage-query
```

**Pros**: Zero setup, works immediately, can ask follow-ups  
**Cons**: Requires opening a Copilot CLI session

### Option 2: PowerShell Script (Scriptable)

```powershell
. d:\_AI_GIT\copilot\scripts\Get-CopilotUsage.ps1
Get-CopilotUsage
```

**Common options**:
```powershell
Get-CopilotUsage -Month 8 -Year 2026           # Different month
Get-CopilotUsage -OutputFormat JSON -OutputFile usage.json  # Export
Get-CopilotUsage -IncludeProjection            # Month-end estimate
```

**Pros**: Standalone, supports export, scriptable, automation-ready  
**Cons**: Needs sqlite3/pssqlite, requires initialization

---

## Output Format (Both Methods)

```
========================================
  COPILOT USAGE REPORT — September 2026
========================================

Summary:
  Period: 09/01/2026 to 09/30/2026
  Sessions: 12 total
  Total Tokens: 1,691,356
  Estimated Cost: $45.67

Breakdown by Model:
  claude-opus-4.8
    Input:  500,000 tokens
    Output: 200,000 tokens
    Cost:   $24.50
    Sessions: 3
  
  [More models...]

========================================
```

---

## Pricing Reference (Verified Sept 2026)

| Model | Input Rate | Output Rate |
|---|---|---|
| **Claude Opus 4.8** | $15/MTok | $75/MTok |
| **Claude Sonnet 5** | $3/MTok | $15/MTok |
| **Claude Haiku 4.5** | $0.80/MTok | $4/MTok |
| **GPT-5.5** | $20/MTok | $60/MTok |
| **GPT-5.4** | $10/MTok | $30/MTok |
| **Gemini 3.7-Flash** | $0.075/MTok | $0.30/MTok |
| **Gemini 3.5-Flash** | $0.075/MTok | $0.30/MTok |

*MTok = Million tokens. Rates may have changed — verify at provider sites if precision matters.*

---

## Documentation by Use Case

### "I want to check my usage right now"

**→ Read**: `d:\WORK\AI\knowledge-base\copilot-usage-tracking.md` §Quick Start  
**→ Try**: `copilot` → `@copilot-usage-query`

### "I need to understand the framework design"

**→ Read**: `d:\_AI_GIT\copilot\USAGE-TRACKING-README.md`  
**→ Why**: Design decisions, skill vs. script trade-offs, why not an agent

### "I want to export data or automate this"

**→ Read**: `d:\_AI_GIT\copilot\scripts\Get-CopilotUsage.ps1` (inline help)  
**→ Try**: `. .\Get-CopilotUsage.ps1; Get-CopilotUsage -OutputFormat JSON -OutputFile usage.json`

### "How does the skill work?"

**→ Read**: `d:\_AI_GIT\copilot\skills\COPILOT-USAGE-QUERY.md`  
**→ Invocation**: Inside Copilot CLI: `@copilot-usage-query`

### "Where is this integrated into the global system?"

**→ Read**: `d:\WORK\AI\knowledge-base\system-overview.md` §1b  
**→ Also**: `d:\WORK\AI\knowledge-base\system-overview.md` Quick reference table

### "I'm having a problem"

**→ Read**: `d:\WORK\AI\knowledge-base\copilot-usage-tracking.md` §Troubleshooting  
**→ Also**: `d:\_AI_GIT\copilot\scripts\Get-CopilotUsage.ps1` error handling comments

---

## Integration Ideas

### Add a PowerShell Alias

Edit `$PROFILE` and add:

```powershell
function copilot-usage { & 'd:\_AI_GIT\copilot\scripts\Get-CopilotUsage.ps1' @args }
Set-Alias cop-usage copilot-usage
```

Then use: `cop-usage` or `cop-usage -Month 8 -Year 2026`

### Monthly Scheduled Export

Create a scheduled task to export usage as CSV on the 1st of each month:

```powershell
$action = New-ScheduledTaskAction -Execute 'powershell.exe' `
  -Argument "-NoProfile -File 'd:\_AI_GIT\copilot\scripts\Get-CopilotUsage.ps1' -OutputFormat CSV -OutputFile '$env:USERPROFILE\Desktop\usage-$(Get-Date -Format yyyy-MM).csv'"

$trigger = New-ScheduledTaskTrigger -AtLogon

Register-ScheduledTask -Action $action -Trigger $trigger -TaskName 'Copilot Usage Export' -Description 'Monthly usage report'
```

### CI/CD Integration

Export JSON for processing in a pipeline:

```yaml
- name: Export Copilot usage
  run: |
    . 'd:\_AI_GIT\copilot\scripts\Get-CopilotUsage.ps1'
    Get-CopilotUsage -OutputFormat JSON -OutputFile usage.json

- name: Upload artifact
  uses: actions/upload-artifact@v3
  with:
    name: copilot-usage
    path: usage.json
```

---

## Important Caveats

### ⚠️ Estimated Cost Only

Uses **public API rates**, not your company's negotiated pricing. Actual billing may differ significantly based on:
- Volume discounts
- Enterprise agreements
- Custom terms

**Use for tracking trends, not authoritative billing.**

### ⚠️ Personal Usage Only

Tracks your own sessions. For org-wide billing:
- **GitHub Settings** → **Billing** → **Copilot** (admin access required)
- Or contact your GitHub admin

### ⚠️ Time Zone Aware

"Current month" = calendar month in your **system time zone**. Database stores UTC; script converts to local time.

### ⚠️ Static Pricing

Rates are baked in (verified Sept 2026). Check provider sites if values seem off:
- Anthropic: https://www.anthropic.com/pricing
- OpenAI: https://openai.com/pricing
- Google: https://ai.google.dev/pricing

---

## Architecture

```
User Request
    ↓
┌─ Interactive ─────────┐  ┌─ Standalone ─────┐
│  copilot CLI session  │  │  PowerShell CLI   │
│  @copilot-usage-query │  │  Get-CopilotUsage │
└───────────┬───────────┘  └────────┬──────────┘
            │                        │
            └────────────┬───────────┘
                         ↓
         ~/.copilot/session-store.db
                  (SQLite)
                         ↓
            Query: Sessions in current month
                         ↓
         Sum tokens by model, apply pricing
                         ↓
            Format output (Console/JSON/CSV/Markdown)
                         ↓
        Display to user or export to file
```

---

## Version & Maintenance

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-09-03 | Initial release: Skill + Script + Framework documentation |

**Maintained by**: AI Framework — Copilot Tooling  
**Status**: Production-ready  
**Last verified**: Sept 2026 (pricing, SQLite schema, file locations, syntax)

---

## Related

### Copilot CLI Framework
- `d:\_AI_GIT\copilot\README.md` — Copilot scaffold overview
- `d:\_AI_GIT\copilot\AGENTS.md` — Copilot-side doctrine pointer
- `d:\_AI_GIT\copilot\AGENT-TEMPLATE-BASELINE.md` — File shapes for future ports

### Claude Code (Main Tool)
- `d:\_AI_GIT\claude\README.md` — Claude Code branch overview
- `d:\_AI_GIT\claude\CLAUDE.md` — Claude-side doctrine pointer

### Knowledge Base
- `d:\WORK\AI\knowledge-base\system-overview.md` — Complete AI system map
- `d:\WORK\AI\knowledge-base\command-inventory.md` — Complete agent/skill/command list
- `d:\WORK\AI\knowledge-base\mcp-reference.md` — MCP server configuration

---

## Next Steps

1. **Try it**: `copilot` → `@copilot-usage-query`
2. **Explore options**: `Get-CopilotUsage -OutputFormat JSON -OutputFile ~/usage.json`
3. **Integrate**: Add alias to PowerShell profile or set up scheduled export
4. **Track trends**: Export monthly reports and monitor usage patterns over time

---

**Questions?** Check the relevant doc in this index, or see the "Troubleshooting" section in `d:\WORK\AI\knowledge-base\copilot-usage-tracking.md`.
