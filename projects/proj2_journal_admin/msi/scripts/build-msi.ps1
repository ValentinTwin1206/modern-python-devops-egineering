<#
.SYNOPSIS
    Compile the Simply Journal Admin MSI from the WiX sources.

.DESCRIPTION
    Locates the built wheel, then runs the WiX v3 toolchain (candle + light) to
    produce simply-journal-admin-<version>.msi. Run from the project root so the
    relative WiX source paths resolve.

.PARAMETER WheelDir
    Directory containing the built simply_journal_admin-*.whl.

.PARAMETER OutDir
    Directory the finished .msi is written to.

.PARAMETER Version
    MSI ProductVersion. Defaults to the version embedded in the wheel name.
#>
param(
    [string]$WheelDir = "C:\build\wheel",
    [string]$OutDir   = "C:\build",
    [string]$Version  = ""
)

$ErrorActionPreference = "Stop"

$wheel = Get-ChildItem -Path $WheelDir -Filter "simply_journal_admin-*.whl" |
    Sort-Object Name | Select-Object -Last 1
if ($null -eq $wheel) {
    throw "No wheel found under $WheelDir"
}

if ([string]::IsNullOrEmpty($Version)) {
    # simply_journal_admin-2.0.0-py3-none-any.whl -> 2.0.0
    if ($wheel.Name -match "simply_journal_admin-([0-9][0-9A-Za-z.\-]*)-py3") {
        $Version = $Matches[1]
    } else {
        $Version = "0.0.0"
    }
}

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$objDir = Join-Path $OutDir "obj"
New-Item -ItemType Directory -Force -Path $objDir | Out-Null

$wixObj = Join-Path $objDir "Product.wixobj"
$msi    = Join-Path $OutDir "simply-journal-admin-$Version.msi"

Write-Host "Building MSI $msi from wheel $($wheel.Name)"

& candle.exe `
    -nologo `
    -arch x64 `
    -dWheelSource="$($wheel.FullName)" `
    -dWheelName="$($wheel.Name)" `
    -dProductVersion="$Version" `
    -ext WixUtilExtension `
    -out $wixObj `
    "msi\wix\Product.wxs"
if ($LASTEXITCODE -ne 0) { throw "candle.exe failed with exit code $LASTEXITCODE" }

& light.exe `
    -nologo `
    -ext WixUtilExtension `
    -sval `
    -out $msi `
    $wixObj
if ($LASTEXITCODE -ne 0) { throw "light.exe failed with exit code $LASTEXITCODE" }

Write-Host "Wrote $msi"
