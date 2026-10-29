# Dependency Caching with uv — Bob Follows the Cache

Bob explores downloaded wheels, an unzipped source distribution, a locally
built wheel, link modes, and three cleanup commands in
[uv_cache_lab.ipynb](./uv_cache_lab.ipynb). The technical companion is
[Chapter 03, Section 03](../../docs/chapter-03/section-03.md).

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
See [the CI cache explanation](../../docs/chapter-03/section-04.md).

### Run the CI comparison from the command line

Use Bash and an installed [GitHub CLI (`gh`)](https://cli.github.com/).
Authenticate with an account that can run workflows in this repository. A
fine-grained token needs access to this repository with **Actions: Read and
write**; a classic token needs the appropriate repository scope. Keep tokens out
of commands, source files, and chat messages. Use `gh auth login` or supply
`GH_TOKEN` through your environment or a secret manager.

Check authentication before dispatching any runs.

```bash
gh auth status
```

Set the repository for the following commands.

```bash
export GH_REPO=ValentinTwin1206/modern-python-devops-egineering
```

Record the current `main` commit SHA. Keep this branch unchanged throughout the
experiment; local uncommitted changes do not run on GitHub.

```bash
gh api "repos/$GH_REPO/commits/main" --jq .sha
```

Start a cache-enabled run to populate the cache.

```bash
gh workflow run uv-cache.yml --ref main -F cold_cache=false
```

List recent manual runs and identify the one you just dispatched by its creation
time and commit SHA. Do not assume the first entry is yours if someone else is
running the workflow.

```bash
gh run list --workflow uv-cache.yml --branch main --event workflow_dispatch --limit 10 --json databaseId,createdAt,headSha,status,conclusion,url
```

Enter that run's `databaseId`.

```bash
read -r -p "Workflow run ID: " RUN_ID
```

Wait for success before starting the next run. A failed run makes this command
exit with an error; inspect its logs instead of treating it as a measurement.

```bash
gh run watch "$RUN_ID" --exit-status
```

Dispatch another cache-enabled run for the warm measurement.

```bash
gh workflow run uv-cache.yml --ref main -F cold_cache=false
```

Repeat the list, ID selection, and watch commands above for this new run. Retrieve
its provenance and confirm that the commit SHA matches the recorded revision.

```bash
gh run view "$RUN_ID" --json url,headSha,conclusion
```

Read the cache status and installation duration from the completed job's logs.
These are the environment values printed for **Show cache and installation
time**, not the runner's rounded step duration. Only accept `RESTORE_STATUS:
Restored` as a warm measurement; if it reports `Not restored`, repeat the
cache-enabled run.

```bash
gh run view "$RUN_ID" --log | grep -E 'RESTORE_STATUS:|INSTALL_MS:'
```

Record the URL, SHA, and duration, then dispatch a cold run.

```bash
gh workflow run uv-cache.yml --ref main -F cold_cache=true
```

Repeat the list, ID selection, watch, provenance, and log commands for the cold
run. Require the same SHA, a successful conclusion, and `RESTORE_STATUS: Skipped`.
Record its duration, then repeat the warm/cold pair with unchanged inputs. Copy
the results into the documentation's comparison table; do not include the
cache-population run or compare different revisions.

#### Dispatch with curl instead

With the same repository and a securely configured `GH_TOKEN`, the REST API
can dispatch the cold run directly. Use `"cold_cache": false` for a cache-enabled
run. `--fail-with-body` makes HTTP errors visible; a successful dispatch does not
mean the job has completed.

```bash
curl --fail-with-body --request POST \
  --header "Accept: application/vnd.github+json" \
  --header "Authorization: Bearer ${GH_TOKEN:?Set GH_TOKEN securely before dispatching}" \
  --header "X-GitHub-Api-Version: 2022-11-28" \
  "https://api.github.com/repos/$GH_REPO/actions/workflows/uv-cache.yml/dispatches" \
  --data '{"ref":"main","inputs":{"cold_cache":true}}'
```

Use the `gh` commands above to identify the resulting run, wait for it, and
retrieve its logs. The REST API also supports listing workflow runs and
downloading job logs, but it does not provide a dedicated endpoint for the
rendered `GITHUB_STEP_SUMMARY` Markdown. No workflow changes are needed to read
the measurements already present in the logs.

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
