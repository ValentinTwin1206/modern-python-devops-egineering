# Dependency management with uv

## Introduction

Modern Python applications are built on top of dependencies. Managing those dependencies becomes increasingly challenging when developers work on different operating systems, use different Python versions, or require platform-specific tooling. 

## Environment Isolation

`uv` manages a persistent virtual environment in a `.venv` directory next to the `pyproject.toml`. The environment is created and updated automatically by commands such as `uv venv`, `uv add`, `uv sync`, or `uv run`.

Using `uv python install` and `.python-version`, projects can pin an exact Python version which is managed by `uv` as part of the project setup. Developers do not need to manually create environments with a specific Python executable or keep track of interpreter paths. When entering a project, `uv` automatically discovers the required interpreter, creates the virtual environment with that interpreter, and keeps the interpreter and environment aligned

The relationship between the pinned interpreter and the virtual environment is recorded in `.venv/pyvenv.cfg`:

```ini
home = /root/.local/share/uv/python/cpython-3.10-linux-x86_64-gnu/bin
implementation = CPython
uv = 0.11.19
version_info = 3.10.20
include-system-site-packages = false
```

This allows developers to work with the exact Python version required by the project while keeping the system Python untouched.

!!! note "Interpreter change"
    Interpreter changes forces to remove and recreate the `.venv` folder against the new interpreter. Dependency versions still follow `uv.lock`; package artifacts are usually reused from `~/.cache/uv` and hard-linked into the new environment, and are only downloaded again when they are missing or incompatible with the new Python version/platform.

## Locking

Dependency locking ensures that every installation uses the exact same dependency versions, making builds reproducible and preventing unexpected breakages caused by newly released package versions.

Traditional Python package managers such as `pip` only provide limited support for dependency locking. While developers often use `pip freeze` to generate a `requirements.txt` file, this approach merely captures the current state of a local environment and may produce inconsistent results across different platforms and Python versions.

`uv` addresses this problem out of the box through its built-in lockfile mechanism. Whenever dependencies are added, removed, or updated, `uv` resolves the complete dependency graph and stores the result in the `uv.lock` file.

!!! note "uv.lock file"
    The `uv.lock` file serves as the single source of truth for your project's dependencies.It contains the fully resolved dependency graph, including all direct and transitive dependencies, along with the exact versions that should be installed. Because uv uses a universal resolution strategy, the lockfile remains portable across operating systems and Python environments.

The uv.lock file remains unchanged until it is explicitly updated. This ensures that dependency versions stay consistent across development, CI, and production environments.

Validate that the lockfile is in sync with the project's dependency definitions:

```shell
uv lock --check
```

Update all locked dependencies to the latest compatible versions and regenerate the lockfile:

```shell
uv lock --upgrade
```

Update a single dependency while leaving the rest of the lockfile unchanged:

```shell
uv lock --upgrade-package fastapi
```

By requiring explicit updates to uv.lock, dependency changes become predictable, reviewable, and fully reproducible.

## Resolution

Before a lockfile can be created, the package manager must first resolve a valid dependency graph - this process is called **resolution**. 

`uv` performs dependency resolution automatically whenever dependencies are added, updated, or synchronized.

### Strategies

By default, `uv` prefers the latest compatible version of each dependency. This keeps projects up to date while still respecting version constraints defined in `pyproject.toml`.

When developing libraries, however, testing only against the latest versions is often insufficient. A dependency declaration such as `fastapi>=0.100.0` the following claims compatibility with every version starting from `0.100.0`, not just the latest release.

To validate these compatibility guarantees, `uv` supports alternative resolution strategies:

```shell
uv sync --resolution lowest
```

Installs the lowest compatible version for all direct and transitive dependencies.

```shell
uv sync --resolution lowest-direct
```

Installs the lowest compatible versions for direct dependencies while keeping transitive dependencies at their latest compatible versions.

These strategies are particularly useful in CI pipelines to verify that declared version bounds are accurate and that a project does not accidentally depend on newer package releases.

### Dependency Groups

Not all dependencies are required in every environment. Development tools, test frameworks, and documentation generators are typically only needed during development.

Dependency groups allow related dependencies to be separated from production requirements:

```yaml
[dependency-groups]
dev = [
    "pytest",
    "ruff",
]
```

