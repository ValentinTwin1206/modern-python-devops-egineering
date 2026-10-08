# Dependency Caching with uv

The cache is one of `uv`'s key features and a major contributor to its speed: it reuses package metadata, downloads, and built packages instead of fetching or building them again. This chapter explores how the cache is organized and how to create, reuse, and clean it during local development and in continuous integration (CI) environments.

## Applied Project

The [uv cache demo](https://github.com/ValentinTwin1206/modern-python-devops-egineering/tree/main/projects/proj5_uv_cache) project hosts a `Dockerfile.devEnv` to provide a Jenkins environment with `uv` and Python 3.12 for local exploration and Continuous Integration (CI) builds. The Groovy script in `Jenkinsfile` defines a simple pipeline that recreates `.venv` from `uv.lock`, reuses cached dependencies, and checks package imports. Running it twice demonstrates cache reuse between builds.

## Building Blocks

### Environment Variables That Influence Cache Behavior

The following environment variables configure where `uv` stores cache data, how it uses that data, or how it installs cached files. See the [uv environment variable reference](https://docs.astral.sh/uv/reference/environment/) for the full list.

| Variable | Cache behavior |
| --- | --- |
| `UV_CACHE_DIR` | Sets the cache directory, equivalent to `--cache-dir`. It takes precedence over the default location. |
| `XDG_CACHE_HOME` | Changes the default cache base directory on Unix-like systems; unless `UV_CACHE_DIR` is set, the cache defaults to `$XDG_CACHE_HOME/uv` (or `$HOME/.cache/uv` when unset). |
| `UV_NO_CACHE` | Disables reading and writing the persistent cache, equivalent to `--no-cache`. `uv` uses a temporary cache for that invocation. |
| `UV_OFFLINE` | Disables network access, so `uv` must rely on cached data and locally available files, equivalent to `--offline`. |
| `UV_LINK_MODE` | Chooses how `uv` installs files from its cache into an environment (for example, by copying or hard-linking). |
| `UV_LOCK_TIMEOUT` | Sets how long `uv` waits to acquire a file lock, including when cache operations are blocked by other `uv` processes. |
| `UV_CONCURRENT_CACHE_READS` | Controls the number of threads used to read cached HTTP responses. |

### Commands That Influence the Cache

Install and project commands populate or reuse the cache; `uv cache` commands inspect or remove its contents. `uv add` also changes project files. See [*Dependency Management with uv*](./section-02.md) for details on locking and syncing dependencies, and the [uv caching guide](https://docs.astral.sh/uv/concepts/cache/) for cache semantics.

| Command | Effect on the cache |
| --- | --- |
| `uv pip install {pkg}` | Installs a package, reusing cached metadata and artifacts and adding newly downloaded or built data to the cache. |
| `uv add {pkg}` | Adds a dependency, resolves and synchronizes the project, and reuses or adds package data in the cache. Also updates `pyproject.toml` and `uv.lock`. |
| `uv sync` | Synchronizes the project environment and reuses or adds cached package data. |
| `uv tool install {tool}` | Installs a tool in its own environment while sharing `uv`'s package cache. |
| `uv cache dir` | Prints the active cache directory. |
| `uv cache size --human` | Reports the cache's total size in human-readable units such as GiB. The command is experimental in current uv releases. |
| `uv cache prune` | Removes unused cache entries and centralized project environments while retaining entries still in use. |
| `uv cache prune --ci` | Removes downloaded wheels and unpacked source distributions while retaining wheels built from source, a strategy intended for CI cache persistence. |
| `uv cache clean [package]` | Removes all cache entries, or only entries for the named package. |
| `uv sync --refresh` / `uv pip install --refresh` | Forces cached data to be revalidated and updates it for subsequent operations. `--refresh-package {pkg}` limits this to one package. |

## Using uv Cache for Local Development

For day-to-day development, `uv` manages the cache automatically, and your project's `.venv` usually stays in place between sessions. Understanding the cache is useful when recreating environments, working offline, or freeing disk space, but managing it is less critical than in CI/CD, where environments are often rebuilt for every run. The following workflow lets you explore cache reuse and cleanup locally.

From the repository's `projects/` directory, the following command builds the image from `Dockerfile.devEnv` and launches a `bash` session inside the container:

```bash
./build.sh build \
    --path proj5_uv_cache/Dockerfile.devEnv \
    --rm-container
```

!!! warning "The project is bind-mounted"
    Changes to `/app` also change `projects/proj5_uv_cache` on your host. The following steps recreate `.venv`; do not use that environment in another session while following them. The container's package cache is disposable and is not the named volume used by the Jenkins example.

### Inspect and Reuse the Cache

#### Create and Inspect the Cache

The `uv sync` command creates `.venv` if it does not exist and installs the project's dependencies there. In the background, `uv` maintains its package cache and updates `uv.lock` when needed:

```bash
uv sync
```

Inspect the populated cache, including hidden housekeeping files; `uv cache dir` supplies the active cache path:

```bash
tree -a -L 1 --noreport "$(uv cache dir)"
```

You should see an output similiar to the following:

```text
/var/jenkins_home/.cache/uv
├── .gitignore
├── .lock
├── CACHEDIR.TAG
├── archive-v0
├── interpreter-v4
├── sdists-v9
└── wheels-v6
```

> The layout was observed with `uv` 0.11.1

Each entry stores reusable package data or helps `uv` manage the cache safely:

| Entry | Purpose |
| --- | --- |
| `archive-v0` | Stores unpacked package files that `uv` copies or links into an environment. Reusing these files avoids downloading and unpacking the same package again. |
| `wheels-v6` | Stores records for `.whl`s (ready-to-install packages), including download metadata and links to unpacked files. These records help `uv` locate cached packages for installation. |
| `interpreter-v4` | Stores information about Python interpreters, such as their versions and supported platforms. `uv` can reuse this information instead of inspecting the same interpreter repeatedly. |
| `sdists-v9` | Stores cached source distributions and build results for packages that need to be built into wheels. The directory can exist even when all installed packages came from ready-made wheels. |
| `.gitignore`, `.lock`, `CACHEDIR.TAG` | `.gitignore` keeps cache contents out of Git, `.lock` coordinates cache access, and `CACHEDIR.TAG` marks the directory as disposable cache data. `uv` manages these files; they are not dependency declarations or settings to edit. |

Further inspect the wheel record of `scikit-learn` package:

```bash
tree -L 1 --noreport "$(uv cache dir)/wheels-v6/pypi/scikit-learn"
```

The dedicated cache folder for `scikit-learn` contains the structure shown below. The first entry marks a symbolic link (`->`) to the unpacked files in `archive-v0`, and the `.http` file stores download-cache metadata managed by `uv`, not project settings. Other workflows may also create package-index metadata in `simple-v20`.

```text
/var/jenkins_home/.cache/uv/wheels-v6/pypi/scikit-learn
├── <version>-<python-tag>-<abi-tag>-<platform-tag> -> /var/jenkins_home/.cache/uv/archive-v0/<archive-id>
└── <version>-<python-tag>-<abi-tag>-<platform-tag>.http
```

> See [Package Layout in Chapter 2, Section 1](../chapter-02/section-01.md#package-layout) to undertand wheel filename tags.

Check the cache size with `uv cache size --human`:

```bash
uv cache size --human
```

In this run, the cache size was about 1.6 GiB:

```text
1.6GiB
```

#### Reuse the Cache

To demonstrate cache reuse, remove the `.venv` first. Thus, `uv` must recreate the environment from `uv.lock` instead of using packages already installed there. Removing it deletes the environment's installed packages, scripts, and metadata; it does not delete the separate `uv` cache. In this demo, `UV_LINK_MODE=copy` makes `uv` copy package files from its cache into `.venv`, so reusable cache data and the active environment reside in two locations. The `--offline` flag prevents downloads, requiring the sync to use the local cache:

```bash
rm -r .venv && uv sync --offline
```

A successful run installs the ML dependencies from the local cache without downloading them. Verify that `scikit-learn` imports from `.venv`, not the cache:

```bash
.venv/bin/python -c "import sklearn; print(sklearn.__file__)"
```

### Manage uv Cache

#### Prune Cache

The `uv cache prune` command frees disk space by removing cache data the current `uv` can no longer use, such as entries in obsolete formats and unpacked files no cache record refers to. It keeps valid cached packages and does not uninstall packages from project environments.

To demonstrate `uv cache prune`, use `uvx` to run `uv` 0.4.12 in an isolated environment and create cache entries in a retired format, that is no longer supported. Create a temporary installation directory outside the project:

```bash
prune_demo=$(mktemp -d)
```

Install `scipy` with the older `uv` release, skipping dependencies with `--no-deps`:

```bash
uvx --from uv==0.4.12 uv pip install --python "$(uv python find 3.12)" --no-deps --target "$prune_demo" "scipy==1.15.3"
```

The older `uv` release created a `scipy` cache record under `wheels-v1` without changing the project dependencies. Use `find` to locate the record and see which cache format contains it:

```bash
find "$(uv cache dir)" -type d -path '*/wheels-v*/pypi/scipy' -print
```

Check the size again with `uv cache size --human`; in this run it grew from about 1.6 GiB to 1.8 GiB:

```text
1.8GiB
```

Remove the temporary installation; the old-format cache entries remain until they are pruned:

```bash
rm -r "$prune_demo"
```

Finally, validate that the `scipy` package get removed by running the following command:

```bash
uv cache prune
```

In this run, `uv` reported:

```text
Removed 1460 files (144.3MiB)
```

After pruning, `wheels-v1` was deleted, but the cache remained slightly larger than it was initially as `uvx` cached the `uv` 0.4.12 tool in the current `wheels-v6` format. `uv cache size --human` reported:

```text
1.7 GiB
```

#### Clean Cache

The `uv cache clean` command removes **all** entries from the cache, including valid wheels and unpacked package files. Packages already installed in project environments remain, but future installs that need those packages must download or build them again:

```bash
uv cache clean
```

Inspect the project files with `ls -lah`; `uv cache clean` leaves `.venv` and its installed packages untouched, along with `pyproject.toml` and `uv.lock`. It removes cached wheel data, not the package files already installed from those wheels. Verify that `scikit-learn` still works:

```bash
.venv/bin/python -c "import sklearn; print(sklearn.__file__)"
```

#### Cleanup Summary

**To remove installed packages while keeping cached data**, run `rm -r .venv`. This deletes the project's environment but leaves the shared cache available for a later `uv sync` to reuse.

**To free cache space while keeping reusable packages**, run `uv cache prune`. It removes obsolete and unreferenced cache data, keeps valid package entries, and leaves `.venv` unchanged.

**To remove both the project's installed packages and cached package data**, run `rm -r .venv` and `uv cache clean`. The latter clears the shared cache for all projects but does not delete their environments. A later `uv sync` must download or build the dependencies again; `--offline` cannot restore them from an empty cache.

## Using uv Cache in CI(/CD) Environments

In CI(/CD) workflows such as *GitHub Actions*, *GitLab pipelines*, or *Jenkins builds*, understanding and using the `uv` cache effectively is an essential (DevOps) skill. Reusing the cache avoids repeated downloads and builds, shortening pipelines, reducing network and compute usage, and giving your team faster feedback.

The caching strategy depends on your workflow and pipeline structure: feature-branch builds, release builds, and jobs using different Python versions or operating systems may need different cache keys and sharing rules. CI jobs often start with a fresh environment, so preserve the cache separately between runs. Reuse the cached package data, then create a new `.venv` from the committed lockfile on each run rather than caching the environment itself.

### Prune for CI

`uv cache prune --ci` removes downloaded prebuilt wheels and unpacked source distributions but retains wheels built from source. This reduces the cache transferred between jobs while keeping potentially expensive build results. Unlike normal pruning, it intentionally discards reusable downloaded wheels.

To measure the difference in the development container, first reinstall the locked dependencies from `/app`. `--reinstall` repopulates the cache even if `.venv` survived an earlier cleanup:

```bash
uv sync --locked --reinstall --python 3.12
```

Record the size with `uv cache size --human`, then apply the CI strategy:

```bash
uv cache prune --ci
```

Check the size again with `uv cache size --human` and inspect the remaining entries with `tree -a -L 1 --noreport "$(uv cache dir)"`. The installed environment still works, but an offline reinstall now fails if it needs a removed wheel.

The same locked ML packages produced this comparison with uv 0.11.1:

| Stage | Cache size |
| --- | --- |
| Before CI pruning | About 1.6 GiB |
| After `uv cache prune --ci` | 36 KiB |

Only a small amount of metadata remained; the downloaded package files were removed. Your result may differ by platform and package versions.

!!! info "Measure the whole job"
    A smaller cache is not automatically faster. This ML demo installs prebuilt wheels, so CI pruning leaves little package data to reuse and later jobs download the wheels again. Compare cache-transfer time and package-download time, not only installation time. See [uv's CI cache guidance](https://docs.astral.sh/uv/concepts/cache/#caching-in-continuous-integration).

### GitHub Actions

The [demo workflow](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/.github/workflows/uv-cache.yml) lets you compare full and CI-pruned caches. Its manual-run inputs are:

| Input | Default | Effect |
| --- | --- | --- |
| `prune_cache` | `true` | Runs `uv cache prune --ci` after installation and measures the change in disk usage. |
| `clean_cache` | `false` | Clears the restored local cache before installation to demonstrate a cold run. |

This setup step installs uv and restores its package cache. Dependency files and the selected strategy contribute to the cache key, so full and CI-pruned runs use separate cache entries:

```yaml
- name: Set up uv and restore its package cache
  uses: astral-sh/setup-uv@v5
  with:
    version: "0.11.1"
    enable-cache: true
    cache-dependency-glob: |
      projects/proj5_uv_cache/pyproject.toml
      projects/proj5_uv_cache/uv.lock
    cache-suffix: ${{ inputs.prune_cache && 'ml-demo-ci-pruned' || 'ml-demo-full' }}
    prune-cache: false
```

- `uses` selects the `setup-uv` action.
- `with` configures the action:
  - `version` pins uv to `0.11.1`.
  - `enable-cache` enables uv package-cache restoration and saving.
  - `cache-dependency-glob` lists files used to derive the cache key:
    - `pyproject.toml` declares the project's dependencies.
    - `uv.lock` records the resolved dependency versions.
  - `cache-suffix` separates the two cache strategies so their results do not mix.
  - `prune-cache: false` disables the action's automatic post-job pruning; the workflow runs and measures pruning explicitly instead.

Run this command from the repository root to create the project's `.venv` from the committed lockfile. `--locked` makes uv fail rather than update an out-of-date lockfile; the virtual environment is separate from the uv package cache.

```yaml
- name: Install ML packages into a fresh virtual environment
  shell: bash
  run: |
    uv sync --directory projects/proj5_uv_cache --locked --python 3.12
```

- `shell` selects Bash to run the step.
- `run` invokes `uv sync` with these options:
  - `--directory` points uv to the demo project.
  - `--locked` fails if the lockfile needs an update instead of changing it.
  - `--python` selects Python 3.12 for the environment.

After verifying the imports, the workflow records cache size, optionally runs `uv cache prune --ci`, and measures the remaining size. Its job summary reports those sizes in KiB, reclaimed space, the cache-restoration result, and the time spent in `uv sync`.

Run each strategy twice on the same branch without changing the dependency files, leaving `clean_cache` disabled. Full-cache runs can reinstall from restored wheels; CI-pruned runs download prebuilt wheels again. Compare **whole job times**, since downloading and uploading the CI cache also takes time.

!!! info "Cache hits and measurements"
    `setup-uv@v5` normally skips its pruning hook on exact cache-key hits. This workflow's explicit pruning step still runs when requested, but GitHub does not overwrite an existing exact-key cache entry. Reported sizes describe the local cache, not GitHub's compressed archive.

### Jenkins

Jenkins can keep uv's cache between builds by running on the same agent with `UV_CACHE_DIR` inside persistent storage. The [demo Dockerfile.devEnv](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/proj5_uv_cache/Dockerfile.devEnv) includes Jenkins, Python 3.12, uv, and the locked dependency files. It opens Bash by default; the [Jenkins setup](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/proj5_uv_cache/README.md#run-the-jenkins-demo-in-docker) explicitly starts Jenkins instead and mounts `/var/jenkins_home` as a persistent volume. The cache lives at `/var/jenkins_home/.cache/uv`, and both Bash and Jenkins run as `bob`. This single-node teaching example enables one executor on the controller.

Paste this pipeline into a Jenkins **Pipeline script** job (it is also available as [`Jenkinsfile`](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/proj5_uv_cache/Jenkinsfile)):

```groovy
pipeline {
    agent any
    options { disableConcurrentBuilds() }
    stages {
        stage('Install from lockfile') {
            steps {
                dir('/opt/uv-cache-demo') {
                    sh 'rm -rf .venv'
                    sh 'uv sync --locked --python 3.12'
                }
            }
        }
        stage('Verify dependencies') {
            steps {
                dir('/opt/uv-cache-demo') {
                    sh '.venv/bin/python -c "import tensorflow, transformers, sklearn; print(\'ML packages imported successfully\')"'
                }
            }
        }
    }
}
```

The pipeline removes only the project's `.venv` before each build, then installs the locked dependencies and checks imports. The uv cache remains in the persistent Jenkins volume, so running **Build Now** twice demonstrates reuse. Keeping the volume also preserves the cache if you recreate the Jenkins container; removing the volume starts over. Unlike GitHub Actions, this example reuses a local directory rather than downloading a cache artifact on every run.
