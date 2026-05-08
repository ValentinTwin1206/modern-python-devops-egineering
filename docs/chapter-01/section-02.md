# Python `venv` environments

This page covers Python's standard-library `venv` module. The example uses the tiny Bottle web server project. Step-by-step development workflow instructions live in the section [`README.md`](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-02/README.md).

| Component            | Description                                      | Role in this section                                  |
| -------------------- | ------------------------------------------------ | ----------------------------------------------------- |
| [Bottle](https://bottlepy.org/docs/dev/) | Lightweight Python web framework.              | Example application dependency and web server         |
| [Karva](https://matthewmckee4.github.io/karva/) | Python test runner written in Rust.            | Test runner used for the section test workflow        |
| [Ruff](https://docs.astral.sh/ruff/) | Fast Python linter and formatter.              | Linter used for the section code-quality checks       |
| [`venv`](https://docs.python.org/3/library/venv.html) | Standard-library tool for virtual environments. | Environment boundary that isolates Python packages    |

!!! info "`Dockerfile.devEnv` and `Dockerfile`"
	The development image creates a virtual environment under `/opt/venv`, installs the project into it with `pip`, and activates it for interactive shells. The deployment image builds a wheel, installs it into the same `/opt/venv`, and starts the `tiny-webserver` entry point.

## Python footprint inside a virtual environment

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

On this system, a fresh Python 3.12 `venv` contains `pip/` and its `.dist-info` metadata by default, but not project packages such as Bottle, Karva, Ruff, or `tiny_webserver`. The bundled `pip` version is the one bootstrapped by the Python build through `ensurepip`, so the exact version depends on the Python version and distribution build that created the environment. In newer Python releases, you should also not assume `setuptools` is present, because modern `venv` creation no longer treats it as a guaranteed core dependency.

### Key directories and files

- **`bin/`:** contains the virtual environment's Python executables, `pip`, and the shell activation scripts.

- **`include/python3.x/`:** contains headers used when native extensions compile against the interpreter inside the virtual environment.

- **`lib/python3.x/site-packages/`:** contains the packages installed into the virtual environment.

- **`lib64/`:** is a platform-specific library alias that appears on some Linux systems.

- **`pyvenv.cfg`:** stores the base interpreter reference and flags such as whether system site-packages are visible. A fresh `pyvenv.cfg` looks like this:

    ```ini
    home = /usr/bin
    include-system-site-packages = false
    version = 3.12.3
    executable = /usr/bin/python3.12
	command = /usr/bin/python3 -m venv /tmp/tmp.XUOUzoskul/.venv
    ```

### Activation and import path

- **Environment-local interpreter:** the `python3` binary inside `.venv/bin/` becomes the first interpreter on `PATH` after activation on Linux.
- **Environment-local packages:** installed packages land under `.venv/lib/python3.x/site-packages/`, which keeps them separate from the system interpreter.
- **Prefix inspection:** `sys.prefix` points at the virtual environment, while `sys.base_prefix` still points at the underlying system Python.

    ```python
    import sys
    print(sys.prefix)
    print(sys.base_prefix)
    ```

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

Usually the next step is to upgrade `pip` inside the new environment before installing project dependencies.

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
