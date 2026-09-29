$ErrorActionPreference = "Stop"

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$buildDir = if ($env:BUILD_DIR) { $env:BUILD_DIR } else { Join-Path $projectRoot ".build" }

New-Item -ItemType Directory -Path $buildDir -Force | Out-Null
$executable = Join-Path $buildDir "server-cli.exe"
Remove-Item $executable -Force -ErrorAction SilentlyContinue

Push-Location $projectRoot
try {
    $sitePackages = uv run python -c "import site; print(site.getsitepackages()[0])"
    $env:PYTHONPATH = "$projectRoot\src;$sitePackages"

    nuitka `
        --onefile `
        --assume-yes-for-downloads `
        --output-dir="$buildDir" `
        --output-filename=server-cli.exe `
        --include-package=server_cli `
        src/server_cli/cli.py

    if ($LASTEXITCODE -ne 0) {
        throw "Nuitka failed with exit code $LASTEXITCODE"
    }
}
finally {
    Pop-Location
}

Write-Host "Built $executable"
