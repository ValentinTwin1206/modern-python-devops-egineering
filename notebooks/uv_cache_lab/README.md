# Dependency Caching with uv — Bob Follows the Cache

Bob explores downloaded wheels, an unzipped source distribution, a locally
built wheel, link modes, and three cleanup commands in
[uv_cache_lab.ipynb](./uv_cache_lab.ipynb). The technical companion is
[Chapter 03, Section 03](../../docs/chapter-03/section-03/uv_cache.md).

## Run the lab

1. Open `notebooks/uv_cache_lab` in VS Code using **Dev Containers: Reopen in Container**.
2. Open `uv_cache_lab.ipynb` and choose **Python 3 - uv Cache Lab**.
3. Run the notebook top to bottom. A network connection is needed for the first installs.

The Dev Container installs uv 0.13.3, Python 3.12, and a Jupyter kernel but
does not sync the project or run a post-create command. The notebook populates
uv's container-local cache deliberately. Its Bash cells run from `/workspace`,
which is the bind-mounted lab folder; `.venv`, generated `embeddings.bin`, and
`reports/` stay on the host but are ignored by Git. Temporary comparison
environments live under ignored `lab/`. The container uses `UV_LINK_MODE=copy`
so the main environment still works after cleaning the package cache.

## CI example

[uv-cache.yml](../../.github/workflows/uv-cache.yml) builds the same local
package from the lockfile on fresh runners with uv 0.11.1. `setup-uv` restores
the package cache and handles CI pruning before saving new archives, retaining
source-built wheels. Exact cache hits skip pruning and saving. Each run creates
a fresh `.venv` and reports the cache restore result, whether a cold experiment
was requested, and `uv sync` duration in milliseconds (excluding cache transfers).

Manual runs offer `cold_cache` (default: `false`). Enabling it skips cache
restoration and saving. Each fresh GitHub-hosted runner starts without the
project's package cache, so no cleaning command is needed and remote archives
remain unchanged. The summary distinguishes skipped restoration from a cache
miss. Compare several
warm and cold runs with unchanged dependencies and build inputs; a larger wheel
does not guarantee a faster total job.
See [the CI cache explanation](../../docs/chapter-03/section-03/uv_cache_ci.md).

### Fixture size

From the lab folder, generate a larger fixture with:

```bash
python scripts/generate_fixture.py --size 256
CACHE_DEMO_KEY=$(python scripts/build_key.py) uv sync --locked --no-editable --python 3.12
.venv/bin/python -m uv_cache_demo.main --output reports/embeddings.png
```

`--size` is a positive integer in MiB. The default is 16 MiB for the notebook;
CI uses 256 MiB. Generation writes deterministic 1 MiB blocks and updates
`src/uv_cache_demo/data/fixture.json` with the actual row count. The generated
binary is ignored by Git; the metadata is tracked and will show a local change
when using a different size. Run the generator without `--size` to return to
the 16 MiB fixture and default metadata. Recalculate `CACHE_DEMO_KEY` after
generation so uv invalidates the local wheel when its contents change. The CI
action's dependency globs also include the generated data and metadata.

The report memory-maps the installed matrix and processes it in chunks to keep
working memory bounded; its per-row norms and distances still grow with row count.
