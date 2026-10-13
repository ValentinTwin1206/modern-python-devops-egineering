# Dependency Management with uv

## Introduction

Modern Python applications are built on top of dependencies. Managing those dependencies becomes increasingly challenging when developers work on different operating systems, use different Python versions, or require platform-specific tooling.

`uv` splits dependency management into three concerns: **declaring** what a project needs (`pyproject.toml`), **locking** the resolved versions (`uv.lock`), and **synchronizing** the environment (`.venv`) to match the lockfile. Each concern has its own commands, and each file has exactly one responsibility.

!!! note "Scope"
    For project setup, Python versions, and project environments, see [Project Scaffolding with uv](./section-01.md). Standalone environments and tools are covered in [Section 04](./section-04.md).

## Declaring Dependencies

### The `pyproject.toml`

The `pyproject.toml` declares the *intent* of a project: which packages it needs and which version ranges are acceptable. It does not record exact versions of transitive dependencies — that is the lockfile's job.

A minimal, complete project file looks like this:

```toml
[project]
name = "license-service"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115,<0.116",
    "httpx==0.27.2",
    "rich>=13.7,<14",
]
```

### Add and Remove

Instead of editing the file by hand, `uv` can modify the `dependencies` entry for you and immediately re-resolve.

Add a runtime dependency:

```shell
uv add requests
```

Without an explicit constraint, `uv` writes a lower bound at the current version into `pyproject.toml`:

```toml
dependencies = [
    "requests>=2.32.3",
]
```

Add a dependency with an explicit constraint:

```shell
uv add "httpx==0.27.2"
```

Remove a dependency:

```shell
uv remove requests
```

Every `uv add` / `uv remove` updates `pyproject.toml`, re-resolves the graph into `uv.lock`, and syncs the `.venv` in one step.

### Alternative Sources

`uv add` can also install from a Git repository. For example, add `httpx` from its source repository:

```shell
uv add "httpx @ git+https://github.com/encode/httpx"
```

`uv` records `httpx` as a dependency in `[project]` and its Git location under `[tool.uv.sources]`. Prefer a released package from an index unless you need code from a repository.

### Version Constraints

The constraint style controls how much freedom the resolver has:

| Constraint | Meaning | Typical use |
| --- | --- | --- |
| `httpx==0.27.2` | exactly this version | maximum reproducibility at declaration level |
| `fastapi>=0.115,<0.116` | any patch release within a minor version | applications |
| `rich>=13.7` | this version or anything newer | libraries with wide compatibility |

Prefer ranges for applications and libraries; the lockfile already guarantees exact versions at install time. Exact pins in `pyproject.toml` are only needed when a specific version is a hard requirement.

### Dependency Groups

Development tools, test frameworks, and documentation generators are not needed in production. Dependency groups separate them from runtime requirements:

```toml
[project]
name = "license-service"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115,<0.116",
]

[dependency-groups]
dev = [
    "pytest>=8.0",
    "ruff>=0.15",
]
```

Add a package directly into a group:

```shell
uv add --group dev pytest
```

The `dev` group is special-cased and can also be targeted with a shortcut:

```shell
uv add --dev ruff
```

Remove a package from a group:

```shell
uv remove --group dev pytest
```

### Dependency Markers

Some dependencies are only valid on specific platforms or Python versions. Without additional information, the resolver assumes that every dependency must be installed in every environment.

Consider a project that uses Windows Authentication through `pywin32`. Declared unconditionally, `uv sync` fails on Linux because `pywin32` publishes no Linux wheels. A marker restricts the dependency to the platforms where it exists:

```toml
[project]
name = "license-service"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115,<0.116",
    "pywin32>=310; sys_platform == 'win32'",
]
```

The resolver now includes `pywin32` only on Windows systems, producing a valid dependency graph across all environments.

!!! note
    Dependency markers are defined by the `PEP 508` standard; see the [common markers](https://docs.astral.sh/uv/concepts/resolution/#common-marker-values) documentation of `uv`. Operating system and Python version markers are by far the most common use cases, especially in mixed environments such as Windows, Linux, WSL, CI runners, and production containers.

## Locking

### The Lockfile

The `uv.lock` file records exact versions of direct and transitive dependencies, their relationships, package sources, and download hashes so later installations can reuse the resolved versions. Dependency locking is a tool-agnostic technique also used by `npm`, `cargo`, `go`, etc., though lockfile formats differ. `uv` generates this TOML file next to `pyproject.toml`, covering the project's supported operating systems and Python versions. Run `uv lock` to resolve the requirements declared in `pyproject.toml` and create or update the lockfile without installing packages into the project environment.

```bash
uv lock
```

Download entries and other packages are omitted for readability. Each `[[package]]` entry identifies a resolved package. Here, FastAPI is locked to `0.115.14`, which satisfies the declared range, and Starlette is one of its transitive dependencies. The top-level `version` and `revision` describe the lockfile format, not the project's version.

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

Commit `uv.lock` to version control and review changes alongside `pyproject.toml` so development, CI, and production can reuse the reviewed versions. Let uv manage the file rather than editing it manually.

!!! info "Commands that update the lockfile"
    `uv lock`, `uv add`, `uv remove`, `uv sync`, `uv run`, `uv tree`, and `uv export` create or update `uv.lock` as needed.

### Upgrade the Lockfile

The `uv lock` command creates or updates the lockfile without creating a project virtual environment or installing packages into one. It may download package metadata, wheels, or source archives to resolve dependencies. It keeps existing locked versions where possible and leaves an up-to-date lockfile unchanged, even when newer versions are available. To force a fresh search for newer versions, use `--upgrade` or `--upgrade-package`; the dependencies in `pyproject.toml` still apply.

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

Verify that the lockfile is still in sync with `pyproject.toml` — use this in CI or before committing:

```bash
uv lock --check
```

## Synchronizing

### Install from the Lockfile

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

The `uv sync --frozen` command performs *frozen installs* that use the dependency versions recorded in an existing lockfile without checking whether it matches the declarations in `pyproject.toml` or updating it. Any dependency change in `pyproject.toml` is therefore not resolved into a new lockfile during the sync.

It can be used in CI after [lockfile validation](#validate-and-upgrade), or in intermediate `Dockerfile` layers where the files needed for validation are not yet available, including builds of [`uv` workspaces](./section-01.md#manage-related-projects-with-uv-workspaces). These layers can install dependencies separately from the project source. Once all project files are available, uv's [intermediate-layer guidance](https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers) recommends a final sync with `--locked` to validate the lockfile.

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

## Resolution

Before a lockfile can be written, the package manager must find a set of versions that satisfies every declared constraint, including all transitive constraints — this process is called **resolution**. `uv` resolves automatically whenever dependencies are added, updated, or synchronized.

### Strategies

By default, `uv` prefers the latest compatible version of each dependency. For libraries, testing only against the latest versions is insufficient: a declaration such as `fastapi>=0.100.0` claims compatibility with *every* version from `0.100.0` upward, not just the newest release.

Install the lowest compatible version for all direct and transitive dependencies:

```shell
uv sync --resolution lowest
```

Install the lowest compatible versions for direct dependencies only, keeping transitive dependencies at their latest:

```shell
uv sync --resolution lowest-direct
```

These strategies are particularly useful in CI pipelines to verify that declared version bounds are accurate.

### Inspect the Graph

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
