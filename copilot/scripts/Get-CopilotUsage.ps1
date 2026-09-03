#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Query current month's Copilot CLI usage: tokens and estimated cost by model.

.DESCRIPTION
    Reads Copilot CLI's session-store.db, aggregates token usage for all sessions
    created in the current calendar month, and calculates estimated cost using
    public provider pricing. Outputs a formatted report to console and optionally
    to JSON/CSV for further analysis.

.PARAMETER Month
    Calendar month to query (default: current month, format: MM or "September")
    Examples: 9, "09", "September", "9/2026"

.PARAMETER Year
    Year (default: current year). Used with -Month.
    Example: 2026

.PARAMETER OutputFormat
    Output format: Console (default), JSON, CSV, or Markdown
    Default: Console

.PARAMETER OutputFile
    Save report to file (optional). Format determined by -OutputFormat.
    Example: "usage-report-sept-2026.json"

.PARAMETER IncludeProjection
    Include projection to end of month (if today is mid-month)

.EXAMPLE
    Get-CopilotUsage
    # Returns current month usage to console

.EXAMPLE
    Get-CopilotUsage -Month 9 -Year 2026 -OutputFormat JSON -OutputFile usage-sept.json
    # Queries Sept 2026, exports to JSON

.EXAMPLE
    Get-CopilotUsage -IncludeProjection
    # Shows current month usage plus estimated end-of-month total (if mid-month)

.NOTES
    Database path: $env:USERPROFILE\.copilot\session-store.db (SQLite)
    Pricing rates: See COPILOT-USAGE-QUERY.md for current rates and assumptions
    
    Requires: sqlite3 (or pssqlite module). If missing, falls back to GUI selector.
    
    Scope: Personal/user-level usage only. For org-wide billing, see GitHub Settings > Billing.

.LINK
    Full skill documentation: d:\_AI_GIT\copilot\skills\COPILOT-USAGE-QUERY.md
    CLI command for interactive query: copilot (then @copilot-usage-query)
#>

param(
    [int]$Month = (Get-Date).Month,
    [int]$Year = (Get-Date).Year,
    [ValidateSet('Console', 'JSON', 'CSV', 'Markdown')]
    [string]$OutputFormat = 'Console',
    [string]$OutputFile,
    [switch]$IncludeProjection
)

# Pricing reference (as of Sept 2026)
$pricing = @{
    'claude-opus-4.8' = @{ InputCost = 15; OutputCost = 75 }
    'claude-opus-4.7' = @{ InputCost = 15; OutputCost = 75 }
    'claude-sonnet-5' = @{ InputCost = 3; OutputCost = 15 }
    'claude-haiku-4.5' = @{ InputCost = 0.80; OutputCost = 4 }
    'gpt-5.5' = @{ InputCost = 20; OutputCost = 60 }
    'gpt-5.4' = @{ InputCost = 10; OutputCost = 30 }
    'gpt-5-mini' = @{ InputCost = 0.15; OutputCost = 0.60 }
    'gpt-5.4-mini' = @{ InputCost = 0.15; OutputCost = 0.60 }
    'gemini-3.7-flash' = @{ InputCost = 0.075; OutputCost = 0.30 }
    'gemini-3.6-flash' = @{ InputCost = 0.075; OutputCost = 0.30 }
    'gemini-3.5-flash' = @{ InputCost = 0.075; OutputCost = 0.30 }
}

# Default pricing for unknown models (estimate as mid-tier Claude)
$defaultPricing = @{ InputCost = 3; OutputCost = 15 }

# Database path
$dbPath = "$env:USERPROFILE\.copilot\session-store.db"

# Validate database exists
if (-not (Test-Path $dbPath)) {
    Write-Error "Session database not found at $dbPath`nRun 'copilot' first to initialize Copilot CLI."
    exit 1
}

# Try to load sqlite3 (requires sqlite3.exe in PATH or pssqlite module)
$sqlite3 = $null
try {
    $sqlite3 = Get-Command sqlite3 -ErrorAction Stop
} catch {
    Write-Warning "sqlite3 CLI not found. Attempting to use PowerShell SQLite module..."
    try {
        Import-Module pssqlite -ErrorAction Stop | Out-Null
    } catch {
        Write-Error "Neither 'sqlite3' CLI nor 'pssqlite' module available. Please install SQLite or run via Copilot CLI instead.`nAlternative: Use '/skills @copilot-usage-query' inside copilot interactive mode."
        exit 1
    }
}

