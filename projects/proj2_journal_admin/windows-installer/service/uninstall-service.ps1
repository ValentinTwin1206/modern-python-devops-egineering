<#
.SYNOPSIS
    Stop and remove the Simply Journal Admin Windows service (NSSM).

.DESCRIPTION
    Reverses install-service.ps1. Run from an elevated PowerShell prompt.
#>
param(
    [string]$Nssm = "nssm"
)

$ErrorActionPreference = "SilentlyContinue"

$ServiceName = "SimplyJournalAdmin"

if (Get-Service -Name $ServiceName -ErrorAction SilentlyContinue) {
    Write-Host "Stopping service '$ServiceName'"
    Stop-Service $ServiceName -Force
    & $Nssm remove $ServiceName confirm
    Write-Host "Service '$ServiceName' removed."
} else {
    Write-Host "Service '$ServiceName' is not installed."
}
