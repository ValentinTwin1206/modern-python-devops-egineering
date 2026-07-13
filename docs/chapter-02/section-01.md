# Python Wheels

Python wheels are the standard built package format for Python projects. They let installers such as `pip` copy ready-to-install files instead of rebuilding the project every time.

## Applied Project

### Project Setup

The applied project is a small utility library called `Docslug Project`. It turns headings and file names into stable slugs without any runtime dependencies beyond the Python standard library. This makes it a good fit for wheels because a pure-Python library shows clearly how a project can be built into a lightweight, platform-independent distribution artifact.

### Run the Project

Application, test, lint, and shell-exit commands are documented in the [section README](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/proj1_docslug/README.md).

## Distribution Fundamentals

### Overview

A Python wheel is a built distribution format defined by PEP 427. It lets tools such as `pip` and `uv` install pre-built code instead of rebuilding from source.

- ✅ Python libraries
- ✅ CLI applications
- ✅ internal tools, SDKs and frameworks 

### Python Packaging Ecosystem

Modern Python packaging separates the command-line frontend from the backend that creates distribution artifacts. The frontend reads `pyproject.toml` to choose the backend, which keeps packaging tools interchangeable.

The build backend is configured in the `build-system` section of the `pyproject.toml` file:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

Common frontend and backend tools include:

| Type | Tool | Description |
|--------|--------|--------|
| Frontend | `uv build` | Build command from the uv ecosystem |
| Frontend | `python -m build` | PyPA's reference build frontend |
| Backend | `hatchling` | Lightweight backend |
| Backend | `setuptools` | Widely used backend |
| Backend | `uv_build` | Backend used by uv-based projects |

### Project Layout

A wheel is built from the project files, source code, and packaging metadata already in the repository.

```text
{project_root}/
├── src/
│   └── docslug/
│       ├── __init__.py
│       └── core.py
├── tests/
├── README.md
├── LICENSE
└── pyproject.toml
```

- `src/`: Contains the importable package code. This widely used `src` layout keeps the project root separate from Python modules, which helps prevent accidental local imports and makes development behavior match the installed package.
- `pyproject.toml`: The **central configuration file** for modern Python packaging. It stores the package metadata, dependency list, build backend settings, and CLI entry points in one place.
- `README.md`: Project description displayed on package repositories such as PyPI.
- `LICENSE`: Defines the legal terms under which the package can be used and distributed.

### Package Layout

A Python wheel is represented by a `*.whl` file. Its filename follows this general structure:

```text
{NAME}-{VERSION}-{PYTHON_TAG}-{ABI_TAG}-{PLATFORM_TAG}.whl
```

The individual identifiers have the following meaning:

- `{NAME}`: Package name taken from `project.name` in `pyproject.toml`.
- `{VERSION}`: Package version taken from `project.version` in `pyproject.toml`.
- `{PYTHON_TAG}`: Python tag describing the supported Python interpreter version.
    - `py3` → Any Python 3 version
    - `py310` → Python 3.10
    - `py311` → Python 3.11
    - ...
- `{ABI_TAG}`: The *Application Binary Interface (ABI)* tag describing binary compatibility.
    - `none` → No compiled extensions
    - `cp310` → CPython 3.10 ABI
    - `cp311` → CPython 3.11 ABI
    - ...
- `{PLATFORM_TAG}`: Platform tag describing the target operating system and architecture.
    - `any` → Platform independent
    - `win_amd64` → Windows 64-bit
    - `manylinux_x86_64` → Linux 64-bit
    - `manylinux_aarch64` → Linux ARM64
    - `macosx_11_0_arm64` → macOS Apple Silicon
    - `macosx_10_9_x86_64` → macOS Intel

Typical wheel contents look like this:

```text
docslug-1.0.0-py3-none-any.whl
├── docslug/
│   ├── __init__.py
│   └── core.py
└── docslug-1.0.0.dist-info/
    ├── METADATA
    ├── RECORD
    └── WHEEL
```

The distinct package artifacts are:

- `docslug/`: The importable package code that ships inside the wheel, including the Python modules that make up the application.
- `*.dist-info/`: The metadata directory that records the package name, version, dependencies, and installation records.

## Packaging Workflow

