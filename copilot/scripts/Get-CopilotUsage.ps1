#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Copilot CLI usage for one calendar month: tokens, list-price cost, Copilot's own cost, premium units.

.DESCRIPTION
    Thin wrapper over the shared cross-tool usage toolkit (D:\_AI_GIT\_scripts\usage, see its README.md).
    Rewritten 2026-09-11: the previous version queried sessions.usage_model / usage_input_tokens, which do
    not exist in session-store.db (tokens live in assistant_usage_events), ignored cache tokens, and priced
    Opus at $15/$75 (current list: $5/$25). Needs Python 3 on PATH; no pssqlite module.

.EXAMPLE
    & 'd:\_AI_GIT\copilot\scripts\Get-CopilotUsage.ps1'                  # current month, Copilot only
.EXAMPLE
    & 'd:\_AI_GIT\copilot\scripts\Get-CopilotUsage.ps1' -Month 9 -AllTools -OutputFile usage-sept.md
#>
param(
    [int]$Month = (Get-Date).Month,
    [int]$Year = (Get-Date).Year,
    [string]$OutputFile,
    [switch]$AllTools
)
$start = Get-Date -Year $Year -Month $Month -Day 1
$pyArgs = @("$PSScriptRoot/../../_scripts/usage/usage_report.py",
            '--since', $start.ToString('yyyy-MM-dd'), '--until', $start.AddMonths(1).ToString('yyyy-MM-dd'))
if (-not $AllTools) { $pyArgs += @('--tool', 'copilot') }
if ($OutputFile) { $pyArgs += @('--out', $OutputFile) } else { $pyArgs += '--stdout' }
python @pyArgs
