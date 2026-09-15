#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Copilot usage for one UTC calendar month, priced as the company plan bills it (GitHub AI Credits).

.DESCRIPTION
    Thin wrapper over the shared usage toolkit (D:\_AI_GIT\_scripts\usage, see its README.md).
    Default: copilot_bill.py - credits used, the seat's included credits, usage above them, company cost,
    month-end projection, by model / initiator / session. Figures are Copilot's own recorded charge
    (total_nano_aiu), which since 2026-06-01 is what Business/Enterprise seats are billed.
    -Detailed: the full cross-tool comparison report instead (usage_report.py). Its Claude $ is a notional
    list price, not a subscription bill. Needs Python 3 on PATH.

    Rewritten 2026-09-15: the previous default showed "premium units" summed over every model call,
    ~30x the retired premium-request count and no longer billed at all.

.EXAMPLE
    & 'd:\_AI_GIT\copilot\scripts\Get-CopilotUsage.ps1'                        # current month, Business plan
.EXAMPLE
    & 'd:\_AI_GIT\copilot\scripts\Get-CopilotUsage.ps1' -Month 8 -Plan enterprise -OutputFile usage-aug.md
.EXAMPLE
    & 'd:\_AI_GIT\copilot\scripts\Get-CopilotUsage.ps1' -Detailed -AllTools
#>
param(
    [int]$Month = (Get-Date).ToUniversalTime().Month,
    [int]$Year = (Get-Date).ToUniversalTime().Year,
    [ValidateSet('business', 'enterprise')][string]$Plan,
    [string]$OutputFile,
    [switch]$Detailed,
    [switch]$AllTools
)
$usage = "$PSScriptRoot/../../_scripts/usage"
$start = Get-Date -Year $Year -Month $Month -Day 1
if ($Detailed -or $AllTools) {
    $pyArgs = @("$usage/usage_report.py", '--since', $start.ToString('yyyy-MM-dd'), '--until', $start.AddMonths(1).ToString('yyyy-MM-dd'))
    if (-not $AllTools) { $pyArgs += @('--tool', 'copilot') }
    if ($OutputFile) { $pyArgs += @('--out', $OutputFile) } else { $pyArgs += '--stdout' }
} else {
    $pyArgs = @("$usage/copilot_bill.py", '--month', $start.ToString('yyyy-MM'))
    if ($Plan) { $pyArgs += @('--plan', $Plan) }
    if ($OutputFile) { $pyArgs += @('--out', $OutputFile) }
}
python @pyArgs
