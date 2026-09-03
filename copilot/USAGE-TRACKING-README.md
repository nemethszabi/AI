# Copilot Usage Tracking Framework

**Version**: 1.0.0 (Sept 2026)  
**Status**: Ready for production use  
**Scope**: Personal/user-level Copilot CLI session tracking

---

## Overview

This framework provides **two complementary ways** to query your current month's Copilot CLI usage (tokens + estimated USD cost) — choose the one that fits your workflow:

1. **Interactive Skill** (`@copilot-usage-query`) — Use inside a Copilot CLI session
2. **PowerShell Script** (`Get-CopilotUsage.ps1`) — Use from the command line or automation

Both aggregate the same underlying data (your Copilot CLI session-store.db) and produce identical results.

---

## Quick Start

### Option A: Interactive Query (Easiest)

```powershell
copilot
# Inside copilot CLI:
@copilot-usage-query
```

This invokes the **COPILOT-USAGE-QUERY** skill (see `skills/COPILOT-USAGE-QUERY.md`).

**Pros**: 
- Zero setup, works immediately
- Can ask follow-up questions naturally
- Full context awareness

**Cons**:
- Requires opening a Copilot CLI session first

---

### Option B: PowerShell Script (Scriptable)

```powershell
# From d:\_AI_GIT\copilot\scripts\
. .\Get-CopilotUsage.ps1
Get-CopilotUsage
```

Or with options:

```powershell
# Current month, export to JSON
Get-CopilotUsage -OutputFormat JSON -OutputFile usage-sept.json

# Previous month
Get-CopilotUsage -Month 8 -Year 2026

# With end-of-month projection (mid-month only)
Get-CopilotUsage -IncludeProjection
```

**Pros**:
- Runs standalone, no Copilot session needed
- Supports multiple output formats (Console/JSON/CSV/Markdown)
- Easy to integrate into automation or scheduled tasks
- Can export for further analysis

**Cons**:
- Requires sqlite3 or pssqlite module (fallback available)
- CLI-only, no interactive follow-ups

---

## Output Format

Both approaches return:

```
# Copilot Usage Report — September 2026

## Summary
- **Period**: 2026-09-01 to 2026-09-03 (3 days)
- **Sessions**: 12 total
- **Total Input Tokens**: 1,234,567
- **Total Output Tokens**: 456,789
- **Estimated Cost**: $45.67 USD

## Breakdown by Model

| Model | Input Tokens | Output Tokens | Estimated Cost |
|-------|---|---|---|
| claude-opus-4.8 | 500,000 | 200,000 | $24.50 |
| gpt-5.5 | 300,000 | 150,000 | $13.00 |
| claude-sonnet-5 | 434,567 | 106,789 | $7.17 |
```

---

## File Locations

| File | Purpose | Location |
|---|---|---|
| **COPILOT-USAGE-QUERY.md** | Interactive skill definition | `skills/COPILOT-USAGE-QUERY.md` |
| **Get-CopilotUsage.ps1** | PowerShell script | `scripts/Get-CopilotUsage.ps1` |
| **USAGE-TRACKING-README.md** | This file — framework overview | `USAGE-TRACKING-README.md` |

---

## Pricing Reference

Rates are baked into both the skill and script. Updated Sept 2026:

### Claude (Anthropic)
- **Opus 4.8**: $15/MTok input, $75/MTok output
- **Sonnet 5**: $3/MTok input, $15/MTok output
- **Haiku 4.5**: $0.80/MTok input, $4/MTok output

### GPT (OpenAI)
- **GPT-5.5**: $20/MTok input, $60/MTok output
- **GPT-5.4**: $10/MTok input, $30/MTok output
- **GPT-5-mini**: $0.15/MTok input, $0.60/MTok output

### Gemini (Google)
- **3.7-Flash**: $0.075/MTok input, $0.30/MTok output
- **3.5-Flash**: $0.075/MTok input, $0.30/MTok output

*MTok = Million tokens. Rates subject to change — confirm against provider dashboards if precision matters.*

---

## Design Decisions

### Why a Skill + Script, not a single Agent?

**Skill** (`COPILOT-USAGE-QUERY.md`):
- ✅ Always available, no overhead
- ✅ Can be invoked with `@copilot-usage-query` from any session
- ✅ Pairs well with natural-language follow-ups
- ✅ No specialized tooling needed

**Script** (`Get-CopilotUsage.ps1`):
- ✅ Standalone, scriptable, no Copilot session overhead
- ✅ Easy to automate or call from CI/CD
- ✅ Multiple output formats (JSON/CSV/Markdown)
- ✅ Can be aliased in PowerShell profile for easy access

