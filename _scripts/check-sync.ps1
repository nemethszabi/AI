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

# CLAUDE.md is HAND-MERGED into each destination (claude\README.md rollout step 4), never copied - each
# root may carry its own extra lines legitimately. Byte equality is therefore the wrong test; what matters
# is that every staged line is PRESENT somewhere in the destination. Returns the staged lines that aren't.
# Added 2026-09-05 after framework-review F-01/F-02: the staged req-*/sa: pointer block was missing from
# all three roots for 24 days and this script structurally could not see it.
function Get-MissingStagedLines($stagedPath, $livePath) {
    if (-not (Test-Path $stagedPath) -or -not (Test-Path $livePath)) { return @() }
    $liveLines = @{}
    foreach ($line in (Get-Content $livePath)) { $liveLines[$line.Trim()] = $true }
    $missingLines = @()
    foreach ($line in (Get-Content $stagedPath)) {
        $t = $line.Trim()
        if ($t -eq '') { continue }
        if (-not $liveLines.ContainsKey($t)) { $missingLines += $t }
    }
    return $missingLines
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

# Copilot side IS now checked (added 2026-09-05, framework-review F-02/F-08). The old comment here said it
# held "nothing to sync"; by then ~\.copilot already held 1 agent, 1 command, 3 Copilot skills and 5 shared
# skill folders. Source layout differs from the Claude side: Copilot gets its OWN AGENT-TEMPLATE-BASELINE.md
# and AGENTS.md/COPILOT.md from copilot\, but shares the other three doctrine files and the skills\ folders.
# Repo-side-only files (copilot\scripts\, copilot\README.md, the two USAGE-TRACKING docs) are deliberately
# not listed - they are documentation of the rollout, not part of it.
$copilotStaged = Get-FileHashMapRemapped $repoRoot @{
    'copilot\agents'   = 'agents'
    'copilot\commands' = 'commands'
    'copilot\skills'   = 'skills'
    'copilot\hooks'    = 'hooks'      # user-level hook files, added 2026-09-14 (framework-change-flag)
    'skills'           = 'skills'
    'dev-framework'    = 'dev-framework'
    'sa-framework'     = 'sa-framework'
}
foreach ($f in @('CONSTITUTION.md', 'AGENT-CONDUCT-BASELINE.md', 'DESIGN-PRINCIPLES-BASELINE.md')) {
    $p = Join-Path $repoRoot $f
    if (Test-Path $p) { $copilotStaged[$f] = Get-Sha256 $p }
}
# PORT-NOTES.md added 2026-09-07 with the full sa: pipeline port - it carries the six standing
# divergences every ported req-* agent cites instead of restating, so it is load-bearing at the live
# root, not repo-side documentation.
foreach ($f in @('AGENT-TEMPLATE-BASELINE.md', 'AGENTS.md', 'COPILOT.md', 'PORT-NOTES.md')) {
    $p = Join-Path $repoRoot "copilot\$f"
    if (Test-Path $p) { $copilotStaged[$f] = Get-Sha256 $p }
}
# copilot\agents\README.md documents the folder for a repo reader; it is not part of the rollout.
# (copilot\skills\README.md IS rolled out - Copilot reads it - so only this one is dropped.)
$copilotStaged.Remove('agents\README.md') | Out-Null

# DELIBERATELY NOT PORTED to Copilot - absence here is the intended state, not drift.
# A thin dispatcher skill is useless without its agent, and these agents have no Copilot counterpart
# (the req-*/dev-* families are a standing scope decision). Reporting them MISSING every run would
# train the reader to ignore this section - and did real damage on 2026-09-07, when the first run of
# this Copilot check listed framework-review as MISSING and it was duly "fixed" by rolling it out,
# producing a /framework-review on the Copilot side that dispatches an agent that isn't there.
# Add to this list only with the matching note in copilot\README.md; never to silence a real gap.
$copilotNotPorted = @(
    'skills\framework-review\SKILL.md'   # -> framework-strategist, Claude-side only
)
foreach ($k in $copilotNotPorted) { $copilotStaged.Remove($k) | Out-Null }

$anyDrift = $false
$anyAdvisory = $false

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

    # Hand-merged file - advisory only, never counted as STALE (see Get-MissingStagedLines).
    $claudeMdMissing = Get-MissingStagedLines (Join-Path $repoRoot 'claude\CLAUDE.md') (Join-Path $destRoot 'CLAUDE.md')

    if ($missing.Count -eq 0 -and $stale.Count -eq 0 -and $extra.Count -eq 0 -and $claudeMdMissing.Count -eq 0) {
        Write-Host "  IN SYNC" -ForegroundColor Green
    } else {
        if ($missing.Count -gt 0 -or $stale.Count -gt 0 -or $extra.Count -gt 0) { $anyDrift = $true }
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
        if ($claudeMdMissing.Count -gt 0) {
            $anyAdvisory = $true
            Write-Host "  ADVISORY-DRIFT - staged claude\CLAUDE.md has $($claudeMdMissing.Count) line(s) absent from this root's CLAUDE.md:" -ForegroundColor Magenta
            $claudeMdMissing | Select-Object -First 12 | ForEach-Object { Write-Host "    $_" }
            if ($claudeMdMissing.Count -gt 12) { Write-Host "    ... and $($claudeMdMissing.Count - 12) more" }
            Write-Host "    -> hand-merge these (rollout step 4). Do NOT -Force copy; this file is merged, not copied." -ForegroundColor Magenta
        }
    }
    Write-Host ""
}

