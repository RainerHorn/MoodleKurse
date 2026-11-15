<# Canonical repository files only. Default: read-only profile preview. #>
[CmdletBinding()]
param(
    [string]$RepoRoot = $PSScriptRoot,
    [string]$ProfilesRoot = "",
    [string]$ApplyPlan = "",
    [switch]$InstallHermes,
    [switch]$ForceRepoFiles,
    [switch]$SkipProfiles,
    [switch]$SkipMoodleMcp,
    [string]$MoodleMcpRoot = ""
)
$ErrorActionPreference = "Stop"
if ($ForceRepoFiles -or $InstallHermes -or $MoodleMcpRoot -or $SkipMoodleMcp) {
    throw "Alte Setup-Option entfernt. Siehe docs/hermes-setup.md: keine eingebetteten Regeln oder automatische Konfigurationsinstallation."
}
if ($SkipProfiles) {
    Write-Output "Profilabgleich uebersprungen; keine Aenderungen."
    exit 0
}
$syncArgs = @((Join-Path $RepoRoot "scripts/profile_sync.py"), "--repo", $RepoRoot)
if ($ProfilesRoot) { $syncArgs += @("--profiles", $ProfilesRoot) }
if ($ApplyPlan) { $syncArgs += @("--apply", $ApplyPlan) }
& python @syncArgs
if ($LASTEXITCODE -ne 0) { throw "Profilabgleich fehlgeschlagen (Exit $LASTEXITCODE)." }
