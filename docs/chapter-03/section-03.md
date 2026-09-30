# Dependency Management with uv

## Introduction

Modern Python applications are built on top of dependencies. Managing those dependencies becomes increasingly challenging when developers work on different operating systems, use different Python versions, or require platform-specific tooling.

`uv` splits dependency management into three concerns: **declaring** what a project needs (`pyproject.toml`), **locking** the resolved versions (`uv.lock`), and **synchronizing** the environment (`.venv`) to match the lockfile. Each concern has its own commands, and each file has exactly one responsibility.

!!! note "Scope"
    Project setup, Python version pinning, and virtual environment internals are covered in *Project Management with uv*. This section focuses purely on dependencies.

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

Dependency locking ensures that every installation uses the exact same dependency versions, making builds reproducible and preventing unexpected breakages caused by newly released package versions.

Resolve the declared dependencies and write the result to `uv.lock`:

```shell
uv lock
```

!!! note "uv.lock file"
    The `uv.lock` file is the single source of truth for a project's installed versions. It contains the fully resolved dependency graph — all direct and transitive dependencies with exact versions. Because `uv` uses a universal resolution strategy, the lockfile is portable across operating systems and Python versions.

The lockfile only changes when a command explicitly re-resolves (`uv add`, `uv remove`, `uv lock`, `uv lock --upgrade`). This makes dependency changes predictable and reviewable: a changed `uv.lock` in a pull request is a deliberate act, never a side effect.

!!! note "Commit the lockfile"
    Commit `uv.lock` to version control. Only then do development, CI, and production install the same versions.

### Validate and Upgrade

Verify that the lockfile is still in sync with `pyproject.toml` — use this in CI or before committing:

```shell
uv lock --check
```

Upgrade a single dependency to the latest version its constraint allows, leaving everything else untouched:

```shell
uv lock --upgrade-package fastapi
```

Upgrade all dependencies to the latest versions allowed by their declared ranges:

```shell
uv lock --upgrade
```

## Synchronizing

### Install from the Lockfile

Make the `.venv` match `uv.lock` exactly — packages are installed, upgraded, downgraded, or removed as needed:

```shell
uv sync
```

Include a dependency group:

```shell
uv sync --group dev
```

Include all groups:

```shell
uv sync --all-groups
```

If the lockfile is outdated relative to `pyproject.toml`, `uv sync` re-locks automatically before installing.

### Frozen Installs

In CI and production, an automatic re-lock is unwanted: the build must install *exactly* what was reviewed. The `--frozen` flag installs strictly from the existing `uv.lock` and fails if the lockfile is stale:

```shell
uv sync --frozen
```

A failing frozen sync is a feature — it signals that someone changed `pyproject.toml` without re-locking.

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

## The `uv pip` Layer

`uv` also ships a low-level interface that mirrors the classic `pip` commands — same syntax, dramatically faster, but **without** touching `pyproject.toml` or `uv.lock`.

Install a package into the active environment:

```shell
uv pip install cowsay
```

List installed packages:

```shell
uv pip list
```

!!! warning "Escape hatch, not a workflow"
    `uv pip` operates on the environment directly. Anything installed this way is invisible to the lockfile, and the next `uv sync` removes it again. Use `uv pip` for quick experiments and for migrating legacy `requirements.txt` projects — use `uv add` for anything the project actually depends on.

## Tools

Command-line tools such as linters and formatters are not project dependencies — they should not appear in `pyproject.toml` of the project they are run against.

### Ephemeral Runs with `uvx`

Run a tool in a temporary, cached environment without installing anything:

```shell
uvx ruff check .
```

`uvx` resolves the tool, executes it, and leaves the project environment untouched. Ideal for one-off usage.

### Persistent Tools

Install a tool user-wide so its executable is permanently on `PATH`:

```shell
uv tool install ruff
```

List installed tools:

```shell
uv tool list
```

Uninstall a tool:

```shell
uv tool uninstall ruff
```
