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

## Try the Cache in GitHub Actions

The [uv cache demo project](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/proj5_uv_cache/README.md) declares
heavy CPU-based ML dependencies (`tensorflow-cpu`, `transformers`, and
`scikit-learn`) in its own `pyproject.toml` and commits a `uv.lock`. The
[manual workflow](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/.github/workflows/uv-cache.yml) uses
`astral-sh/setup-uv` to restore and save uv's cache between runs. Each run
creates a **new** `.venv` and installs from the lockfile with `uv sync --locked`.
No GPU or model download is needed.

After the workflow has been pushed to the repository's default branch:

1. Open **Actions → uv cache demo (ML dependencies) → Run workflow**, choose
   the same branch for both runs, leave **Prune cache** and **Clean cache**
   unchecked, and start the first run.
2. Wait until it finishes successfully (the cache is saved at the end of the
   job), then run it again without changing `pyproject.toml` or `uv.lock`.
3. Compare **Cache restored before optional clearing** and **uv sync duration**
   in each run's summary.
   The first run normally reports `false`; the second should report `true`
   and can install the already-downloaded packages more quickly.

You can also start a run from the command line with
`gh workflow run uv-cache.yml --ref main` (replace `main` if using another
branch). The reported duration measures `uv sync`, **excluding** time spent
transferring the GitHub Actions cache. Compare the whole job duration in the
Actions UI as well: transferring large ML wheels can offset installation
savings. Cache entries are scoped to the repository and branch according to
GitHub Actions' cache rules, and changing the dependency files creates a new
cache key.

The optional **Prune cache** checkbox removes downloaded wheels *before saving*
a new cache, but does not affect installation on the current run. The separate
**Clean cache** checkbox runs `uv cache clean` *after restoration but before
installation*, giving that run a cold install. Neither checkbox deletes an
existing GitHub Actions cache entry, which cannot be overwritten under the
same key. Leave both unchecked when comparing cached installation times.

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