Dependencies can then be installed selectively:

```shell
uv sync --group dev
```

Grouping dependencies keeps production environments lean while ensuring that development tooling remains easy to install and manage.

### Dependency Markers

Some dependencies are only valid on specific platforms or Python versions. Without additional information, the resolver assumes that every dependency must be installed in every environment.

Consider a project that uses Windows Authentication through `pywin32`:

```yaml
dependencies = [
    "fastapi",
    "sqlalchemy",
    "pywin32"
]
```

While the project perfectly bootstraps on Windows, the same setup on WSL crashes with the following hint

```bash
error: Distribution `pywin32==312 @ registry+https://pypi.org/simple` can't be installed because it doesn't have a source distribution or wheel for the current platform
```

Dependency markers allow such constraints to be expressed directly:

```yaml
dependencies = [
    "fastapi",
    "sqlalchemy",
    "pywin32; sys_platform == 'win32'"
]
```

The resolver now includes `pywin32` only on Windows systems, producing a valid dependency graph across different environments.

!!! note
    Dependency markers are defined by the `PEP 508` standard and can be looked up from the [common markers](https://docs.astral.sh/uv/concepts/resolution/#common-marker-values) documentation of `uv`. In practice, operating system and Python version markers are by far the most common use cases, especially when supporting mixed environments such as Windows, Linux, WSL, CI runners, and production containers.

## Comparison

The table below compares `uv`, `poetry`, and `pip` across environment isolation, locking, and resolution—the core components of dependency management.

<table>
<tbody>
<tr style="background-color: #f5f5f5;">
<td style="font-weight: bold;">Environment Isolation</td>
<td style="text-align: center; font-weight: bold;">uv</td>
<td style="text-align: center; font-weight: bold;">Poetry</td>
<td style="text-align: center; font-weight: bold;">pip</td>
</tr>
<tr>
<td>Automatic environment creation</td>
<td style="text-align: center;">✓</td>
<td style="text-align: center;">✓</td>
<td style="text-align: center;">✗</td>
</tr>
<tr>
<td>Automatic environment selection</td>
<td style="text-align: center;">✓</td>
<td style="text-align: center;">✓</td>
<td style="text-align: center;">✗</td>
</tr>
<tr>
<td>Install python version</td>
<td style="text-align: center;">✓</td>
<td style="text-align: center;">✗</td>
<td style="text-align: center;">✗</td>
</tr>
<tr>
<td>Switch python version</td>
<td style="text-align: center;">✓</td>
<td style="text-align: center;">✓</td>
<td style="text-align: center;">✗</td>
</tr>
<tr style="background-color: #f5f5f5;">
<td colspan="4" style="font-weight: bold;">Locking</td>
</tr>
<tr>
<td>Native lock file</td>
<td style="text-align: center;">✓</td>
<td style="text-align: center;">✓</td>
<td style="text-align: center;">✗</td>
</tr>
<tr>
<td>Stores full dependency graph</td>
<td style="text-align: center;">✓</td>
<td style="text-align: center;">✓</td>
<td style="text-align: center;">✗</td>
</tr>
<tr>
<td>Reproducible installations</td>
<td style="text-align: center;">✓</td>
<td style="text-align: center;">✓</td>
<td style="text-align: center;">✗</td>
</tr>
<tr style="background-color: #f5f5f5;">
<td colspan="4" style="font-weight: bold;">Resolution</td>
</tr>
<tr>
<td>Full dependency graph resolution</td>
<td style="text-align: center;">✓</td>
<td style="text-align: center;">✓</td>
<td style="text-align: center;">✓</td>
</tr>
<tr>
<td>Lock-file-based resolution</td>
<td style="text-align: center;">✓</td>
<td style="text-align: center;">✓</td>
<td style="text-align: center;">(✓)</td>
</tr>
<tr>
<td>Deterministic dependency graph</td>
<td style="text-align: center;">✓</td>
<td style="text-align: center;">✓</td>
<td style="text-align: center;">(✓)</td>
</tr>
<tr>
<td>Optimized for resolution speed</td>
<td style="text-align: center;">✓</td>
<td style="text-align: center;">(✓)</td>
<td style="text-align: center;">✗</td>
</tr>
</tbody>
</table>
