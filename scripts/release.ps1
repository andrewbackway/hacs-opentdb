#!/usr/bin/env pwsh
[CmdletBinding()]
param(
    [ValidateSet("patch", "minor", "major")]
    [string]$Bump = "patch",
    [string]$Version,
    [string]$Remote = "origin",
    [switch]$NoPush,
    [switch]$NoRelease
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$ManifestPath = Join-Path $RepoRoot "custom_components/opentdb/manifest.json"
$ConstPath = Join-Path $RepoRoot "custom_components/opentdb/const.py"
$CardPath = Join-Path $RepoRoot "custom_components/opentdb/www/opentdb-card.js"
foreach ($path in @($ManifestPath, $ConstPath, $CardPath)) {
    if (-not (Test-Path $path)) { throw "Required file not found: $path" }
}

$manifestRaw = Get-Content $ManifestPath -Raw
if ($manifestRaw -notmatch '"version"\s*:\s*"(?<v>\d+\.\d+\.\d+)"') { throw "No semantic version found" }
$current = $Matches.v
if ($Version) {
    if ($Version -notmatch '^\d+\.\d+\.\d+$') { throw "Version must be X.Y.Z" }
    $new = $Version
} else {
    $parts = $current.Split("."); [int]$major = $parts[0]; [int]$minor = $parts[1]; [int]$patch = $parts[2]
    switch ($Bump) { "major" { $major++; $minor = 0; $patch = 0 } "minor" { $minor++; $patch = 0 } "patch" { $patch++ } }
    $new = "$major.$minor.$patch"
}
if ($new -eq $current) { throw "New version matches current version" }
$dirty = git -C $RepoRoot status --porcelain
if ($dirty) { throw "Working tree is not clean:`n$dirty" }
$manifestRaw = $manifestRaw -replace '("version"\s*:\s*")\d+\.\d+\.\d+(")', "`${1}$new`${2}"
Set-Content -Path $ManifestPath -Value $manifestRaw -NoNewline
$constRaw = Get-Content $ConstPath -Raw
$constRaw = $constRaw -replace '(VERSION\s*:\s*Final\s*=\s*")\d+\.\d+\.\d+(")', "`${1}$new`${2}"
Set-Content -Path $ConstPath -Value $constRaw -NoNewline
$tag = "v$new"
git -C $RepoRoot add "custom_components/opentdb/manifest.json" "custom_components/opentdb/const.py"
git -C $RepoRoot commit -m "Release $tag"
git -C $RepoRoot tag $tag
if ($NoPush) { Write-Host "Created $tag locally."; return }
$branch = git -C $RepoRoot rev-parse --abbrev-ref HEAD
git -C $RepoRoot push $Remote $branch
git -C $RepoRoot push $Remote $tag
if ($NoRelease) { return }
$gh = Get-Command gh -ErrorAction SilentlyContinue
if (-not $gh) { Write-Warning "gh not found; tag pushed without a GitHub release."; return }
gh release create $tag --repo andrewbackway/hacs-opentdb --title $tag --generate-notes
