# Python system environment

This page explains how Python is installed on a typical Linux host and where packages land.

## Tiny Webserver Project

The example uses the tiny Bottle web server project. Step-by-step development workflow instructions live in the section [`README.md`](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-01/README.md).

### Used DevTools

These tools define the example application's runtime dependency and the development utilities referenced throughout the chapter.

| Component            | Description |
| -------------------- | ----------- |
| [Bottle](https://bottlepy.org/docs/dev/) | Bottle is the lightweight web framework used by the example application. It gives the section a concrete Python package to track across system, administrator, and user installation targets. |
| [Karva](https://matthewmckee4.github.io/karva/) | Karva is the Rust-based test runner used elsewhere in Chapter 01. It appears here as an example of a user-installed development tool rather than an operating-system package. |
| [Ruff](https://docs.astral.sh/ruff/) | Ruff is the linter and formatter used throughout the chapter. It helps show how Python tooling can live outside APT while still being available on the command line. |

### Project Files

These project files show how the example is packaged and how the section reproduces the Python installation layout being discussed.

| Component            | Description |
| -------------------- | ----------- |
| [`Dockerfile.devEnv`](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-01/Dockerfile.devEnv) | This development image defines a safe environment for inspecting Python installation targets. It mirrors the package-installation layers discussed below without modifying the host machine. |
| [`Dockerfile`](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-01/Dockerfile) | This deployment image shows the same system-level installation model in a runtime container. It complements the discussion by demonstrating how a single system interpreter can be sufficient in container-focused workflows. |
| [`pyproject.toml`](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-01/pyproject.toml) | This file holds the Python project metadata for the tiny web server example. It defines the package and dependencies that later installation commands place into different Python package targets. |

## Install Python

### Debian-based baseline

Python is bundled into Linux flavors as part of the operating system. On Debian-based Linux flavors, the default interpreter lives at `/usr/bin/python3` and is managed by APT under `/usr`, alongside the standard library, headers, and distribution-provided packages. The release table below is Ubuntu-specific, but the baseline packaging model is the same across Debian-based systems.

| Ubuntu release | APT suite | Bundled `python3` |
| -------------- | --------- | ----------------- |
| 22.04 LTS      | jammy     | Python 3.10       |
| 24.04 LTS      | noble     | Python 3.12       |
| 26.04 LTS      | resolute  | Python 3.14       |

### Installing other Python versions

As shown in the [Debian-based baseline](#debian-based-baseline), you should avoid replacing the distribution-managed `/usr/bin/python3`, because operating system tools expect the default interpreter that ships with the release.

When the Ubuntu release does not ship the Python version you need, an extra package source is the usual side-by-side installation path. This keeps the system default intact, but it also means you must trust and maintain that additional source.

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

Keep the extra interpreter versioned in your commands instead of changing the system default:

```bash
python3.13 --version
```

Create environments with the explicit interpreter you installed:

```bash
python3.13 -m venv .venv
```

### Python Footprint on Linux

A Python installation includes the CPython interpreter, standard library modules, package directories, native extension headers, build configuration, and shell integration through `PATH`.

- **Python interpreter:** lives at `/usr/bin/python3` and is the executable the shell resolves when you run `python3` inside this Ubuntu-based environment.

- **Standard library:** lives under `/usr/lib/python3.x/` and provides built-in modules such as `os`, `pathlib`, `json`, and `subprocess` without any separate package installation.

- **APT-managed packages:** live under `/usr/lib/python3/dist-packages/` and are installed as part of Debian or Ubuntu packages, so they follow the operating system lifecycle and update through APT.

- **Administrator-managed packages:** `pip` or `uv` installs outside APT usually live under `/usr/local/lib/python3.x/dist-packages/`, which keeps them separate from distribution-owned files while still making them visible to the system interpreter.

- **User-level packages:** live under `~/.local/lib/python3.x/site-packages/`, which lets one user add Python tools without administrator permissions or changes to the system-wide package set.

- **Header files:** for building native extensions live under `/usr/include/python3.x/` and are needed when packages compile C or C++ extension modules against the current interpreter.

- **Standard-library imports:** `import os` works because the standard library ships with Python itself, so the module is already available as soon as the interpreter is installed.

    ```python
    import os
    ```

- **Installed-package imports:** `import bottle` only works when `bottle` is installed into one of the active package directories on `sys.path`, such as the APT-managed, administrator-managed, or user-level locations listed above.

    ```python
    import bottle
    ```

- **Import resolution:** the exact file that Python imports depends on where the package was installed, because `sys.path` determines which matching module or package directory is found first.

## Python package installation targets

Python packages can land in three different places. The target decides who can import them and which projects are affected by future upgrades.

| Target              | Typical path                                    | When to use                                |
| ------------------- | ----------------------------------------------- | ------------------------------------------ |
| System              | `/usr/lib/python3/dist-packages/`               | Single-purpose containers and base images. |
| Local administrator | `/usr/local/lib/python3.x/dist-packages/`       | `uv` or `pip` installs outside APT.        |
| User                | `~/.local/lib/python3.x/site-packages/`         | One user, no admin rights.                 |

### System target

The system target is owned by the operating system package manager. Use it for distribution-managed Python packages that should track the base image or host lifecycle.

Install a distribution-managed Python package with APT:

```bash
sudo apt install python3-systemd
```

### Local administrator target

The local administrator target installs packages outside APT while still making them available to the system interpreter. On modern Debian and Ubuntu, the interpreter is marked as externally managed under PEP 668, so `pip` and `uv` require an explicit override.

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

### User target

The user target keeps packages inside the current user's home directory. It avoids administrator permissions, but every project for that user still shares the same package directory.

=== "uv"

    Install user-level tools with `uv`:

    ```bash
    uv pip install --user karva ruff
    ```

=== "pip"

    Install user-level tools with `pip`:

    ```bash
    pip3 install --user karva ruff
    ```

## PATH and import path

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

## Inspecting installed packages

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

## Tradeoffs

### Pros

- ✅ System installs work well in containers because there is exactly one interpreter to manage.
- ✅ APT-managed packages integrate cleanly with the base operating system and follow the image lifecycle.
- ✅ User-level installs avoid administrator permissions when you only need tools for one account.

### Cons

- ⚠️ System installs are risky on developer machines because one upgrade can affect operating system tooling.
- ⚠️ Administrator-managed installs outside APT add another package layer that must be tracked separately from the distribution.
- ⚠️ User installs still share one package directory across every project for that user, so they do not provide project isolation.
- ⚠️ The remaining sections show why virtual environments, Conda environments, Pipenv environments, and Dev Containers are usually better choices for per-project development workflows.

