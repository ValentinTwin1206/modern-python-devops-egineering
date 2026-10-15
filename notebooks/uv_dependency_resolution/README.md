# Dependency Management — Bob Discovers the Force of uv

After [his first uv project](../uv_proj_scaffolding/uv_proj_scaffolding_lab.ipynb),
**Bob** teaches himself dependency management with `uv`.
One project, three files — `pyproject.toml` (intent), `uv.lock` (truth),
`.venv` (reality) — and one command per step.

The notebook runs inside its own Ubuntu-based development container so the
commands and Python interpreter are reproducible and do not depend on the
host machine. It accompanies the technical documentation in
`docs/chapter-03/section-02.md`.

| Section | Content |
| --- | --- |
| Introduction | Bob's motivation, the three-file mental model, and lab reset. |
| Declaring Dependencies | Index and Git sources (including a local helper), dependency groups, markers, and removal. |
| Locking | Inspect the lockfile, repair a broken pin, upgrade within constraints, and detect drift. |
| Synchronizing | Default, frozen, and locked installs; non-editable source-edit experiment; lowest resolution and dependency tree. |
| Export Dependencies | Share a requirements file from the lockfile. |
| Epilogue | Bob's runbook notes and three rules. |

## Files in this directory

| Path | Description |
| --- | --- |
| `.devcontainer/Dockerfile` | Ubuntu 24.04 image with Python 3, `pip`, `venv`, JupyterLab, `ipykernel`, and `uv`, running as `bob`. |
| `.devcontainer/devcontainer.json` | VS Code Dev Container configuration. It mounts this directory at `/workspace` and uses the `bob` container user. |
| `uv_dependency_lab.ipynb` | The dependency-management lab. It creates and edits a local `pyproject.toml`, `uv.lock`, `.venv`, separate `installed-demo/` and `resolution-demo/` projects, and a disposable Git helper as it runs. |

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
and `.venv` files therefore belong to this dedicated lab workspace. The first
reset cell also removes the lab-generated `requirements.txt`, `installed-demo/`,
`resolution-demo/`, and `local-helper/` from a previous run; keep other work outside this folder.
