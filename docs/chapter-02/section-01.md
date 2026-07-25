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
zipinfo -1 dist/docslug-1.0.0-py3-none-any.whl
```

Read the wheel metadata that describes the wheel format version, generator, root layout, and compatibility tags.

```bash
unzip -p dist/docslug-1.0.0-py3-none-any.whl docslug-1.0.0.dist-info/WHEEL
```

Read the package metadata that installers and package indexes use for the project name, version, description, and dependency declarations.

```bash
unzip -p dist/docslug-1.0.0-py3-none-any.whl docslug-1.0.0.dist-info/METADATA
```

List the files inside the source distribution TAR archive.

```bash
tar -tzf dist/docslug-1.0.0.tar.gz
```

### Publish The Package

!!! info
    This workflow assumes that the Cloudsmith repository in the [`pravi-brothers`](https://app.cloudsmith.com/pravi-brothers) workspace already exists and that you already exported `CLOUDSMITH_API_KEY` on the host.

Once you have inspected the wheel package, upload it to the proprietary Python repository hosted on Cloudsmith.

Publish the package to the Cloudsmith PyPI repository with `uv`.

```bash
uv publish --publish-url "https://python.cloudsmith.io/${CLOUDSMITH_REPOSITORY}/" --token "$CLOUDSMITH_API_KEY"
```

Check that the uploaded release is visible through the Cloudsmith `/simple/` API used by installers.

```bash
curl -fsSL "https://dl.cloudsmith.io/public/pravi-brothers/modern-python-engineering/python/simple/docslug/" | grep "docslug-1.0.0"
```

## Consumer Workflow

### Install The Package

After publication, users can create a small project, install `docslug` from the Cloudsmith PyPI repository, and run a short script against the created environment. `uv` can read package indexes directly from `pyproject.toml`, so the project can describe both the public PyPI index and the proprietary Cloudsmith index in one place. `pip` does not read package indexes from `pyproject.toml`, so its install command still needs an explicit `--extra-index-url` argument.

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

    [tool.uv]

    [[tool.uv.index]]
    name = "pypi"
    url = "https://pypi.org/simple"

    [[tool.uv.index]]
    name = "modern-python-engineering"
    url = "https://dl.cloudsmith.io/public/pravi-brothers/modern-python-engineering/python/simple/"
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

    Sync the project environment with `uv`. It reads the package indexes from `pyproject.toml` and resolves `docslug` from the configured Cloudsmith repository.

    ```bash
    uv sync
    ```

=== "pip"

    Create a virtual environment and install `docslug` with an explicit extra index URL, because `pip` does not read repository indexes from `pyproject.toml`.

    ```bash
    python -m venv .venv && . .venv/bin/activate && pip install --extra-index-url https://dl.cloudsmith.io/public/pravi-brothers/modern-python-engineering/python/simple/ docslug
    ```
    
Run the script from the same virtual environment.

```bash
.venv/bin/python hello.py
```

## Useful Links

- [PEP 517 - A build-system independent format for source trees](https://peps.python.org/pep-0517/)
- [PEP 518 - Specifying Minimum Build System Requirements for Python Projects](https://peps.python.org/pep-0518/)