# Tiny Webserver `venv` Environment

This project shows how Python's standard-library `venv` module creates a
project-local environment. It uses the shared tiny `bottle` web server,
`karva` test runner, and `ruff` linting setup.

## Docker Images

The `Dockerfile.devEnv` is the important demonstration. It builds a container
that uses `venv` as the environment boundary:

- It starts from `ubuntu:24.04` and uses Ubuntu's standard Python 3.12.
- It installs Bash and a minimal build toolchain with APT.
- It creates a virtual environment under `/opt/venv`.
- It puts `/opt/venv/bin` first on `PATH`.
- It installs the project into that virtual environment with `pip`.
- It activates the environment automatically for interactive shells.

The companion `Dockerfile` is the deployment image. It builds a wheel,
installs that wheel into `/opt/venv`, and starts the `tiny-webserver`
entry point directly.

## Virtual Environment Footprint

### Overview

`venv` ships with Python itself. It creates a private directory with its
own `python`, `pip`, package directory, console scripts, and
`pyvenv.cfg` file. Installing packages while the environment is active
writes into that directory instead of the system interpreter.

Activation is mostly a `PATH` change. After activation, the shell finds
the environment-local `python` and `pip` before any system-level
commands with the same names.

### Folder Structure

A typical `venv` directory has this shape:

```text
.venv/
├── bin/
├── include/
├── lib/
|   └── pythonX.Y/
|       └── site-packages/
├── lib64/
└── pyvenv.cfg
```

- **Executables** live under `bin/`.
  This includes `python`, `pip`, and package-provided console scripts.

- **Installed packages** live under `lib/pythonX.Y/site-packages/`.
  This is where `bottle`, `karva`, `ruff`, and the installed example
  project are written.

- **Header files** live under `include/`.
  They are used when compiling native extension modules.

- **Environment metadata** lives in `pyvenv.cfg`.
  The file records the base interpreter and whether system packages are
  visible from inside the environment.

## Dependency Workflow

### Create The Environment

Create a local environment from this folder:

```sh
python -m venv .venv
```

Activate it on Linux or macOS:

```sh
source .venv/bin/activate
```

### Install The Project

Install the project and its declared dependencies into the active
environment:

```sh
pip install .
```

### Run The Project

Run the tiny Bottle application:

```sh
python -m tiny_webserver.app
```

Run tests and linting:

```sh
karva test tests/
ruff check .
```

### Leave The Environment

Return the shell to its previous `PATH` state:

```sh
deactivate
```

## Tradeoffs

### Pros

- `venv` is bundled with Python
- It creates lightweight folder-based environments
- It is familiar to almost every Python developer.

### Cons

- `venv` does not manage Python versions
- It does not install non-Python system libraries
- It does not provide a lockfile by itself.

## Useful Inspection Commands

Use these command patterns inside the container to inspect the active
environment.

### Python Prefixes

```sh
python -c "import sys; print('prefix =', sys.prefix); print('base_prefix =', sys.base_prefix)"
```

Expected output:

```text
prefix = /opt/venv
base_prefix = /usr/local
```

### Package Locations

```sh
python -c "import bottle, tiny_webserver; print('bottle =', bottle.__file__); print('tiny_webserver =', tiny_webserver.__file__)"
```

Expected output includes paths under:

```text
/opt/venv/lib/python3.12/site-packages/
/app/src/tiny_webserver/
```
