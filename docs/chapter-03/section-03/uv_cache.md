# Dependency Caching with uv

`uv` caches package metadata, downloaded wheels, and wheels built from source. A project environment (`.venv`) is normally beside `pyproject.toml`; it is **not** the package cache. The [Bob Follows the Cache notebook](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/notebooks/uv_cache_lab/uv_cache_lab.ipynb) runs the same experiments as this section. Run the commands below from `/workspace` in the [lab's Dev Container](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/notebooks/uv_cache_lab/README.md), in order. A first run needs network access.

## Applied Lab

The lab locks NumPy, SciPy, and Matplotlib and builds a local `uv-cache-demo` wheel containing a generated 16 MiB synthetic matrix. Its fixture is deterministic and not a trained model. Downloaded numerical-library wheels make cache growth visible; the locally built wheel makes CI pruning visible. The container supplies `uv` 0.13.3 (for the centralized-environment preview), Python 3.12, and Jupyter, but does not install the project or populate its `uv` cache at startup. The separate CI workflow pins `uv` 0.11.1. The lab's `UV_LINK_MODE=copy` keeps installed files independent of the cache. The container's cache is separate from your host's.

## Building Blocks

### Environment Variables That Influence Cache Behavior

These variables configure where `uv` caches data, whether it can reuse it, and how it installs files from the cache. See the [`uv` environment variable reference](https://docs.astral.sh/uv/reference/environment/) for the complete list.

| Variable | Cache behavior |
| --- | --- |
| `UV_CACHE_DIR` | Selects the shared cache directory instead of the system default; equivalent to `--cache-dir`. |
| `UV_NO_CACHE` | Uses a temporary cache for that invocation rather than the persistent cache; equivalent to `--no-cache`. |
| `UV_OFFLINE` | Disables network access, requiring cached or local packages; equivalent to `--offline`. |
| `UV_LINK_MODE` | Chooses `clone` (copy-on-write when supported), `hardlink` (shared files on one filesystem), `copy` (independent files), or `symlink` (depends on the cache). Defaults to `clone` on Linux/macOS and `hardlink` on Windows. |
| `UV_LOCK_TIMEOUT` | Sets how long `uv` waits for a cache lock, including when other `uv` processes are using the cache. |
| `UV_CONCURRENT_CACHE_READS` | Controls threads reading cached HTTP responses; defaults to `4`. |

### Commands That Populate the Cache

Package operations populate or reuse cache entries; cleanup commands remove them. For project locking and syncing, see [Dependency Management with `uv`](../section-02.md).

| Command | Effect on the cache |
| --- | --- |
| `uv pip install {pkg}` | Reuses or adds package metadata and wheels. `--refresh` revalidates cached data; `--refresh-package {pkg}` limits that to one package. |
| `uv add {pkg}` | Adds a dependency, resolves and synchronizes the project, and reuses or adds cached packages. |
| `uv sync` | Synchronizes a project from its lockfile, using or adding cached packages. |
| `uv tool install {tool}` | Installs a tool in its own environment while sharing `uv`'s package cache. |
| `uv cache prune` | Removes unused entries and centralized project environments. With `--ci`, also removes prebuilt wheels and unzipped source distributions while retaining source-built wheels. |
| `uv cache clean [package]` | Removes all cache entries, or entries for only the named package. |

### Build Configuration and Wheel Reuse

For a local package, `tool.uv.cache-keys` in `pyproject.toml` defines which build inputs invalidate a cached wheel. Keys replace `uv`'s default checks: include every input that affects the build. A key containing only `pyproject.toml`, for example, may miss source-only changes. These configurations illustrate three ways to track inputs:

=== "Files"

    Track the manifest and an additional dependency file used by the build.

    ```toml
    [tool.uv]
    cache-keys = [{ file = "pyproject.toml" }, { file = "requirements.txt" }]
    ```

=== "Git Commit"

    Track the manifest and Git commit when the build depends on version control; add `tags = true` if tags affect it too. A commit key alone will not detect uncommitted source edits.

    ```toml
    [tool.uv]
    cache-keys = [{ file = "pyproject.toml" }, { git = { commit = true } }]
    ```

=== "Environment Variable"

    Track the manifest and a build-setting variable, whose changed value forces a rebuild.

    ```toml
    [tool.uv]
    cache-keys = [{ file = "pyproject.toml" }, { env = "MY_BUILD_SETTING" }]
    ```

!!! info "The lab's content fingerprint"

    This lab uses `cache-keys = [{ env = "CACHE_DEMO_KEY" }]`. After generating the fixture, `scripts/build_key.py` hashes `pyproject.toml`, Python source, JSON, and bundled data. Supply its result to every sync that installs the local package. Identical content can reuse a wheel across fresh CI checkouts even when file timestamps differ. `--no-editable` installs that wheel instead of linking the source tree.

## Populate and Inspect the Cache

`uv` organizes cached data into distinct target types. These include *Prebuilt Wheels* downloaded from package indexes, *Source-built Wheels* built locally, and *Unpacked Source Distributions* used during builds. When enabled, *Centralized Project Environments* are also cached so a project can reuse its installed packages.

=== "Downloaded wheels"

    *Prebuilt Wheels* are downloaded from package indexes and can be installed without building the package from source. `uv` caches them so later installs can reuse them instead of downloading them again.

    Create an ignored directory for the disposable experiments in later tabs.

    ```bash
    mkdir -p lab
    ```

    Create the project environment for the following experiments.

    ```bash
    uv venv --python 3.12
    ```

    Install a small numerical-computing stack directly with `uv pip install`. `--only-binary :all:` selects prebuilt wheels when available.

    ```bash
    uv pip install \
      --python .venv/bin/python \
      --only-binary :all: \
      numpy \
      scipy \
      matplotlib
    ```

    Measure the populated cache; `cache-size` is a preview feature in this `uv` version.

    ```bash
    uv cache size --human --preview-features cache-size
    ```

=== "Locally built wheel"

    *Source-built Wheels* are built locally from source packages and stored in the cache. Reusing a cached wheel avoids repeating the build when its inputs have not changed.

    Generate the deterministic 16 MiB fixture before building the local package.

    ```bash
    .venv/bin/python scripts/generate_fixture.py
    ```

    Install the project as a regular wheel; the content fingerprint determines when `uv` rebuilds it.

    ```bash
    CACHE_DEMO_KEY=$(.venv/bin/python scripts/build_key.py) \
    uv sync \
      --locked \
      --no-editable \
      --python 3.12
    ```

    Run the installed package and write a PNG report.

    ```bash
    .venv/bin/python -m uv_cache_demo.main --output reports/embeddings.png
    ```

    Locate the locally built wheel; its path is the checkpoint for later pruning.

    ```bash
    find "$(uv cache dir)" -type f -name 'uv_cache_demo-*.whl' -print
    ```

=== "Unzipped source distribution"

    *Unpacked Source Distributions* are extracted source trees that `uv` uses to build wheels. `uv` can cache both the unpacked source and the wheel produced from it.

    Force a source build of small `idna` into an ignored target, without changing the project's lockfile.

    ```bash
    uv pip install \
      --python "$(uv python find 3.12)" \
      --target lab/sdist-target \
      --no-deps \
      --no-binary idna \
      'idna==3.10'
    ```

    Inspect source-cache buckets; their version suffixes are internal details and may change.

    ```bash
    find "$(uv cache dir)" -type d -name 'sdists-v*' -print
    ```

    Locate `uv`'s unpacked `idna` source (`src/idna`) while it is still present.

    ```bash
    find "$(uv cache dir)" -type d -path '*/sdists-v*/pypi/idna/3.10/*/src/idna' -print
    ```

    Find the `idna` wheel built from that source, distinct from the downloaded numerical-library wheels.

    ```bash
    find "$(uv cache dir)" -type f -name 'idna-*.whl' -print
    ```

=== "Centralized project environment"

    *Centralized Project Environments* store a project's installed packages in `uv`'s cache instead of beside `pyproject.toml`. The opt-in `centralized-project-envs` preview feature connects `.venv` to the cached environment, usually with a link.

    Create an ignored, disposable project to keep the main `.venv` separate.

    ```bash
    mkdir -p lab/centralized
    ```

    Copy the locked project declarations into that directory; the project itself will not be installed there.

    ```bash
    cp pyproject.toml uv.lock lab/centralized/
    ```

    Populate the cached environment without specifying `UV_PROJECT_ENVIRONMENT` or `--active`: explicit environment paths bypass centralization.

    ```bash
    uv --preview-features centralized-project-envs sync \
      --directory lab/centralized \
      --locked \
      --no-install-project \
      --python 3.12
    ```

    Inspect the `.venv` link pointing into `uv`'s cache (`uv` may use a path file if linking is unavailable).

    ```bash
    ls -ld lab/centralized/.venv
    ```

    Check that dependencies import from the new environment rather than the main project's `.venv`.

    ```bash
    lab/centralized/.venv/bin/python -c 'import numpy; print(numpy.__version__)'
    ```

=== "Other Unused Cache Entries"

    *Other Unused Cache Entries* are classified by cache metadata and references, not installation status. An older `uv` may create cache entries in a format a newer version does not recognize; those entries can be removed while the installed package remains in `.venv` or `--target`. Unreferenced unpacked wheel archives may also be considered unused, but a current-format wheel is not unused just because its package is uninstalled.
    
    Create a directory for the disposable package installs.

    ```bash
    mkdir -p lab/prune-probe
    ```

    Use `uv` 0.4.12 through `uvx` to install a prebuilt `packaging` wheel into an ignored target.

    ```bash
    UV_CACHE_DIR="$HOME/.cache/uvx-prune-bootstrap" \
      uvx --from 'uv==0.4.12' uv \
      --cache-dir "$(uv cache dir)" \
      pip install \
      --python "$(uv python find 3.12)" \
      --target lab/prune-probe/old-wheel \
      --reinstall \
      --no-deps \
      --only-binary packaging \
      'packaging==24.2'
    ```

    Use the same old `uv` version to build a wheel from the `idna` source distribution.

    ```bash
    UV_CACHE_DIR="$HOME/.cache/uvx-prune-bootstrap" \
      uvx --from 'uv==0.4.12' uv \
      --cache-dir "$(uv cache dir)" \
      pip install \
      --python "$(uv python find 3.12)" \
      --target lab/prune-probe/old-sdist \
      --reinstall \
      --no-deps \
      --no-binary idna \
      'idna==3.10'
    ```

    Inspect the cache buckets created by both the current and older `uv` versions; bucket names and versions are implementation details and may change.

    ```bash
    find "$(uv cache dir)" -mindepth 1 -maxdepth 1 -type d -printf '%f\n' | sort
    ```

## Reuse Cached Packages

### Offline Synchronization

Remove just the installed environment, leaving `uv`'s cache available.

```bash
rm -rf .venv
```

Restore it without network access; the fixture and build fingerprint are still available.

```bash
CACHE_DEMO_KEY=$("$(uv python find 3.12)" scripts/build_key.py) \
  uv sync \
  --locked \
  --no-editable \
  --offline \
  --python 3.12
```

Confirm that NumPy and the local wheel import from `.venv`.

```bash
.venv/bin/python -c 'import numpy, uv_cache_demo; print(numpy.__file__, uv_cache_demo.__file__)'
```

### Compare UV_LINK_MODE

Use four disposable environments to compare installation modes without changing the main `.venv`. Each tab synchronizes the locked dependencies into a separate environment; `--offline` ensures these trials reuse the cached wheels. On a bind-mounted workspace, `hardlink` or `clone` may fall back to copying if the cache and environment are on different filesystems.

=== "Clone"

    Sync into a disposable environment with `clone`, `uv`'s normal Linux/macOS mode. Where supported, the environment initially shares disk blocks with the cache, then gets separate blocks when files change. This can use less disk space than making full copies.

    ```bash
    UV_PROJECT_ENVIRONMENT=lab/clone \
      UV_LINK_MODE=clone \
      uv sync \
      --locked \
      --no-install-project \
      --offline \
      --python 3.12
    ```

    Inspect the installed file and its hard-link count; `stat` alone cannot prove whether copy-on-write cloning occurred.

    ```bash
    stat -c '%F; hard links: %h' lab/clone/lib/python3.12/site-packages/numpy/__init__.py
    ```

    Verify the installed NumPy version.

    ```bash
    lab/clone/bin/python -c 'import numpy; print(numpy.__version__)'
    ```

=== "Copy"

    Sync using `copy` to make independent files in the environment. This uses more disk space than shared-block modes, but changes to installed files do not change the cached files.

    ```bash
    UV_PROJECT_ENVIRONMENT=lab/copy \
      UV_LINK_MODE=copy \
      uv sync \
      --locked \
      --no-install-project \
      --offline \
      --python 3.12
    ```

    Inspect the installed file's type and link count.

    ```bash
    stat -c '%F; hard links: %h' lab/copy/lib/python3.12/site-packages/numpy/__init__.py
    ```

=== "Hardlink"

    Use `hardlink` to let the environment and cache share the same file on one filesystem, which saves disk space. Editing a hardlinked file also changes the cached file. If they are on different filesystems, `uv` falls back to making a copy.

    ```bash
    UV_PROJECT_ENVIRONMENT=lab/hardlink \
      UV_LINK_MODE=hardlink \
      uv sync \
      --locked \
      --no-install-project \
      --offline \
      --python 3.12
    ```

    Check whether the installed file has multiple hard links (`%h` greater than one).

    ```bash
    stat -c '%F; hard links: %h' lab/hardlink/lib/python3.12/site-packages/numpy/__init__.py
    ```

=== "Symlink"

    Use `symlink` to make the environment's files point to files in the cache, avoiding separate copies. The environment depends on those cache paths, so cleaning or moving the cache can break it.

    ```bash
    UV_PROJECT_ENVIRONMENT=lab/symlink \
      UV_LINK_MODE=symlink \
      uv sync \
      --locked \
      --no-install-project \
      --offline \
      --python 3.12
    ```

    Inspect a link target to see why cleaning the cache would break this installation.

    ```bash
    readlink lab/symlink/lib/python3.12/site-packages/numpy/__init__.py
    ```

    Remove this disposable environment before the cleanup stages; retain the copy-mode `.venv`.

    ```bash
    rm -rf lab/symlink
    ```

## Cache Cleanup Operations

`uv` provides different *Cleanup Operations*, each with its own rules for deciding what to remove from the cache. Depending on the command, cleanup may affect *Prebuilt Wheels*, *Source-built Wheels*, *Unpacked Source Distributions*, and *Centralized Project Environments*, as well as other *Unused Cache Entries*. The disk space reclaimed by each operation depends on the cache contents and artifact sizes, so a broader cleanup does not necessarily reclaim more space in a particular run.

=== "Normal prune"

    The `uv cache prune` command performs the standard cleanup by removing *Unused Cache Entries* and all *Centralized Project Environments*. Unused entries may include *Prebuilt Wheels*, *Unpacked Source Distributions*, and *Source-built Wheels*. It retains entries that `uv` still considers in use, unlike `uv cache clean`, which removes every cache entry. Run the ordinary prune command:

    ```bash
    uv cache prune
    ```

    Confirm that the obsolete cache buckets created by `uv` 0.4.12 are gone. They contained the old `packaging` wheel and old `idna` built wheel.

    ```bash
    find "$(uv cache dir)" -maxdepth 1 -type d \
      \( -name 'wheels-v1' -o -name 'built-wheels-v3' \) \
      -print
    ```

    Confirm that the current prebuilt wheel entries for NumPy, SciPy, and Matplotlib remain.

    ```bash
    find "$(uv cache dir)" -type d \
      \( -path '*/wheels-v*/pypi/numpy' \
        -o -path '*/wheels-v*/pypi/scipy' \
        -o -path '*/wheels-v*/pypi/matplotlib' \) \
      -print
    ```

    Confirm that the current-format wheels built from the local project and `idna` source remain.

    ```bash
    find "$(uv cache dir)" -type f \
      \( -name 'uv_cache_demo-*.whl' -o -name 'idna-*.whl' \) \
      -print
    ```

    Confirm that the unpacked `idna` source remains after ordinary pruning.

    ```bash
    find "$(uv cache dir)" -type d \
      -path '*/sdists-v*/pypi/idna/3.10/*/src/idna' \
      -print
    ```

    Confirm that pruning has not removed the packages installed into `--target`.

    ```bash
    test -d lab/prune-probe/old-wheel/packaging
    test -d lab/prune-probe/old-sdist/idna
    ```

    Confirm the main, non-centralized `.venv` remains usable.

    ```bash
    .venv/bin/python -c 'import numpy; print(numpy.__version__)'
    ```

    Measure the cache size after pruning.

    ```bash
    uv cache size --human --preview-features cache-size
    ```

=== "CI prune"

    The `uv cache prune --ci` command is designed for CI environments. To support this strategy, it retains *current-format Source-built Wheels*, which can take significant time and computing resources to build and can save time in later CI runs. It removes *Prebuilt Wheels* and *Unpacked Source Distributions* to reduce cache size as those are generally quick to download again. The command also performs ordinary pruning, so it can remove obsolete source-built wheels. Run the CI-specific prune command:

    ```bash
    uv cache prune --ci
    ```

    Confirm that the obsolete cache buckets created by `uv` 0.4.12 are gone. They contained the old `packaging` wheel and old `idna` built wheel.

    ```bash
    find "$(uv cache dir)" -maxdepth 1 -type d \
      \( -name 'wheels-v1' -o -name 'built-wheels-v3' \) \
      -print
    ```

    Confirm that the prebuilt wheel entries for NumPy, SciPy, and Matplotlib are gone (no output expected).

    ```bash
    find "$(uv cache dir)" -type d \
      \( -path '*/wheels-v*/pypi/numpy' \
        -o -path '*/wheels-v*/pypi/scipy' \
        -o -path '*/wheels-v*/pypi/matplotlib' \) \
      -print
    ```

    Confirm that the current-format wheels built from the local project and `idna` source remain.

    ```bash
    find "$(uv cache dir)" -type f \
      \( -name 'uv_cache_demo-*.whl' -o -name 'idna-*.whl' \) \
      -print
    ```

    Check that the unzipped `idna` source is gone (no output expected).

    ```bash
    find "$(uv cache dir)" -type d -path '*/sdists-v*/pypi/idna/3.10/*/src/idna' -print
    ```

    Verify the saved centralized environment target is gone; its `.venv` link may be dangling.

    ```bash
    test ! -d "$(cat lab/centralized-target)"
    ```

    Confirm that pruning has not removed the packages installed into `--target`.

    ```bash
    test -d lab/prune-probe/old-wheel/packaging
    test -d lab/prune-probe/old-sdist/idna
    ```

    Measure the cache size after pruning.

    ```bash
    uv cache size --human --preview-features cache-size
    ```

    Confirm that installed packages in the main copy-mode `.venv` still import.

    ```bash
    .venv/bin/python -c 'import numpy; from uv_cache_demo.main import cache_message; print(cache_message())'
    ```

=== "Complete Clean"

    The `uv cache clean` command removes *All Cache Entries*, including *Prebuilt Wheels*, *Unpacked Source Distributions*, *Source-built Wheels*, and *Centralized Project Environments*. Since every cache target is in scope, this is the most aggressive cleanup command. Run the complete cleanup:

    ```bash
    uv cache clean
    ```

    Confirm that the old cache buckets are gone (no output expected).

    ```bash
    find "$(uv cache dir)" -maxdepth 1 -type d \
      \( -name 'wheels-v1' -o -name 'built-wheels-v3' \) \
      -print
    ```

    Confirm that the NumPy, SciPy, and Matplotlib prebuilt wheel entries are gone (no output expected).

    ```bash
    find "$(uv cache dir)" -type d \
      \( -path '*/wheels-v*/pypi/numpy' \
        -o -path '*/wheels-v*/pypi/scipy' \
        -o -path '*/wheels-v*/pypi/matplotlib' \) \
      -print
    ```

    Measure the emptied cache; `uv` may retain housekeeping files.

    ```bash
    uv cache size --human --preview-features cache-size
    ```

    Verify that the local and `idna` source-built wheels are no longer cached (no output expected).

    ```bash
    find "$(uv cache dir)" -type f \
      \( -name 'uv_cache_demo-*.whl' -o -name 'idna-*.whl' \) \
      -print
    ```

    Verify that the unpacked `idna` source is no longer cached (no output expected).

    ```bash
    find "$(uv cache dir)" -type d \
      -path '*/sdists-v*/pypi/idna/3.10/*/src/idna' \
      -print
    ```

    Verify that the centralized environment target is gone (no output expected).

    ```bash
    test ! -d "$(cat lab/centralized-target)"
    ```

    Confirm that cleanup has not removed the packages installed into `--target`.

    ```bash
    test -d lab/prune-probe/old-wheel/packaging
    test -d lab/prune-probe/old-sdist/idna
    ```

    Confirm installed copies still work. A symlink-mode environment would instead depend on the removed cache paths.

    ```bash
    .venv/bin/python -c 'import numpy; from uv_cache_demo.main import cache_message; print(cache_message())'
    ```

    Check that the previously generated report also remains in the workspace.

    ```bash
    test -f reports/embeddings.png
    ```

The table compares five deliberately populated cache targets after each operation runs with `uv` 0.13.3. A check mark means the target was removed; a dash means it was retained. The obsolete-format entries were created with `uv` 0.4.12. Ordinary pruning can also remove orphaned current-format archives that are no longer referenced by current wheel or source buckets. `uv cache clean` removes other cache entries, such as metadata and index responses; in this probe, the cache root and lock file remain.

| Target | `uv cache prune` | `uv cache prune --ci` | `uv cache clean` |
| --- | :---: | :---: | :---: |
| Current-format prebuilt/downloaded wheel (`wheels-v7`) | — | ✓ | ✓ |
| Current-format source-built wheel (`sdists-v10`, `.whl`) | — | — | ✓ |
| Unpacked source distribution (`sdists-v10`, `src/`) | — | ✓ | ✓ |
| Centralized project environment (`environments-v2`) | ✓ | ✓ | ✓ |
| Obsolete-format entries from uv 0.4.12 (`wheels-v1`, `built-wheels-v3`, including its built wheel and sdist) | ✓ | ✓ | ✓ |
