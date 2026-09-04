#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Query current month's Copilot CLI usage: tokens and estimated cost by model.

.EXAMPLE
    & 'd:\_AI_GIT\copilot\scripts\Get-CopilotUsage-Fixed.ps1'
#>

# Import SQLite module
try {
    Import-Module pssqlite -ErrorAction Stop
} catch {
    Write-Host "Error: pssqlite module not found. Install with: Install-Module pssqlite -Scope CurrentUser" -ForegroundColor Red
    exit 1
}

$dbPath = "$env:USERPROFILE\.copilot\session-store.db"

# Validate database exists
if (-not (Test-Path $dbPath)) {
    Write-Error "Database not found at $dbPath. Run 'copilot' first."
    exit 1
}

$connection = New-SQLiteConnection -DataSource $dbPath

# Query usage events
$query = @"
    SELECT 
        model,
        COUNT(*) as event_count,
        SUM(CAST(input_tokens as INTEGER)) as total_input,
        SUM(CAST(output_tokens as INTEGER)) as total_output,
        MAX(created_at) as last_event
    FROM assistant_usage_events
    WHERE DATE(created_at) >= DATE('now', '-30 days')
    GROUP BY model
    ORDER BY (total_input + total_output) DESC
"@

try {
    $data = Invoke-SQLiteQuery -SQLiteConnection $connection -Query $query
} catch {
    Write-Host "Error querying database: $_" -ForegroundColor Red
    $connection.Close()
    exit 1
}

# Pricing rates (Sept 2026)
$pricing = @{
    'claude-opus-4.8' = @{ Input = 15; Output = 75 }
    'claude-opus-4.7' = @{ Input = 15; Output = 75 }
    'claude-sonnet-5' = @{ Input = 3; Output = 15 }
    'claude-haiku-4.5' = @{ Input = 0.80; Output = 4 }
    'gpt-5.5' = @{ Input = 20; Output = 60 }
    'gpt-5.4' = @{ Input = 10; Output = 30 }
    'gpt-5-mini' = @{ Input = 0.15; Output = 0.60 }
    'gemini-3.7-flash' = @{ Input = 0.075; Output = 0.30 }
    'gemini-3.5-flash' = @{ Input = 0.075; Output = 0.30 }
}

$default = @{ Input = 3; Output = 15 }

# Calculate totals
$totalInputAll = 0
$totalOutputAll = 0
$totalCostAll = 0
$results = @()

if ($data) {
    foreach ($row in @($data)) {
        $model = $row.model
        $inTokens = [int]($row.total_input ?? 0)
        $outTokens = [int]($row.total_output ?? 0)
        
        $rate = $pricing[$model] ?? $default
        $inCost = ($inTokens / 1000000) * $rate.Input
        $outCost = ($outTokens / 1000000) * $rate.Output
        $cost = $inCost + $outCost
        
        $totalInputAll += $inTokens
        $totalOutputAll += $outTokens
        $totalCostAll += $cost
        
        $results += [PSCustomObject]@{
            Model = $model
            InputTokens = $inTokens
            OutputTokens = $outTokens
            Cost = $cost
            Events = $row.event_count
        }
    }
}

$connection.Close()

# Display output
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  COPILOT USAGE REPORT" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($results.Count -gt 0) {
    Write-Host "Summary:" -ForegroundColor Green
    Write-Host "  Input Tokens:  $($totalInputAll.ToString('N0'))"
    Write-Host "  Output Tokens: $($totalOutputAll.ToString('N0'))"
    Write-Host "  Total Tokens:  $($($totalInputAll + $totalOutputAll).ToString('N0'))"
    Write-Host "  Estimated Cost: USD $($totalCostAll.ToString('F2'))"
    Write-Host ""
    
    Write-Host "Breakdown by Model:" -ForegroundColor Green
    Write-Host ""
    
    foreach ($r in $results) {
        Write-Host "  $($r.Model)" -ForegroundColor Yellow
        Write-Host "    Input:  $($r.InputTokens.ToString('N0')) tokens"
        Write-Host "    Output: $($r.OutputTokens.ToString('N0')) tokens"
        Write-Host "    Cost:   USD $($r.Cost.ToString('F2'))"
        Write-Host "    Events: $($r.Events)"
        Write-Host ""
    }
} else {
    Write-Host "No usage data found (last 30 days)." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To generate usage:" -ForegroundColor Cyan
    Write-Host "  1. Run: copilot" -ForegroundColor White
    Write-Host "  2. Ask it something" -ForegroundColor White
    Write-Host "  3. Exit and run this script again" -ForegroundColor White
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Note: Costs are estimated (public API rates, Sept 2026)." -ForegroundColor Gray
Write-Host "Actual billing depends on your company plan." -ForegroundColor Gray
