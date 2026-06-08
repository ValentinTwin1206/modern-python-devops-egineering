# Python system environment

This page explains how Python is installed on common operating systems and where packages land.

## Applied Project

### Project Setup

The applied project is a small admin CLI called `journal-admin` that reads recent `systemd` journal entries. It imports [`systemd.journal`](https://www.freedesktop.org/software/systemd/python-systemd/journal.html) from the APT package [`python3-systemd`](https://packages.ubuntu.com/noble/python3-systemd) and declares no PyPI runtime dependencies because the binding comes from the distribution package manager and links against `libsystemd` in `/usr/lib`. This makes it a good fit for the system environment because the runtime dependency is intentionally owned by the operating system package manager instead of a project-local environment.

### Run the Project

Application, test, lint, and shell-exit commands are documented in the [section README](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/proj1_journal_admin/README.md). The project components are documented in the [Project Components](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/proj1_journal_admin/README.md#project-components) section of the section README.

## Python System Setup

### When to use the system environment?

Use the system environment when Python is part of the operating system or container base image rather than a per-project setup. Common examples include distribution-managed tools, administrator-provided utilities, and very small runtime containers where the image itself is the isolation boundary.

### Tradeoffs

#### Pros

- ✅ Works well in containers with one interpreter to manage.
- ✅ APT packages follow the base operating system lifecycle.
- ✅ User installs avoid administrator permissions for one account.

#### Cons

- ⚠️ Risky on developer machines because upgrades can affect system tools.
- ⚠️ Local administrator installs add a package layer outside APT.
- ⚠️ User installs still share one package directory across projects.
- ⚠️ Shared targets can make projects affect each other.
- ⚠️ Poor fit for normal per-project development.

### Install Python

Python can be installed by the operating system, by a language-specific installer, or by a third-party package manager. The project in this section still uses Linux containers, but the host-level installation model differs across Linux, Windows, and macOS.

#### Default Python

=== "Linux (Debian-based)"

    Debian-based systems such as Debian, Ubuntu, Linux Mint, and Raspberry Pi OS ship Python as part of the operating system. The default interpreter lives at `/usr/bin/python3` and is managed by APT under `/usr`, alongside the standard library, headers, and distribution-provided packages.

    | Ubuntu release | APT suite | Bundled `python3` |
    | -------------- | --------- | ----------------- |
    | 22.04 LTS      | jammy     | Python 3.10       |
    | 24.04 LTS      | noble     | Python 3.12       |
    | 26.04 LTS      | resolute  | Python 3.14       |

    Avoid replacing the distribution-managed `/usr/bin/python3`, because operating system tools expect the default interpreter that ships with the release.

=== "Windows"

    Windows does not ship a distribution-managed Python in the same way Debian-based Linux does. The usual choices are the [python.org installer](https://www.python.org/downloads/windows/), [winget](https://learn.microsoft.com/windows/package-manager/winget/), or the Microsoft Store package.

    !!! info

        The Python launcher (`py`) is useful on Windows because multiple Python versions can be installed at the same time without relying only on `PATH` order. It is typically installed alongside the above mentioned installation packages.

=== "macOS"

    Modern macOS does not provide a full Python setup for project development. Since macOS Monterey 12.3, Apple has discouraged relying on the system-provided Python for development work, so developers usually install Python from [python.org](https://www.python.org/downloads/macos/), [Homebrew](https://brew.sh/), `uv`, or `pyenv`.

    !!! info

        On Ventura, Sonoma, and Sequoia, `python3` may be missing, may point to an Apple-managed `/usr/bin/python3` stub, or may come from Xcode Command Line Tools. Do not treat that interpreter as a stable project dependency.

#### Install another version

=== "Linux (Debian-based)"

    Install another Python version side by side instead of replacing the distribution-managed interpreter. On Ubuntu, an extra package source is the common path when the release does not ship the Python version you need.

    Add the extra package source:

    ```bash
    sudo add-apt-repository ppa:deadsnakes/ppa
    ```

    Refresh the APT package index:

    ```bash
    sudo apt update
    ```

    Install the versioned interpreter together with the matching `venv` and header packages:

    ```bash
    sudo apt install python3.13 python3.13-venv python3.13-dev
    ```

    Create environments with the explicit interpreter command you installed:

    ```bash
    python3.13 -m venv .venv
    ```

=== "Windows"

    Install Python with `winget`:

    ```powershell
    winget install Python.Python.3.13
    ```

    Check the installed version with the Python launcher:

    ```powershell
    py -3.13 --version
    ```

    Create environments with the explicit version:

    ```powershell
    py -3.13 -m venv .venv
    ```

=== "macOS"

    Install Python with Homebrew:

    ```bash
    brew install python@3.13
    ```

    Check the installed version:

    ```bash
    python3.13 --version
    ```

    Create environments with the explicit interpreter:

    ```bash
    python3.13 -m venv .venv
    ```

### Installation footprint

A Python installation includes the CPython interpreter, standard library modules, package directories, native extension headers, build configuration, and integration with the operating system shell through `PATH` entries or launchers.

=== "Linux (Debian-based)"

    | Component | Common Debian-based path |
    | --------- | ------------------------ |
    | Interpreter | `/usr/bin/python3` |
    | Standard library | `/usr/lib/python3.x/` |
    | Interpreter installation packages | `/usr/lib/python3/dist-packages/` |
    | System-wide administrator-installed packages | `/usr/local/lib/python3.x/dist-packages/` |
    | User packages | `~/.local/lib/python3.x/site-packages/` |
    | Header files | `/usr/include/python3.x/` |

=== "Windows"

    | Component | Common Windows path |
    | --------- | ------------------- |
    | Interpreter | `%LocalAppData%\Programs\Python\Python313\python.exe` |
    | Standard library | `%LocalAppData%\Programs\Python\Python313\Lib` |
    | Interpreter installation packages |  |
    | System-wide administrator-installed packages | `C:\Program Files\Python313\Lib\site-packages` if Python is installed for all users |
    | User packages | `%AppData%\Python\Python313\site-packages` |
    | Header files | `%LocalAppData%\Programs\Python\Python313\include` |

=== "macOS"

    | Component | Common macOS path |
    | --------- | ----------------- |
    | Interpreter | `/opt/homebrew/bin/python3.13` |
    | Standard library | `/opt/homebrew/Frameworks/Python.framework/Versions/3.13/lib/python3.13/` |
    | Interpreter installation packages |  |
    | System-wide administrator-installed packages | `/Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/site-packages` |
    | User packages | `~/Library/Python/3.13/lib/python/site-packages` |
    | Header files | `/opt/homebrew/Frameworks/Python.framework/Versions/3.13/include/python3.13/` |

- **Standard library:** built-in modules such as `os`, `pathlib`, `json`, and `subprocess` ship with Python itself.

- **Interpreter installation packages:** in this section, the concrete example is the Debian [system target](#system-target), where a package such as `python3-systemd` lands under `/usr/lib/python3/dist-packages/`.

- **System-wide administrator-installed packages:** packages installed into the administrator-controlled prefix affect every project that uses that interpreter. They are covered in [Local administrator target](#local-administrator-target).

- **User packages:** packages installed with `--user` stay under the current user's home directory and are only available to that user's Python processes. They are covered in [User target](#user-target).

- **Header files:** development headers are needed when packages compile C or C++ extension modules against the current interpreter. On Debian-based Linux, they come from packages such as `python3-dev` or `python3.13-dev`; python.org installers for Windows and macOS include the development files needed for common extension builds.

### Package installation targets

Python packages can land in [operating-system](#system-target), [administrator](#local-administrator-target), or [user](#user-target) locations. A package can be used with an `import` statement when it is installed into a directory that the active interpreter searches on `sys.path`, and Python resolves that import from the first matching package directory on that search path. The target therefore decides who can import the package and which projects are affected by future upgrades. The [PATH and import path](#path-and-import-path) inspection commands show how to inspect that search path.


#### System target

=== "Linux (Debian-based)"

    The system target is owned by APT. Importable Python packages typically land under `/usr/lib/python3/dist-packages/`. This exists because Linux distributions package Python libraries for operating-system tools and stable release updates.

    Use APT for Python libraries that support system services, distribution-managed automation, or operating-system integration. The `journal-admin` project in this section is a concrete example: it imports `systemd.journal`, which is part of the APT package `python3-systemd` and binds to `libsystemd` shipped with the operating system. There is no equivalent wheel on PyPI that works without that system library, so APT is the right install path. Avoid APT for normal project dependencies like `python3-requests`, as APT packages follow the operating-system release cycle and can be older or patched differently than the versions on PyPI.

    Install the distribution-managed Python binding with the distribution package manager:

    ```bash
    sudo apt install python3-systemd
    ```

    Import it with the system interpreter:

    ```bash
    python3 -c "import systemd.journal; print(systemd.journal.__file__)"
    ```

=== "Windows"

    Windows does not have an APT-like Python package target that is part of the operating system. 

    !!! info

        WinGet is useful for installing Python, applications, and tools such as `uv`, but Python libraries for `import` statements usually come from [Local administrator targets](#local-administrator-target), [User targets](#user-target), or a virtual environment.

        Install `uv` with Windows Package Manager:

        ```powershell
        winget install astral-sh.uv
        ```

=== "macOS"

    Apple-managed Python paths are for operating-system or developer-tool use.

    !!! info

        Homebrew can install Python-based tools such as `uv`, but those packages live in Homebrew's own prefix, not in an Apple-managed system Python target. Python libraries for `import` statements usually come from [Local administrator targets](#local-administrator-target), [User targets](#user-target), or a virtual environment.

        Install `uv` with Homebrew:

        ```bash
        brew install uv
        ```

#### Local administrator target

=== "Linux (Debian-based)"

    The local administrator target installs packages outside APT while still making them available to the system interpreter. Those installs usually land under `/usr/local/lib/python3.x/dist-packages/`. On modern Debian and Ubuntu, the interpreter is marked as externally managed under PEP 668, so `pip` and `uv` require an explicit override.

    === "uv"

        Install a package into the local administrator target with `uv`:

        ```bash
        uv pip install --system --break-system-packages requests
        ```

    === "pip"

        Install a package into the local administrator target with `pip`:

        ```bash
        pip3 install --break-system-packages requests
        ```

=== "Windows"

    An all-users Python install under `C:\Program Files\Python313\` is the closest equivalent. Installing packages into it usually requires administrator permissions.

    === "uv"

        Install a package into the selected all-users interpreter with `uv`:

        ```powershell
        uv pip install --python "C:\Program Files\Python313\python.exe" requests
        ```

    === "pip"

        Install a package into the selected all-users interpreter with `pip`:

        ```powershell
        py -3.13 -m pip install requests
        ```

=== "macOS"

    A Homebrew or python.org interpreter prefix is the closest equivalent. Installing packages into that prefix affects every project using that interpreter.

    === "uv"

        Install a package into the selected interpreter prefix with `uv`:

        ```bash
        uv pip install --python /opt/homebrew/bin/python3.13 --break-system-packages requests
        ```

    === "pip"

        Install a package into the selected interpreter prefix with `pip`:

        ```bash
        python3.13 -m pip install --break-system-packages requests
        ```

#### User target

=== "Linux (Debian-based)"

    The user target keeps packages inside the current user's home directory, usually under `~/.local/lib/python3.x/site-packages/`.

    ```bash
    pip3 install --user karva ruff
    ```

=== "Windows"

    Install user-level tools without administrator permissions:

    ```powershell
    py -3.13 -m pip install --user karva ruff
    ```

    User packages usually land under `%AppData%\Python\Python313\site-packages`.

=== "macOS"

    Install user-level tools without writing into the interpreter prefix:

    ```bash
    python3.13 -m pip install --user karva ruff
    ```

    User packages usually land under `~/Library/Python/3.13/lib/python/site-packages`.

## Inspection

### PATH and import path

The shell searches `PATH` from left to right. Python's import resolver searches `sys.path`, which is independent from `PATH`.

Show the resolved interpreter:

```bash
which python3
```

Show the active import path:

```bash
python3 -c "import sys; [print(path) for path in sys.path]"
```

Show the full site configuration:

```bash
python3 -m site
```

### Inspecting installed packages

Show where the APT-managed `systemd.journal` binding lives:

```bash
python3 -c "import systemd.journal; print(systemd.journal.__file__)"
```

Show where user-installed packages and their console scripts live:

```bash
python3 -c "import karva, ruff; print(karva.__file__); print(ruff.__file__)"
```

Show the files owned by an APT-managed Python package:

```bash
dpkg -L python3-systemd | grep -E '/dist-packages/systemd(/|$)' | head
```
