# Dependency Caching with uv

`uv` keeps package metadata, downloads, and built packages so it can reuse them instead of fetching or building them again. This saves time when you install the same dependency in another project or recreate an environment. `uv.lock` records *which versions* to install; the cache makes obtaining them faster; each project's `.venv` contains the packages it can actually import. See [Dependency Management with uv](./section-02.md) for locking and syncing.

## Used Project

The [uv cache demo](https://github.com/ValentinTwin1206/modern-python-devops-egineering/tree/main/projects/proj5_uv_cache) provides the same Python 3.12 environment for local exploration and Jenkins builds

## The Cache Workflow

Follow this pattern with the demo's ML dependencies: **create the cache, reuse it, then clear it**. The container keeps its cache separate from your host's uv cache; the first download is several hundred megabytes.

### Start the Development Container

From the repository's `projects/` directory, use [build.sh](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/build.sh) to build the image and open the dedicated `uv` cache development container:

```bash
./build.sh build --path proj5_uv_cache/Dockerfile.devEnv --rm-container
```

The command opens Bash as `bob` in `/app`. The Jenkins image already includes Bash; its entrypoint forwards `/bin/bash` instead of starting Jenkins. The image sets `UV_CACHE_DIR` to `/var/jenkins_home/.cache/uv`, so no export or project initialization is needed.

!!! warning "The project is bind-mounted"
    Changes to `/app` also change `projects/proj5_uv_cache` on your host. The following steps recreate `.venv`; do not use that environment in another session while following them. The container's package cache is disposable and is not the named volume used by the Jenkins example.

### uv Commands That Use the Cache

The table shows which commands update uv's cache. `uv add` changes project files; `uv sync` installs the project's declared dependencies.

| Command | Update Cache | Summary |
| --- | --- | --- |
| `uv pip install {pkg}` | ✅  | Installs a `{pkg}` uses uv's cache without changing project files. |
| `uv add {pkg}` | ✅ | Adds a `{pkg}` to a project, updates `uv.lock` as well as `pyproject.toml`, and synchronizes the environment. |
| `uv sync` | ✅ | Creates the environment from `uv.lock`. |
| `uv tool install {tool}` | ✅ | Installs a `{tool}` in its own tool environment while sharing uv's package cache. |

### Install Project Dependencies

Install the demo's locked dependencies into `.venv`. uv downloads missing packages into its cache without changing the dependency files:

```bash
uv sync --locked --python 3.12
```

### Inspect the Cache

Run `uv cache dir` the active cache path. You should see:

```text
/var/jenkins_home/.cache/uv
```

Inspect the populated cache, including its hidden housekeeping files:

```bash
tree -a -L 1 --noreport "$(uv cache dir)"
```

The following layout was observed with uv 0.11.1. Cache directory versions and package versions can change:

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

Each entry stores reusable package data or helps uv manage the cache safely:

| Entry | Purpose |
| --- | --- |
| `archive-v0` | Stores unpacked package files that uv copies or links into an environment. Reusing these files avoids downloading and unpacking the same package again. |
| `wheels-v6` | Stores records for wheels (ready-to-install packages), including download metadata and links to unpacked files. These records help uv locate cached packages for installation. |
| `interpreter-v4` | Stores information about Python interpreters, such as their versions and supported platforms. uv can reuse this information instead of inspecting the same interpreter repeatedly. |
| `sdists-v9` | Stores cached source distributions and build results for packages that need to be built into wheels. The directory can exist even when all installed packages came from ready-made wheels. |
| `.gitignore`, `.lock`, `CACHEDIR.TAG` | `.gitignore` keeps cache contents out of Git, `.lock` coordinates cache access, and `CACHEDIR.TAG` marks the directory as disposable cache data. uv manages these files; they are not dependency declarations or settings to edit. |

Inspect the wheel record of `scikit-learn` package:

```bash
tree -L 1 --noreport "$(uv cache dir)/wheels-v6/pypi/scikit-learn"
```

In this shortened example, `<wheel-tag>` represents its Python/platform tags and `<archive-id>` is a randomly generated directory name:

```text
/var/jenkins_home/.cache/uv/wheels-v6/pypi/scikit-learn
|-- 1.9.1-<wheel-tag> -> /var/jenkins_home/.cache/uv/archive-v0/<archive-id>
`-- 1.9.1-<wheel-tag>.http
```

The arrow points to `scikit-learn`'s unpacked files in `archive-v0`. The `.http` file holds cache metadata, not project settings. Other workflows may also create package-index metadata in `simple-v20`.

Check the cache's disk usage with `du -sh "$(uv cache dir)"`; this run used about 1.6 GiB:

```text
1.6G    /var/jenkins_home/.cache/uv
```

### Reuse the Cache

Remove only the project's `venv` from `/app`:

```bash
rm -r .venv
```

Recreate `.venv` from the unchanged `uv.lock`:

```bash
uv sync --locked --offline --python 3.12
```

> `--offline` disables downloads, confirming cache reuse.

A successful run installs the ML dependencies without downloads or a `Prepared` step. If a required package is missing from the cache, offline installation fails instead.

Verify the ML imports and show where `scikit-learn` is installed. The path points into `.venv`, not the cache:

```bash
.venv/bin/python -c "import sklearn; print(sklearn.__file__)"
```

### Destroy the Cache

Use uv's cleanup commands rather than deleting cache files directly. Neither command removes the project's `.venv` or dependency files:

=== "Prune"

    Remove **unused** cache entries to reclaim space without clearing the entire cache. Here, unused means obsolete cache data, such as entries from older uv versions, not simply packages absent from the current project:

    ```bash
    uv cache prune
    ```

=== "Clean"

    Remove **all** cached entries so future installations must download or build packages again:

    ```bash
    uv cache clean
    ```

Inspect the surviving environment and dependency files after cleanup by running `ls -lah`:

```text
.venv
pyproject.toml
uv.lock
```

Verify that the installed `scikit-learn` still works after cache cleanup:

```bash
.venv/bin/python -c "import sklearn; print(sklearn.__file__)"
```

**Result:** deleting `.venv` preserves the cache for reuse; cache cleanup preserves `.venv`. After `uv cache clean`, deleting `.venv` and syncing again requires fresh downloads, so an offline sync cannot restore the dependencies.

!!! info
    For persistent cache-location settings, see [uv's cache directory documentation](https://docs.astral.sh/uv/concepts/cache/#cache-directory).

## Using uv Cache in CI(/CD) Environments

CI jobs often start with a fresh environment. Reuse **package artifacts**, then create a new `.venv` from the committed lockfile on each run. For a realistic example, [`projects/proj5_uv_cache`](https://github.com/ValentinTwin1206/modern-python-devops-egineering/tree/main/projects/proj5_uv_cache) locks `tensorflow-cpu`, `transformers`, and `scikit-learn` for Python 3.12; its first install can be large.

### GitHub Actions

Use this action step in a GitHub Actions job to install uv and restore or save its package cache across runs. The dependency files contribute to the cache key, so changing either file selects a new entry:

```yaml
- name: Set up uv and restore its package cache
  uses: astral-sh/setup-uv@v5
  with:
    version: "0.11.1"
    enable-cache: true
    cache-dependency-glob: |
      projects/proj5_uv_cache/pyproject.toml
      projects/proj5_uv_cache/uv.lock
```

- `uses` selects the `setup-uv` action.
- `with` configures the action:
  - `version` pins uv to `0.11.1`.
  - `enable-cache` enables uv package-cache restoration and saving.
  - `cache-dependency-glob` lists files used to derive the cache key:
    - `pyproject.toml` declares the project's dependencies.
    - `uv.lock` records the resolved dependency versions.

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

Run the workflow twice on the same branch without changing those files. The first run populates the cache; the next can reuse it. Compare **whole job times**, since downloading and uploading the CI cache also takes time.

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
