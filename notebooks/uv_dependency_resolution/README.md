# Dependency Management with uv — Bob Learns New Tricks

A monolog notebook: **Bob**, the reformed server admin from the
`system_interpreter` lab, teaches himself dependency management with `uv`.
One project, three files — `pyproject.toml` (intent), `uv.lock` (truth),
`.venv` (reality) — and one command per step.

The notebook runs inside its own Ubuntu-based development container so the
commands and Python interpreter are reproducible and do not depend on the
host machine. It accompanies the technical documentation in
`docs/chapter-03/section-03.md`.

| Act | Content |
| --- | --- |
| Prologue | Bob's motivation and the three-file mental model. |
| I — A Clean Desk | Verify `uv`, remove leftover project files. |
| II — Declaring Intent | Write a `pyproject.toml`; `uv add` / `uv remove`; dependency groups; PEP 508 markers. |
| III — Lock, Then Sync | `uv lock`, `uv tree`, `uv sync`. |
| IV — Change Is Constant | Bump an exact pin; watch a broken pin fail at resolution; repair it. |
| V — Trust, but Verify | Drift detection with `uv lock --check`; strict installs with `uv sync --frozen`. |
| VI — Upgrades on Bob's Terms | `uv lock --upgrade-package` against exact vs. ranged constraints; `uv lock --upgrade`. |
| VII — The Old Reflexes | The `uv pip` escape hatch (and how `uv sync` undoes it); `uvx`; `uv tool`. |
| Epilogue | File/command/effect table and Bob's three rules. |

## Files in this directory

| Path | Description |
| --- | --- |
| `.devcontainer/Dockerfile` | Ubuntu 24.04 image with Python 3, `pip`, `venv`, JupyterLab, `ipykernel`, and `uv`. It creates the same `bob` and `alice` users as the system-interpreter lab. |
| `.devcontainer/devcontainer.json` | VS Code Dev Container configuration. It mounts this directory at `/workspace` and uses the `bob` container user. |
| `uv_dependency_lab.ipynb` | The dependency-management lab. It creates and edits a local `pyproject.toml`, `uv.lock`, and `.venv` as it runs. |

The image contains Jupyter tooling and `uv`, but no application dependencies.
The notebook installs those dependencies deliberately with `uv` commands so
the lockfile and environment changes remain visible.

## Usage

### Prerequisites

- VS Code with the Dev Containers extension
- Docker Desktop or another Docker-compatible engine

### Getting started

1. Open the repository root in VS Code.
2. Run **Dev Containers: Reopen in Container** and choose the
   `notebooks/uv_dependency_resolution` folder.
3. Open `uv_dependency_lab.ipynb` after the container is ready.
4. Select **Python 3 - uv Dependency Resolution** as the notebook kernel.
5. Run the cells from top to bottom.

The notebook's shell commands run from `/workspace`, which is the mounted
`uv_dependency_resolution` directory. Generated `pyproject.toml`, `uv.lock`,
and `.venv` files therefore belong to this dedicated lab workspace.
