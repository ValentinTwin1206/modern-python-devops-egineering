# Modern Python Workflows with uv

## Introduction

Chapter 03 introduces `uv`, Astral's Rust-based Python project and package manager, first released in 2024. Its project configuration centers on `pyproject.toml`, which records project metadata and dependencies, while its lockfile supports reproducible installs. The chapter covers scaffolding workspaces, building and publishing packages, managing and caching dependencies, using the cache in CI, and workflows for standalone scripts, environments, and command-line tools with `uvx` or `uv pip`.

## Overview

Use the navigation on the left to move through the chapter's sections:

| Section | Summary | Project | Notebook |
|---------|---------|---------|-----------|
| [Section 01](./section-01.md) | Project scaffolding with uv | - | [A New Hope for Bob](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/notebooks/nb3_uv_proj_scaffolding_lab/uv_proj_scaffolding_lab.ipynb) |
| [Section 02](./section-02.md) | Dependency management with uv | - | [Bob Discovers the Force of uv](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/notebooks/nb4_uv_dependency_lab/uv_dependency_lab.ipynb) |
| [Section 03](./section-03.md) | Dependency caching with uv | [uv-cache-demo](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/notebooks/nb5_uv_cache_lab/pyproject.toml) | [Bob Follows the Cache](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/notebooks/nb5_uv_cache_lab/uv_cache_lab.ipynb) |
| [Section 04](./section-04.md) | Using uv's cache in CI | [uv-cache.yml](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/.github/workflows/uv-cache.yml) | - |
| [Bonus 05](./bonus-05.md) | Additional uv workflows: Docker builds, scripts, and tools | - | [Return of the Admin: Bob Brings Balance to uv](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/notebooks/nb6_uv_extra_features/uv_extra_features.ipynb) |
