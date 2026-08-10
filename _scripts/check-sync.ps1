<#
Checks whether ~\.claude\ (live) actually matches this repo's staged agents\/skills\/commands\/doctrine
files. This repo is the source of truth; drift means the Rollout step (README.md) was missed or a file
changed only on one side. Run after any edit here, before assuming ~\.claude\ picked it up.

Usage: powershell -File _scripts\check-sync.ps1
#>

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$globalRoot = Join-Path $env:USERPROFILE '.claude'

function Get-Sha256($path) {
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        $bytes = [System.IO.File]::ReadAllBytes($path)
        return [BitConverter]::ToString($sha.ComputeHash($bytes)) -replace '-', ''
    } finally {
        $sha.Dispose()
    }
}

function Get-FileHashMap($root, $relativeDirs) {
    $map = @{}
    foreach ($dir in $relativeDirs) {
        $full = Join-Path $root $dir
        if (-not (Test-Path $full)) { continue }
        Get-ChildItem -Path $full -Recurse -File | ForEach-Object {
            $rel = $_.FullName.Substring($root.Length).TrimStart('\')
            $map[$rel] = Get-Sha256 $_.FullName
        }
    }
    return $map
}

$staged = Get-FileHashMap $repoRoot @('agents', 'skills', 'commands')
$live = Get-FileHashMap $globalRoot @('agents', 'skills', 'commands')

# Doctrine files copied flat to global root, not into a subfolder
$doctrineFiles = @('CONSTITUTION.md', 'AGENT-CONDUCT-BASELINE.md', 'AGENT-TEMPLATE-BASELINE.md', 'DESIGN-PRINCIPLES-BASELINE.md')
foreach ($f in $doctrineFiles) {
    $stagedPath = Join-Path $repoRoot $f
    $livePath = Join-Path $globalRoot $f
    if (Test-Path $stagedPath) { $staged[$f] = Get-Sha256 $stagedPath }
    if (Test-Path $livePath) { $live[$f] = Get-Sha256 $livePath }
}

$missingInGlobal = @()
$staleInGlobal = @()
$extraInGlobal = @()

foreach ($key in $staged.Keys) {
    if (-not $live.ContainsKey($key)) {
        $missingInGlobal += $key
    } elseif ($live[$key] -ne $staged[$key]) {
        $staleInGlobal += $key
    }
}
foreach ($key in $live.Keys) {
    if (-not $staged.ContainsKey($key)) {
        $extraInGlobal += $key
    }
}

Write-Host "=== Sync check: $repoRoot  vs  $globalRoot ===" -ForegroundColor Cyan
Write-Host ""

if ($missingInGlobal.Count -eq 0 -and $staleInGlobal.Count -eq 0 -and $extraInGlobal.Count -eq 0) {
    Write-Host "IN SYNC - every staged file matches global, nothing extra." -ForegroundColor Green
} else {
    if ($missingInGlobal.Count -gt 0) {
        Write-Host "MISSING in global (staged here, never copied):" -ForegroundColor Yellow
        $missingInGlobal | ForEach-Object { Write-Host "  $_" }
        Write-Host ""
    }
    if ($staleInGlobal.Count -gt 0) {
        Write-Host "STALE in global (content differs - re-copy needed):" -ForegroundColor Yellow
        $staleInGlobal | ForEach-Object { Write-Host "  $_" }
        Write-Host ""
    }
    if ($extraInGlobal.Count -gt 0) {
        Write-Host "EXTRA in global (not staged here - check if intentional):" -ForegroundColor DarkYellow
        $extraInGlobal | ForEach-Object { Write-Host "  $_" }
        Write-Host ""
    }
    Write-Host "Run the Rollout Copy-Item steps in README.md to fix MISSING/STALE." -ForegroundColor Cyan
}
