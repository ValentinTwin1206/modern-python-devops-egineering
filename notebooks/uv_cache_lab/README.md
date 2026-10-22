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
package from the lockfile on fresh runners, compares full and CI-pruned caches,
and reports install time and cache sizes. `prune_cache` keeps source-built
wheels while dropping downloaded wheels and unzipped source distributions;
`clean_cache` simulates a cold install. These are independent workflow inputs.
See [the CI cache explanation](../../docs/chapter-03/section-03/uv_cache_ci.md).
