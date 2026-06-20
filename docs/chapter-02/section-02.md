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

Unlike a wheel, an OS package is usually published through a platform-specific distribution channel. The most common distribution methods are:

| Distribution Method | Purpose |
| ------------------- | ------- |
| APT repository | Standard Debian and Ubuntu distribution channel for Linux packages |
| Windows software distribution platform | Standard enterprise channel for MSI deployment, such as Intune, Group Policy, or an internal software catalog |
| GitHub Releases | Simple release distribution for public or internal download |
| Internal artifact repository | Controlled distribution of build artifacts inside an organization |

### Install the OS Package

Users typically install the package through the native package-management workflow of the target platform.

=== "Linux (.deb)"

	From end-user perspective, install the Debian package directly from the file system:

	```bash
	sudo apt install ./simply-journal-admin_<version>_all.deb
	```

=== "Windows (.msi)"

	From end-user perspective, install the MSI package and write an installation log:

	```powershell
	msiexec /i "$PWD\simply-journal-admin-<version>.msi" /L*V! "$PWD\install.log"
	```