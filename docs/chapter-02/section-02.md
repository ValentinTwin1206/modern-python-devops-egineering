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

### Package Layout

The packaged result includes the Python application payload together with platform-native installation metadata and launcher behavior.

Examples:

=== "Debian"

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

	The Debian package installs an embedded Python runtime under `/opt/simply-journal-admin`, unpacks the built wheel into `app/site-packages`, and exposes a thin wrapper in `/usr/bin`. The package also declares `python3-systemd` as an OS-level dependency, so APT resolves that dependency during installation.

=== "MSI"

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

	The MSI stages an embedded Python runtime under `runtime`, extracts the built wheel into `app\site-packages`, and installs a `simply-journal-admin.cmd` launcher in the install root. The installer also updates the machine `PATH`, which lets the command run from a standard Windows shell after installation.

!!! info
	The package does not ask end users to run `pip` on the target machine. Instead, it bundles the application payload ahead of time and installs it through the operating system's native package manager.

## Packaging Workflow

### Create the OS Package

Build the Python wheel first, then wrap that wheel in the target operating system's package format.

=== "Debian package"

	```bash
	../build.sh build --path proj2_journal_admin/Dockerfile.devEnv
	```

	Inside the container, synchronize the environment and build the wheel:

	```bash
	uv sync --all-groups
	```

	```bash
	uv build --wheel --out-dir /build
	```

	Then build the Debian package:

	```bash
	dpkg-buildpackage -us -uc -b
	```

=== "MSI package"

	```powershell
	docker build -f Dockerfile.windows -t sja-msi-builder .
	```

	```powershell
	New-Item -ItemType Directory -Path .build -Force
	```

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

Unlike a wheel, an OS package is usually published through a platform-specific distribution channel.

The most common distribution methods are:

| Distribution Method | Purpose |
| ------------------- | ------- |
| APT repository | Standard Debian and Ubuntu distribution channel for Linux packages |
| Windows software distribution platform | Standard enterprise channel for MSI deployment, such as Intune, Group Policy, or an internal software catalog |
| GitHub Releases | Simple release distribution for public or internal download |
| Internal artifact repository | Controlled distribution of build artifacts inside an organization |

### Install the OS Package

Users typically install the package through the native package-management workflow of the target platform.

=== "Linux (.deb)"

	```bash
	sudo apt install ./simply-journal-admin_<version>_all.deb
	```

=== "Windows (.msi)"

	```powershell
	msiexec /i "$PWD\simply-journal-admin-<version>.msi" /L*V! "$PWD\install.log"
	```