**Not an Agent** (deliberate):
- Agent dispatch adds overhead and complexity for a simple query task
- Skill + Script cover 99% of use cases more efficiently
- Could promote to an agent later if recurring automation is needed

---

## Limitations & Caveats

### ⚠️ Pricing is Estimated

- **Actual invoicing** depends on your company's billing plan (volume discounts, enterprise rates, custom terms)
- Use this for *approximate* tracking, not authoritative billing
- For exact figures, check your GitHub Billing dashboard: https://github.com/settings/billing

### ⚠️ Personal Usage Only

- Tracks **your session data only** in `~/.copilot/session-store.db`
- If your company shares a billing profile, this does NOT show team usage
- For org-wide billing, admins can access GitHub Settings > Billing > Copilot

### ⚠️ Time Zone Awareness

- "Current month" = calendar month in your system timezone
- Database timestamps stored in UTC; script converts to local time
- If you work across time zones, reconcile against `/usage` in a Copilot session

### ⚠️ Pricing May Lag

- Rates are static in both files (last updated Sept 2026)
- Providers update pricing periodically — check official pages if costs look off:
  - OpenAI: https://openai.com/pricing
  - Anthropic: https://www.anthropic.com/pricing
  - Google: https://ai.google.dev/pricing

---

## Troubleshooting

### "Session database not found"

```
Error: Session database not found at C:\Users\...\AppData\Local\copilot\session-store.db
```

**Fix**: Run `copilot` once to initialize the Copilot CLI. The database will be created on first use.

### Script fails with "sqlite3 CLI not found"

```
Warning: sqlite3 CLI not found...
Error: Neither 'sqlite3' CLI nor 'pssqlite' module available
```

**Options**:
1. Install SQLite: `winget install SQLite.SQLite` (recommended)
2. Install pssqlite module: `Install-Module pssqlite -Scope CurrentUser`
3. Use the interactive skill instead: `copilot` → `@copilot-usage-query`

### Different numbers from `/usage` command

The `/usage` command in Copilot CLI shows **current session only**. This framework shows **all sessions in the current month**. They measure different things — both are correct.

---

## Automation & Integration

### Add PowerShell Alias

Edit your PowerShell profile (`notepad $PROFILE`) and add:

```powershell
function copilot-usage { & 'd:\_AI_GIT\copilot\scripts\Get-CopilotUsage.ps1' @args }
alias cop-usage copilot-usage
```

Then use:
```powershell
cop-usage                              # Current month
cop-usage -Month 8 -Year 2026          # August 2026
cop-usage -OutputFormat JSON -OutputFile ~/usage.json   # Export
```

### Scheduled Task

Create a monthly scheduled task to export usage as CSV:

```powershell
$action = New-ScheduledTaskAction -Execute "powershell.exe" `
  -Argument "-NoProfile -File 'd:\_AI_GIT\copilot\scripts\Get-CopilotUsage.ps1' -OutputFormat CSV -OutputFile '$env:USERPROFILE\Desktop\copilot-usage-$(Get-Date -Format yyyy-MM).csv'"

$trigger = New-ScheduledTaskTrigger -AtLogon

Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "Copilot Usage Export" -Description "Monthly Copilot usage report"
```

### CI/CD Integration

Export JSON for downstream processing:

```yaml
# Example GitHub Actions workflow
- name: Export Copilot usage
  run: |
    . 'd:\_AI_GIT\copilot\scripts\Get-CopilotUsage.ps1'
    Get-CopilotUsage -OutputFormat JSON -OutputFile usage-report.json
  
- name: Upload to artifact
  uses: actions/upload-artifact@v3
  with:
    name: copilot-usage-${{ github.run_id }}
    path: usage-report.json
```

---

## See Also

- **Skill documentation**: `skills/COPILOT-USAGE-QUERY.md`
- **Script source**: `scripts/Get-CopilotUsage.ps1`
- **Copilot CLI docs**: `/help` (inside copilot interactive mode)
- **GitHub Billing**: https://github.com/settings/billing
- **Provider pricing**:
  - OpenAI: https://openai.com/pricing
  - Anthropic: https://www.anthropic.com/pricing
  - Google: https://ai.google.dev/pricing

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-09-03 | Initial release: Skill + Script + Framework documentation |

---

## Questions or Issues?

- Check `skills/COPILOT-USAGE-QUERY.md` for interactive skill details
- Check `scripts/Get-CopilotUsage.ps1` for script parameters and options
- Verify pricing rates against official provider pages (rates subject to change)
- For GitHub Copilot licensing or org-wide billing, contact your GitHub admin
