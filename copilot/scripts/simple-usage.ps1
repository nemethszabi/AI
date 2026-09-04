#!/usr/bin/env pwsh
# Simple Copilot usage query - copy-paste friendly
# Usage: & 'd:\_AI_GIT\copilot\scripts\simple-usage.ps1'

Import-Module pssqlite -EA Stop
$db = "$env:USERPROFILE\.copilot\session-store.db"
$conn = New-SQLiteConnection -DataSource $db

$data = Invoke-SQLiteQuery -SQLiteConnection $conn -Query @"
SELECT model, COUNT(*) events, SUM(input_tokens) input_toks, SUM(output_tokens) output_toks
FROM assistant_usage_events WHERE DATE(created_at) >= DATE('now', '-30 days')
GROUP BY model ORDER BY input_toks + output_toks DESC
"@

$conn.Close()

$pricing = @{'claude-opus-4.8' = @{i=15;o=75}; 'claude-sonnet-5' = @{i=3;o=15}; 'gpt-5.5' = @{i=20;o=60}; 'gemini-3.7-flash' = @{i=0.075;o=0.30}}
$default = @{i=3;o=15}

"`n=== COPILOT USAGE ===" | Write-Host -ForegroundColor Cyan
$totalCost = 0

if ($data) {
    foreach ($row in @($data)) {
        $r = $pricing[$row.model] ?? $default
        $cost = ($row.input_toks / 1e6 * $r.i) + ($row.output_toks / 1e6 * $r.o)
        $totalCost += $cost
        "$($row.model): Input=$($row.input_toks) Output=$($row.output_toks) Cost=`$$($cost.ToString('F2'))" | Write-Host
    }
    "`nTOTAL COST: `$$($totalCost.ToString('F2'))" | Write-Host -ForegroundColor Green
} else {
    "No usage found yet. Run 'copilot' first, ask it something, then exit and try again." | Write-Host -ForegroundColor Yellow
}
"`n" | Write-Host
