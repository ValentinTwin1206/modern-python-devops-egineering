# Dependency Caching with uv

## Understand the uv Cache

`uv` keeps package metadata, downloads, and built packages so it can reuse them instead of fetching or building them again. This saves time when you install the same dependency in another project or recreate an environment. `uv.lock` records *which versions* to install; the cache makes obtaining them faster; each project's `.venv` contains the packages it can actually import. See [Dependency Management with uv](./section-02.md) for locking and syncing.

## Explore the Cache with `click`

### Compare Installation Commands

These tabs show different ways to use a package. Work in a disposable project or virtual environment: `uv add` changes project files, while `uv sync` needs a project that already declares `click` and has a lockfile. The uv commands can all use uv's cache; `pip` uses its own.

=== "pip install"

    With an existing virtual environment active, install `click` using pip:

    ```shell
    pip install click
    ```

=== "uv pip install"

    With an existing virtual environment active, install `click` without editing project files:

    ```shell
    uv pip install click
    ```

=== "uv add"

    In a uv project, declare `click`, update the lockfile, and install it:

    ```shell
    uv add click
    ```

=== "uv sync"

    In that project, synchronize its environment from the existing lockfile, reusing cached packages where possible:

    ```shell
    uv sync --locked
    ```

=== "uv tool"

    `click` is a library, not a command-line application. To see uv's shared cache used for an executable tool instead, install `black`:

    ```shell
    uv tool install black
    ```

    Tools get their own environments; they can still draw packages from the same uv cache.

After using the `uv add` tab in a disposable project, remove its environment so the next sync must install `click` again:

```shell
rm -rf .venv
```

Recreate that environment from the lockfile; uv can reuse `click` from its cache:

```shell
uv sync --locked
```

### Find Packages on Disk

The `uv cache dir` subcommand resolves uv's active cache path, using `UV_CACHE_DIR` or the configured `cache-dir` when set. On Linux, the default is usually `~/.cache/uv` or `$XDG_CACHE_HOME/uv`. Run `ls -lah` with that path to list the cache, including hidden files and directory sizes:

```shell
ls -lah "$(uv cache dir)"
```

The cache layout is versioned and can change. For example, inspect the top level of the wheel cache:

```shell
ls -1 "$(uv cache dir)/wheels-v6"
```

```text
index
pypi
```

Packages do not necessarily appear in directories named after the package. The project's `.venv` is separate and lives outside the shared cache.

### Cache Files and Configuration

The cache root may contain `CACHEDIR.TAG`, which marks it as disposable, and `.gitignore`, which keeps cache contents out of Git. Inspect these housekeeping files with `cat`:

```shell
cat "$(uv cache dir)/CACHEDIR.TAG"
```

```text
Signature: 8a477f597d28d172789f06886806bc55
```

```shell
cat "$(uv cache dir)/.gitignore"
```

```text
*
```

These files are not dependency declarations or settings to edit. To change the cache location, set `UV_CACHE_DIR` or configure `cache-dir` in `uv.toml` or `[tool.uv]` in `pyproject.toml`; most projects need no cache configuration. See [uv's cache directory documentation](https://docs.astral.sh/uv/concepts/cache/#cache-directory).

## Maintain the Cache

uv normally manages entries for you. To reclaim space from unused entries, prune the cache:

```shell
uv cache prune
```

To clear all cached entries and make the next installation fetch or build them again, clean the cache:

```shell
uv cache clean
```

Use these commands rather than deleting individual files in the cache. Neither command removes the project's lockfile.

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

Jenkins can keep uv's cache between builds by running on the same agent with `UV_CACHE_DIR` inside persistent storage. The [demo Dockerfile](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/proj5_uv_cache/Dockerfile) runs Jenkins and keeps `/var/jenkins_home` in a Docker volume; the cache lives at `/var/jenkins_home/.cache/uv`. It includes Python 3.12, uv, and the demo's locked dependency files. See the [demo setup](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/proj5_uv_cache/README.md) for build and startup instructions. This single-node teaching example enables one executor on the controller.

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
