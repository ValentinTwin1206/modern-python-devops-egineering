# Python system environment

This page explains how Python is installed on common operating systems and where packages land.

## Tiny Webserver Project

The example uses the tiny Bottle web server project. Step-by-step development workflow instructions live in the section [`README.md`](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-01/README.md).

### Project Setup

This example uses [Bottle](https://bottlepy.org/docs/dev/) as the application dependency, with [Karva](https://matthewmckee4.github.io/karva/) and [Ruff](https://docs.astral.sh/ruff/) as user-facing development tools. The project files below show how that setup maps onto the system, administrator, and user installation targets discussed in this section.

| Component            | Description |
| -------------------- | ----------- |
| [`Dockerfile.devEnv`](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-01/Dockerfile.devEnv) | This development image defines a safe environment for inspecting Python installation targets. It mirrors the package-installation layers discussed below without modifying the host machine. |
| [`Dockerfile`](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-01/Dockerfile) | This deployment image shows the same system-level installation model in a runtime container. It complements the discussion by demonstrating how a single system interpreter can be sufficient in container-focused workflows. |
| [`pyproject.toml`](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-01/pyproject.toml) | This file holds the Python project metadata for the tiny web server example. It defines the package and dependencies that later installation commands place into different Python package targets. |

### Run the project

Application, test, lint, and shell-exit commands are documented in the [section README](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-01/README.md).

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

    The Python launcher (`py`) is useful on Windows because multiple Python versions can be installed at the same time without relying only on `PATH` order.

=== "macOS"

    Modern macOS does not ship a full Python for project development. Since macOS Monterey 12.3, Apple expects developers to install their own Python from [python.org](https://www.python.org/downloads/macos/), [Homebrew](https://brew.sh/), `uv`, or `pyenv`.

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

A Python installation includes the CPython interpreter, standard library modules, package directories, native extension headers, build configuration, and shell integration through `PATH` or a launcher.

=== "Linux (Debian-based)"

    | Component | Common Debian-based path |
    | --------- | ------------------------ |
    | Interpreter | `/usr/bin/python3` |
    | Standard library | `/usr/lib/python3.x/` |
    | Installed packages | `/usr/lib/python3/dist-packages/` |
    | Administrator packages | `/usr/local/lib/python3.x/dist-packages/` |
    | User packages | `~/.local/lib/python3.x/site-packages/` |
    | Virtual environment packages | `.venv/lib/python3.x/site-packages/` |
    | Header files | `/usr/include/python3.x/` |

=== "Windows"

    | Component | Common Windows path |
    | --------- | ------------------- |
    | Interpreter | `%LocalAppData%\Programs\Python\Python313\python.exe` |
    | Standard library | `%LocalAppData%\Programs\Python\Python313\Lib` |
    | Installed packages | `%LocalAppData%\Programs\Python\Python313\Lib\site-packages` |
    | Administrator packages | `C:\Program Files\Python313\Lib\site-packages` |
    | User packages | `%AppData%\Python\Python313\site-packages` |
    | Virtual environment packages | `.venv\Lib\site-packages` |
    | Header files | `%LocalAppData%\Programs\Python\Python313\include` |

=== "macOS"

    | Component | Common macOS path |
    | --------- | ----------------- |
    | Interpreter | `/opt/homebrew/bin/python3.13` |
    | Standard library | `/opt/homebrew/Frameworks/Python.framework/Versions/3.13/lib/python3.13/` |
    | Installed packages | `/opt/homebrew/lib/python3.13/site-packages` |
    | Administrator packages | `/Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/site-packages` |
    | User packages | `~/Library/Python/3.13/lib/python/site-packages` |
    | Virtual environment packages | `.venv/lib/python3.13/site-packages` |
    | Header files | `/opt/homebrew/Frameworks/Python.framework/Versions/3.13/include/python3.13/` |

- **Standard library:** built-in modules such as `os`, `pathlib`, `json`, and `subprocess` ship with Python itself.

- **Header files:** development headers are needed when packages compile C or C++ extension modules against the current interpreter. On Debian-based Linux, they come from packages such as `python3-dev` or `python3.13-dev`; python.org installers for Windows and macOS include the development files needed for common extension builds.

- **Installed-package imports:** `import bottle` only works when `bottle` is installed into one of the package directories on the active interpreter's `sys.path`.

    ```python
    import bottle
    ```

- **Import resolution:** the exact file that Python imports depends on where the package was installed, because `sys.path` determines which matching module or package directory is found first.

### Package installation targets

Python packages can land in operating-system, administrator, user, or environment-specific locations. The target decides who can import them and which projects are affected by future upgrades.

#### System target

=== "Linux (Debian-based)"

    The system target is owned by APT. Packages typically land under `/usr/lib/python3/dist-packages/` and update with the base operating system.

    Install a distribution-managed Python package with the distribution package manager:

    ```bash
    sudo apt install python3-systemd
    ```

=== "Windows"

    Windows does not have an APT-like Python package target that is part of the operating system. Packages are installed into the selected Python distribution, a user site directory, or a virtual environment.

=== "macOS"

    Apple-managed Python paths are for operating-system or developer-tool use. Project packages should go into a separate Python installation, a user site directory, or a virtual environment.

#### Local administrator target

=== "Linux (Debian-based)"

    The local administrator target installs packages outside APT while still making them available to the system interpreter. Those installs usually land under `/usr/local/lib/python3.x/dist-packages/`. On modern Debian and Ubuntu, the interpreter is marked as externally managed under PEP 668, so `pip` and `uv` require an explicit override.

    === "uv"

        Install a package into the local administrator target with `uv`:

        ```bash
        uv pip install --system --break-system-packages bottle
        ```

    === "pip"

        Install a package into the local administrator target with `pip`:

        ```bash
        pip3 install --break-system-packages bottle
        ```

=== "Windows"

    An all-users Python install under `C:\Program Files\Python313\` is the closest equivalent. Installing packages into it usually requires administrator permissions.

    === "uv"

        Install a package into the selected all-users interpreter with `uv`:

        ```powershell
        uv pip install --python "C:\Program Files\Python313\python.exe" bottle
        ```

    === "pip"

        Install a package into the selected all-users interpreter with `pip`:

        ```powershell
        py -3.13 -m pip install bottle
        ```

=== "macOS"

    A Homebrew or python.org interpreter prefix is the closest equivalent. Installing packages into that prefix affects every project using that interpreter.

    === "uv"

        Install a package into the selected interpreter prefix with `uv`:

        ```bash
        uv pip install --python /opt/homebrew/bin/python3.13 --break-system-packages bottle
        ```

    === "pip"

        Install a package into the selected interpreter prefix with `pip`:

        ```bash
        python3.13 -m pip install --break-system-packages bottle
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

    User packages usually land under `%AppData%\Python\Python313\site-packages`, while virtual environment packages land under `.venv\Lib\site-packages`.

=== "macOS"

    Install user-level tools without writing into the interpreter prefix:

    ```bash
    python3.13 -m pip install --user karva ruff
    ```

    User packages usually land under `~/Library/Python/3.13/lib/python/site-packages`, while virtual environment packages land under `.venv/lib/python3.13/site-packages`.

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

Show where a `uv`-installed system package lives:

```bash
python3 -c "import bottle; print(bottle.__file__)"
```

Show where user-installed packages and their console scripts live:

```bash
python3 -c "import karva, ruff; print(karva.__file__); print(ruff.__file__)"
```

Show the files owned by an APT-managed Python package:

```bash
dpkg -L python3-pip | grep -E '/usr/bin/pip3$|/dist-packages/pip(/|$)' | head
```
