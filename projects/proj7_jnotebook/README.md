# uv Dependency Resolution Notebook

This project contains a training notebook that demonstrates `uv` dependency management, locking, resolution, and reproducible environment synchronization by editing a local `pyproject.toml` beside the notebook.

## Contents

- `uv_dependency_resolution.ipynb`: The executable teaching notebook.
- `pyproject.toml`: A small example project file created and edited by the notebook.
- `uv.lock`: The lockfile generated during the exercises.

## Prerequisites

Install the following tools before running the notebook:

- Python 3.11 or newer
- Jupyter support in VS Code or another Jupyter environment
- [`uv`](https://docs.astral.sh/uv/) available on your `PATH`

Check that `uv` is installed:

```bash
uv --version
```

## How to run

1. Open `uv_dependency_resolution.ipynb` in VS Code.
2. Select a Python kernel.
3. Run the notebook from top to bottom.

The notebook creates and updates `pyproject.toml` in this directory. It may also write `uv.lock` and `.venv` as part of the exercises. These generated files can be deleted and recreated by rerunning the notebook.

## What you will learn

- How `uv` creates and manages project environments.
- How `pyproject.toml`, `uv.lock`, and `.venv` work together.
- How dependency resolution differs from locking and synchronization.
- How to update pinned and ranged dependencies safely.
- How to use `uv sync --frozen` and `uv lock --check` in CI/CD pipelines.
