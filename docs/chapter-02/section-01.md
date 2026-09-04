# Python Wheels

Python wheels are the standard built package format for Python projects. They let installers such as `pip` copy ready-to-install files instead of rebuilding the project every time.

## Applied Project

### Project Setup

The applied project is a small utility library called `PyGuard Project`. It blocks suspicious web requests before they reach application handlers without any runtime dependencies beyond the Python standard library. This makes it a good fit for wheels because a pure-Python library shows clearly how a project can be built into a lightweight, platform-independent distribution artifact.

### Run the Project

Application, lint, build, and shell-exit commands are documented in the [section README](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/proj1_pyguard/README.md).

## Building Blocks

### Overview

Python wheels are built distributions defined by PEP 427. A wheel contains installable Python code and metadata in a ZIP-based `.whl` artifact, so an installer can copy files into an environment without rebuilding the project from source. Wheels are typically used for Python libraries, command-line applications, SDKs, and frameworks; pure-Python wheels can work across operating systems, while wheels containing native extensions target specific Python versions, ABIs, and platforms.

Wheel distribution depends on four connected building blocks: the wheel artifact carries the installable payload, project and embedded metadata describe the release, a Python package manager resolves and installs it, and a remote repository makes releases discoverable. Build frontends such as `uv build` or `python -m build` use the backend declared in `pyproject.toml` to create the artifact before publication.

| Building Block | Role | Common Examples |
|----------------|------|-----------------|
| Package Format | Stores the built Python package, compatibility tags, and embedded installation metadata. | `.whl` |
| Maintainer / Metadata File | Defines project metadata, dependencies, and the build backend; the wheel embeds generated metadata under `*.dist-info/`. | `pyproject.toml`, `METADATA`, `WHEEL`, `RECORD` |
| Package Manager | Resolves dependencies and installs wheels into a Python environment. | `pip`, `uv` |
| Remote Repository | Publishes package releases and exposes an index that package managers can query. | PyPI, Cloudsmith, Artifactory |

### Project Layout

A wheel is built from the project files, source code, and packaging metadata already in the repository.

```text
{project_root}/
├── src/
│   └── {module}/
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

### Package Manifest

!!! note
    Chapter 04 covers [`pyproject.toml` project configuration](../chapter-04/section-01.md) in more detail.
    
The `pyproject.toml` file defines the project metadata, Python requirements, dependencies, command-line entry points, and build backend used to create the wheel.

```toml
[build-system]
requires = ["uv_build>=0.11.8,<0.12"]
build-backend = "uv_build"

[project]
name = "pyguard"
version = "0.1.0"
description = "Lightweight security middleware for Python web applications."
readme = "README.md"
requires-python = ">=3.9"
license = "MIT"
authors = [
    { name = "Julius Pravtchev" },
    { name = "Valentin Pravtchev" }
]
dependencies = []

# [project.scripts]
# pyguard = "pyguard.cli:main"
# [project.urls]
# Homepage = "https://example.com/project"
```

- `name`: Defines the distribution name used in package indexes and wheel filenames.
- `version`: Identifies the published release.
- `requires-python`: Declares compatible Python versions.
- `dependencies`: Lists packages required when the wheel is installed.
- `[build-system]`: Selects the build backend and the packages needed to run it.

### Package Layout

A Python wheel is a ZIP archive with a `.whl` extension. It bundles the importable package, distribution metadata, and an installation record that lets Python package managers place and track the files in an environment.

```text
{name}-{version}-{python-tag}-{abi-tag}-{platform-tag}.whl
├── {import-package}/
│   ├── __init__.py
│   └── ...
└── {name}-{version}.dist-info/
    ├── METADATA
    ├── RECORD
    ├── WHEEL
    └── entry_points.txt
```

- `{import-package}/`: Contains the Python modules and package data installed into the environment.
- `METADATA`: Records package identity, Python requirements, dependencies, and descriptive metadata.
- `WHEEL`: Records the wheel format and compatibility tags.
- `RECORD`: Lists installed files and their hashes so the installer can track and uninstall them.

The filename tags tell the package manager which Python interpreter, ABI, and platform can use the wheel. A pure-Python wheel commonly ends in `py3-none-any.whl`, while a wheel with compiled extensions uses more specific tags.

## Packaging Workflow

!!! info
    This workflow assumes that you have a valid Cloudsmith repository and API key. Replace `<cloudsmith-repo>` with your Cloudsmith repository slug, export `CLOUDSMITH_API_KEY` on the host, and pass both values into the container.

From the `projects/` directory, open the dedicated packaging container and forward the Cloudsmith configuration into the container session.

```bash
../build.sh build --path proj1_pyguard/Dockerfile.devEnv \
    --cloudsmith-workspace "<cloudsmith-repo>" \
    --cloudsmith-api-key "$CLOUDSMITH_API_KEY"