# --- Copilot CLI destination -------------------------------------------------------------------
$copilotRoot = Join-Path $env:USERPROFILE '.copilot'
Write-Host "=== copilot CLI  ($copilotRoot) ===" -ForegroundColor Cyan
if (-not (Test-Path $copilotRoot)) {
    Write-Host "  Root does not exist - skipping (not set up on this machine)." -ForegroundColor DarkGray
} else {
    $copilotLive = Get-FileHashMap $copilotRoot @('agents', 'commands', 'skills', 'hooks', 'dev-framework', 'sa-framework')
    foreach ($f in @('CONSTITUTION.md', 'AGENT-CONDUCT-BASELINE.md', 'DESIGN-PRINCIPLES-BASELINE.md',
                     'AGENT-TEMPLATE-BASELINE.md', 'AGENTS.md', 'COPILOT.md', 'PORT-NOTES.md')) {
        $p = Join-Path $copilotRoot $f
        if (Test-Path $p) { $copilotLive[$f] = Get-Sha256 $p }
    }

    $cMissing = @(); $cStale = @(); $cExtra = @()
    foreach ($key in $copilotStaged.Keys) {
        if (-not $copilotLive.ContainsKey($key)) { $cMissing += $key }
        elseif ($copilotLive[$key] -ne $copilotStaged[$key]) { $cStale += $key }
    }
    foreach ($key in $copilotLive.Keys) {
        if (-not $copilotStaged.ContainsKey($key)) { $cExtra += $key }
    }

    if ($cMissing.Count -eq 0 -and $cStale.Count -eq 0 -and $cExtra.Count -eq 0) {
        Write-Host "  IN SYNC" -ForegroundColor Green
    } else {
        $anyDrift = $true
        if ($cMissing.Count -gt 0) {
            Write-Host "  MISSING (staged here, never copied to this destination):" -ForegroundColor Yellow
            $cMissing | ForEach-Object { Write-Host "    $_" }
        }
        if ($cStale.Count -gt 0) {
            Write-Host "  STALE (content differs - re-copy needed):" -ForegroundColor Yellow
            $cStale | ForEach-Object { Write-Host "    $_" }
        }
        if ($cExtra.Count -gt 0) {
            Write-Host "  EXTRA (not staged here - check if intentional):" -ForegroundColor DarkYellow
            $cExtra | ForEach-Object { Write-Host "    $_" }
        }
    }
}
Write-Host ""

if ($anyDrift) {
    Write-Host "Run the Rollout Copy-Item steps in claude\README.md (all three Claude destinations, plus" -ForegroundColor Cyan
    Write-Host "the Copilot rollout in copilot\README.md) to fix." -ForegroundColor Cyan
}
if ($anyAdvisory) {
    Write-Host "CLAUDE.md advisory drift above is fixed by HAND-MERGING (rollout step 4), not by copying." -ForegroundColor Magenta
}
if (-not $anyDrift -and -not $anyAdvisory) {
    Write-Host "All destinations fully in sync (including CLAUDE.md containment and the Copilot root)." -ForegroundColor Green
}
