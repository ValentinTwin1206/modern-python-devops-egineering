# Python `venv` environments

This page covers Python's standard-library `venv` module.

## Tiny Webserver Project

The example uses the tiny Bottle web server project. Step-by-step development workflow instructions live in the section [`README.md`](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-02/README.md).

### Used DevTools

These tools cover the example application's runtime package, development utilities, and the environment tool being explained in this section.

| Component            | Description |
| -------------------- | ----------- |
| [Bottle](https://bottlepy.org/docs/dev/) | Bottle is the application dependency used by the sample web server. It provides a concrete runtime package to install into the virtual environment. |
| [Karva](https://matthewmckee4.github.io/karva/) | Karva is the test runner used for the section workflow. It shows how development-only tools can live inside the same isolated environment as the application. |
| [Ruff](https://docs.astral.sh/ruff/) | Ruff is the linter and formatter used for code-quality checks. It is part of the shared project tooling that benefits from per-project isolation. |
| [`venv`](https://docs.python.org/3/library/venv.html) | `venv` is Python's built-in virtual environment tool. It is the main subject of this section and defines the package boundary being inspected. |

### Project Files

These project files show how the virtual-environment workflow is reproduced in development and deployment for the tiny web server example.

| Component            | Description |
| -------------------- | ----------- |
| [`Dockerfile.devEnv`](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-02/Dockerfile.devEnv) | This development image creates and activates a virtual environment at `/opt/venv`. It gives you a reproducible example of how the project and its tools are installed into an isolated interpreter. |
| [`Dockerfile`](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-02/Dockerfile) | This deployment image builds the project wheel and installs it into the same virtual-environment layout. It shows how the `venv` pattern carries from interactive development into container deployment. |
| [`pyproject.toml`](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-02/pyproject.toml) | This file defines the package metadata and dependencies for the example project. Those dependencies are what get installed into the virtual environment during the workflow shown below. |

## Install `venv`

`venv` is bundled with Python, so there is no separate Python package to install. On Debian-based systems, the `python3-venv` operating system package provides the pieces needed to create environments with the distribution Python.

Install the `venv` support package when it is not already present:

```bash
sudo apt install python3-venv
```

## `venv` environment model

`venv` ships with Python. It creates a project-local directory with a private interpreter, `pip`, package directory, console scripts, and a `pyvenv.cfg` file. Activation is mostly a `PATH` change so that the environment-local interpreter resolves first.

### Environment layout

A typical environment uses this layout:

```text
.venv/
├── bin/
│   ├── Activate.ps1
│   ├── activate
│   ├── activate.csh
│   ├── activate.fish
│   ├── pip
│   ├── pip3
│   ├── pip3.x
│   ├── python
│   ├── python3
│   └── python3.x
├── include/
│   └── python3.x/
├── lib/
│   └── python3.x/
│       └── site-packages/
│           ├── pip/
│           └── pip-*.dist-info/
├── lib64/
└── pyvenv.cfg
```

### Key directories and files

- **`bin/`:** contains the virtual environment's Python executables, `pip`, and the shell activation scripts. On Linux, a fresh `venv` commonly uses symlinks for the Python executables, so the environment-local `python3` can still point back to the base interpreter while the surrounding environment changes where packages and scripts are installed.

    Inspect the executable directory:

    ```bash
    ls -lah .venv/bin/
    ```

    A shortened output focused on the executable entries looks like this:

    ```text
    -rwxr-xr-x 1 user user  253 May  9 05:46 pip
    -rwxr-xr-x 1 user user  253 May  9 05:46 pip3
    -rwxr-xr-x 1 user user  253 May  9 05:46 pip3.12
    lrwxrwxrwx 1 user user    7 May  9 05:46 python -> python3
    lrwxrwxrwx 1 user user   16 May  9 05:46 python3 -> /usr/bin/python3
    lrwxrwxrwx 1 user user    7 May  9 05:46 python3.12 -> python3
    ```

    The arrows show the redirect chain. `python` points to `python3`, `python3.12` points to `python3`, and `python3` points to the base interpreter at `/usr/bin/python3`.

- **`include/python3.x/`:** contains headers used when native extensions compile against the interpreter inside the virtual environment.

- **`lib/python3.x/site-packages/`:** contains the packages installed into the virtual environment. On a fresh Python 3.x `venv` contains `pip/` and its `.dist-info` metadata by default and no other Python packages.

- **`lib64/`:** is a platform-specific library alias that appears on some Linux systems.

- **`pyvenv.cfg`:** stores the base interpreter reference and flags such as whether system site-packages are visible. When you run the environment-local `python3`, CPython reads this file early during startup. The `home` key points back to the base Python installation that owns the standard library, while `sys.prefix` and `sys.exec_prefix` are redirected to the local `.venv/` directory.

    A fresh `pyvenv.cfg` looks like this:

    ```ini
    home = /usr/bin
    include-system-site-packages = false
    version = 3.12.3
    executable = /usr/bin/python3.12
    command = /usr/bin/python3 -m venv /tmp/tmp.XUOUzoskul/.venv
    ```

### Activation and import path

- **Environment-local interpreter:** the `activate` script puts `.venv/bin/` at the front of `PATH` on Linux. It does not change Python itself; it changes which executable the shell finds first when you run `python`, `python3`, or `pip`.

    ```text
    Before activation:
    PATH=/usr/local/bin:/usr/bin:/bin:...
    python3 -> /usr/bin/python3

    After activation:
    PATH=/path/to/project/.venv/bin:/usr/local/bin:/usr/bin:/bin:...
    python3 -> /path/to/project/.venv/bin/python3
    ```

- **Environment-local packages:** installed packages land under `.venv/lib/python3.x/site-packages/`, which keeps them separate from the system interpreter. A virtual environment does not replace the base standard library; it uses the base Python's standard library and puts the environment-local `site-packages/` ahead of any inherited package directories.

- **System package visibility:** with the default `include-system-site-packages = false` setting in `pyvenv.cfg`, system-wide package directories are normally omitted. That is why a `venv` feels isolated even though it still relies on the base standard library.

- **Prefix inspection:** `sys.prefix` points at the virtual environment, while `sys.base_prefix` still points at the underlying system Python.

    ```python
    import sys
    print(sys.prefix)
    print(sys.base_prefix)
    ```

### Technical Note: Why **`.venv/`** is not portable

You should treat the **`.venv/`** directory as disposable rather than movable. Virtual environments often contain absolute paths in **`pyvenv.cfg`**, console scripts under **`bin/`**, and shebang lines that point at the original interpreter location, so renaming or moving the directory can leave the environment pointing at paths that no longer exist.

In practice, rebuilding is safer than relocating. If the project moves, the usual fix is to remove **`.venv/`** and recreate it from the dependency files instead of trying to preserve the old directory byte-for-byte.

## Workflow

### Create and activate

Create the environment from the section folder:

```bash
python3 -m venv .venv
```

Activate it on Linux or macOS:

```bash
source .venv/bin/activate
```

The new environment starts with the `pip` version supplied by the Python installation. Upgrade it before installing project dependencies.

=== "pip"

	```bash
	pip install --upgrade pip
	```

=== "uv"

	```bash
	uv pip install --upgrade pip
	```

### Install the project

=== "pip"

	Install the project and its declared dependencies with `pip`:

	```bash
	pip install .
	```

=== "uv"

	Install the project and its declared dependencies with `uv` into the active virtual environment:

	```bash
	uv pip install .
	```

### Run the project

Application, test, lint, and shell-exit commands are documented in the [section README](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-02/README.md).

## Inspection

Show the active prefixes:

```bash
python3 -c "import sys; print(sys.prefix); print(sys.base_prefix)"
```

Show where installed packages live:

```bash
python3 -c "import bottle, tiny_webserver; print(bottle.__file__); print(tiny_webserver.__file__)"
```

## Tradeoffs

### Pros

- ✅ Bundled with Python and familiar to most users.
- ✅ Lightweight folder-based environment that is easy to inspect and remove.
- ✅ Clear `PATH` and `sys.path` behavior once the environment is activated.

### Cons

- ⚠️ Does not manage Python versions by itself.
- ⚠️ Cannot install non-Python system libraries such as compiler toolchains or database client packages.
- ⚠️ Does not provide a built-in lockfile for fully reproducible installs.
