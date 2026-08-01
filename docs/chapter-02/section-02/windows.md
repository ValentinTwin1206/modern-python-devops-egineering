# Windows MSI Packages

Windows Installer packages distribute applications as `.msi` databases that Windows can install, upgrade, repair, and remove. This guide applies the [OS package fundamentals](index.md) to the `simply-journal-admin` MSI package and its WinGet distribution workflow.

## Applied Project

### Project Setup

The applied project is a small cross-platform admin CLI called `simply_journal_admin`, exposed as the `simply-journal-admin` command. It reads recent log entries from the host operating system through a unified interface while using platform-specific packaging: a Debian package for Linux and an MSI package for Windows. On Linux it imports [`systemd.journal`](https://www.freedesktop.org/software/systemd/python-systemd/journal.html) from the APT package [`python3-systemd`](https://packages.ubuntu.com/noble/python3-systemd); on Windows it reads the Event Log through `pywin32` with a `wevtutil` fallback. This makes it a good fit for operating-system packaging because installation, service integration, and runtime dependencies are intentionally managed at the operating-system level.

### Run the Project

Application, test, lint, packaging, and shell-exit commands are documented in the [section README](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/proj2_journal_admin/README.md).

## Building Blocks

Microsoft Installer (MSI) packages are native Windows installation databases stored as `.msi` files. An MSI describes the application payload as features and components together with installation directories, registry or environment changes, upgrade rules, and removal behavior. MSI packages are typically used for desktop applications, command-line tools, and enterprise software that require repeatable machine-wide installation and managed upgrades.

The MSI workflow connects four building blocks: the `.msi` database stores the payload and installer tables, a WiX source file defines how the installer is assembled, Windows Installer executes the installation, and a remote repository or package source makes the installer discoverable. WinGet can act as the package-management frontend while Windows Installer performs the actual MSI transaction.

| Building Block | Role | Windows MSI Example |
|----------------|------|---------------------|
| Package Format | Stores installer tables, application files, features, components, and installation actions. | `.msi` |
| Maintainer / Metadata File | Defines product identity, version, payload components, directories, and upgrade behavior. | WiX `Product.wxs` |
| Package Manager | Discovers the package and delegates installation, repair, upgrade, or removal to Windows Installer. | WinGet, Windows Installer (`msiexec`) |
| Remote Repository | Publishes package manifests and provides a stable URL for the MSI artifact. | WinGet source, Microsoft Store, Cloudsmith |

### Project Layout

The MSI packaging layout centers on the WiX installer definition and its build script:

```text
{project_root}/
└── msi/
    ├── scripts/
    │   └── build-msi.ps1
    └── wix/
        └── Product.wxs
```

- `wix/Product.wxs`: Defines the product identity, package metadata, features, installation directories, and upgrade behavior for WiX.
- `scripts/build-msi.ps1`: Stages the application payload and invokes the WiX compiler and linker to create the MSI artifact.

### Package Manifest

The WiX `Product.wxs` file defines the MSI product identity, install location, upgrade behavior, bundled components, and machine-wide `PATH` integration.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi"
     xmlns:util="http://schemas.microsoft.com/wix/UtilExtension">

  <Product Id="*"
        Name="{product-name}"
        Language="{language-code}"
        Version="{product-version}"
        Manufacturer="{manufacturer-name}"
        UpgradeCode="{stable-upgrade-guid}">

    <Package InstallerVersion="{installer-version}"
             Compressed="yes"
          InstallScope="{install-scope}"
          Description="{package-description}"
          Manufacturer="{manufacturer-name}" />

    <MajorUpgrade DowngradeErrorMessage="A newer version of [ProductName] is already installed." />
    <MediaTemplate EmbedCab="yes" />

        <Feature Id="MainFeature" Title="{feature-name}" Level="1">
            <ComponentGroupRef Id="{component-group-id}" />
    </Feature>

    <Directory Id="TARGETDIR" Name="SourceDir">
      <Directory Id="ProgramFiles64Folder">
                <Directory Id="INSTALLFOLDER" Name="{install-directory-name}" />
      </Directory>
    </Directory>
  </Product>
</Wix>
```

- `Product`: Defines the MSI identity, version, vendor, and upgrade behavior.
- `Package`: Sets installer scope, compression, and Windows Installer metadata.
- `MajorUpgrade`: Prevents downgrades and manages in-place upgrades.
- `Feature`: Groups related components into an installable feature. A maintainer can include a staged Python runtime by declaring its files as components and referencing their component group here.
- `Directory`: Defines the target directory tree under `Program Files` or another Windows location.

Unlike Debian packages, an MSI cannot ask Windows Installer to resolve dependencies from a repository. A self-contained MSI must therefore bundle dependencies such as Python; here, `build-msi.ps1` stages the runtime, WiX Heat defines its components, and `MediaTemplate EmbedCab="yes"` embeds the payload. Other installers may require Python beforehand or install it through a bootstrapper such as WiX Burn.

### Package Layout

An MSI package uses the Microsoft Compound File Binary format. It combines summary information, Windows Installer database tables, and usually compressed cabinet streams containing the application payload. The tables describe properties, directories, features, components, files, and installation actions. Windows Installer uses this information to install the payload and track its components for repair, upgrade, and removal.

## Packaging Workflow

!!! info
    This workflow assumes that you have a valid Cloudsmith repository and API key. Replace `<cloudsmith-repo>` with your Cloudsmith repository slug, define `CLOUDSMITH_API_KEY` on the Windows host, and pass both values into the container.

### Create the OS Package

Move into the `projects/proj2_journal_admin` directory first. This workflow depends on Docker's **Windows Container Engine (`dockerd.exe`)** because the MSI build image and packaging steps run inside a Windows container. Switch Docker Desktop to the Windows engine from Windows PowerShell.

```powershell
& "$Env:ProgramFiles\Docker\Docker\DockerCli.exe" -SwitchWindowsEngine
```

Confirm that Docker is using the Windows engine.

```powershell
docker info --format "{{.OSType}}"
```

The expected output is:

```text
windows
```

Build the container image.

```powershell
docker build -f Dockerfile.windows -t sja-msi-builder .
```

Create the host `.build` output directory.

```powershell
New-Item -ItemType Directory -Path .build -Force
```

Start the Windows build container with the project and build directories mounted.

```powershell
docker run --rm -it `
    -v "$($PWD.ProviderPath):C:\workspace" `
    -v "$($PWD.ProviderPath)\.build:C:\build" `
    -e CLOUDSMITH_REPOSITORY="<cloudsmith-repo>" `
    -e CLOUDSMITH_API_KEY="$env:CLOUDSMITH_API_KEY" `
    sja-msi-builder
```

Inside the running container, build the wheel.

```powershell
uv build --wheel --out-dir C:\build\wheel
```

Then build the MSI package.

```powershell
powershell -ExecutionPolicy Bypass `
    -File .\msi\scripts\build-msi.ps1 `
    -WheelDir C:\build\wheel `
    -OutDir C:\build
```

> The resulting `.msi` package is written to the `.build` output directory on the host.

### Inspect the Package

An MSI package (`.msi`) is a Windows Installer database stored in the OLE Compound File Binary Format. It records installer tables, embedded cabinets, features, components, and installation actions.

Use WiX `dark.exe` to decompile the MSI database and embedded cabinets into an inspection directory.

```powershell
dark.exe -x C:\build\msi-inspect -out C:\build\msi-inspect\Product.wxs C:\build\simply-journal-admin-2.0.0.msi
```

List the files extracted from the MSI payload.

```powershell
Get-ChildItem -Recurse C:\build\msi-inspect\File
```

Read the decompiled WiX source that represents the MSI tables and component metadata.

```powershell
Get-Content C:\build\msi-inspect\Product.wxs
```

### Publish the OS Package

Unlike Debian, WinGet separates installer artifacts from the package index. The MSI package is stored in a **generic HTTPS artifact repository** that provides a stable installer URL, while a **WinGet package index** stores manifests that describe where the installer can be downloaded.

The package maintainer therefore publishes two artifacts:

- MSI installer (`*.msi`)
- WinGet package manifests in YAML

When a user executes `winget install`, WinGet downloads the package manifest from the index, reads its `InstallerUrl` and `InstallerSha256`, downloads the installer, verifies its integrity, and hands it to the appropriate installer mechanism.

The repository layout below highlights the structure of a WinGet package index.

```text
/
└── manifests/
    └── {project}/
        └── {package}/
            └── 1.0.0/
                ├── package.yaml
                ├── installer.yaml
                └── locale.en-US.yaml
```

Open an interactive Windows container and forward the Cloudsmith API key.

```powershell
docker run --rm -it `
    -v "$($PWD.ProviderPath):C:\workspace" `
    -v "$($PWD.ProviderPath)\.build:C:\build" `
    -e CLOUDSMITH_REPOSITORY="<cloudsmith-repo>" `
    -e CLOUDSMITH_API_KEY="$env:CLOUDSMITH_API_KEY" `
    sja-msi-builder
```

Upload the generated MSI to the Cloudsmith repository.

```powershell
cloudsmith push generic `
    "$env:CLOUDSMITH_REPOSITORY" `
    .\.build\simply-journal-admin-1.0.0.msi `
    --filepath "simply-journal-admin/1.0.0/simply-journal-admin-1.0.0.msi" `
    --name "simply-journal-admin" `
    --version "1.0.0"
```

Verify that Cloudsmith stores the uploaded installer.

```powershell
cloudsmith list packages "$env:CLOUDSMITH_REPOSITORY"
```

Exit the Windows container before continuing. The next steps use `winget` and `wingetcreate`, which are installed on the Windows host but are not available inside the build container.

Create the directory that will become the local package index. Rewinged will mount and serve this package-manifest directory later.

```powershell
New-Item -ItemType Directory -Path .\.build\rewinged\packages -Force
```

```text
.build/
└── rewinged/
    └── packages/
```

Generate the WinGet manifests from the published MSI installer URL. Run `wingetcreate` inside the package index directory so that it writes the manifests directly into the directory Rewinged will serve.

```powershell
Push-Location .\.build\rewinged\packages
wingetcreate new 'https://generic.cloudsmith.io/<cloudsmith-repo>/simply-journal-admin/1.0.0/simply-msi-journal-admin-1.0.0.msi'
Pop-Location
```

The generated YAML manifests contain all metadata required by WinGet.

```text
.build/
└── rewinged/
    └── packages/
        └── manifests/
            └── m/
                └── ModernPythonEngineering/
                    └── SimplyJournalAdmin/
                        └── 1.0.0/
                            ├── ModernPythonEngineering.SimplyJournalAdmin.yaml
                            ├── ModernPythonEngineering.SimplyJournalAdmin.installer.yaml
                            └── ModernPythonEngineering.SimplyJournalAdmin.locale.en-US.yaml
```

The installer manifest is the most important file for the installation process.

```yaml
PackageIdentifier: ModernPythonEngineering.SimplyJournalAdmin
PackageVersion: 1.0.0

Installers:
- Architecture: x64
  InstallerType: wix
    InstallerUrl: https://dl.cloudsmith.io/public/<cloudsmith-repo>/raw/versions/1.0.0/simply-journal-admin-1.0.0.msi
  InstallerSha256: <sha256>
```

The local WinGet package index is now ready. Start [Rewinged](https://github.com/jantari/rewinged) to expose this manifest directory as a private WinGet package source. First, switch Docker Desktop back to the Linux engine because `ghcr.io/jantari/rewinged:stable` is Linux based.

```powershell
& "$Env:ProgramFiles\Docker\Docker\DockerCli.exe" -SwitchLinuxEngine
```

Confirm that Docker is using the Linux engine.

```powershell
docker info --format "{{.OSType}}"
```

The expected output is:

```text
linux
```

Start the local Rewinged package index and mount the generated manifest directory. WinGet REST sources require HTTPS, so this command assumes that `certs/cert.pem` and `certs/private.key` exist and that the certificate is trusted by the Windows client.

```powershell
docker run --rm -it `
    -e REWINGED_HTTPS=true `
    -e REWINGED_LISTEN='0.0.0.0:8443' `
    -e REWINGED_MANIFESTPATH=/packages `
    -e REWINGED_HTTPSCERTIFICATEFILE=/certs/cert.pem `
    -e REWINGED_HTTPSPRIVATEKEYFILE=/certs/private.key `
    -p 8443:8443 `
    -v "$($PWD.ProviderPath)\.build\rewinged\packages:/packages:ro" `
    -v "$($PWD.ProviderPath)\certs:/certs:ro" `
    ghcr.io/jantari/rewinged:stable
```

Because `.build\rewinged\packages` is bind-mounted to `/packages`, the YAML files generated by `wingetcreate` are already visible to the running package index.

## Consumer Workflow

### Configure the Package Manager

Before installing packages from a private WinGet index, configure WinGet to use the additional source. Unlike APT, WinGet does not require a GPG key or repository source file. Package sources are registered through the WinGet client and expose a REST API that provides package manifests.

For this local workflow, use the [Rewinged](https://github.com/jantari/rewinged) index started during publishing.

!!! info
    WinGet requires REST sources to use HTTPS. For a local test, the development certificate used by Rewinged must be trusted on the Windows machine before adding the source.

Register the Rewinged API as an additional WinGet source.

```powershell
winget source add `
    --name modern-python-engineering `
    --arg https://localhost:8443/api `
    --type Microsoft.Rest
```

List the configured package sources.

```powershell
winget source list
```

The expected output should contain both the Microsoft community source and the local Rewinged package index.

```text
Name                         Argument
------------------------------------------------------------
winget                       https://cdn.winget.microsoft.com/cache
modern-python-engineering    https://localhost:8443/api
```

Refresh the local WinGet source cache.

```powershell
winget source update
```

During the refresh, WinGet queries the Rewinged REST API and updates its local cache with the returned package metadata. Unlike `apt update`, WinGet does not download a compressed package index such as `Packages.gz`.

Search for the published package in the private source.

```powershell
winget search --source modern-python-engineering SimplyJournalAdmin
```

The package should now appear in the search results.

```text
Name                     Id
-----------------------------------------------
Simply Journal Admin     ModernPythonEngineering.SimplyJournalAdmin
```

### Install the OS Package

Install the published MSI using WinGet. This command looks up the package in the configured Rewinged source, downloads the MSI from the Cloudsmith URL in the manifest, verifies the installer metadata and hash, and hands it to Windows Installer.

```powershell
winget install --id ModernPythonEngineering.SimplyJournalAdmin --source modern-python-engineering
```

> WinGet downloads the manifest from Rewinged, then uses its stable Cloudsmith URL to download the MSI.

## Useful Links

- [Submitting a package to `winget-pkgs`](https://learn.microsoft.com/en-us/windows/package-manager/package/repository)
- [WinGet Releaser GitHub Action](https://github.com/vedantmgoyal9/winget-releaser)