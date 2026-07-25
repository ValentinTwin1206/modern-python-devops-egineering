# OS Packages

OS packages distribute Python applications through the package manager of an operating system, such as `apt` on Debian-based systems or Windows Installer on Microsoft Windows. They are useful when a Python tool must follow system-level installation, upgrade, service registration, and removal workflows.

## Applied Project

### Project Setup

The applied project is a small cross-platform admin CLI called `simply_journal_admin`, exposed as the `simply-journal-admin` command. It reads recent log entries from the host operating system through a unified interface while using platform-specific packaging: a Debian package for Linux and an MSI package for Windows. On Linux it imports [`systemd.journal`](https://www.freedesktop.org/software/systemd/python-systemd/journal.html) from the APT package [`python3-systemd`](https://packages.ubuntu.com/noble/python3-systemd); on Windows it reads the Event Log through `pywin32` with a `wevtutil` fallback. This makes it a good fit for operating-system packaging because installation, service integration, and runtime dependencies are intentionally managed at the operating-system level.

### Run the Project

Application, test, lint, packaging, and shell-exit commands are documented in the [section README](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/proj2_journal_admin/README.md).

## Distribution Fundamentals

### Overview

Operating-system packages wrap a Python application in the installation format expected by the target platform. Unlike a plain wheel, the final artifact is designed to be installed with the operating system's built-in tools, such as `apt` on Debian-based Linux systems or `msiexec` on Windows.

For Python applications, this usually means the package bundles everything the program needs at install time: the application code, its Python runtime or Python-facing dependencies, launchers, and platform-specific metadata. End users do not need to create a virtual environment or run `pip install` on the target machine. Instead, they install one OS-native package and let the platform package manager handle installation, upgrades, and removal.

* ✅ command-line tools installed for all users
* ✅ software managed through system upgrade workflows
* ✅ internal tools distributed through platform-native artifacts

### OS Packaging Ecosystem

Python OS packaging differs from Python package distribution because the final artifact must match the conventions of the target operating system.

The most common package formats for projects like this are:

| Format | Description |
| ------ | ----------- |
| Debian package (`.deb`) | Standard package format on Debian-based Linux systems. It integrates with `apt`, can declare system dependencies such as `python3-systemd`, and can register `systemd` services through maintainer scripts and package metadata. |
| Windows Installer (`.msi`) | Standard enterprise-friendly installer format on Windows. It integrates with Windows Installer, can place files under `Program Files`, update `PATH`, register uninstall metadata, and package launchers plus offline application payloads in one installer. |
| macOS installer package (`.pkg`) | Standard installer format on macOS. It integrates with built-in tools such as `installer`, can place files in system-managed locations, and is commonly produced with Apple's packaging utilities such as `pkgbuild` and `productbuild`. This project does not ship a macOS package, but the packaging model is similar: prepare one platform-native artifact that macOS can install directly. |

> In many production environments, the OS package bundles the Python application together with the runtime or required dependencies so the target machine can install the software with native OS tools alone.

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

#### Main Configuration Files

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
	 entries (Linux) through the APT-managed python3-systemd binding. The same code
	 base also supports the Windows Event Log when installed from the MSI package.
	 .
	 The Debian package ships a fully offline runtime under
	 /opt/simply-journal-admin: an embedded Python interpreter, the unpacked
	 project wheel, and a thin wrapper at /usr/bin/simply-journal-admin. No pip,
	 virtualenv creation, or internet access is needed on the target host.
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

	Run the Debian package build to create the `.deb` artifact:

	```bash
	./scripts/build-deb.sh
	```

	> Use the `build-deb.sh` script to build the Debian package to not pollute the container and host environment

=== "MSI package"

	Build the Windows MSI builder image first:

	```powershell
	docker build -f Dockerfile.windows -t sja-msi-builder .
	```

	Create the host `.build` output directory:

	```powershell
	New-Item -ItemType Directory -Path .build -Force
	```

	Start the Windows build container with the project and build directories mounted:

	```powershell
	docker run --rm -it -v "$($PWD.ProviderPath):C:\workspace" -v "$($PWD.ProviderPath)\.build:C:\build" sja-msi-builder
	```

	Inside the running container, build the wheel:

	```powershell
	uv build --wheel --out-dir C:\build\wheel
	```

	Then build the MSI package:

	```powershell
	powershell -ExecutionPolicy Bypass -File .\msi\scripts\build-msi.ps1 -WheelDir C:\build\wheel -OutDir C:\build
	```

The resulting package is written to the `.build` output directory on the host.

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

Once you have inspected the OS package, publish it through the distribution channel that end users consume.

=== "Debian"

	From the `projects/` directory, open the dedicated Debian packaging container and forward the API key into the container session.

	```bash
	../build.sh build --path proj2_journal_admin/Dockerfile.devEnv \
		-- --env CLOUDSMITH_API_KEY="$CLOUDSMITH_API_KEY"
	```

	Upload the generated Debian package for the Ubuntu 24.04 and Ubuntu 26.04 APT distributions. The upload stores the `.deb` in a Cloudsmith `debian` repository, and Cloudsmith then generates the signed APT metadata and package indexes that clients consume.

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

=== "MSI"

	Open an interactive Windows container and forward the Cloudsmith API key before uploading the MSI.

	```powershell
	docker run --rm -it \
		-v "$($PWD.ProviderPath):C:\workspace" \
		-v "$($PWD.ProviderPath)\.build:C:\build" \
		-e CLOUDSMITH_API_KEY="$env:CLOUDSMITH_API_KEY" sja-msi-builder
	```

	Upload the generated MSI to the Cloudsmith Raw repository in the `pravi-brothers` workspace. The raw repository provides the stable installer URL that the Winget manifest references.

	```powershell
	cloudsmith push raw "$env:CLOUDSMITH_REPOSITORY" \
		.\.build\simply-journal-admin-1.0.0.msi --version 1.0.0
	```

	Calculate the installer hash used by the Winget manifest.

	```powershell
	Get-FileHash .\.build\simply-journal-admin-1.0.0.msi -Algorithm SHA256
	```

	Generate a new manifest set for the first release. Use the URL of the published MSI, not a local file path.

	```powershell
	wingetcreate new "https://dl.cloudsmith.io/public/pravi-brothers/modern-python-engineering/raw/versions/1.0.0/simply-journal-admin-1.0.0.msi"
	```

	The generated installer manifest records the stable Cloudsmith URL and the MSI hash.

	```yaml
	PackageIdentifier: ModernPythonEngineering.SimplyJournalAdmin
	PackageVersion: 1.0.0
	InstallerType: wix
	Installers:
	- Architecture: x64
	  InstallerUrl: https://dl.cloudsmith.io/public/pravi-brothers/modern-python-engineering/raw/versions/1.0.0/simply-journal-admin-1.0.0.msi
	  InstallerSha256: <sha256>
	```

	!!! info ""
		For later releases, update the existing package identifier instead of starting from scratch.

		```powershell
		wingetcreate update ModernPythonEngineering.SimplyJournalAdmin -u "https://dl.cloudsmith.io/public/pravi-brothers/modern-python-engineering/raw/versions/<version>/simply-journal-admin-<version>.msi" -v "<version>"
		```

	External contributors have to submit manifests through a fork of `microsoft/winget-pkgs`. Prepare a local submission branch in your fork with sparse checkout enabled for this publisher folder.

	```powershell
	git clone --filter=blob:none --no-checkout https://github.com/<github-user>/winget-pkgs.git
	Set-Location winget-pkgs
	git sparse-checkout set manifests\m\ModernPythonEngineering
	git checkout
	git checkout -b add-simply-journal-admin-1.0.0
	```

	Place the generated manifest files in the forked repository under the directory derived from the package identifier and version.

	```text
	manifests/
	└── m/
	    └── ModernPythonEngineering/
	        └── SimplyJournalAdmin/
	            └── 1.0.0/
	                ├── ModernPythonEngineering.SimplyJournalAdmin.yaml
	                ├── ModernPythonEngineering.SimplyJournalAdmin.installer.yaml
	                └── ModernPythonEngineering.SimplyJournalAdmin.locale.en-US.yaml
	```

	Validate the manifest directory before opening a pull request. If Windows Sandbox is available, run the sandbox test as part of the same local check.

	```powershell
	winget validate --manifest .\manifests\m\ModernPythonEngineering\SimplyJournalAdmin\1.0.0
	powershell .\Tools\SandboxTest.ps1 manifests\m\ModernPythonEngineering\SimplyJournalAdmin\1.0.0
	```

	Commit the manifest files and push the submission branch to your fork.

	```powershell
	git add .\manifests\m\ModernPythonEngineering\SimplyJournalAdmin\1.0.0
	git commit -m "Add ModernPythonEngineering.SimplyJournalAdmin 1.0.0"
	git push -u origin add-simply-journal-admin-1.0.0
	```

	Open a pull request from the pushed fork branch against `microsoft/winget-pkgs`.

	!!! info "Winget Manigest Flow"
		Microsoft validation checks the manifest schema, installer URL, hash, metadata, and installation behavior before the pull request is merged. Future versions are published by uploading a new MSI version to the Cloudsmith Raw repository, creating a new manifest version directory, updating the installer URL and SHA-256 hash, validating the manifest, and submitting one pull request per package version.

## Consumer Workflow

### Configure Package Manager

=== "Debian (.deb)"

	Before installing a package from a private Debian repository, configure APT on the target machine. APT needs a trusted signing key, a source file that points to the repository, and a refreshed local package index before it can resolve and install and Debian package.

	Debian repositories follow a dedicated directory structure so `apt` can download the correct metadata and package files for the current system. A remote repository is usually split into `/dists`, which stores release metadata and package indexes, and `/pool`, which stores the actual `.deb` package files.
	
	```text
	deb/ubuntu/
	├── dists/
	│   └── noble/
	│       ├── InRelease
	│       ├── Release
	│       ├── Release.gpg
	│       └── main/
	│           └── binary-amd64/
	│               └── Packages.gz
	└── pool/
		└── main/
			└── s/
				└── simply-journal-admin/
					└── simply-journal-admin_2.0.0-1_amd64.deb
	```

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

	No additional local package-manager repository configuration is required as the package manifest is hosted in `winget-pkgs`.

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

	Install the published MSI using WinGet. This command looks up `ModernPythonEngineering.SimplyJournalAdmin` in the configured WinGet source, reads the published manifest, downloads the MSI from the Cloudsmith Raw repository URL recorded in that manifest, verifies the installer metadata and hash, and invokes Windows Installer to complete the installation.

	> WinGet downloads the manifest from `winget-pkgs`, then uses the manifest's stable Cloudsmith URL to download the MSI.

	```powershell
	winget install --id ModernPythonEngineering.SimplyJournalAdmin --source winget
	```

## Useful Links

- [Submitting a package to `winget-pkgs`](https://learn.microsoft.com/en-us/windows/package-manager/package/repository)
- [Winget Releaser GitHub Action](https://github.com/vedantmgoyal9/winget-releaser)