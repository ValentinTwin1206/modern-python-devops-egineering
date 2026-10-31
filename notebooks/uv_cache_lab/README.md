# Dependency Caching with uv — Bob Follows the Cache

After learning to scaffold projects and manage their dependencies with `uv`, Bob turns his attention to the cache. Still determined to show that the old administrator has something to contribute, he wants to know which downloads and builds can be reused and what happens when the cache is cleaned. He sets up a small numerical project and follows its artifacts through installation, offline reuse, and cleanup. Each experiment brings another useful answer to his growing runbook.

![uv Cache Lab project logo](./project_logo.png)

## Overview

- Cache configuration, cache locations, and the distinction between the cache and `.venv`.
- Downloaded wheels, source-built wheels, unpacked source distributions, and centralized project environments.
- Local package build cache keys and a deterministic synthetic data fixture.
- Offline synchronization and `clone`, `copy`, `hardlink`, and `symlink` installation modes.
- Comparing `uv cache prune`, `uv cache prune --ci`, and `uv cache clean`.
- Inspecting cache entries created by different `uv` versions and their cleanup behavior.

## Documentation

- [Chapter 03, Section 03: Dependency Caching with uv](../../docs/chapter-03/section-03.md)
- [Chapter 03, Section 04: Using uv's cache in CI](../../docs/chapter-03/section-04.md) and the [CI workflow](../../.github/workflows/uv-cache.yml).
- [Open the notebook](./uv_cache_lab.ipynb).

To run the lab, open `notebooks/uv_cache_lab` in VS Code with Docker and the Dev Containers extension, then select **Dev Containers: Reopen in Container**. Open the notebook, select **Python 3 - uv Cache Lab**, and run the cells in order; the first installs require network access. The container supplies `uv` 0.13.3, Python 3.12, and Jupyter, and the notebook populates its container-local cache. Generated environments, fixture data, and reports are stored in the mounted lab folder; the main environment uses copy mode so it remains usable after cache cleanup.
