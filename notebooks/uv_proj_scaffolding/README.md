# Project Scaffolding with uv — A New Hope for Bob

Bob builds his first modern Python project, one visible step at a time. This lab accompanies [Chapter 03, Section 01](../../docs/chapter-03/section-01.md). Its Dev Container supplies uv and a Jupyter kernel; the notebook creates projects and manages their Python environments.

| Stage | What Bob explores |
| --- | --- |
| Getting started | Install options and the uv version in the container |
| Initialize | `--no-package`, `--package`, `--lib`, `--bare` and their generated files |
| Python and environment | Interpreter pin, `requires-python`, `uv sync` and `.venv` |
| Configure and run | `uv add`, `uv run`, and `[tool.ruff]` |
| Distribute | `uv_build`, wheel, source archive, and publication guidance |
| Grow | A local workspace member and shared lockfile |

## Run the lab

1. Install Docker and the VS Code Dev Containers extension.
2. Open the `notebooks/uv_proj_scaffolding` folder in a Dev Container.
3. Select the **Python 3 - uv Project Scaffolding** kernel and run `uv_proj_scaffolding_lab.ipynb` from top to bottom.

The notebook creates examples in `lab/` within this folder. Its first executable setup cell resets **only** `lab/` so the lab can be rerun. This directory is git-ignored. A network connection is needed for the first interpreter, dependency, and build-backend downloads. Publishing is explained but never executed.

Continue with [Bob's dependency lab](../uv_dependency_resolution/uv_dependency_lab.ipynb) for locking, syncing, and upgrading dependencies.
