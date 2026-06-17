<#
.SYNOPSIS
    Create the virtual environment for Simply Journal Admin and install the
    shipped wheel into it.

.DESCRIPTION
    Invoked as a deferred custom action by the MSI (and usable manually). The
    system Python interpreter is never modified: a dedicated venv is created
    under <InstallRoot>\venv, the prebuilt wheel from <InstallRoot>\wheel is
    installed into it, and the pywin32 binding is added so the Windows Event
    Log backend uses the fast native API. A simply-journal-admin.cmd launcher is
    written to the install root.
#>
param(
    [string]$InstallRoot = "C:\Program Files\SimplyJournalAdmin"
)

$ErrorActionPreference = "Stop"

$venvDir  = Join-Path $InstallRoot "venv"
$wheelDir = Join-Path $InstallRoot "wheel"
$pythonExe = Join-Path $venvDir "Scripts\python.exe"
$pipExe    = Join-Path $venvDir "Scripts\pip.exe"

# 1. Create the virtual environment if it does not already exist.
if (-not (Test-Path $pythonExe)) {
    Write-Host "Creating virtual environment at $venvDir"
    & python -m venv $venvDir
}

# 2. Upgrade pip (best effort; offline hosts continue).
try {
    & $pythonExe -m pip install --upgrade pip
} catch {
    Write-Warning "Could not upgrade pip: $_"
}

# 3. Install the shipped wheel and the Windows extra (pywin32).
$wheel = Get-ChildItem -Path $wheelDir -Filter "simply_journal_admin-*.whl" |
    Sort-Object Name | Select-Object -Last 1
if ($null -eq $wheel) {
    throw "No wheel found under $wheelDir"
}
Write-Host "Installing $($wheel.Name) into the virtual environment"
& $pipExe install --upgrade --no-deps $wheel.FullName
& $pipExe install --upgrade "pywin32>=306"

# 4. Write a launcher that forwards to the venv entry point.
$launcher = Join-Path $InstallRoot "simply-journal-admin.cmd"
$venvExe  = Join-Path $venvDir "Scripts\simply-journal-admin.exe"
$content  = "@echo off`r`n`"$venvExe`" %*`r`n"
Set-Content -Path $launcher -Value $content -Encoding Ascii
Write-Host "Wrote launcher $launcher"
