# Dependency Caching with uv — Bob Follows the Cache

After learning to scaffold projects and manage their dependencies with `uv`, Bob turns his attention to the cache. Still determined to show that the old administrator has something to contribute, he wants to know which downloads and builds can be reused and what happens when the cache is cleaned. He sets up a small numerical project and follows its artifacts through installation, offline reuse, and cleanup. Each experiment brings another useful answer to his growing runbook.

![uv Cache Lab project logo](./project_logo.png)

## Learning Objectives

- Identify cached artifacts and distinguish the package cache from project environments.
- Configure cache behavior and local build cache keys, and reuse artifacts offline.
- Compare installation link modes and the effects of pruning and cleaning the cache.

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
- [Open the notebook](./uv_cache_lab.ipynb); follow [Bob Discovers the Force of uv](../uv_dependency_lab/uv_dependency_lab.ipynb).

## Run The Lab

1. Install Docker, VS Code, and the VS Code Dev Containers extension.
2. Open `notebooks/uv_cache_lab` as the folder in VS Code and select **Dev Containers: Reopen in Container**.
3. Open `uv_cache_lab.ipynb`, select the **Python 3 - uv Cache Lab** kernel, and run the cells in order.

The container supplies `uv` 0.13.3, Python 3.12, and Jupyter. Initial downloads require network access. The setup cell resets `lab/`, `.venv`, `reports/`, and the generated `src/uv_cache_demo/data/embeddings.bin`, and clears the container-local uv package cache; keep unrelated work elsewhere. Generated files live in the mounted lab folder, while the main environment uses copy mode so it remains usable after cache cleanup.
