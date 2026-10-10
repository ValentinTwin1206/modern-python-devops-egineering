# uv Cache Demo (ML Dependencies)

This project declares `tensorflow-cpu`, `transformers`, and `scikit-learn` in
`pyproject.toml`. The committed `uv.lock` pins their resolved dependencies.
The [GitHub Actions workflow](../../.github/workflows/uv-cache.yml) compares
cache strategies. The package in `src/uv_cache_demo/` bundles a 16 MiB synthetic
embedding matrix, making its retained source-built wheel visible after CI
pruning. The examples do not download models or need a GPU.

## Run Locally

With Python 3.12 and uv installed, run this from the project directory to
install the locked dependencies and build or reuse the local package's wheel:

```shell
python scripts/generate_fixture.py
UV_CACHE_DEMO_BUILD_KEY=$(python scripts/build_key.py) uv sync --locked --no-editable
```

The generator uses `data/fixture.json` to create 32,768 rows of 512 unsigned
8-bit features. Its deterministic bytes compress poorly, so the wheel stays
roughly 16 MiB instead of shrinking to a tiny archive. The matrix is synthetic
sample data, not trained model weights. Only its specification and generator
are tracked in Git; `data/embeddings.bin` is generated before packaging.
Change the dimensions or seed in the specification and regenerate to try
different sizes or invalidate the cached wheel.

The command sets a content fingerprint for uv's `cache-keys` setting. Recompute
it before each sync so changes to `pyproject.toml` or source `.py`, `.json`, and
`.bin` files rebuild the
wheel. This replaces timestamp checks, allowing unchanged sources to reuse a
wheel even after a fresh checkout. Include any future build inputs, such as
package data files, in both the script and the workflow's cache globs.
`--no-editable` installs a regular wheel instead of linking to the source tree;
`uv build --wheel` alone produces a distribution artifact, not this installation
cache demonstration. Run `uv lock` after changing dependencies.

Check that the local package and ML packages can be imported:

```shell
.venv/bin/python -c "import tensorflow, transformers, sklearn; from uv_cache_demo import cache_message, fixture_shape; print(cache_message()); print('Bundled matrix:', fixture_shape()); print('ML packages imported successfully')"
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
GitHub's Actions tab. It also runs on pushes to `main` that change this project
or the workflow file, with pruning enabled and cache clearing disabled.
Manual inputs control two independent choices:

| Input | Default | Effect |
| --- | --- | --- |
| `prune_cache` | `true` | Runs `uv cache prune --ci` after installation. Removes downloaded wheels while retaining wheels built from source. |
| `clean_cache` | `false` | Clears the restored local cache before installation to demonstrate a cold run. |

The workflow uses separate cache-key suffixes for full and CI-pruned caches.
Run each strategy twice without changing the dependency files or package source and compare
the job summaries: they report cache restoration, installation duration,
and a cache-size timeline in KiB:

1. At job start, before restoring anything (normally 0 KiB).
2. After restoring GitHub's saved cache.
3. After optional `uv cache clean` (0 KiB when cleared).
4. After `uv sync`, including downloaded dependencies and the built wheel.
5. After optional `uv cache prune --ci`, retaining the built wheel.

Each row shows the change from the previous measurement: positive means growth,
negative means reclaimed space. Optional commands are measured even when skipped.
The helper uses `du -sk` on the same `UV_CACHE_DIR` used by `setup-uv` and uv;
a missing directory counts as zero. Measurements are outside the sync timer.
Also compare whole job durations, since cache transfers take time.

On a cold run, the installation log shows `Building` and `Built uv-cache-demo`.
After the cache is saved, an unchanged warm run should install that package
without building it again. A GitHub cache hit alone does not prove wheel reuse:
uv also checks the build fingerprint. Changes to the source or build settings
invalidate both the saved-cache key and the local wheel's fingerprint.

Pruning runs explicitly before the summary, rather than in `setup-uv`'s
post-job hook, so its effect is measurable even on cache hits. Exact cache-key
hits are not overwritten; the reported sizes describe the local cache, not
the compressed archive stored by GitHub.

CI pruning retains the local package's built wheel but removes the downloaded
ML wheels, so subsequent runs download those dependencies again. The bundled
data makes retained space visible, but packaging it is still quick; wheel size
does not imply expensive compilation or a guaranteed speedup. Keeping the full
cache (`prune_cache=false`) can be preferable for large downloads; measure
both strategies rather than assuming pruning always makes jobs faster.

For a local cache walkthrough and an explanation of the CI example,
see [Dependency Caching with uv](../../docs/chapter-03/section-03.md#using-uvs-cache-in-ci-environments).
