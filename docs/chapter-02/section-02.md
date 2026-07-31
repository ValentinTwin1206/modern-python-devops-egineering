# OS Packages

Operating-system (OS) packages are the native software distribution format for operating systems. They allow Python applications to be installed, upgraded, and removed using the platform's standard software management tools instead of Python-specific package managers such as `pip` or `uv`.

## Applied Project

### Project Setup

The applied project is a small cross-platform admin CLI called `simply_journal_admin`, exposed as the `simply-journal-admin` command. It reads recent log entries from the host operating system through a unified interface while using platform-specific packaging: a Debian package for Linux and an MSI package for Windows. On Linux it imports [`systemd.journal`](https://www.freedesktop.org/software/systemd/python-systemd/journal.html) from the APT package [`python3-systemd`](https://packages.ubuntu.com/noble/python3-systemd); on Windows it reads the Event Log through `pywin32` with a `wevtutil` fallback. This makes it a good fit for operating-system packaging because installation, service integration, and runtime dependencies are intentionally managed at the operating-system level.

### Run the Project

Application, test, lint, packaging, and shell-exit commands are documented in the [section README](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/proj2_journal_admin/README.md).

## Distribution Fundamentals

### Overview

OS packages distribute Python applications through platform-native package management systems, such as `apt` on Debian-based Linux distributions, `dnf` on Red Hat-based Linux distributions, `Homebrew` on macOS, or Windows Installer (`.msi`) on Microsoft Windows. Unlike Python wheels, an OS package typically bundles everything required to run the application, including the application code, a Python runtime (if needed), third-party dependencies, launchers, and platform-specific metadata. End users do not need to install Python, create a virtual environment, or run `pip install` or `uv tool install` on the target machine. Instead, they install a single OS-native package that behaves like any other application managed by the operating system.

OS packages are particularly well suited for:

- ✅ System utilities and command-line applications
- ✅ Software tightly integrated with the operating system
- ✅ Enterprise applications managed through centralized deployment and patch management
- ✅ Internal developer tools distributed via native package repositories

### OS Package Ecosystem

Unlike [Python packaging](./section-01.md), OS package distribution follows the conventions of the target platform. While Python projects can typically distribute the same wheel format across multiple operating systems — or build platform-specific wheels when native code is required — OS package distribution always targets a specific operating system and its native packaging ecosystem. As a result, projects that distribute Python applications as OS packages typically produce different package artifacts for each supported platform.

Although the technologies differ between operating systems, the packaging lifecycle remains largely the same. Every platform distributes native packages through a **package repository**, installs them using a platform-specific **package manager**, and relies on **package metadata** to resolve dependencies, verify package integrity, and perform installation, upgrades, and removal.

Every OS package ecosystem consists of three core building blocks:

- **Package Manager** – The client application that discovers, downloads, verifies, installs, upgrades, and removes software on the local machine.
- **Package Format** – The platform-specific installation artifact that contains the application together with the metadata required by the operating system.
- **Remote Repository** – The server that stores packages and repository metadata, allowing package managers to discover and download software.

The following table summarizes the most common operating-system packaging ecosystems.

| Platform | Package Manager | Package Format | Repository Examples |
|----------|-----------------|----------------|---------------------|
| Debian / Ubuntu | `apt` | `.deb` | Ubuntu Repository, Debian Repository, Cloudsmith, Artifactory |
| Fedora / Red Hat Enterprise Linux | `dnf` | `.rpm` | Fedora Repository, Red Hat Repository, Cloudsmith, Artifactory |
| openSUSE | `zypper` | `.rpm` | openSUSE Repository, Cloudsmith, Artifactory |
| Windows | `winget`, Microsoft Store | `.msi`, `.exe`, `.msix` | Microsoft Store, WinGet Community Repository, Cloudsmith |
| macOS | `Homebrew`, `installer` | `.pkg` | Homebrew Tap, Cloudsmith |

### Project Layout

A typical Python project prepared for OS packaging separates application code from operating-system-specific packaging metadata:

```text
{project_root}/
├── debian/
│   ├── changelog
│   ├── control
│   ├── rules
│   ├── simply-journal-admin.install
│   ├── extra/
│   │   └── simply-journal-admin
│   └── source/
│       └── format
├── msi/
│   ├── scripts/
│   │   └── build-msi.ps1
│   └── wix/
│       └── Product.wxs
├── src/
├── tests/
├── .dockerignore
├── Dockerfile.devEnv
├── Dockerfile.windows
├── LICENSE
├── pyproject.toml
├── README.md
└── uv.lock
```

* `src/`: Contains the application source code.
* `tests/`: Contains automated tests for CLI behavior and platform abstractions.
* `pyproject.toml`: Defines project metadata, entry points, optional dependencies, and build configuration.
* `debian/`: Contains the main Debian packaging files, including `control` for package metadata and dependencies, `rules` for the build/install steps, `simply-journal-admin.install` for installed file mappings, and `extra/simply-journal-admin` for the launcher placed in `/usr/bin`.
* `msi/`: Contains the main MSI packaging files, including `wix/Product.wxs` for the installer definition and `scripts/build-msi.ps1` for assembling the offline payload and compiling the final `.msi` artifact.
* `Dockerfile.devEnv`: Provides the Linux packaging and test environment.
* `Dockerfile.windows`: Provides the Windows MSI build environment.

### Package Maintainer Files

=== "`control`"

	The Debian `control` file defines the package identity, build requirements, runtime dependencies, and end-user package description.

	```text
	Source: simply-journal-admin
	Section: admin
	Priority: optional
	Maintainer: Modern Python Engineering
	Build-Depends: debhelper-compat (= 13)
	Standards-Version: 4.7.0
	Rules-Requires-Root: no
	Homepage: https://github.com/ValentinTwin1206/modern-python-devops-egineering

	Package: simply-journal-admin
	Architecture: any
	Depends:
	 ${misc:Depends},
	 ${shlibs:Depends},
	 python3-systemd
	Description: cross-platform admin CLI for reading systemd journal entries
	 simply-journal-admin is a command-line tool that reads recent systemd journal
	 entries (Linux) through ...
	```

	* `Source`: Declares the source package name used by Debian packaging tools.
	* `Build-Depends`: Lists the tools required to build the `.deb` package.
	* `Package`: Names the binary package that end users install.
	* `Architecture`: Marks the package as architecture-specific because it ships an embedded runtime.
	* `Depends`: Pulls in required system packages, especially `python3-systemd`.
	* `Description`: Explains the installed CLI and its offline runtime layout.

=== "`Product.wxs`"

	The WiX `Product.wxs` file defines the MSI product identity, install location, upgrade behavior, and machine-wide `PATH` integration.

	```xml
	<?xml version="1.0" encoding="UTF-8"?>
	<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi"
	     xmlns:util="http://schemas.microsoft.com/wix/UtilExtension">

	  <Product Id="*"
	           Name="Simply Journal Admin"
	           Language="1033"
	           Version="$(var.ProductVersion)"
	           Manufacturer="Modern Python Engineering"
	           UpgradeCode="6B6F2C2E-2C2A-4E2E-9D0E-7A2C9B5D1A20">

	    <Package InstallerVersion="500"
	             Compressed="yes"
	             InstallScope="perMachine"
	             Description="Simply Journal Admin $(var.ProductVersion) installer"
	             Manufacturer="Modern Python Engineering" />

	    <MajorUpgrade DowngradeErrorMessage="A newer version of [ProductName] is already installed." />
	    <MediaTemplate EmbedCab="yes" />

	    <Property Id="ARPURLINFOABOUT" Value="https://github.com/ValentinTwin1206/modern-python-devops-egineering" />
	    <Property Id="ARPNOREPAIR" Value="1" />

	    <Feature Id="MainFeature" Title="Simply Journal Admin" Level="1">
	      <ComponentGroupRef Id="StagedPayload" />
	      <ComponentRef Id="LauncherAndPath" />
	    </Feature>

	    <Directory Id="TARGETDIR" Name="SourceDir">
	      <Directory Id="ProgramFiles64Folder">
	        <Directory Id="INSTALLFOLDER" Name="SimplyJournalAdmin" />
	      </Directory>
	    </Directory>

	    <Component Id="LauncherAndPath" Directory="INSTALLFOLDER" Guid="1B0E7E54-9A2E-4E3B-9B7C-2E6A1D4F0005">
	      <CreateFolder />
	      <Environment Id="UpdatePath"
	                   Name="PATH"
	                   Value="[INSTALLFOLDER]"
	                   Permanent="no"
	                   Part="last"
	                   Action="set"
	                   System="yes" />
	    </Component>
	  </Product>
	</Wix>
	```

	* `Product`: Defines the MSI identity, version, vendor, and upgrade behavior.
	* `Package`: Sets installer scope, compression, and Windows Installer metadata.
	* `MajorUpgrade`: Prevents downgrades and manages in-place upgrades.
	* `Feature`: Groups the staged payload and launcher into the installable feature.
	* `Directory`: Places the application under `Program Files\SimplyJournalAdmin`.
	* `Environment`: Appends the install directory to the machine `PATH`.

### Package Layout

The packaged result includes the Python application payload together with platform-native installation metadata and launcher behavior.

Examples:

=== "Debian"

	The Debian package installs an embedded Python runtime under `/opt/simply-journal-admin`, unpacks the built wheel into `app/site-packages`, and exposes a thin wrapper in `/usr/bin`. The package also declares `python3-systemd` as an OS-level dependency, so APT resolves that dependency during installation.
	
	```text
	/opt/simply-journal-admin/
	├── app/
	│   └── site-packages/
	│       └── simply_journal_admin/
	└── python/
	    ├── bin/
	    │   └── python3
	    └── lib/
	        └── python<major.minor>/

	/usr/bin/simply-journal-admin
	```

=== "MSI"

	The MSI stages an embedded Python runtime under `runtime`, extracts the built wheel into `app\site-packages`, and installs a `simply-journal-admin.cmd` launcher in the install root. The installer also updates the machine `PATH`, which lets the command run from a standard Windows shell after installation.

	```text
	C:\Program Files\SimplyJournalAdmin\
	├── app\
	│   └── site-packages\
	│       └── simply_journal_admin\
	├── runtime\
	│   ├── python.exe
	│   ├── Lib\
	│   └── DLLs\
	└── simply-journal-admin.cmd
	```

!!! info
	The package does not ask end users to run `pip` on the target machine. Instead, it bundles the application payload ahead of time and installs it through the operating system's native package manager.

## Packaging Workflow

### Create the OS Package

!!! info
    This workflow assumes that the Cloudsmith repository in the [`pravi-brothers`](https://app.cloudsmith.com/pravi-brothers) workspace already exists and that you already forwarded `CLOUDSMITH_API_KEY` into the running container.
	
=== "Debian package"

	Use the helper script to open the Linux packaging environment.

	```bash
	../build.sh build --path proj2_journal_admin/Dockerfile.devEnv
	```

	Inside the container, synchronize the environment and build the wheel:

	```bash
	uv sync --all-groups
	```

	Build the wheel artifact into the shared build directory:

	```bash
	uv build --wheel --out-dir /build
	```

	Run the Debian package build to create the `.deb` artifact. Use the `build-deb.sh` script to build the Debian package to not pollute the container and host environment:

	```bash
	./scripts/build-deb.sh
	```
	
	> The resulting `.deb` package is written to the `.build` output directory on the host.

=== "MSI package"

	Move into the `projects/proj2_journal_admin` directory first. This workflow depends on Docker's **Windows Container Engine (`dockerd.exe`)**, because the MSI build image and the packaging steps run inside a Windows container rather than a Linux container. Switch Docker Desktop back to the Windows engine before starting by running following in Windows PowerShell.

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

	Then start building the container image:

	```powershell
	docker build -f Dockerfile.windows -t sja-msi-builder .
	```

	Create the host `.build` output directory:

	```powershell
	New-Item -ItemType Directory -Path .build -Force
	```

	Start the Windows build container with the project and build directories mounted:

	```powershell
	docker run --rm -it `
		-v "$($PWD.ProviderPath):C:\workspace" `
		-v "$($PWD.ProviderPath)\.build:C:\build" `
		-e CLOUDSMITH_API_KEY="$env:CLOUDSMITH_API_KEY" `
		sja-msi-builder
	```

	Inside the running container, build the wheel:

	```powershell
	uv build --wheel --out-dir C:\build\wheel
	```

	Then build the MSI package:

	```powershell
	powershell -ExecutionPolicy Bypass `
		-File .\msi\scripts\build-msi.ps1 `
		-WheelDir C:\build\wheel `
		-OutDir C:\build
	```

	> The resulting `.msi` package is written to the `.build` output directory on the host.

### Inspect The Package

=== "Debian package"

	A Debian package (`.deb`) is an AR archive that contains `debian-binary`, a compressed `control.tar.*` metadata archive, and a compressed `data.tar.*` payload archive.

	List the AR members inside the Debian package.

	```bash
	ar t /build/simply-journal-admin_2.0.0-1_amd64.deb
	```

	Inspect the Debian control metadata, including package name, version, architecture, dependencies, and description.

	```bash
	dpkg -I /build/simply-journal-admin_2.0.0-1_amd64.deb
	```

	List the filesystem payload that the Debian package installs.

	```bash
	dpkg -c /build/simply-journal-admin_2.0.0-1_amd64.deb
	```

=== "MSI package"

	An MSI package (`.msi`) is a Windows Installer database stored in the OLE Compound File Binary Format; it records installer tables, embedded cabinets, features, components, and installation actions.

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

Once you have created and inspected the OS package, publish it through the distribution channel that end users consume.

=== "Debian"

	Debian repositories are typically managed using repository software such as Cloudsmith rather than directly by package maintainers. In practice, the package maintainer creates the `.deb`, and that package already contains the package metadata from the Debian `control` file. Cloudsmith then stores the artifact, extracts that package metadata, and generates the repository metadata that APT consumes. APT does not discover packages by inspecting uploaded files directly; it reads the generated repository metadata first and uses that metadata to locate the right `.deb` file. Understanding this repository layout helps explain how package and repository metadata work together to allow APT to discover (`apt update`) and install (`apt install`) software.

	The directory tree below illustrates the generic structure of a Debian-compatible APT repository. The placeholders represent values that are resolved when a package is published.

	```text
	/
	├── dists/
	│   └── {suite}/
	│       ├── InRelease
	│       ├── Release
	│       ├── Release.gpg
	│       └── {component}/
	│           └── binary-{arch}/
	│               └── Packages.gz
	└── pool/
		└── {component}/
			└── {package-prefix}/
				└── {package-name}/
					└── {package-name}_{version}_{arch}.deb
	```

	- **`/`** – The repository root configured in the APT source. It serves as the entry point for all repository metadata and package downloads.

	- **`dists/{suite}/`** – Stores the repository metadata for a Linux distribution. For example, `{suite}` becomes `noble` for Ubuntu 24.04. During publication, the repository client (for example, Cloudsmith) generates files such as `InRelease`, `Release`, `Release.gpg`, and the package indexes that APT consumes.

	- **`dists/{suite}/{component}/binary-{arch}/`** – Stores package indexes such as `Packages.gz`. For example, `{component}` is typically `main` and `{arch}` might be `amd64`. These indexes are generated from the uploaded `.deb` package and contain metadata extracted from its `control` file, including the package name, version, architecture, dependencies, checksums, and the location of the corresponding package artifact. When a new package enters the repository, Cloudsmith updates the dedicated `Packages.gz` file for the affected suite, component, and architecture.

	- **`Packages.gz`** – The compressed package index that APT downloads during `apt update`. It lists installable packages together with fields such as `Package`, `Version`, `Depends`, `SHA256`, and `Filename`. Cloudsmith regenerates this file automatically whenever a newly uploaded package changes the available package set for that target.

	- **`Release`** – The repository summary file for one suite. It describes which package indexes belong to that suite and records checksums for files such as `Packages.gz`. If the repository uses generated release metadata, Cloudsmith updates this file automatically after a new package changes the indexed repository contents.

	- **`Release.gpg`** – The detached GPG signature for the `Release` file. APT uses it to verify that the repository metadata came from a trusted publisher.

	- **`pool/{component}/...`** – Stores the actual `.deb` package artifacts uploaded by the package maintainer. For example, a package named `simply-journal-admin` version `2.0.0-1` for `amd64` is stored as `pool/main/s/simply-journal-admin/simply-journal-admin_2.0.0-1_amd64.deb`. During `apt install`, APT locates this file through `Packages.gz`, downloads it, and hands it to `dpkg` for installation.

	From the `projects/` directory, open the dedicated Debian packaging container and forward the API key into the container session.

	```bash
	../build.sh build --path proj2_journal_admin/Dockerfile.devEnv \
		-- --env CLOUDSMITH_API_KEY="$CLOUDSMITH_API_KEY"
	```

	When you publish, you can upload the same `.deb` package into multiple Ubuntu distributions because Cloudsmith generates repository metadata independently for each target distribution. The `noble` and `resolute` segments in the upload commands tell Cloudsmith which distribution-specific repository metadata to generate.

	```bash
	cloudsmith push deb "${CLOUDSMITH_REPOSITORY}/ubuntu/noble" \
		.build/simply-journal-admin_2.0.0-1_amd64.deb
	```
	
	> `noble` targets Ubuntu 24.04, 

	```bash
	cloudsmith push deb "${CLOUDSMITH_REPOSITORY}/ubuntu/resolute" \
		.build/simply-journal-admin_2.0.0-1_amd64.deb
	```

	> `resolute` targets Ubuntu 26.04.

	Verify that Cloudsmith indexed the uploaded package.

	```bash
	cloudsmith list packages "${CLOUDSMITH_REPOSITORY}" -q "simply-journal-admin"
	```

	At that point, APT clients can download the repository metadata during `apt update`, discover `simply-journal-admin`, and install it normally.

=== "MSI"

	Unlike Debian, WinGet separates installer artifacts from the package index. The MSI package is stored in a ***Generic HTTPs Artifact Repository*** that provides a stable HTTPS installer URL, while a ***WinGet Package Index*** stores package manifests that describe where the installer can be downloaded.

	Therefore, the package maintainer publishes two different artifacts:

	- MSI installer (`*.msi`)
	- WinGet package manifests YAML

	When a user executes `winget install`, WinGet first downloads the package manifest from the package index, reads the `InstallerUrl` and `InstallerSha256` checksum from the manifest, downloads the referenced installer artifact from the installer repository, verifies its integrity, and then hands it off to the appropriate installer mechanism for that package type.

	The repository layout below highlights the structure of a *WinGet Package Index*.

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

	Before continuing, **exit the running Windows container** and return to your Windows host machine.

	The next steps use `winget` and `wingetcreate`. These tools are installed on the Windows host, but they are **not available inside the Windows container** that was used to build the MSI installer.

	We will now prepare the local **WinGet package index**. This directory will contain the WinGet package manifests that describe our application. Later, the Rewinged package index server will mount this directory and serve it as a local WinGet-compatible package source.

	First, create the directory structure that will become the local package index:

	```powershell
	New-Item -ItemType Directory -Path .\.build\rewinged\packages -Force
	```

	The resulting directory will be mounted into Rewinged as its package-manifest directory:

	```text
	.build/
	└── rewinged/
		└── packages/
	```

	Next, use `wingetcreate` to generate the WinGet manifest files from the published MSI installer URL.

	Run the command inside the package index directory so that the generated manifests are written directly into the directory that Rewinged will serve:

	```powershell
	Push-Location .\.build\rewinged\packages
	wingetcreate new 'https://generic.cloudsmith.io/pravi-brothers/modern-python-engineering/simply-journal-admin/1.0.0/simply-msi-journal-admin-1.0.0.msi'
	Pop-Location
	```

	The generated manifests YAML contain all metadata required by WinGet.

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

	The most important file for the installation process is the installer manifest:

	```yaml
	PackageIdentifier: ModernPythonEngineering.SimplyJournalAdmin
	PackageVersion: 1.0.0

	Installers:
	- Architecture: x64
	  InstallerType: wix
	  InstallerUrl: https://dl.cloudsmith.io/public/pravi-brothers/modern-python-engineering/raw/versions/1.0.0/simply-journal-admin-1.0.0.msi
	  InstallerSha256: <sha256>
	```

	At this point, the local WinGet package index is ready. The next step is to start [Rewinged](https://github.com/jantari/rewinged) and let it expose this manifest directory as a private WinGet package source.

	Thus, switch Docker Desktop back to the Linux engine, since the container image `ghcr.io/jantari/rewinged:stable` is Linux based.

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

	Start the local Rewinged package index and mount the generated manifest directory into the container. WinGet REST sources require HTTPS, so this command assumes that `certs/cert.pem` and `certs/private.key` exist and that the certificate is trusted by the Windows client.

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

	For Rewinged, uploading manifest YAML means placing the files in the mounted package directory. Because `.build\rewinged\packages` is bind-mounted to `/packages`, the YAML files generated by `wingetcreate` are already visible to the running package index.

## Consumer Workflow

### Configure Package Manager

=== "Debian (.deb)"

	Before installing a package from a private Debian repository, configure APT on the target machine. APT needs a trusted signing key, a source file that points to the repository, and a refreshed local package index before it can resolve and install and Debian package.

	Import the Cloudsmith signing key from the `pravi-brothers` workspace first. APT uses this key to verify repository metadata before trusting packages from the repository.

	```bash
	curl -fsSL "https://dl.cloudsmith.io/public/pravi-brothers/modern-python-engineering/gpg.key" | sudo gpg --dearmor -o /usr/share/keyrings/pravi-brothers-modern-python-engineering.gpg
	```

	Add the Debian repository to the local APT sources by creating a deb822 source file.

	```bash
	printf 'Types: deb\nURIs: https://dl.cloudsmith.io/public/pravi-brothers/modern-python-engineering/deb/ubuntu\nSuites: noble\nComponents: main\nSigned-By: /usr/share/keyrings/pravi-brothers-modern-python-engineering.gpg\n' | sudo tee /etc/apt/sources.list.d/cloudsmith.sources
	```

	The dedicated source file `cloudsmith.sources` contains the repository metadata in stanza form.

	```text
	Types: deb
	URIs: https://dl.cloudsmith.io/public/pravi-brothers/...
	Suites: noble
	Components: main
	Signed-By: /usr/share/keyrings/pravi-brothers-modern-python-engineering.gpg
	```

	APT reads the values from `cloudsmith.sources` and combines entries such as `Suite` and `Component` with the local system architecture to choose the correct repository paths.

	- `Types`: Tells APT which repository format to read. `deb` means this source provides binary packages for installation.
	- `URIs`: Declares the repository base URL that APT uses before resolving release-specific metadata and package indexes.
	- `Suites`: Selects the release subtree inside the repository. Here, `noble` points APT to the Ubuntu 24.04 distribution metadata.
	- `Components`: Selects the repository component within the chosen suite. Here, `main` tells APT which package index to read inside the `noble` release.
	- `Signed-By`: Restricts signature verification to the imported Cloudsmith keyring for this repository.

	Refresh the local APT metadata. With the source file in place, `apt update` downloads the release metadata, verifies it with the configured Cloudsmith key, and then downloads the package index for this host, such as `dists/noble/main/binary-amd64/Packages`.

	```bash
	sudo apt update
	```

	Afterward, inspect the downloaded package index in APT's local metadata cache.

	```bash
	batcat /var/lib/apt/lists/*modern-python-engineering*_Packages
	```

	The expected output should include the important fields below:

	```text
	Package: simply-journal-admin
	Version: 2.0.0-1
	Architecture: amd64
	Depends: libbz2-1.0, ..., python3-systemd
	Description: cross-platform admin CLI for reading systemd journal entries
	 simply-journal-admin is a command-line tool that reads recent systemd journal
	 ...
	Filename: pool/noble/main/s/si/simply-journal-admin_2.0.0-1/simply-journal-admin_2.0.0-1_amd64.deb
	SHA256: <sha256>
	```

	The `Filename` field gives APT the package path inside `/pool`. Combined with the repository base URL, this is enough for APT to build the full download URL when someone installs a specific version, such as `simply-journal-admin=2.0.0-1`.

=== "MSI (.msi)"

	Before installing packages from a private WinGet package index, configure WinGet to use the additional package source. Unlike APT, WinGet does not require a GPG key or a repository source file. Instead, package sources are registered through the WinGet client and expose a REST API that provides package manifests.

	For this local workflow, use the [Rewinged](https://github.com/jantari/rewinged) WinGet package index started during the MSI publishing workflow. Rewinged reads WinGet package manifests from a local directory and serves them through the REST API that WinGet understands.

	!!! info
		WinGet requires REST sources to use HTTPS. For a local test, the development certificate used by Rewinged must be trusted on the Windows machine before adding the source.

	The Rewinged API should now be available at `https://localhost:8443/api`. Register it as an additional WinGet source.

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

Users typically install the package through the native package-management workflow of the target platform.

=== "Linux (.deb)"

	Install the published package through APT. This command reads the repository metadata cached during `apt update`, resolves `simply-journal-admin` from that package index, downloads the required `.deb` archives and dependencies, and then invokes `dpkg` to unpack the package and register the installed command on the system.

	```bash
	sudo apt install simply-journal-admin
	```

	Run `simply-journal-admin` next to confirm that the launcher works and that the package can read recent journal entries on the host.

	```bash
	simply-journal-admin --since-minutes 60
	```

	Inspect the registration stage last by asking `dpkg` for the files it recorded for `simply-journal-admin` in its local package database.

	```bash
	dpkg -L simply-journal-admin
	```

=== "Windows (.msi)"

	Install the published MSI using WinGet. This command looks up `ModernPythonEngineering.SimplyJournalAdmin` in the configured Rewinged source, reads the published manifest, downloads the MSI from the Cloudsmith Raw repository URL recorded in that manifest, verifies the installer metadata and hash, and hands the installer to the appropriate Windows installation mechanism.

	```powershell
	winget install --id ModernPythonEngineering.SimplyJournalAdmin --source modern-python-engineering
	```

	> WinGet downloads the manifest from Rewinged, then uses the manifest's stable Cloudsmith URL to download the MSI.

## Useful Links

- [Submitting a package to `winget-pkgs`](https://learn.microsoft.com/en-us/windows/package-manager/package/repository)
- [Winget Releaser GitHub Action](https://github.com/vedantmgoyal9/winget-releaser)