```

### Create The Package

Modern Python builds split responsibilities between a **build frontend** and a **build backend**. The frontend is the command-line tool you run, while the backend is the project-specific implementation that produces the wheel (`.whl`) and source distribution (`.tar.gz`). PEP 517 defines the interface between both sides, and PEP 518 defines the `[build-system]` table in `pyproject.toml` where the backend and its requirements are declared.

In this project, the build backend is `uv_build`. It is declared in `pyproject.toml`, which tells the build frontend which backend to load and which packages must be installed before the build starts. Popular build backends include `uv_build`, `hatchling`, `setuptools.build_meta`, `poetry.core.masonry.api`, etc.

```toml
[build-system]
requires = ["uv_build>=0.11.8,<0.12"]
build-backend = "uv_build"
```

In this project, the build frontend is `uv build`. It creates the isolated build environment, installs the backend requirements, and invokes `uv_build` to create the final artifacts. The command accepts a source directory, so the `pyproject.toml` file is discovered from that project path. Popular build frontends include `uv build`, `python -m build`, `pip wheel`, `pip install`, `hatch build`, `poetry build`, etc.

```bash
uv build <path-to-project-root>
```

List the generated distribution files in the `dist/` directory.

```bash
ls dist/
```

### Inspect The Package

A wheel (`.whl`) is a **ZIP archive** with Python modules and a `*.dist-info/` metadata directory. The source distribution created next to it is a gzip-compressed TAR archive (`.tar.gz`) that stores the source tree used to rebuild the package.

List the files inside the wheel archive without extracting it.

```bash
zipinfo -1 dist/pyguard-0.1.0-py3-none-any.whl
```

Read the wheel metadata that describes the wheel format version, generator, root layout, and compatibility tags.

```bash
unzip -p dist/pyguard-0.1.0-py3-none-any.whl pyguard-0.1.0.dist-info/WHEEL
```

Read the package metadata that installers and package indexes use for the project name, version, description, and dependency declarations.

```bash
unzip -p dist/pyguard-0.1.0-py3-none-any.whl pyguard-0.1.0.dist-info/METADATA
```

List the files inside the source distribution TAR archive.

```bash
tar -tzf dist/pyguard-0.1.0.tar.gz
```

### Publish The Package

Once you have inspected the wheel package, upload it to the proprietary Python repository hosted on Cloudsmith.

Publish the package to the Cloudsmith PyPI repository with `uv`.

```bash
uv publish --publish-url "https://python.cloudsmith.io/${CLOUDSMITH_REPOSITORY}/" --token "$CLOUDSMITH_API_KEY"
```

Check that the uploaded release is visible through the Cloudsmith `/simple/` API used by installers.

```bash
curl -fsSL "https://dl.cloudsmith.io/public/<cloudsmith-repo>/python/simple/pyguard/" | grep "pyguard-0.1.0"
```

## Consumer Workflow

### Install The Package

After publication, users can create a small project, install `pyguard` from the Cloudsmith PyPI repository, and run a short script against the created environment.

Create a new working directory for a small consumer project.

```bash
mkdir pyguard-consumer && cd pyguard-consumer
```

Add the project files.

=== "pyproject.toml"

    ```toml
    [project]
    name = "pyguard-consumer"
    version = "0.1.0"
    requires-python = ">=3.12"
    dependencies = [
        "pyguard",
    ]

    [tool.uv]

    [[tool.uv.index]]
    name = "pypi"
    url = "https://pypi.org/simple"

    [[tool.uv.index]]
    name = "modern-python-engineering"
    url = "https://dl.cloudsmith.io/public/<cloudsmith-repo>/python/simple/"
    ```

=== "hello.py"

    ```python
    from pyguard import PyGuardMiddleware, Request, RequestBlocked

    def main() -> None:
        guard = PyGuardMiddleware()
        request = Request(method="GET", path="/download", query="file=../../etc/passwd")

        try:
            guard.before_request(request)
        except RequestBlocked as exc:
            print(exc)


    if __name__ == "__main__":
        main()
    ```

Install the dependency and run the script.

=== "uv"

    Sync the project environment with `uv`, which reads the package indexes directly from `pyproject.toml`, resolves `pyguard` from the configured Cloudsmith repository, and lets the project describe both the public PyPI index and the proprietary Cloudsmith index in one place.

    ```bash
    uv sync
    ```

=== "pip"

    Create a virtual environment and install `pyguard` with an explicit `--extra-index-url` argument, because `pip` does not read repository indexes from `pyproject.toml`.

    ```bash
    python -m venv .venv && . .venv/bin/activate && pip install --extra-index-url https://dl.cloudsmith.io/public/<cloudsmith-repo>/python/simple/ pyguard
    ```
    
Run the script from the same virtual environment.

```bash
.venv/bin/python hello.py
```

## Useful Links

- [PEP 517 - A build-system independent format for source trees](https://peps.python.org/pep-0517/)
- [PEP 518 - Specifying Minimum Build System Requirements for Python Projects](https://peps.python.org/pep-0518/)