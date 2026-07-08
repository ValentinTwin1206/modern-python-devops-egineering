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

Build the Python wheel first, then wrap that wheel in the target operating system's package format.

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

After building the package, verify that:

* the installer completes successfully on a clean target system
* the launcher is created in the expected platform-specific location
* the bundled runtime and application payload are installed in the expected directories
* the CLI starts successfully and returns log entries
* package removal cleans up generated state correctly

For example:

=== "Debian"

	Install the generated Debian package with `apt`:

	```bash
	sudo apt install ./simply-journal-admin_<version>_all.deb
	simply-journal-admin --since-minutes 60
	sudo apt remove simply-journal-admin
	```

=== "MSI"

	Install the generated MSI and capture a log file:

	```powershell
	msiexec /i "$PWD\simply-journal-admin-<version>.msi" /L*V! "$PWD\install.log"
	simply-journal-admin --since-minutes 60
	msiexec /x "$PWD\simply-journal-admin-<version>.msi"
	```

### Publish the OS Package

Publishing starts after the `.deb` or `.msi` artifact already exists. The publication step moves the package from a local build output into the distribution channel that end users consume.

=== "Debian"

	The Debian package is published to a JFrog Artifactory Debian repository. This workflow assumes that you already have an Artifactory instance, a local Debian repository, and an access token with permission to upload packages.

	Configure the JFrog CLI with the existing access token.

	```bash
	jf c add modern-python --url "https://<tenant>.jfrog.io" --access-token "$JFROG_ACCESS_TOKEN" --interactive=false
	```

	Confirm that the CLI can access Artifactory.

	```bash
	jf rt ping
	```

	Upload the generated Debian package. The `--deb` value sets the Debian distribution, component, and architecture that APT uses when resolving the package.

	```bash
	jf rt upload "<path-to-package>/simply-journal-admin_<debian-version>_<architecture>.deb" "debian-local/pool/main/s/simply-journal-admin/" --deb "bookworm/main/amd64"
	```

	Verify that Artifactory indexed the uploaded package.

	```bash
	jf rt search "debian-local/pool/main/s/simply-journal-admin/"
	```

	Future versions follow the same path: update the Debian version in `debian/changelog`, rebuild the package, upload the new `.deb` with `jf rt upload`, and let configured APT clients install or upgrade from the repository.

=== "MSI"

	The MSI package is published through the Windows Package Manager [community repository](https://github.com/microsoft/winget-pkgs). This workflow assumes that you already have a GitHub account, a fork of `microsoft/winget-pkgs`, and the required Winget tooling installed.

	Upload the generated MSI to the repository's GitHub Release for `v1.0.0`. The release can contain all package artifacts for the repository, but the Winget manifest references only the Windows installer asset.

	```powershell
	gh release upload v1.0.0 .\.build\simply-journal-admin-1.0.0.msi --clobber
	```

	The release asset URL becomes the `InstallerUrl` in the Winget manifest.

	```text
	https://github.com/ValentinTwin1206/modern-python-devops-egineering/releases/download/v1.0.0/simply-journal-admin-1.0.0.msi
	```

	Calculate the installer hash used by the Winget manifest.

	```powershell
	Get-FileHash .\.build\simply-journal-admin-1.0.0.msi -Algorithm SHA256
	```

	Generate a new manifest set for the first release. Use the URL of the published MSI, not a local file path.

	```powershell
	wingetcreate new "https://github.com/ValentinTwin1206/modern-python-devops-egineering/releases/download/v1.0.0/simply-journal-admin-1.0.0.msi"
	```

	For later releases, update the existing package identifier instead of starting from scratch.

	```powershell
	wingetcreate update ModernPythonEngineering.SimplyJournalAdmin -u "https://github.com/ValentinTwin1206/modern-python-devops-egineering/releases/download/v<version>/simply-journal-admin-<version>.msi" -v "<version>"
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

	Microsoft validation checks the manifest schema, installer URL, hash, metadata, and installation behavior before the pull request is merged. Future versions are published by adding a new GitHub Release asset, creating a new manifest version directory, updating the installer URL and SHA-256 hash, validating the manifest, and submitting one pull request per package version.

### Install the OS Package

Users typically install the package through the native package-management workflow of the target platform.

=== "Linux (.deb)"

	From the end-user perspective, configure the JFrog Artifactory Debian repository first. Use the exact key URL and private-auth snippet from the Artifactory repository setup page when your repository requires authentication.

	```bash
	curl -fsSL "<artifactory-public-gpg-key-url>" | sudo gpg --dearmor -o /usr/share/keyrings/jfrog-debian-local.gpg
	```

	Add the Debian repository to the local APT sources.

	```bash
	printf 'deb [signed-by=/usr/share/keyrings/jfrog-debian-local.gpg] https://<tenant>.jfrog.io/artifactory/debian-local bookworm main\n' | sudo tee /etc/apt/sources.list.d/simply-journal-admin.list
	```

	!!! note
		For private repositories, use the authentication configuration shown by Artifactory instead of writing tokens or passwords directly into source control, shared shell scripts, or command history.

	Refresh APT metadata on the target machine.

	```bash
	sudo apt update
	```

	Install the published package through APT.

	```bash
	sudo apt install simply-journal-admin
	```

=== "Windows (.msi)"

	From the end-user perspective, install the published MSI through the Windows Package Manager community source:

	```powershell
	winget install --id ModernPythonEngineering.SimplyJournalAdmin --source winget
	```

## Useful Links

- [Submitting a package to `winget-pkgs`](https://learn.microsoft.com/en-us/windows/package-manager/package/repository)
- [Winget Releaser GitHub Action](https://github.com/vedantmgoyal9/winget-releaser)