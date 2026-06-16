<#
.SYNOPSIS
    Register Simply Journal Admin as a Windows service using NSSM.

.DESCRIPTION
    NSSM (the Non-Sucking Service Manager) wraps the console-script entry point
    from the dedicated virtual environment as an auto-starting Windows service
    with restart-on-failure semantics. Run from an elevated PowerShell prompt.

.PARAMETER InstallRoot
    Install root containing the venv.

.PARAMETER Nssm
    Path to nssm.exe (defaults to 'nssm' on PATH).
#>
param(
    [string]$InstallRoot = "C:\Program Files\SimplyJournalAdmin",
    [string]$Nssm = "nssm"
)

$ErrorActionPreference = "Stop"

$ServiceName = "SimplyJournalAdmin"
$DisplayName = "Simply Journal Admin"
$exe = Join-Path $InstallRoot "venv\Scripts\simply-journal-admin.exe"
$logFile = Join-Path $InstallRoot "simply-journal-admin.log"

if (-not (Test-Path $exe)) {
    throw "Console script not found: $exe (run install-venv.ps1 first)"
}

Write-Host "Registering service '$ServiceName' via NSSM"
& $Nssm install $ServiceName $exe "--follow" "--format" "json"
& $Nssm set $ServiceName DisplayName $DisplayName
& $Nssm set $ServiceName Description "Tails the Windows Event Log as JSON via simply-journal-admin."
& $Nssm set $ServiceName Start SERVICE_AUTO_START
& $Nssm set $ServiceName AppExit Default Restart
& $Nssm set $ServiceName AppRestartDelay 5000
& $Nssm set $ServiceName AppStdout $logFile
& $Nssm set $ServiceName AppStderr $logFile

Start-Service $ServiceName
Write-Host "Service '$ServiceName' installed and started."
