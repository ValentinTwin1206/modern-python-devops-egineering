<#
.SYNOPSIS
    Compile the Simply Journal Admin MSI from the WiX sources.

.DESCRIPTION
    Stages an offline installation layout containing an embedded Python runtime,
    the unpacked project wheel, and a generated launcher, then harvests that
    payload into WiX so the resulting MSI needs no internet access and performs
    no install-time pip or virtualenv work. Run from the project root so the
    relative WiX source paths resolve.

.PARAMETER WheelDir
    Directory containing the built simply_journal_admin-*.whl.

.PARAMETER OutDir
    Directory the finished .msi is written to.

.PARAMETER Version
    MSI ProductVersion. Defaults to the version embedded in the wheel name.

.PARAMETER PythonCommand
    Python executable used to source the embedded runtime payload.
#>
param(
    [string]$WheelDir = "C:\build\wheel",
    [string]$OutDir = "C:\build",
    [string]$Version = "",
    [string]$PythonCommand = "python"
)

$ErrorActionPreference = "Stop"

function Copy-RuntimePath {
    param(
        [string]$Source,
        [string]$Destination
    )

    if (Test-Path $Source) {
        Copy-Item -Path $Source -Destination $Destination -Recurse -Force
    }
}

$wheel = Get-ChildItem -Path $WheelDir -Filter "simply_journal_admin-*.whl" |
    Sort-Object Name | Select-Object -Last 1
if ($null -eq $wheel) {
    throw "No wheel found under $WheelDir"
}

if ([string]::IsNullOrEmpty($Version)) {
    if ($wheel.Name -match "simply_journal_admin-([0-9][0-9A-Za-z.\-]*)-py3") {
        $Version = $Matches[1]
    } else {
        $Version = "0.0.0"
    }
}

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$objDir = Join-Path $OutDir "obj"
New-Item -ItemType Directory -Force -Path $objDir | Out-Null

$stageRoot = Join-Path $objDir "stage"
if (Test-Path $stageRoot) {
    Remove-Item -Path $stageRoot -Recurse -Force
}

$runtimeDir = Join-Path $stageRoot "runtime"
$sitePackagesDir = Join-Path $stageRoot "app\site-packages"
New-Item -ItemType Directory -Force -Path $runtimeDir, $sitePackagesDir | Out-Null

$pythonInfoJson = & $PythonCommand -c "import json, sys; print(json.dumps({'base_prefix': sys.base_prefix, 'major': sys.version_info.major, 'minor': sys.version_info.minor}))"
if ($LASTEXITCODE -ne 0) {
    throw "Unable to inspect Python runtime via '$PythonCommand'"
}
$pythonInfo = $pythonInfoJson | ConvertFrom-Json
$pythonRoot = $pythonInfo.base_prefix
$pythonVersionTag = "{0}{1}" -f $pythonInfo.major, $pythonInfo.minor

Write-Host "Staging embedded Python runtime from $pythonRoot"
foreach ($pattern in @("python.exe", "pythonw.exe", "python$pythonVersionTag.dll", "python3.dll", "vcruntime*.dll")) {
    Get-ChildItem -Path $pythonRoot -Filter $pattern -ErrorAction SilentlyContinue |
        ForEach-Object {
            Copy-Item -Path $_.FullName -Destination $runtimeDir -Force
        }
}
Copy-RuntimePath -Source (Join-Path $pythonRoot "DLLs") -Destination $runtimeDir
Copy-RuntimePath -Source (Join-Path $pythonRoot "Lib") -Destination $runtimeDir
Copy-RuntimePath -Source (Join-Path $pythonRoot "LICENSE.txt") -Destination $runtimeDir
Remove-Item -Path (Join-Path $runtimeDir "Lib\site-packages") -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "Extracting wheel payload to $sitePackagesDir"
& $PythonCommand -m zipfile -e $wheel.FullName $sitePackagesDir
if ($LASTEXITCODE -ne 0) {
    throw "Failed to extract wheel $($wheel.FullName)"
}

$launcher = Join-Path $stageRoot "simply-journal-admin.cmd"
$launcherContent = @"
@echo off
setlocal
set "PYTHONHOME=%~dp0runtime"
set "PYTHONPATH=%~dp0app\site-packages"
"%~dp0runtime\python.exe" -m simply_journal_admin.cli %*
"@
Set-Content -Path $launcher -Value $launcherContent -Encoding Ascii

$harvest = Join-Path $objDir "Harvest.wxs"
$productObj = Join-Path $objDir "Product.wixobj"
$harvestObj = Join-Path $objDir "Harvest.wixobj"
$msi = Join-Path $OutDir "simply-journal-admin-$Version.msi"

Write-Host "Building MSI $msi from wheel $($wheel.Name)"

& heat.exe `
    dir $stageRoot `
    -nologo `
    -cg StagedPayload `
    -dr INSTALLFOLDER `
    -gg `
    -g1 `
    -sfrag `
    -srd `
    -var var.StageRoot `
    -out $harvest
if ($LASTEXITCODE -ne 0) { throw "heat.exe failed with exit code $LASTEXITCODE" }

& candle.exe `
    -nologo `
    -arch x64 `
    -dProductVersion="$Version" `
    -ext WixUtilExtension `
    -out $productObj `
    "msi\wix\Product.wxs"
if ($LASTEXITCODE -ne 0) { throw "candle.exe failed with exit code $LASTEXITCODE" }

& candle.exe `
    -nologo `
    -arch x64 `
    -dStageRoot="$stageRoot" `
    -ext WixUtilExtension `
    -out $harvestObj `
    $harvest
if ($LASTEXITCODE -ne 0) { throw "candle.exe failed with exit code $LASTEXITCODE" }

& light.exe `
    -nologo `
    -ext WixUtilExtension `
    -sval `
    -out $msi `
    $productObj `
    $harvestObj
if ($LASTEXITCODE -ne 0) { throw "light.exe failed with exit code $LASTEXITCODE" }

Write-Host "Wrote $msi"
