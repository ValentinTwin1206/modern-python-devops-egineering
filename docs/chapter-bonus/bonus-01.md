# Windows MSI Packages

Windows Installer packages distribute applications as `.msi` databases that Windows can install, upgrade, repair, and remove. This bonus section compiles Server CLI into a Windows executable, packages it with WiX, and makes the installer discoverable through WinGet.

## Applied Project

### Project Setup

The applied project is the Click-based `Server CLI`, exposed on Windows as `server-cli.exe`. Nuitka first compiles the Python application into a platform-specific executable. WiX then places that executable under `Program Files`, adds its directory to the machine `PATH`, and creates a transactional MSI installer.

Unlike an installer that embeds an ordinary Python distribution and an unpacked wheel, this MSI contains the already-compiled Nuitka executable. Users do not need Python, `uv`, or network access when Windows Installer installs the package.

### Run the Project

Application, test, lint, executable-build, and MSI commands are documented in the [project README](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/proj4_servercli/README.md).

## Building Blocks

| Building Block | Role | Server CLI Example |
|----------------|------|--------------------|
| Package Format | Stores installer tables and the compressed application payload. | `.msi` |
| Maintainer File | Defines product identity, version, install location, components, and upgrade behavior. | `msi/wix/Product.wxs` |
| Package Manager | Discovers the package and delegates installation to Windows Installer. | WinGet, `msiexec` |
| Remote Repository | Hosts the MSI and the manifest metadata that points to it. | Cloudsmith Raw, WinGet source |

### Project Layout

```text
proj4_servercli/
├── msi/
│   ├── scripts/
│   │   └── build-msi.ps1
│   └── wix/
│       └── Product.wxs
├── scripts/
│   └── build-executable.ps1
├── src/server_cli/
├── Dockerfile.windows
├── pyproject.toml
└── uv.lock
```

- `Dockerfile.windows`: Provides Python, `uv`, Nuitka, Visual C++ Build Tools, WiX, and Cloudsmith CLI on Windows Server Core.
- `scripts/build-executable.ps1`: Uses Nuitka to produce `.build/server-cli.exe`.
- `msi/wix/Product.wxs`: Defines the MSI product, executable component, install directory, upgrades, and `PATH` integration.
- `msi/scripts/build-msi.ps1`: Compiles and links the WiX source into `.build/server-cli-<version>.msi`.

### Package Manifest

The WiX product definition identifies the package and includes the compiled executable as its key component:

```xml
<Product Id="*"
         Name="Server CLI"
         Language="1033"
         Version="$(var.ProductVersion)"
         Manufacturer="Modern Python Engineering"
         UpgradeCode="D5743C73-4CA2-4D94-BE2B-EF77834DBA91">
  <Package InstallerVersion="500"
           Compressed="yes"
           InstallScope="perMachine" />
  <MajorUpgrade DowngradeErrorMessage="A newer version of [ProductName] is already installed." />
  <MediaTemplate EmbedCab="yes" />
</Product>
```

The stable `UpgradeCode` associates releases of the same product, while the generated product ID identifies one specific MSI release. `MajorUpgrade` permits a newer release to replace an older one and prevents accidental downgrades.

### Package Layout

An MSI is a Windows Installer database in the Compound File Binary format. Its tables describe products, features, directories, files, components, and installation actions; an embedded cabinet carries `server-cli.exe`.

```text
C:\Program Files\ServerCLI\
└── server-cli.exe
```

Windows Installer tracks the executable as a component so it can upgrade, repair, and remove it consistently.

### Python Binaries

Python binary tools collect an application, imported dependencies, and the runtime components needed to launch it as a platform-specific executable. Both approaches below can produce one `.exe`, but the result must be built on Windows for the intended Windows architecture.

=== "PyInstaller"

    PyInstaller bundles the Python interpreter, application bytecode, imports, and resources. It emphasizes application collection and does not compile the entire Python program to native C code.

    ```powershell
    uv run pyinstaller `
        --onefile `
        --name server-cli `
        --paths src `
        src\server_cli\cli.py
    ```

=== "Nuitka"

    Nuitka translates Python modules into C and invokes a native compiler. It also follows imports and includes required runtime components, but Server CLI's Python modules become compiled machine code.

    ```powershell
    powershell -ExecutionPolicy Bypass `
        -File .\scripts\build-executable.ps1
    ```

    The script invokes Nuitka with the project entry point:

    ```powershell
    nuitka `
        --onefile `
        --output-dir=.build `
        --output-filename=server-cli.exe `
        --include-package=server_cli `
        src\server_cli\cli.py
    ```

## Tradeoffs

