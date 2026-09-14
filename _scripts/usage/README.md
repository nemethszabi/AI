# AI usage toolkit

> Version: 1.0.0 (2026-09-11)

Measures token use and estimated cost across AI coding tools on one scale, so tools, models, effort levels
and task types can be compared. Claude Code and GitHub Copilot CLI today; another tool is one more
`collect_<tool>.py` that fills the same `requests` row shape.

## Files

| File | What it does |
|---|---|
| `usage_lib.py` | Config, SQLite store schema, pricing, task classification - shared by everything below |
| `collect_claude.py` | Reads Claude Code transcripts from every profile root (`~/.claude`, `~/AppData/Local/claude-*`), incrementally (byte offsets) |
| `collect_copilot.py` | Reads `~/.copilot/session-store.db` → `assistant_usage_events` |
| `usage_report.py` | Runs both collectors, then writes a Markdown report (by tool/model/effort, task type, agent, skill, project, month, top sessions, signals) |
| `statusline.py` | Claude Code status line, two rows. **Row 1**: profile chip, model·effort, session name, context size (coloured against the guard thresholds and labelled with the action it implies), context added by the last turn, cache hit ratio with the reason for the last miss. **Row 2**: working folder, each rate-limit window as *remaining* plus its reset clock, git branch (suppressed when it equals the folder), PR number and review state, session duration and lines changed. Segments shrink to shorter forms before dropping, least important first; the context segment and the 5h window always survive. No session $ - on a subscription that is a notional API price; cost belongs in the reports. **Item-by-item reference for every segment, colour and threshold: `d:\WORK\AI\knowledge-base\token-economy.md` §7** - kept there rather than duplicated here |
| `context_guard.py` | `UserPromptSubmit` hook: warns once per threshold step when main-thread context passes 150k / 300k (+100k steps), pointing at `/handoff` → `/clear` → `/handoff resume` |
| `pricing.json` | List prices per 1M tokens + cache multipliers. **Edit here only** - costs are computed at report time, so a fix re-prices history |
| `usage-config.json` | Generic defaults: task rules (skill/agent prefix → dev / sa / framework / personal), guard thresholds |

Machine-specific settings (store path, profile roots, cwd → task rules, excluded folders) go in
`~/.ai-usage/config.json`, never in this repo; its top-level keys replace the defaults wholesale.

## Wiring (per Claude profile `settings.json`)

```json
"hooks": {
  "UserPromptSubmit": [{ "hooks": [{ "type": "command", "command": "python \"D:/_AI_GIT/_scripts/usage/context_guard.py\"", "timeout": 5 }] }],
  "Stop":             [{ "hooks": [{ "type": "command", "command": "python \"D:/_AI_GIT/_scripts/usage/collect_claude.py\" --hook", "async": true }] }]
},
"statusLine": { "type": "command", "command": "python D:/_AI_GIT/_scripts/usage/statusline.py" }
```

A related hook lives outside this folder: `_scripts\hooks\framework-change-flag.py` (`PostToolUse`, matcher `Edit|Write|MultiEdit|NotebookEdit`) suggests `/doc-sync` once per session after a framework or prompting edit. Wiring is in its own docstring.

The `Stop` hook copies each turn into the store as it happens. That matters because Claude Code deletes
transcripts after `cleanupPeriodDays` (default 30), and the store is the durable copy. Hook failures are
logged to `~/.ai-usage/collector-errors.log` and never reach the session.

## Usage

```powershell
python D:\_AI_GIT\_scripts\usage\usage_report.py                         # everything → <report_dir>\usage-report-YYYYMMDD.md
python D:\_AI_GIT\_scripts\usage\usage_report.py --since 2026-09-01 --stdout
python D:\_AI_GIT\_scripts\usage\usage_report.py --tool copilot --stdout  # or copilot\scripts\Get-CopilotUsage.ps1
python D:\_AI_GIT\_scripts\usage\collect_claude.py --full                 # re-read all transcripts from byte 0
```

## The record (one row per model request)

`tool, account, project, cwd, session_id, ts, model, effort, agent, run_id, skill, is_subagent, initiator,
input, output, cache_read, cache_write, cache_write_1h, reasoning, context, tool_cost_usd, billed_units, duration_ms`

- `input` never includes cache tokens. Copilot's `input_tokens` does, so its collector splits them back out.
- `context` is everything the model received for that request (input plus cache read plus cache write).
- `tool_cost_usd` is the tool's own figure where it records one: Copilot's `total_nano_aiu / 1e11`.
- `billed_units` is Copilot's premium-request multiplier.

**Task type** is resolved at report time, first match wins:
1. The request's own skill or agent rule.
2. A `/rename` title tag such as `sa: TOBi estimate`.
3. The session's dominant classified type.
4. A cwd rule.
5. `generic`.

## Limits

- **Estimates, not invoices.** Claude subscriptions and Copilot premium requests bill differently from list price, so compare *relative* numbers.
- **Copilot subagents are unnamed.** `session-store.db` records only an agent UUID, which the report shows as `(unnamed)`.
- **Effort is recorded per request** by both tools. Claude rows made before per-request effort logging show `-`.
