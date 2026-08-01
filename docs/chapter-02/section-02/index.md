# OS Packages

Operating-system (OS) packages are native software distributions designed for a specific operating-system family.

## Overview

OS packages let users install, upgrade, verify, and remove applications through the software-management tools already provided by their operating system. A package can contain application code, launchers, configuration, shared libraries, or an embedded runtime, and it can declare dependencies on components supplied by the platform. This makes OS packaging especially useful for system utilities, command-line applications, desktop software, and enterprise tools that require predictable installation or close operating-system integration.

Package formats are platform-specific rather than universally portable. A project that supports several operating systems therefore creates a separate native artifact for each target family, even when every artifact contains the same application. The most common combinations are:

| Operating System | Package Format | Common Package Manager |
|------------------|----------------|------------------------|
| Debian and Ubuntu | `.deb` | `apt`, `dpkg` |
| Fedora and Red Hat Enterprise Linux | `.rpm` | `dnf`, `rpm` |
| openSUSE | `.rpm` | `zypper`, `rpm` |
| Windows | `.msi`, `.msix` | WinGet, Windows Installer |
| macOS | `.pkg` | `installer` |

## Platform Guides

The platform guides use the same heading layout so that you can compare each packaging workflow directly.

- [Debian packages](debian.md)
- [Windows MSI packages](windows.md)