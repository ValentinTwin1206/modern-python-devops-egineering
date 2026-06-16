<#
.SYNOPSIS
    Remove the Simply Journal Admin virtual environment and launcher.

.DESCRIPTION
    Invoked as a deferred custom action during MSI uninstall (and usable
    manually). Files tracked by the MSI (the wheel and scripts) are removed by
    Windows Installer itself; this script only removes the dynamically created
    venv and the generated launcher.
#>
param(
    [string]$InstallRoot = "C:\Program Files\SimplyJournalAdmin"
)

$ErrorActionPreference = "SilentlyContinue"

$venvDir  = Join-Path $InstallRoot "venv"
$launcher = Join-Path $InstallRoot "simply-journal-admin.cmd"

if (Test-Path $venvDir) {
    Write-Host "Removing virtual environment $venvDir"
    Remove-Item -Path $venvDir -Recurse -Force
}
if (Test-Path $launcher) {
    Write-Host "Removing launcher $launcher"
    Remove-Item -Path $launcher -Force
}
