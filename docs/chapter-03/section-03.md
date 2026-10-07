# Dependency Caching with uv

The cache is one of `uv`'s key features and a major contributor to its speed: it reuses package metadata, downloads, and built packages instead of fetching or building them again. This chapter explores how the cache is organized and how to create, reuse, and clean it during local development and in continuous integration (CI) environments.

## Applied Project

The [uv cache demo](https://github.com/ValentinTwin1206/modern-python-devops-egineering/tree/main/projects/proj5_uv_cache) project hosts a `Dockerfile.devEnv` to provide a Jenkins environment with `uv` and Python 3.12 for local exploration and Continuous Integration (CI) builds. The Groovy script in `Jenkinsfile` defines a simple pipeline that recreates `.venv` from `uv.lock`, reuses cached dependencies, and checks package imports. Running it twice demonstrates cache reuse between builds.

## The Cache Workflow

From the repository's `projects/` directory, the following command builds the image from `Dockerfile.devEnv` and launches a `bash` session inside the container:

```bash
./build.sh build \
    --path proj5_uv_cache/Dockerfile.devEnv \
    --rm-container
```

!!! warning "The project is bind-mounted"
    Changes to `/app` also change `projects/proj5_uv_cache` on your host. The following steps recreate `.venv`; do not use that environment in another session while following them. The container's package cache is disposable and is not the named volume used by the Jenkins example.

### uv Commands That Use the Cache

The table shows which commands update `uv`'s cache. `uv add` changes project files. See [*Dependency Management with uv*](./section-02.md) for details on locking and syncing dependencies.

| Command | Update Cache | Summary |
| --- | --- | --- |
| `uv pip install {pkg}` | ✅  | Installs a `{pkg}` uses uv's cache without changing project files. |
| `uv add {pkg}` | ✅ | Adds a `{pkg}` to a project, updates `uv.lock` as well as `pyproject.toml`, and synchronizes the environment. |
| `uv sync` | ✅ | Synchronizes the project's environment and updates `uv.lock` when needed. |
| `uv tool install {tool}` | ✅ | Installs a `{tool}` in its own tool environment while sharing uv's package cache. |

### Install Project Dependencies

Install the project's dependencies into `.venv`. `uv` caches downloaded packages and updates `uv.lock` when needed:

```bash
uv sync
```

### Inspect the Cache

Inspect the populated cache, including hidden housekeeping files; `uv cache dir` supplies the active cache path:

```bash
tree -a -L 1 "$(uv cache dir)"
```

You should see an output similiar to the following:

```text
/var/jenkins_home/.cache/uv
|-- .gitignore
|-- .lock
|-- CACHEDIR.TAG
|-- archive-v0
|-- interpreter-v4
|-- sdists-v9
`-- wheels-v6
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

This output was observed in the container with Python 3.12 on x86-64 Linux. The `->` marks a symbolic link to `scikit-learn`'s unpacked files in `archive-v0`. The `.http` file stores download-cache metadata managed by `uv`, not project settings. Other workflows may also create package-index metadata in `simple-v20`.

```text
/var/jenkins_home/.cache/uv/wheels-v6/pypi/scikit-learn
|-- 1.9.1-cp312-cp312-manylinux_2_27_x86_64.manylinux_2_28_x86_64 -> /var/jenkins_home/.cache/uv/archive-v0/x784IyACviPb2rHI6P3OB
`-- 1.9.1-cp312-cp312-manylinux_2_27_x86_64.manylinux_2_28_x86_64.http
```

> Wheel tags vary with Python and platform; randomly generated archive IDs can differ between downloads.

Check the cache's disk usage with `du -sh "$(uv cache dir)"`; this run used about 1.6 GiB:

```text
1.6G    /var/jenkins_home/.cache/uv
```

### Reuse the Cache

To demonstrate cache reuse, remove the project's virtual environment and recreate it using the previously created `uv.lock` file and local cache:

```bash
rm -r .venv && uv sync --offline
```

> `--offline` disables downloads.

A successful run installs the ML dependencies from the local cache without downloading them. Verify that `scikit-learn` imports from `.venv`, not the cache:

```bash
.venv/bin/python -c "import sklearn; print(sklearn.__file__)"
```

### Compare Cache Cleanup

#### Create Obsolete Cache Entries

!!! info
    To demonstrate `uv cache prune`, first create obsolete cache entries by running `uv` 0.4.12 with `uvx`, which runs tools in isolated environments. This older release uses a cache format that the current `uv` no longer uses, giving the prune command artifacts to remove. `scipy`'s large unpacked files make the resulting disk-space reduction easier to see than a small package such as Click.

Create a temporary installation directory outside the project:

```bash
prune_demo=$(mktemp -d)
```

Install `scipy` with the older `uv` release, skipping dependencies with `--no-deps`:

```bash
uvx --from uv==0.4.12 uv pip install --python "$(uv python find 3.12)" --no-deps --target "$prune_demo" "scipy==1.15.3"
```

Inspect the cache entry for `scipy`:

```bash
tree -L 1 "$(uv cache dir)/wheels-v1/pypi/scipy"
```

The older `uv` release created `scipy`'s record in `wheels-v1` without changing the project dependencies. The arrow points to its unpacked files in `archive-v0`. This output was observed with Python 3.12 on x86-64 Linux; wheel tags depend on the interpreter and platform, while archive IDs can differ between fresh downloads.

```text
/var/jenkins_home/.cache/uv/wheels-v1/pypi/scipy
|-- scipy-1.15.3-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64 -> /var/jenkins_home/.cache/uv/archive-v0/0jVNiH_qYTwttuRGvgwjZ
`-- scipy-1.15.3-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.http

2 directories, 1 file
```

Check the size with `du -sh "$(uv cache dir)"`; this run grew from about 1.6 GiB to 1.8 GiB:

```text
1.8G    /var/jenkins_home/.cache/uv
```

Remove the temporary installation; the old-format cache entries remain until they are pruned:

```bash
rm -r "$prune_demo"
```

#### Prune Cache

Remove obsolete cache formats and unpacked files no longer referenced by cache records using the current `uv` release:

```bash
uv cache prune
```

In this run, `uv` reported:

```text
Removed 1460 files (144.3MiB)
```

Inspect the top level with `tree -a -L 1 "$(uv cache dir)"`; `wheels-v1` is gone, while the current `wheels-v6` remains. Check the size again with `du -sh "$(uv cache dir)"`:

```text
1.7G    /var/jenkins_home/.cache/uv
```

The cache remains larger than its original size because `uvx` downloaded `uv` 0.4.12 as a tool package and cached it in the current `wheels-v6` format. Pruning removed the obsolete entries created by the older executable, but kept the valid cached package containing that executable. The project's ML wheels also remain cached, so you can still recreate its environment offline. Because the cache is shared across projects, removing a dependency from this project's `pyproject.toml` does not make its cached wheel obsolete.

#### Clean Cache

Remove **all** cached entries so future installations must download or build packages again:

```bash
uv cache clean
```

Inspect the project files with `ls -lah`; `uv cache clean` leaves `.venv` and its installed packages untouched, along with `pyproject.toml` and `uv.lock`. It removes cached wheel data, not the package files already installed from those wheels. Verify that `scikit-learn` still works:

```bash
.venv/bin/python -c "import sklearn; print(sklearn.__file__)"
```

#### Cleanup Summary

These commands affect the shared cache and the project's installed environment differently.

| Command | Effect on the Cache | Effect on `.venv` |
| --- | --- | --- |
| `rm -r .venv` | Leaves cached packages available for reuse. | Removes the environment. |
| `uv cache prune` | Removes obsolete and unreferenced data; keeps valid package entries. | Leaves the environment unchanged. |
| `uv cache clean` | Removes all cached entries. | Leaves the environment unchanged. |

**For a completely fresh project sync**, remove `.venv`, run `uv cache clean`, then run `uv sync` to download and install the dependencies again; `--offline` cannot restore them from an empty cache.

## Using uv Cache in CI(/CD) Environments

CI jobs often start with a fresh environment. Reuse **package artifacts**, then create a new `.venv` from the committed lockfile on each run. For a realistic example, [`projects/proj5_uv_cache`](https://github.com/ValentinTwin1206/modern-python-devops-egineering/tree/main/projects/proj5_uv_cache) locks `tensorflow-cpu`, `transformers`, and `scikit-learn` for Python 3.12; its first install can be large.

### Prune for CI

`uv cache prune --ci` removes downloaded prebuilt wheels and unpacked source distributions but retains wheels built from source. This reduces the cache transferred between jobs while keeping potentially expensive build results. Unlike normal pruning, it intentionally discards reusable downloaded wheels.

To measure the difference in the development container, first reinstall the locked dependencies from `/app`. `--reinstall` repopulates the cache even if `.venv` survived an earlier cleanup:

```bash
uv sync --locked --reinstall --python 3.12
```

Record the size with `du -sh "$(uv cache dir)"`, then apply the CI strategy:

```bash
uv cache prune --ci
```

Check the size again with `du -sh "$(uv cache dir)"` and inspect the remaining entries with `tree -a -L 1 --noreport "$(uv cache dir)"`. The installed environment still works, but an offline reinstall now fails if it needs a removed wheel.

The same locked ML packages produced this comparison with uv 0.11.1:

| Stage | Cache Disk Usage |
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
