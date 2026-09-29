param(
    [string]$Executable = ".build\server-cli.exe",
    [string]$OutDir = ".build",
    [string]$Version = "1.0.0"
)

$ErrorActionPreference = "Stop"
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path

if (-not [System.IO.Path]::IsPathRooted($Executable)) {
    $Executable = Join-Path $projectRoot $Executable
}
if (-not (Test-Path $Executable -PathType Leaf)) {
    throw "Executable not found: $Executable. Run scripts\build-executable.ps1 first."
}
if (-not [System.IO.Path]::IsPathRooted($OutDir)) {
    $OutDir = Join-Path $projectRoot $OutDir
}

New-Item -ItemType Directory -Path $OutDir -Force | Out-Null
$objDir = Join-Path $OutDir "msi-obj"
New-Item -ItemType Directory -Path $objDir -Force | Out-Null

$productObject = Join-Path $objDir "Product.wixobj"
$installer = Join-Path $OutDir "server-cli-$Version.msi"

Push-Location $projectRoot
try {
    & candle.exe `
        -nologo `
        -arch x64 `
        -dProductVersion="$Version" `
        -dServerCliExecutable="$Executable" `
        -ext WixUtilExtension `
        -out $productObject `
        "msi\wix\Product.wxs"
    if ($LASTEXITCODE -ne 0) { throw "candle.exe failed with exit code $LASTEXITCODE" }

    & light.exe `
        -nologo `
        -ext WixUtilExtension `
        -sval `
        -out $installer `
        $productObject
    if ($LASTEXITCODE -ne 0) { throw "light.exe failed with exit code $LASTEXITCODE" }
}
finally {
    Pop-Location
}

Write-Host "Built $installer"
