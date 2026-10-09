# uv Cache Demo (ML Dependencies)

This project declares `tensorflow-cpu`, `transformers`, and `scikit-learn` in
`pyproject.toml`. The committed `uv.lock` pins their resolved dependencies.
The [GitHub Actions workflow](../../.github/workflows/uv-cache.yml) compares
cache strategies. The examples do not download models or need a GPU.

## Run Locally

With Python 3.12 and uv installed, run this from the project directory to
install the project's dependencies and update `uv.lock` when needed:

```shell
uv sync
```

Check that the ML packages can be imported:

```shell
.venv/bin/python -c "import tensorflow, transformers, sklearn; print('ML packages imported successfully')"
```

## Start the Development Container

The [Dockerfile.devEnv](./Dockerfile.devEnv) uses Ubuntu 24.04 with uv 0.11.1,
Python 3.12, and `tree`. It opens Bash as `bob` for exploring the cache.

From the repository's `projects/` directory, build the image and open the shell
with [build.sh](../build.sh). The script matches bob's UID/GID to your host user
and bind-mounts this project at `/app`:

```bash
./build.sh build --path proj5_uv_cache/Dockerfile.devEnv --rm-container
```

The image sets `UV_CACHE_DIR` to `/home/bob/.cache/uv` and keeps Python in
`/opt/uv-python`. Packages are copied into each environment, so cleaning the
cache does not remove installed packages. Changes under `/app`, including
`.venv`, affect the host project. The container's package cache is disposable
and separate from your host's uv cache.

Follow [Inspect and Reuse the Cache](../../docs/chapter-03/section-03.md#inspect-and-reuse-the-cache)
to inspect the cache, reinstall offline, and compare pruning with full cleanup.
The pruning showcase uses `uvx` to run an older uv release once and cache
SciPy in its old cache format. The temporary installation stays outside the
project, and neither the dependency files nor the Dockerfile needs changing.

## Compare GitHub Actions Cache Strategies

Run the [uv cache workflow](../../.github/workflows/uv-cache.yml) manually from
GitHub's Actions tab. Its inputs control two independent choices:

| Input | Default | Effect |
| --- | --- | --- |
| `prune_cache` | `true` | Runs `uv cache prune --ci` after installation. Removes downloaded wheels while retaining wheels built from source. |
| `clean_cache` | `false` | Clears the restored local cache before installation to demonstrate a cold run. |

The workflow uses separate cache-key suffixes for full and CI-pruned caches.
Run each strategy twice without changing the dependency files and compare
the job summaries: they report cache restoration, installation duration,
cache sizes before and after optional pruning, and reclaimed space in KiB.
Also compare whole job durations, since cache transfers take time.

Pruning runs explicitly before the summary, rather than in `setup-uv`'s
post-job hook, so its effect is measurable even on cache hits. Exact cache-key
hits are not overwritten; the reported sizes describe the local cache, not
the compressed archive stored by GitHub.

The ML demo uses downloaded wheels, so CI pruning leaves little package data
to reuse and subsequent runs download those wheels again. Keeping the full
cache (`prune_cache=false`) can be preferable for large downloads; measure
both strategies rather than assuming pruning always makes jobs faster.

For a local cache walkthrough and an explanation of the CI example,
see [Dependency Caching with uv](../../docs/chapter-03/section-03.md#using-uvs-cache-in-ci-environments).
