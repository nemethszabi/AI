<#
Checks whether every live Claude Code config location actually matches this repo's staged
agents\/skills\/commands\/doctrine files (sourced from claude\agents\, claude\commands\, and the shared
root doctrine/skills). This repo is the source of truth; drift means the Rollout step (claude\README.md)
was missed or a file changed only on one side.

IMPORTANT (added 2026-08-10, after a real dev-backend-not-found failure): this machine has THREE
independent Claude Code config locations, not one - $env:USERPROFILE\.claude\ (default/legacy, "avoid for
new work" per mcp-reference.md) plus two active profiles (claude-scm, claude-nsz), each fully redirected
via CLAUDE_CONFIG_DIR and NOT falling back to the default location. Rolling out to only one of the three
silently leaves the other two without dev-backend/agent-reviewer/etc. - exactly what happened before this
fix. Checks all three every time, not just the default.

Usage: powershell -File _scripts\check-sync.ps1
#>

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot

$destinations = @(
    @{ Name = 'default (~\.claude, legacy)'; Root = (Join-Path $env:USERPROFILE '.claude') },
    @{ Name = 'claude-scm profile';          Root = (Join-Path $env:LOCALAPPDATA 'claude-scm') },
    @{ Name = 'claude-nsz profile';          Root = (Join-Path $env:LOCALAPPDATA 'claude-nsz') }
)

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

# Same as Get-FileHashMap, but the source dir (under $root) and the key prefix a destination would use
# can differ - needed because agents\/commands\ live at claude\agents\/claude\commands\ in this repo's
# own source layout, but still land at agents\/commands\ (no claude\ prefix) in every Claude destination.
function Get-FileHashMapRemapped($root, $dirMap) {
    $map = @{}
    foreach ($sourceDir in $dirMap.Keys) {
        $keyPrefix = $dirMap[$sourceDir]
        $full = Join-Path $root $sourceDir
        if (-not (Test-Path $full)) { continue }
        Get-ChildItem -Path $full -Recurse -File | ForEach-Object {
            $relFromSourceDir = $_.FullName.Substring($full.Length).TrimStart('\')
            $map[(Join-Path $keyPrefix $relFromSourceDir)] = Get-Sha256 $_.FullName
        }
    }
    return $map
}

$staged = Get-FileHashMap $repoRoot @('skills', 'dev-framework', 'sa-framework')
$stagedClaudeOnly = Get-FileHashMapRemapped $repoRoot @{ 'claude\agents' = 'agents'; 'claude\commands' = 'commands' }
foreach ($key in $stagedClaudeOnly.Keys) { $staged[$key] = $stagedClaudeOnly[$key] }

# Used for the LIVE side below (every destination still has all four flat, unchanged by the move).
$doctrineFiles = @('CONSTITUTION.md', 'AGENT-CONDUCT-BASELINE.md', 'DESIGN-PRINCIPLES-BASELINE.md', 'AGENT-TEMPLATE-BASELINE.md')

# Staged side: the first three still sit flat at the repo root; AGENT-TEMPLATE-BASELINE.md moved to
# claude\ and is read from there, but still compared against each destination's own flat
# AGENT-TEMPLATE-BASELINE.md (only the source moved, not the destination filename/location).
foreach ($f in @('CONSTITUTION.md', 'AGENT-CONDUCT-BASELINE.md', 'DESIGN-PRINCIPLES-BASELINE.md')) {
    $stagedPath = Join-Path $repoRoot $f
    if (Test-Path $stagedPath) { $staged[$f] = Get-Sha256 $stagedPath }
}
$stagedTemplateBaseline = Join-Path $repoRoot 'claude\AGENT-TEMPLATE-BASELINE.md'
if (Test-Path $stagedTemplateBaseline) { $staged['AGENT-TEMPLATE-BASELINE.md'] = Get-Sha256 $stagedTemplateBaseline }

# Copilot side (copilot\agents\, copilot\skills\) is intentionally not checked yet - nothing to sync
# until it holds real files. Add a matching check here once the first Copilot agent/skill is authored.

$anyDrift = $false

foreach ($dest in $destinations) {
    $destName = $dest.Name
    $destRoot = $dest.Root

    Write-Host "=== $destName  ($destRoot) ===" -ForegroundColor Cyan

    if (-not (Test-Path $destRoot)) {
        Write-Host "  Root does not exist - skipping (not set up on this machine)." -ForegroundColor DarkGray
        Write-Host ""
        continue
    }

    $live = Get-FileHashMap $destRoot @('agents', 'skills', 'commands', 'dev-framework', 'sa-framework')
    foreach ($f in $doctrineFiles) {
        $livePath = Join-Path $destRoot $f
        if (Test-Path $livePath) { $live[$f] = Get-Sha256 $livePath }
    }

    $missing = @()
    $stale = @()
    $extra = @()

    foreach ($key in $staged.Keys) {
        if (-not $live.ContainsKey($key)) {
            $missing += $key
        } elseif ($live[$key] -ne $staged[$key]) {
            $stale += $key
        }
    }
    foreach ($key in $live.Keys) {
        if (-not $staged.ContainsKey($key)) {
            $extra += $key
        }
    }

    if ($missing.Count -eq 0 -and $stale.Count -eq 0 -and $extra.Count -eq 0) {
        Write-Host "  IN SYNC" -ForegroundColor Green
    } else {
        $anyDrift = $true
        if ($missing.Count -gt 0) {
            Write-Host "  MISSING (staged here, never copied to this destination):" -ForegroundColor Yellow
            $missing | ForEach-Object { Write-Host "    $_" }
        }
        if ($stale.Count -gt 0) {
            Write-Host "  STALE (content differs - re-copy needed):" -ForegroundColor Yellow
            $stale | ForEach-Object { Write-Host "    $_" }
        }
        if ($extra.Count -gt 0) {
            Write-Host "  EXTRA (not staged here - check if intentional):" -ForegroundColor DarkYellow
            $extra | ForEach-Object { Write-Host "    $_" }
        }
    }
    Write-Host ""
}

if ($anyDrift) {
    Write-Host "Run the Rollout Copy-Item steps in claude\README.md (all three destinations) to fix." -ForegroundColor Cyan
} else {
    Write-Host "All destinations fully in sync." -ForegroundColor Green
}
