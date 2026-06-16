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

### Create The Package

Build the project with either `uv build` or `python -m build`; both create a wheel (`.whl`) and a source distribution (`.tar.gz`) in `dist/`.

=== "`uv`"

    Run following command to build the package:

    ```bash
    uv build
    ```

=== "`build`"

    Install `build`:

    ```bash
    python -m pip install build
    ```

    Run following command to build the package:

    ```bash
    python -m build
    ```

> In addition to the `*.whl` file, the build also creates a `*.tar.gz` source distribution.

### Validate The Package

To validate the generated artifacts, you can use `twine`. Run following command to install `twine`:

=== "`uv`"
    
    ```bash
    uv tool install twine
    ```

=== "`pip`"

    ```bash
    python3 -m pip install twine
    ```

Validate the artifacts with `twine check dist/*`.

```bash
twine check dist/*
```

### Publish The Package

Once a package has been validated, it can be uploaded to a package repository.

| Repository | Type | Purpose |
|------------|------|---------|
| [PyPI](https://pypi.org) | Public | Official Python package repository |
| [TestPyPI](https://test.pypi.org) | Public | Test environment for package publishing workflows |
| Artifactory | Private | Repository manager for internal software distribution |
| Nexus Repository | Private | Repository manager for internal package hosting |

=== "uv"

    Publish the package to PyPI with `uv`.

    ```bash
    uv publish
    ```

    Publish the package to TestPyPI with `uv`.

    ```bash
    uv publish --publish-url https://test.pypi.org/legacy/
    ```

=== "twine"

    Publish the package to PyPI with `twine`.

    ```bash
    twine upload dist/*
    ```

    Publish the package to TestPyPI with `twine`.

    ```bash
    twine upload --repository testpypi dist/*
    ```

### Install The Package

After publication, users can install the package directly from a repository.

=== "uv"

    Install the package with `uv`.

    ```bash
    uv tool install docslug
    ```

=== "pip"

    Install the package with `pip`.

    ```bash
    pip install docslug
    ```