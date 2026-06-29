# uv Dependency Resolution Notebook

This project contains a training notebook that demonstrates `uv` dependency management, locking, resolution, and reproducible environment synchronization with one consistent example project: `weather-dashboard`.

## Contents

- `uv_dependency_resolution.ipynb`: The executable teaching notebook.
- `weather-dashboard/`: A small fictional Python project used throughout the notebook.
- `weather-dashboard/pyproject.toml`: The project metadata, runtime dependencies, and development dependency group.

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

The notebook creates and updates the `weather-dashboard` project in this directory. It writes a `uv.lock` file and a `.venv` directory as part of the exercises. These generated files can be deleted and recreated by rerunning the notebook.

## What you will learn

- How `uv` creates and manages project environments.
- How `pyproject.toml`, `uv.lock`, and `.venv` work together.
- How dependency resolution differs from locking and synchronization.
- How to update dependencies safely.
- How to use `uv sync --frozen` and `uv lock --check` in CI/CD pipelines.
- How dependency groups and platform markers affect resolution.