### Pros

- ✅ Integrates with the Windows lifecycle
- ✅ Supports upgrades, repair, and removal
- ✅ Enables discovery through WinGet
- ✅ Runs without a separate Python installation

### Cons

- ⚠️ Releases may become stale
- ⚠️ Requires a Windows build environment
- ⚠️ WiX configuration adds complexity
- ⚠️ MSI and WinGet publishing are separate workflows

## Packaging Workflow

### Create the Environment

This workflow requires Docker Desktop configured to run Windows containers. From Windows PowerShell, switch to the Windows engine and confirm its operating-system type:

```powershell
& "$Env:ProgramFiles\Docker\Docker\DockerCli.exe" -SwitchWindowsEngine
docker info --format "{{.OSType}}"
```

Move to `projects\proj4_servercli`, build the image, and create the output directory:

```powershell
docker build -f Dockerfile.windows -t server-cli-msi-builder .
New-Item -ItemType Directory -Path .build -Force
```

Start the container with the source and artifact directories mounted:

```powershell
docker run --rm -it `
    -v "$($PWD.ProviderPath):C:\workspace" `
    -v "$($PWD.ProviderPath)\.build:C:\workspace\.build" `
    -e CLOUDSMITH_REPOSITORY="<cloudsmith-repo>" `
    -e CLOUDSMITH_API_KEY="$env:CLOUDSMITH_API_KEY" `
    server-cli-msi-builder
```

Inside the container, synchronize the application dependencies. The Windows
image provides Nuitka, WiX, Visual C++ Build Tools, and Cloudsmith CLI because
these tools are required to build the Windows artifact:

```powershell
uv sync --group dev
```

### Create the Package

Compile the Windows executable:

```powershell
powershell -ExecutionPolicy Bypass `
    -File .\scripts\build-executable.ps1
```

Confirm that it starts:

```powershell
.\.build\server-cli.exe --help
```

Package the executable in an MSI:

```powershell
powershell -ExecutionPolicy Bypass `
    -File .\msi\scripts\build-msi.ps1 `
    -Version 1.0.0
```

The output is `.build\server-cli-1.0.0.msi`.

### Inspect the Package

Use WiX `dark.exe` to decompile the database and extract its cabinet:

```powershell
dark.exe `
    -x .build\msi-inspect `
    -out .build\msi-inspect\Product.wxs `
    .build\server-cli-1.0.0.msi
```

Inspect the extracted files and decompiled tables:

```powershell
Get-ChildItem -Recurse .build\msi-inspect
Get-Content .build\msi-inspect\Product.wxs
```

### Publish the Package

WinGet separates installer storage from package discovery. Publish the MSI to a stable HTTPS endpoint first:

```powershell
cloudsmith push raw `
    "$env:CLOUDSMITH_REPOSITORY" `
    .\.build\server-cli-1.0.0.msi `
    --name "server-cli" `
    --version "1.0.0"
```

Generate a WinGet manifest from the published installer URL:

```powershell
wingetcreate new `
    "https://dl.cloudsmith.io/public/<cloudsmith-repo>/raw/versions/1.0.0/server-cli-1.0.0.msi"
```

Use these package values when prompted:

```text
Package identifier: ModernPythonEngineering.ServerCLI
Package name: Server CLI
Publisher: Modern Python Engineering
Command: server-cli
Installer type: wix
```

Validate the generated manifest directory:

```powershell
winget validate --manifest `
    .\manifests\m\ModernPythonEngineering\ServerCLI\1.0.0
```

The manifests can be submitted to `microsoft/winget-pkgs` or served by a private WinGet-compatible source such as Rewinged.

## Consumer Workflow

### Configure the Package Manager

For the public WinGet community source, no additional source configuration is required. A private Rewinged deployment can be registered as follows after its HTTPS certificate is trusted:

```powershell
winget source add `
    --name modern-python-engineering `
    --arg https://localhost:8443/api `
    --type Microsoft.Rest
winget source update
```

### Install the OS Package

Install Server CLI from the public source:

```powershell
winget install --id ModernPythonEngineering.ServerCLI --source winget
```

For the private source, select its configured name instead:

```powershell
winget install `
    --id ModernPythonEngineering.ServerCLI `
    --source modern-python-engineering
```

Open a new terminal so it receives the updated machine `PATH`, then run:

```powershell
server-cli --help
```

## Useful Links

- [WiX Toolset documentation](https://wixtoolset.org/docs/)
- [WinGet package repository](https://learn.microsoft.com/en-us/windows/package-manager/package/repository)
- [Nuitka User Manual](https://nuitka.net/user-documentation/user-manual.html)
