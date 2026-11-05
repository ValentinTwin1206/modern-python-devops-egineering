# Standalone Environments and Tools with uv — Return of the Admin: Bob Brings Balance to uv

Bob has learned to scaffold projects, resolve dependencies, and make the most of the cache. Proud of his progress, he is ready to help his company: an old requirements-based service needs a repeatable environment, a small report needs to be shared, and the team wants useful tools without disturbing project dependencies. Bob builds a practical runbook for each task.

![uv Extra Features lab logo](./project_logo.svg)

## Learning Objectives

- Manage a standalone virtual environment and synchronize pinned requirements.
- Run a self-contained script with inline metadata and a script lockfile.
- Choose between project commands, isolated tools, and persistent tool installations.

## Overview

- Creating a virtual environment and installing existing requirements with `uv pip`.
- Compiling and synchronizing requirements and inspecting the resulting environment.
- Temporary dependencies, inline script metadata, and locked script execution.
- Running tools with `uvx` and maintaining them with `uv tool`.
- Comparing an isolated tool environment with a project-aware `uv run` command.

## Documentation

- [Chapter 03, Section 05: Standalone Environments and Tools with uv](../../docs/chapter-03/section-05.md)
- [Open the notebook](./uv_extra_features.ipynb); follow [Bob Follows the Cache](../nb5_uv_cache_lab/uv_cache_lab.ipynb).

## Run The Lab

1. Install Docker, VS Code, and the VS Code Dev Containers extension.
2. Open `notebooks/nb6_uv_extra_features` as the folder in VS Code and select **Dev Containers: Reopen in Container**.
3. Open `uv_extra_features.ipynb`, select the **Python 3 - uv Extra Features** kernel, and run the cells in order.

The container supplies `uv` 0.13.3, Python 3.12, and Jupyter. Initial package downloads require network access. The setup cell removes the lab-generated `lab/` directory, including its isolated tool and cache directories; keep unrelated work elsewhere.
