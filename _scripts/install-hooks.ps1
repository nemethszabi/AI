<#
Installs this repo's tracked git hooks into .git\hooks\. Needed because .git\hooks\ itself isn't
version-controlled — the actual hook source lives in _scripts\hooks\ (tracked) and gets copied here.
Re-run this after pulling a change to _scripts\hooks\, or on a fresh clone.

Usage: powershell -File _scripts\install-hooks.ps1
#>

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$hookSourceDir = Join-Path $repoRoot '_scripts\hooks'
$gitHooksDir = Join-Path $repoRoot '.git\hooks'

if (-not (Test-Path $gitHooksDir)) {
    Write-Host "No .git\hooks\ found at $gitHooksDir - is this actually a git repo checkout?" -ForegroundColor Red
    exit 1
}

Get-ChildItem -Path $hookSourceDir -File | ForEach-Object {
    $dest = Join-Path $gitHooksDir $_.Name
    Copy-Item $_.FullName $dest -Force
    Write-Host "Installed: $($_.Name)" -ForegroundColor Green
}

Write-Host "Done. Hooks run automatically from now on - no further setup needed." -ForegroundColor Cyan
