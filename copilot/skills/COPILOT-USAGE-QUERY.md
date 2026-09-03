---
name: Copilot Usage Query
description: Query current month's Copilot CLI token usage and estimated costs by model. Returns cumulative session data with token counts and USD estimation.
license: MIT
version: 1.0.0
author: AI Framework — Usage Tracking
tags: 
  - usage
  - analytics
  - billing
  - tokens
  - cost-estimation
---

# Copilot Usage Query Skill

## What This Skill Does

This skill provides a standardized, repeatable way to query your **current calendar month's Copilot CLI usage** in a single, easy-to-read format.

**Output includes:**
- Total input tokens (cumulative)
- Total output tokens (cumulative)
- Token usage breakdown by model
- Estimated USD cost (based on current OpenAI/Anthropic/Google pricing)
- Session count and date range

## When to Use This

Invoke this skill when you need to:
- **Check month-to-date usage** for billing or quota tracking
- **Understand cost trends** by model (Claude vs. GPT vs. Gemini)
- **Prepare a usage report** for your team or manager
- **Monitor quota against company limits**

### Quick Invoke
From inside a Copilot CLI session, type:
```
@copilot-usage-query
```

Or, ask directly:
```
Query my current month's Copilot usage and show me tokens + USD cost by model.
```

---

## Background: How Copilot Tracks Usage

Copilot CLI maintains session-level metrics in `~/.copilot/session-store.db` (SQLite). Each session captures:
- `usage_model`: The model identifier (e.g., `claude-opus-4.8`, `gpt-5.5`, `gemini-3.7-flash`)
- `usage_input_tokens`: Tokens sent to the model in that session
- `usage_output_tokens`: Tokens returned by the model
- Session timestamp and metadata

This skill queries that database for all sessions **created in the current calendar month**, sums tokens by model, and applies public pricing rates to estimate cost.

---

## Token Pricing Reference (as of Sept 2026)

**Claude (Anthropic)**
- Claude Opus 4.8: $15/MTok input, $75/MTok output
- Claude Sonnet 5: $3/MTok input, $15/MTok output  
- Claude Haiku 4.5: $0.80/MTok input, $4/MTok output

**GPT (OpenAI)**
- GPT-5.5: $20/MTok input, $60/MTok output
- GPT-5.4: $10/MTok input, $30/MTok output
- GPT-5-mini: $0.15/MTok input, $0.60/MTok output

**Gemini (Google)**
- Gemini 3.7-Flash: $0.075/MTok input, $0.30/MTok output
- Gemini 3.5-Flash: $0.075/MTok input, $0.30/MTok output

*Note: Pricing is approximate and subject to API changes. Confirm current rates at provider dashboards.*

---

## Output Format

The skill returns a markdown table and summary:

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

## Raw Data
- Copilot Home: ~/.copilot/
- Database: session-store.db
- Query method: Session event aggregation (current calendar month, all session events with token usage)
```

---

## Limitations

1. **Pricing is estimated** — actual invoicing depends on your company's plan (volume discounts, enterprise rates, etc.). Use this for *approximate* tracking only.
2. **Time zone aware** — "current month" = calendar month in your system timezone. Confirm against `/usage` output if precision matters.
3. **Company billing profile** — if your company uses a shared billing profile, this tracks *your personal session usage only*, not your team's aggregated usage. For org-wide reports, check your GitHub Billing dashboard or contact your admin.
4. **Model pricing may lag** — rates are static in this skill. Check official provider pricing pages if costs look off.

---

## Invocation Examples

**In Copilot CLI (interactive):**
```
> @copilot-usage-query
```

**Or ask naturally:**
```
> Show me my usage for this month — tokens and dollars.
```

**Or with follow-ups:**
```
> @copilot-usage-query

[Skill returns summary]

> Compare to last month.
> What's my average cost per session?
> Which model am I using most?
```

---

## Integration with Your Workflow

### Option A: Manual Query
Invoke via `@copilot-usage-query` whenever you need a snapshot (recommended for infrequent checks).

### Option B: Scheduled Check
Add this to a personal reminder/calendar:
- **First of each month**: Run `@copilot-usage-query` to capture month-start baseline
- **End of month**: Run again to finalize usage report

### Option C: Custom Agent (Future)
If you need recurring, automated reports, a `usage-reporter` agent could:
- Query usage daily
- Accumulate into a `.csv` or JSON log
- Email summaries to you or your manager

See `~/.copilot/AGENT-TEMPLATE-BASELINE.md` for how to draft a custom agent spec.

---

## See Also

- **Copilot CLI built-in**: `/usage` — shows current session usage only
- **GitHub Billing**: https://github.com/settings/billing — org-wide usage (if you're an admin)
- **Copilot API pricing**: https://openai.com/pricing (OpenAI), https://www.anthropic.com/pricing (Anthropic), https://ai.google.dev/pricing (Google)
- **Session tracking**: See `.copilot\session-store.db` schema for low-level details

---

## Version & Maintenance

- **Version**: 1.0.0 (Sept 2026)
- **Last updated**: 2026-09-03
- **Maintained by**: AI Framework — Usage Tracking initiative
- **Status**: Stable, ready for production use