From the `projects/` directory, open the dedicated packaging container and forward the Cloudsmith API key into the container session.

```bash
../build.sh build --path proj1_docslug/Dockerfile.devEnv -- --env CLOUDSMITH_API_KEY="$CLOUDSMITH_API_KEY"
```

### Create The Package

Run following command to build the wheel (`.whl`) package:

```bash
uv build
```

> In addition to the `*.whl` file, the build also creates a `*.tar.gz` source distribution.

### Validate The Package

To validate the generated artifacts, first list the build output and confirm that the wheel and source distribution exist:

```bash
ls dist/
```

Then run a local smoke test by installing the wheel into the project environment with `uv`:

```bash
uv pip install dist/docslug-1.0.0-py3-none-any.whl
```

### Publish The Package

!!! info
    This workflow assumes that the Cloudsmith repository in the [`pravi-brothers`](https://app.cloudsmith.com/pravi-brothers) workspace already exists and that you already exported `CLOUDSMITH_API_KEY` on the host.
    
Once a wheel package passes validation, upload it to the proprietary Python repository hosted on Cloudsmith.


Publish the package to the Cloudsmith PyPI repository with `uv`.

```bash
uv publish --publish-url "https://python.cloudsmith.io/${CLOUDSMITH_REPOSITORY}/" --token "$CLOUDSMITH_API_KEY"
```

## Consumer Workflow

### Configure Package Manager

Before installing packages from a proprietary Python repository, create a user-level configuration file so your package manager consults the dedicated extra package index alongside the default public index.

#### `uv`

Create a user-level `uv.toml` file for your operating system.

=== "Linux"

    Store the file at `~/.config/uv/uv.toml`.

    ```toml
    [[index]]
    url = "https://dl.cloudsmith.io/public/pravi-brothers/modern-python-engineering/python/simple/"
    default = false
    ```

=== "macOS"

    Store the file at `~/.config/uv/uv.toml`.

    ```toml
    [[index]]
    url = "https://dl.cloudsmith.io/public/pravi-brothers/modern-python-engineering/python/simple/"
    default = false
    ```

=== "Windows"

    Store the file at `%APPDATA%\uv\uv.toml`.

    ```toml
    [[index]]
    url = "https://dl.cloudsmith.io/public/pravi-brothers/modern-python-engineering/python/simple/"
    default = false
    ```

#### `pip`

Create a user-level `pip.conf` or `pip.ini` file for your operating system.

=== "Linux"

    Store the file at `~/.config/pip/pip.conf`.

    ```ini
    [global]
    extra-index-url = https://dl.cloudsmith.io/public/pravi-brothers/modern-python-engineering/python/simple/
    ```

=== "macOS"

    Store the file at `$HOME/Library/Application Support/pip/pip.conf`.

    ```ini
    [global]
    extra-index-url = https://dl.cloudsmith.io/public/pravi-brothers/modern-python-engineering/python/simple/
    ```

=== "Windows"

    Store the file at `%APPDATA%\pip\pip.ini`.

    ```ini
    [global]
    extra-index-url = https://dl.cloudsmith.io/public/pravi-brothers/modern-python-engineering/python/simple/
    ```

### Install The Package

After publication, users can create a small project, install `docslug` from the Cloudsmith PyPI repository, and run a short script against the created environment.

Create a new working directory for a small consumer project.

```bash
mkdir docslug-consumer && cd docslug-consumer
```

Add the project files.

=== "pyproject.toml"

    ```toml
    [project]
    name = "docslug-consumer"
    version = "0.1.0"
    requires-python = ">=3.12"
    dependencies = [
	"docslug",
    ]
    ```

=== "hello.py"

    ```python
    from docslug import slugify

    def main() -> None:
	print(slugify("Hello from Docslug"))


    if __name__ == "__main__":
	main()
    ```

Install the dependency and run the script.

=== "uv"

    Sync the project environment with `uv` after you configured the user-level package index.

    ```bash
    uv sync
    ```

=== "pip"

    Create a virtual environment and install `docslug` in one command after you configured the user-level package index.

    ```bash
    python -m venv .venv && . .venv/bin/activate && pip install -e .
    ```
    
Run the script from the same virtual environment.

```bash
.venv/bin/python hello.py
```