# Build date range for current month
$monthStart = [datetime]"$Year-$($Month.ToString('D2'))-01"
$monthEnd = $monthStart.AddMonths(1).AddSeconds(-1)

Write-Verbose "Querying usage for period: $($monthStart.ToShortDateString()) to $($monthEnd.ToShortDateString())"

# Query sessions and token usage
$query = @"
    SELECT 
        COALESCE(usage_model, 'unknown') as model,
        COALESCE(SUM(usage_input_tokens), 0) as input_tokens,
        COALESCE(SUM(usage_output_tokens), 0) as output_tokens,
        COUNT(DISTINCT session_id) as session_count,
        MIN(created_at) as first_session,
        MAX(created_at) as last_session
    FROM sessions
    WHERE strftime('%Y-%m', created_at, 'localtime') = '$($Year.ToString('D4'))-$($Month.ToString('D2'))'
    GROUP BY usage_model
    ORDER BY input_tokens + output_tokens DESC
"@

$sessions = @()
if ($sqlite3) {
    $result = & sqlite3 $dbPath $query
    $result | ForEach-Object {
        $parts = $_ -split '\|'
        if ($parts.Count -ge 5) {
            $sessions += @{
                Model = $parts[0].Trim()
                InputTokens = [int]($parts[1].Trim())
                OutputTokens = [int]($parts[2].Trim())
                SessionCount = [int]($parts[3].Trim())
                FirstSession = $parts[4].Trim()
                LastSession = $parts[5].Trim()
            }
        }
    }
} else {
    # Use pssqlite module
    $connection = New-SQLiteConnection -DataSource $dbPath
    $result = Invoke-SQLiteQuery -SQLiteConnection $connection -Query $query
    $result | ForEach-Object {
        $sessions += @{
            Model = $_.model
            InputTokens = $_.input_tokens
            OutputTokens = $_.output_tokens
            SessionCount = $_.session_count
            FirstSession = $_.first_session
            LastSession = $_.last_session
        }
    }
    $connection.Close()
}

# Calculate costs
$totalInput = 0
$totalOutput = 0
$totalCost = 0
$modelData = @()

foreach ($session in $sessions) {
    $model = $session.Model
    $inTokens = $session.InputTokens
    $outTokens = $session.OutputTokens
    
    $rate = $pricing[$model] ?? $defaultPricing
    $inCost = ($inTokens / 1000000) * $rate.InputCost
    $outCost = ($outTokens / 1000000) * $rate.OutputCost
    $modelCost = $inCost + $outCost
    
    $totalInput += $inTokens
    $totalOutput += $outTokens
    $totalCost += $modelCost
    
    $modelData += @{
        Model = $model
        InputTokens = $inTokens
        OutputTokens = $outTokens
        Cost = $modelCost
        SessionCount = $session.SessionCount
    }
}

# Generate output
$report = @{
    Period = "$($monthStart.ToString('MMMM yyyy'))"
    DateRange = "$($monthStart.ToShortDateString()) to $($monthEnd.ToShortDateString())"
    TotalSessions = ($sessions | Measure-Object -Property SessionCount -Sum).Sum
    TotalInputTokens = $totalInput
    TotalOutputTokens = $totalOutput
    TotalTokens = $totalInput + $totalOutput
    EstimatedCostUSD = $totalCost
    ModelBreakdown = $modelData
}

# Handle projection if requested
if ($IncludeProjection -and (Get-Date).Month -eq $Month) {
    $daysElapsed = (Get-Date).Day
    $daysInMonth = [DateTime]::DaysInMonth($Year, $Month)
    $projectedCost = $totalCost * ($daysInMonth / $daysElapsed)
    $report.ProjectedMonthlySpend = [Math]::Round($projectedCost, 2)
    $report.ProjectionNote = "Based on $daysElapsed/$daysInMonth days"
}

