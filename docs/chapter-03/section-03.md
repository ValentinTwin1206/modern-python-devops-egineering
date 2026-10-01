# Dependency Caching with uv

## Introduction

`uv` caches downloads and built packages so later installs can reuse them. This speeds up repeated work across projects. For the dependency commands themselves, see [Dependency Management with uv](./section-02.md).

## Compare Installation Methods

### Install the Same Package

Each tab installs `click` in a different way. The uv examples share the same cache, but only the project workflow tracks dependencies in `pyproject.toml` and `uv.lock`.

=== "pip"

    Install with the traditional package manager in an existing environment:

    ```shell
    pip install click
    ```

    `pip` maintains its own download cache, separate from uv's cache.

=== "uv pip install"

    Install directly into an existing virtual environment:

    ```shell
    uv pip install click
    ```

    `uv` caches downloaded packages, but this command does not update project metadata.

=== "uv sync"

    In a project that declares `click` as a dependency, install what its lockfile specifies:

    ```shell
    uv sync
    ```

    `uv` can reuse cached packages while keeping the project environment in sync.

### Summary

The cache stores reusable package files; `.venv` holds the packages available to a particular project. A cache is a speed-up, not a replacement for [the lockfile](./section-02.md#the-lockfile), which records the resolved versions.

## Explore the Cache

### Cache Organization

By default, uv's cache lives at `~/.cache/uv` on Linux. It separates package-index data, downloaded wheels, built packages, and unpacked files into directories. Their names and versions are implementation details that may change as uv evolves.

### Different Package Sources

`uv` can cache packages from an index such as PyPI, a Git repository, or a direct URL. These sources have different cache entries, but you can work with them through the same project commands. See [Declaring Dependencies](./section-02.md#declaring-dependencies) for the project workflow.

## Handle uv Upgrades

### Cache Versioning

An upgrade may change the cache format. In that case uv downloads or builds the needed files again; your project requirements and lockfile remain the source of truth. You do not need to manage cache directory names yourself.

## Maintain the Cache

### Clean and Prune

If you need to free space, remove unused cache entries:

```shell
uv cache prune
```

To clear the entire uv cache instead, use:

```shell
uv cache clean
```

After cleaning, the next installation may need to download or build packages again.
