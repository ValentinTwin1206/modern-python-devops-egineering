# Standalone Python Workflows with uv

## Introduction

`uv` can manage existing requirements, run individual scripts, and provide command-line tools without creating a project. This section uses small, independent examples. For project-managed dependencies, see [Dependency Management with uv](./section-02.md).

## Work with Legacy Projects

### Create a Standalone Environment

In a directory for an existing project, create `.venv` using Python 3.12:

```bash
uv venv --python 3.12
```

The following `uv pip` commands select the environment explicitly. They change installed packages but do not update a project's `pyproject.toml` or `uv.lock`.

### Install from a Requirements File

Given an existing `requirements.txt`, install its requirements into the environment:

```bash
uv pip install --python .venv/bin/python -r requirements.txt
```

Inspect the installed packages:

```bash
uv pip list --python .venv/bin/python
```

### Compile and Synchronize Requirements

For a requirements-based workflow, list direct requirements in `requirements.in`. This example requests a compatible range of `requests`:

```text title="requirements.in"
requests>=2.31,<3
```

Resolve the direct and transitive dependencies into a pinned requirements file:

```bash
uv pip compile requirements.in -o requirements.txt
```

Make the selected environment match the compiled file:

```bash
uv pip sync --python .venv/bin/python requirements.txt
```

Unlike `uv pip install`, `uv pip sync` removes packages not listed in the requirements file. Review and retain the generated file if it is your team's installation contract. See [locking environments](https://docs.astral.sh/uv/pip/compile/) for upgrades and platform-specific resolution.

## Run Standalone Scripts

### Run a Script with Temporary Dependencies

For a one-off experiment, request `rich` for a single command without changing project dependencies:

```bash
uv run --no-project --with rich python -c 'from rich import print; print("Hello from uv")'
```

`--no-project` prevents the current project from being loaded. For a reusable script, put its requirements in the script instead.

### Declare Inline Dependencies

Create a script with inline metadata specifying Python 3.12:

```bash
uv init --script report.py --python 3.12
```

Add the library the script needs:

```bash
uv add --script report.py rich
```

The generated [PEP 723](https://peps.python.org/pep-0723/) metadata at the top of the file declares its Python requirement and dependencies. For example, the script can contain:

```python title="report.py"
# /// script
# requires-python = ">=3.12"
# dependencies = ["rich>=13"]
# ///
from rich import print

print("Report ready")
```

Run the script; `uv` prepares an environment for its declared requirements:

```bash
uv run report.py
```

A script with inline metadata uses its own dependencies even when run inside a project. Without inline metadata, `uv run --no-project report.py` avoids using the enclosing project.

### Lock Script Dependencies

Create a separate lockfile beside the script to record its resolved dependencies:

```bash
uv lock --script report.py
```

The result is `report.py.lock`. Run with `--locked` to require an up-to-date script lockfile:

```bash
uv run --locked report.py
```

Commit the script and its lockfile together when reproducible versions matter. See the [script guide](https://docs.astral.sh/uv/guides/scripts/#locking-dependencies) for more details.

## Run Command-Line Tools

### Run a Tool with `uvx`

Run Ruff without installing it into the current project:

```bash
uvx ruff --version
```

`uvx` is an alias for `uv tool run`. The tool runs in an isolated environment, which `uv` may cache for reuse. Request an exact version when the result should not depend on the cached or latest version:

```bash
uvx ruff@0.15.0 --version
```

### Use Project Dependencies with a Tool

Tools that need a project's packages, such as a test runner, should run in the project environment. After adding `pytest` to the project's `dev` group, run:

```bash
uv run pytest
```

`uvx pytest` uses an isolated tool environment instead, so it does not automatically include the project's installed dependencies. See [tool execution versus `uv run`](https://docs.astral.sh/uv/concepts/tools/#relationship-to-uv-run).

### Install and Maintain Tools

Install Ruff in a persistent tool environment and expose its executable on `PATH`:

```bash
uv tool install ruff
```

List installed tools:

```bash
uv tool list
```

Upgrade Ruff within any version constraint used when installing it:

```bash
uv tool upgrade ruff
```

Remove the tool when it is no longer needed:

```bash
uv tool uninstall ruff
```

The executable directory must be on `PATH` to invoke `ruff` directly. Tool environments are separate from the project environment.

## Choose the Right Workflow

| Need | Start with |
| --- | --- |
| Develop a `pyproject.toml` project | `uv add`, `uv sync`, `uv run` |
| Maintain existing requirements | `uv venv`, `uv pip compile`, `uv pip sync` |
| Run a self-contained script | Inline metadata and `uv run` |
| Try an isolated CLI tool | `uvx` |
| Run a tool with project dependencies | `uv run` |
| Keep a CLI tool available | `uv tool install` |

To export requirements **from a managed project**, see [Export Dependencies](./section-02.md#export-dependencies).
