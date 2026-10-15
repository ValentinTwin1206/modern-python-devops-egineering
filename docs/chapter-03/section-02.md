# Dependency Management with uv

## Introduction

This section explains how `uv` manages project dependencies, from adding packages from indexes or Git repositories to organizing development tools and locking resolved versions for consistent environments. See [adding dependencies](#add-dependencies), [dependency groups](#dependency-groups), [Git package sources](#add-a-dependency-from-a-git-repository), and [the lockfile](#the-lockfile) for details.

## Declaring Dependencies

`uv` provides dedicated commands for adding and removing dependencies. By default, these commands update the project's dependency declarations, resolve versions into a lockfile, and synchronize the virtual environment. Runtime requirements belong in the standard project dependency field, while other tables can describe development groups or tool-specific package sources.

Start with a project file that contains metadata but no dependencies:

```toml
[project]
name = "license-service"
version = "0.1.0"
requires-python = ">=3.11"
```

### Add Dependencies

#### Add from a Package Index

Use `uv add` to update the `dependencies` entry in `pyproject.toml` and immediately re-resolve. By default, `uv` selects the newest version compatible with the project's Python requirement and records it as a lower bound (`>=`):

```bash
uv add requests
```

To require an exact version, use the `==` constraint:

```bash
uv add "httpx==0.27.2"
```

To allow patch releases within the `0.115` series, specify a version range:

```bash
uv add "fastapi>=0.115,<0.116"
```

After these commands, the complete project file looks like this. **NOTE** that the `requests` lower bound may vary:

```toml
[project]
name = "license-service"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115,<0.116", # Allow patch releases in 0.115
    "httpx==0.27.2", # Require this exact version
    "requests>=2.32.3", # Set a minimum version
]
```

!!! info "Choosing version constraints"
    **Prefer version ranges for applications and libraries, such as `fastapi>=0.115,<0.116`.** The lockfile records exact resolved versions for reproducible installs, so use exact pins in `pyproject.toml` only when a specific version is required.

#### Add a Dependency from a Git Repository

`uv` can add a package directly from a Git repository:

```bash
uv add "flask @ git+https://github.com/pallets/flask"
```

Instead of putting the Git URL directly in `[project].dependencies`, `uv` adds the package name there and records the repository location under `[tool.uv.sources]`. After this command, the complete project file looks like this:

```toml
[project]
name = "license-service"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115,<0.116", # Allow patch releases in 0.115
    "flask",
    "httpx==0.27.2", # Require this exact version
    "requests>=2.32.3", # Set a minimum version
]

[tool.uv.sources]
flask = { git = "https://github.com/pallets/flask" }
```

#### Dependency Groups

Development tools, test frameworks, and documentation generators are not needed in production. Dependency groups separate them from runtime requirements:

=== "Dev"

    Add test and development tools to the `dev` group with `--group`. The `dev` group is special-cased, so `--dev` can also be used as a shortcut:

    ```bash
    uv add --group dev pytest
    uv add --dev ruff
    ```

=== "Docs"

    Add MkDocs to a separate `docs` group:

    ```bash
    uv add --group docs "mkdocs>=1.6.1,<2.0"
    ```

After these commands, the complete project file looks like this:

```toml
[project]
name = "license-service"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115,<0.116", # Allow patch releases in 0.115
    "flask",
    "httpx==0.27.2", # Require this exact version
    "requests>=2.32.3", # Set a minimum version
]

[dependency-groups]
dev = [
    "pytest>=8.0",
    "ruff>=0.15",
]
docs = [
    "mkdocs>=1.6.1,<2.0",
]

[tool.uv.sources]
flask = { git = "https://github.com/pallets/flask" }
```

#### Dependency Markers

Some packages are available only on specific platforms or Python versions, so PEP 508 environment markers let you declare them only where they can be installed. For example, a Flask web app can use `pywin32` for Windows Integrated Authentication; `uv add` accepts markers with `--marker`, so you can restrict `pywin32` to Windows. See uv's [common markers](https://docs.astral.sh/uv/concepts/resolution/#common-marker-values) for other platform and Python-version conditions used in mixed environments such as Windows, Linux, WSL, CI, and production containers.

```bash
uv add "pywin32>=310" --marker "sys_platform == 'win32'"
```

After this command, the complete project file looks like this:

```toml
[project]
name = "license-service"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115,<0.116", # Allow patch releases in 0.115
    "flask",
    "httpx==0.27.2", # Require this exact version
    "pywin32>=310; sys_platform == 'win32'", # Windows-only
    "requests>=2.32.3", # Set a minimum version
]

[dependency-groups]
dev = [
    "pytest>=8.0",
    "ruff>=0.15",
]
docs = [
    "mkdocs>=1.6.1,<2.0",
]

[tool.uv.sources]
flask = { git = "https://github.com/pallets/flask" }
```

### Remove Dependencies

Use `uv remove` to remove a dependency. Choose the matching command for a normal or grouped dependency:

=== "Normal Dependencies"

    Remove a runtime dependency:

    ```bash
    uv remove requests
    ```

=== "Grouped Dependencies"

    Remove a dependency from the `dev` group:

    ```bash
    uv remove --group dev pytest
    ```

If you run both commands, the complete project file looks like this:

```toml
[project]
name = "license-service"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115,<0.116", # Allow patch releases in 0.115
    "flask",
    "httpx==0.27.2", # Require this exact version
    "pywin32>=310; sys_platform == 'win32'", # Windows-only
]

[dependency-groups]
dev = [
    "ruff>=0.15",
]
docs = [
    "mkdocs>=1.6.1,<2.0",
]

[tool.uv.sources]
flask = { git = "https://github.com/pallets/flask" }
```

## Locking

### The Lockfile

The `uv.lock` file is a TOML file generated by `uv` next to `pyproject.toml`. It records exact dependency versions, their relationships, package sources, and download hashes across the project's supported operating systems and Python versions. It is kept under version control and updated and reviewed alongside `pyproject.toml` so development, CI, and production can reuse the same reviewed versions. 

The `uv lock` command resolves the requirements declared in `pyproject.toml` and creates or updates the lockfile **without** creating a project virtual environment or installing packages. It may download package metadata, wheels, or source archives during resolution. It preserves existing locked versions where possible and leaves an up-to-date lockfile unchanged, even when newer versions are available.

```bash
uv lock
```

The following code block is an excerpt of `uv.lock`, with download entries and other packages omitted for readability. Each `[[package]]` entry describes a resolved package: FastAPI is locked to `0.115.14`, which satisfies the declared range, and Starlette is one of its transitive dependencies. A package's `dependencies` list identifies the packages it requires, whose resolved versions are recorded in their own `[[package]]` entries. Here, FastAPI requires Starlette, which in turn requires AnyIO. The top-level `version` and `revision` describe the lockfile format, not the project's version.

```toml
version = 1
revision = 3
requires-python = ">=3.11"

[[package]]
name = "fastapi"
version = "0.115.14"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "pydantic" },
    { name = "starlette" },
    { name = "typing-extensions" },
]

[[package]]
name = "starlette"
version = "0.46.2"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "anyio" },
]
```

!!! info "Commands that update the lockfile"
    `uv lock`, `uv add`, `uv remove`, `uv sync`, `uv run`, `uv tree`, and `uv export` create or update `uv.lock` as needed.

### Upgrade the Lockfile

The `uv lock --upgrade` command resolves all dependencies to the latest versions allowed by the constraints in `pyproject.toml`. Use `--upgrade-package` instead to upgrade a specific dependency while retaining other locked versions where possible.

=== "Single Dependency"

    Upgrade a single dependency to the latest version its constraint allows, retaining other locked versions where possible.

    ```bash
    uv lock --upgrade-package fastapi
    ```

=== "All Dependencies"

    Upgrade all dependencies to the latest versions allowed by their declared ranges.

    ```bash
    uv lock --upgrade
    ```

Install the updated versions into the project's virtual environment:

```bash
uv sync
```

### Validate the Lockfile

The `uv lock --check` command validates that the lockfile is in sync with `pyproject.toml` without modifying it. Use it in CI or before committing to catch outdated lockfiles:

```bash
uv lock --check
```

## Synchronizing

### Default Synchronization

!!! info "Local Development"
    Use the default sync for day-to-day development. It keeps the virtual environment aligned with the project metadata and, by default, installs the project in editable mode with the configured default dependency groups.

The `uv sync` command prepares a project's Python environment by installing the dependency versions recorded in `uv.lock`. It creates an *in-project* virtual environment (`.venv`) if needed and installs, upgrades, downgrades, or removes packages to match the selected dependencies and dependency groups. If the lockfile is outdated relative to `pyproject.toml`, it re-locks automatically before installing.

=== "Default"

    Install dependencies from `project.dependencies` in `pyproject.toml` and the default dependency groups, including their transitive dependencies (packages those dependencies require). The `dev` group is included by default unless `tool.uv.default-groups` changes that selection.

    ```bash
    uv sync
    ```

=== "Dependency Group"

    Include a dependency group alongside `project.dependencies` and the default groups. This example explicitly selects `dev`, which is normally already included by default.

    ```bash
    uv sync --group dev
    ```

=== "All Groups"

    Install `project.dependencies` and all dependency groups, but not optional extras unless explicitly requested.

    ```bash
    uv sync --all-groups
    ```

### Frozen Installs

!!! info "Intermediate Docker Layers"
    Use frozen syncs in intermediate Docker layers or workspace builds when dependencies need to be installed before all project source files are available. Because `--frozen` skips lockfile freshness checks, validate the lockfile separately and run a final `--locked` sync once all project files are present. See [uv's intermediate-layer guidance](https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers).

The `uv sync --frozen` command performs *frozen installs* that use the dependency versions recorded in an existing lockfile without checking whether it matches the declarations in `pyproject.toml` or updating it. Any dependency change in `pyproject.toml` is therefore not resolved into a new lockfile during the sync.

```bash
uv sync --frozen [--no-install-project] [--no-install-workspace]
```

- `--no-install-project`: Skips installing the project itself while still installing its dependencies.
- `--no-install-workspace`: Installs only dependencies, not workspace projects.

### Locked Installs

!!! info "CI/CD and Production Builds"
    Locked, non-editable installs suit production targets and CI/CD steps that prepare deployment artifacts. Typical locations are *GitHub Actions* workflow files and `Dockerfile` build steps. *Kubernetes Manifests* can also run the command through container `command` and `args` fields, though installing dependencies during the image build avoids startup-time downloads.

The `uv sync --locked` command performs *locked installs* that prepare the project environment using the dependency versions recorded in `uv.lock`, while checking that the lockfile matches the declarations in `pyproject.toml`. If the lockfile is missing or stale, the command fails rather than changing it automatically, requiring it to be created or updated and reviewed before the build proceeds. The `pyproject.toml` must define a `[build-system]` for `uv sync` to install the project itself. See uv's [editable installation guidance](https://docs.astral.sh/uv/concepts/projects/sync/#editable-installation).

=== "Editable"

    By default, `uv sync` installs the project and workspace members in *editable mode*, so imports use their source checkout and reflect source edits without reinstalling.

    ```bash
    uv sync --locked
    ```

=== "Non-Editable"

    With `--no-editable`, the project is installed into the virtual environment as a regular Python package, so Python imports the installed files rather than your source files directly. The installed package can still be imported if you move or remove the source folder, however, editing source files does not change the installed version. 
    
    For example, a package named `sync_demo` on Python 3.12 is installed under `.venv/lib/python3.12/site-packages/sync_demo/`, alongside `sync_demo-0.1.0.dist-info/`, which stores its name, version, and other package information. A regular sync may reuse that installation. To apply your edits, use the optional `--reinstall-package sync-demo` flag to force rebuilding and reinstalling. Running a source file directly still executes your edited code.

    ```bash
    uv sync --locked --no-editable [--reinstall-package sync-demo]
    ```

### Resolution Strategies

Before writing a lockfile, `uv` resolves direct and transitive dependencies to find versions that satisfy all declared constraints. It does this automatically when dependencies are added, updated, or synchronized and, by default, selects the latest compatible version of each dependency.

For libraries, testing only against the latest versions is insufficient: a declaration such as `fastapi>=0.100.0` claims compatibility with *every* version from `0.100.0` upward, not just the newest release.

=== "All Dependencies"

    Install the lowest compatible versions for all direct and transitive dependencies:

    ```bash
    uv sync --resolution lowest
    ```

=== "Direct Dependencies"

    Install the lowest compatible versions for direct dependencies only, keeping transitive dependencies at their latest:

    ```bash
    uv sync --resolution lowest-direct
    ```


#### Inspect the Graph

Display the resolved dependency tree, showing which package pulled in which transitive dependency:

```shell
uv tree
```

## Export Dependencies

### Share a Requirements File

When another tool expects a `requirements.txt`, export one from the project's lockfile:

```shell
uv export --format requirements.txt -o requirements.txt
```

Keep `pyproject.toml` and `uv.lock` as the project's source of truth; regenerate the export after changing dependencies. For working directly with an existing `requirements.txt`, see [Standalone Environments and Tools](./section-04.md#work-with-legacy-projects).
