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

	Run the Debian package build to create the .deb artifact:

	```bash
	dpkg-buildpackage -us -uc -b
	```

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

The resulting package is written to the build output directory.

### Validate the OS Package

After building the package, run a smoke test to confirm that the installer completes, the CLI starts, and the package can be removed cleanly.

=== "Debian"

	```bash
	sudo apt install ./simply-journal-admin_<version>_all.deb
	simply-journal-admin --since-minutes 60
	sudo apt remove simply-journal-admin
	```

=== "MSI"

	```powershell
	msiexec /i "$PWD\simply-journal-admin-<version>.msi" /L*V! "$PWD\install.log"
	simply-journal-admin --since-minutes 60
	msiexec /x "$PWD\simply-journal-admin-<version>.msi"
	```

### Publish the OS Package

Once an OS package passes validation, publish it through the distribution channel that end users consume.

=== "Debian"

	!!! info
		The Debian package is published to a Cloudsmith Debian repository in the [`pravi-brothers`](https://app.cloudsmith.com/pravi-brothers) workspace. This workflow assumes that the repository already exists and that you already exported `CLOUDSMITH_API_KEY` on the host.

	A successful Debian publication depends on a repository endpoint that serves both the uploaded `.deb` artifact and the APT metadata files that clients use for resolution and installation. Cloudsmith hosts both: it stores the Debian packages and generates the repository metadata that APT consumes.

	```mermaid
	flowchart LR
		subgraph PublisherWorkflow[Publisher Workflow]
			direction LR
			DEV[Developer] -->|Builds| PIPE[Build Pipeline]
			PIPE --> DEB["Debian Package (.deb)"]
			DEB -->|Uploads Package| REPO[Cloudsmith APT Repository]
			REPO --> PKGS[Debian Packages]
			REPO --> GZ[Packages.gz]
			REPO --> REL[Release]
			REPO --> IREL[InRelease]
		end

		classDef action fill:#dbeafe,stroke:#2563eb,stroke-width:1.5px,color:#0f172a;
		classDef repository fill:#e2e8f0,stroke:#475569,stroke-width:1.5px,color:#0f172a;
		class DEV,PIPE,DEB action;
		class REPO,PKGS,GZ,REL,IREL repository;
		style PublisherWorkflow fill:#f8fafc,stroke:#cbd5e1,stroke-width:1px;
	```

	From the `projects/` directory, open the dedicated Debian packaging container and forward the API key into the container session.

	```bash
	../build.sh build --path proj2_journal_admin/Dockerfile.devEnv -- --env CLOUDSMITH_API_KEY="$CLOUDSMITH_API_KEY"
	```

	Inside the container, define the repository coordinates once for the session.

	```bash
	export CLOUDSMITH_NAMESPACE=pravi-brothers
	export CLOUDSMITH_REPOSITORY=modern-python-engineering
	export CLOUDSMITH_UBUNTU_2404=ubuntu/noble
	export CLOUDSMITH_UBUNTU_2604=ubuntu/resolute
	```

	Upload the generated Debian package for the Ubuntu 24.04 and Ubuntu 26.04 APT distributions.

	```bash
	cloudsmith push deb "${CLOUDSMITH_NAMESPACE}/${CLOUDSMITH_REPOSITORY}/${CLOUDSMITH_UBUNTU_2404}" \
		"<path-to-package>/simply-journal-admin_<debian-version>_<architecture>.deb"
	```

	```bash
	cloudsmith push deb "${CLOUDSMITH_NAMESPACE}/${CLOUDSMITH_REPOSITORY}/${CLOUDSMITH_UBUNTU_2604}" \
		"<path-to-package>/simply-journal-admin_<debian-version>_<architecture>.deb"
	```

	> `noble` targets Ubuntu 24.04, `resolute` targets Ubuntu 26.04.

	Verify that Cloudsmith indexed the uploaded package.

	```bash
	cloudsmith list packages "${CLOUDSMITH_NAMESPACE}/${CLOUDSMITH_REPOSITORY}" -q "simply-journal-admin"
	```

=== "MSI"

	!!! info
		The Winget Manifest is published to the Windows Package Manager [community repository](https://github.com/microsoft/winget-pkgs). This workflow assumes that you already have a GitHub account, a fork of `microsoft/winget-pkgs`, and the required Winget tooling installed.

	A successful WinGet publication depends on two durable inputs: a stable installer URL that keeps the MSI available at the published location, and a validated manifest that is accepted into the `winget-pkgs` repository.

	```mermaid
	flowchart LR
		subgraph PublisherWorkflow[Publisher Workflow]
			direction LR
			DEV[Developer] -->|Builds| PIPE[Build Pipeline] --> MSI[MSI Package] -->|Uploads MSI| REPO[Cloudsmith Raw Repository]
			DEV2[Developer] -->|Creates Pull Request| WPKG[winget-pkgs Repository] --> MAN[Manifest]
			WPKG --> URL[Installer URL]
			WPKG --> HASH[SHA256]
			WPKG --> VER[Version]
		end

		classDef action fill:#dbeafe,stroke:#2563eb,stroke-width:1.5px,color:#0f172a;
		classDef repository fill:#e2e8f0,stroke:#475569,stroke-width:1.5px,color:#0f172a;
		class DEV,DEV2,PIPE,MSI action;
		class WPKG,REPO,MAN,URL,HASH,VER repository;
		style PublisherWorkflow fill:#f8fafc,stroke:#cbd5e1,stroke-width:1px;
	```

	The Windows builder image already includes the Cloudsmith CLI. In the running container session, define the publication variables before uploading the MSI.

	```powershell
	$env:CLOUDSMITH_API_KEY = "<your-api-key>"
	$cloudsmithNamespace = "pravi-brothers"
	$cloudsmithRepository = "modern-python-engineering"
	```

	Upload the generated MSI to the Cloudsmith Raw repository in the `pravi-brothers` workspace. The raw repository provides the stable installer URL that the Winget manifest references.

	```powershell
	cloudsmith push raw "$cloudsmithNamespace/$cloudsmithRepository" .\.build\simply-journal-admin-1.0.0.msi --version 1.0.0
	```

	The Cloudsmith download URL becomes the `InstallerUrl` in the Winget manifest.

	```text
	https://dl.cloudsmith.io/public/pravi-brothers/modern-python-engineering/raw/versions/1.0.0/simply-journal-admin-1.0.0.msi
	```

	Calculate the installer hash used by the Winget manifest.

	```powershell
	Get-FileHash .\.build\simply-journal-admin-1.0.0.msi -Algorithm SHA256
	```

	Generate a new manifest set for the first release. Use the URL of the published MSI, not a local file path.

	```powershell
	wingetcreate new "https://dl.cloudsmith.io/public/pravi-brothers/modern-python-engineering/raw/versions/1.0.0/simply-journal-admin-1.0.0.msi"
	```

	For later releases, update the existing package identifier instead of starting from scratch.

	```powershell
	wingetcreate update ModernPythonEngineering.SimplyJournalAdmin -u "https://dl.cloudsmith.io/public/pravi-brothers/modern-python-engineering/raw/versions/<version>/simply-journal-admin-<version>.msi" -v "<version>"
	```

	External contributors submit manifests through a fork of `microsoft/winget-pkgs`. Prepare a local submission branch in your fork with sparse checkout enabled for this publisher folder.

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

	Microsoft validation checks the manifest schema, installer URL, hash, metadata, and installation behavior before the pull request is merged. Future versions are published by uploading a new MSI version to the Cloudsmith Raw repository, creating a new manifest version directory, updating the installer URL and SHA-256 hash, validating the manifest, and submitting one pull request per package version.

## Consumer Workflow

### Configure Package Manager

Configure the target package manager before installation so it can resolve packages from the proprietary distribution channel.

=== "Debian (.deb)"

	From the end-user perspective, configure the Cloudsmith APT repository from the `pravi-brothers` workspace first. Cloudsmith hosts both the Debian packages and the repository metadata that APT needs for resolution and installation.

	```bash
	curl -fsSL "https://dl.cloudsmith.io/public/pravi-brothers/modern-python-engineering/gpg.key" | sudo gpg --dearmor -o /usr/share/keyrings/pravi-brothers-modern-python-engineering.gpg
	```

	Add the Debian repository to the local APT sources.

	```bash
	printf 'deb [signed-by=/usr/share/keyrings/pravi-brothers-modern-python-engineering.gpg] https://dl.cloudsmith.io/public/pravi-brothers/modern-python-engineering/deb/ubuntu noble main\n' | sudo tee /etc/apt/sources.list.d/simply-journal-admin.list
	```

	!!! note
		Because this repository is public, the public APT source URL together with the Cloudsmith GPG signing key is sufficient. No authenticated repository URL is required for installation.

=== "MSI (.msi)"

	No local package-manager repository configuration is required when the package manifest is hosted in `winget-pkgs`. WinGet reads the published manifest from the configured WinGet source and uses its installer URL to download the MSI.

### Install the OS Package

Users typically install the package through the native package-management workflow of the target platform.

=== "Linux (.deb)"

	Refresh APT metadata on the target machine.

	```bash
	sudo apt update
	```

	Install the published package through APT.

	```bash
	sudo apt install simply-journal-admin
	```

	The `apt update` and `apt install` commands above invoke the package consumer workflow illustrated in the following simplified diagram.

	```mermaid
	flowchart LR
		subgraph ConsumerWorkflow[Package Consumer Workflow]
			direction LR
			UPDATE[apt update] --> APT[APT Package Manager]
			APT -->|Requests Metadata| REPO2[Cloudsmith APT Repository]
			REPO2 -->|Returns Release + Packages.gz| APT
			INSTALL[apt install simply-journal-admin] --> APT
			APT -->|Requests Package| REPO2
			REPO2 -->|Returns .deb + dependencies| APT
			APT -->|Installs Package| APP[Installed App]
		end

		classDef repository fill:#e2e8f0,stroke:#475569,stroke-width:1.5px,color:#0f172a;
		classDef client fill:#dcfce7,stroke:#15803d,stroke-width:1.5px,color:#0f172a;
		classDef installed fill:#fef3c7,stroke:#b45309,stroke-width:1.5px,color:#0f172a;
		class REPO2 repository;
		class UPDATE,INSTALL,APT client;
		class APP installed;
		style ConsumerWorkflow fill:#f8fafc,stroke:#cbd5e1,stroke-width:1px;
	```

=== "Windows (.msi)"

	From the end-user perspective, following command will install the published MSI using the `winget` command:

	```powershell
	winget install --id ModernPythonEngineering.SimplyJournalAdmin --source winget
	```

	The `winget install` command above invokes the package consumer workflow illustrated in the following simplified diagram. The WinGet client downloads the package manifest from the `winget-pkgs` repository, and the manifest references the MSI hosted in Cloudsmith, so the installer itself is downloaded from the Cloudsmith Raw repository.

	```mermaid
	flowchart LR
		subgraph ConsumerWorkflow[Package Consumer Workflow]
			direction LR
			CMD[winget install] --> WINGET[WinGet Client]
			WINGET -->|Requests Manifest| WPKG2[winget-pkgs]
			WPKG2 -->|Returns Manifest + URL| WINGET
			WINGET -->|Requests MSI| REPO2[Cloudsmith Raw Repository]
			REPO2 -->|Returns MSI| MSI2[Downloaded MSI]
			WINGET -->|invokes| WININST[Windows Installer]
			MSI2 --> WININST -->|installs| APP[Installed App]
		end

		classDef repository fill:#e2e8f0,stroke:#475569,stroke-width:1.5px,color:#0f172a;
		classDef client fill:#dcfce7,stroke:#15803d,stroke-width:1.5px,color:#0f172a;
		classDef tool fill:#dbeafe,stroke:#2563eb,stroke-width:1.5px,color:#0f172a;
		classDef installed fill:#fef3c7,stroke:#b45309,stroke-width:1.5px,color:#0f172a;
		class WPKG2,REPO2 repository;
		class CMD,WINGET client;
		class MSI2,WININST tool;
		class APP installed;
		style ConsumerWorkflow fill:#f8fafc,stroke:#cbd5e1,stroke-width:1px;
	```

## Useful Links

- [Submitting a package to `winget-pkgs`](https://learn.microsoft.com/en-us/windows/package-manager/package/repository)
- [Winget Releaser GitHub Action](https://github.com/vedantmgoyal9/winget-releaser)