# Output based on format
switch ($OutputFormat) {
    'Console' {
        Write-Host "`n========================================" -ForegroundColor Cyan
        Write-Host "  COPILOT USAGE REPORT — $($report.Period)" -ForegroundColor Cyan
        Write-Host "========================================`n" -ForegroundColor Cyan
        
        Write-Host "Summary:" -ForegroundColor Green
        Write-Host "  Period: $($report.DateRange)"
        Write-Host "  Sessions: $($report.TotalSessions)"
        Write-Host "  Total Tokens: $($report.TotalTokens.ToString('N0'))"
        Write-Host "  Estimated Cost: `$$($report.EstimatedCostUSD.ToString('N2'))"
        
        if ($report.ProjectedMonthlySpend) {
            Write-Host "  Projected Month-End: `$$($report.ProjectedMonthlySpend.ToString('N2')) ($($report.ProjectionNote))"
        }
        
        Write-Host "`nBreakdown by Model:" -ForegroundColor Green
        Write-Host ""
        
        $report.ModelBreakdown | ForEach-Object {
            Write-Host "  $($_.Model)" -ForegroundColor Yellow
            Write-Host "    Input:  $($_.InputTokens.ToString('N0')) tokens"
            Write-Host "    Output: $($_.OutputTokens.ToString('N0')) tokens"
            Write-Host "    Cost:   `$$($_.Cost.ToString('N2'))"
            Write-Host "    Sessions: $($_.SessionCount)"
            Write-Host ""
        }
        
        Write-Host "========================================`n" -ForegroundColor Cyan
        Write-Host "Note: Costs are estimated based on public pricing rates."
        Write-Host "Actual billing depends on your company's plan and negotiated rates."
        Write-Host "See: d:\_AI_GIT\copilot\skills\COPILOT-USAGE-QUERY.md`n"
    }
    
    'JSON' {
        $json = $report | ConvertTo-Json -Depth 10
        if ($OutputFile) {
            $json | Out-File $OutputFile -Encoding utf8
            Write-Host "Report saved to: $OutputFile" -ForegroundColor Green
        } else {
            Write-Output $json
        }
    }
    
    'CSV' {
        $csv = @()
        $csv += "Model,InputTokens,OutputTokens,EstimatedCostUSD,SessionCount"
        $report.ModelBreakdown | ForEach-Object {
            $csv += "$($_.Model),$($_.InputTokens),$($_.OutputTokens),$($_.Cost),$($_.SessionCount)"
        }
        $csv += ""
        $csv += "Summary"
        $csv += "Total Input Tokens,$($report.TotalInputTokens)"
        $csv += "Total Output Tokens,$($report.TotalOutputTokens)"
        $csv += "Total Cost,$($report.EstimatedCostUSD)"
        
        if ($OutputFile) {
            $csv | Out-File $OutputFile -Encoding utf8
            Write-Host "Report saved to: $OutputFile" -ForegroundColor Green
        } else {
            $csv | ForEach-Object { Write-Output $_ }
        }
    }
    
    'Markdown' {
        $md = @"
# Copilot Usage Report — $($report.Period)

## Summary
- **Period**: $($report.DateRange)
- **Sessions**: $($report.TotalSessions) total
- **Total Input Tokens**: $($report.TotalInputTokens.ToString('N0'))
- **Total Output Tokens**: $($report.TotalOutputTokens.ToString('N0'))
- **Estimated Cost**: `$$($report.EstimatedCostUSD.ToString('N2')) USD
$( if ($report.ProjectedMonthlySpend) { "`n- **Projected Month-End**: `$$($report.ProjectedMonthlySpend.ToString('N2')) USD ($($report.ProjectionNote))" } else { "" })

## Breakdown by Model

| Model | Input Tokens | Output Tokens | Estimated Cost | Sessions |
|-------|---|---|---|---|
$( $report.ModelBreakdown | ForEach-Object { "| $($_.Model) | $($_.InputTokens.ToString('N0')) | $($_.OutputTokens.ToString('N0')) | `$$($_.Cost.ToString('N2')) | $($_.SessionCount) |" } )

---

**Note**: Costs are estimated based on public pricing rates (Sept 2026). Actual billing depends on your company's plan and negotiated rates. See the full skill documentation at `d:\_AI_GIT\copilot\skills\COPILOT-USAGE-QUERY.md`.
"@
        
        if ($OutputFile) {
            $md | Out-File $OutputFile -Encoding utf8
            Write-Host "Report saved to: $OutputFile" -ForegroundColor Green
        } else {
            Write-Output $md
        }
    }
}
