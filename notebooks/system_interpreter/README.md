# System Interpreter — Dependency Isolation Demonstration

## What the notebook demonstrates

The notebook is organised into these sections. Every section prints the
Python executable and package versions actually in play, so nothing is
implicit.

1. The shared machine — one interpreter and one system package set.
2. Bob and Alice — two real Linux users, one has sudo, the other does not.
3. Three tiny embedded projects written to disk from a cell.
4. Bob works with the shared Requests 2.25.1, while Alice's project fails.
5. The shared Requests copy is removed; Bob and Alice install their required
    releases with `pip install --user`.
6. Alice hits the next wall: two projects with incompatible FastAPI
   requirements cannot both live in her `--user` scope.
7. Each project gets its own `python3 -m venv`. All three apps coexist.
8. An `ipywidgets` dropdown lets students switch between running commands
    as `bob` and `alice` from inside the notebook.
9. A summary table visualises how the isolation boundary tightens across
    the three approaches.

## Files in this directory

| Path | Description |
| --- | --- |
| `.devcontainer/Dockerfile` | Ubuntu 22.04 image with Python 3, `pip`, `venv`, JupyterLab, ipywidgets, `sudo`, and Bob's legacy dependency `requests==2.25.1` pre-installed system-wide. It seeds Alice's `--user` site with her initial app-level dependencies while keeping Requests out of her user site. Creates two real Linux users, `bob` (sudo) and `alice` (no sudo). |
| `.devcontainer/devcontainer.json` | VS Code Dev Container config. Default user is `bob`. Installs the Python and Jupyter extensions and pins the default interpreter to `/usr/bin/python3`. |
| `system_interpreter.ipynb` | Everything else. The three demo applications are embedded in the notebook as Python strings and written to disk from a cell. |


## Usage

### Prerequisites

Before opening the project, make sure you have:

- VS Code + Dev Containers extension for VS Code
- Docker Desktop

### Getting Started

- Open the repository root in VS Code.
- Run **Dev Containers: Reopen in Container** and pick the
  `notebooks/system_interpreter` folder.
- When the container is ready, open `system_interpreter.ipynb`.
- Select the kernel **Python 3 — Ubuntu System** (this is
  `/usr/bin/python3`). Run cells top-to-bottom.
