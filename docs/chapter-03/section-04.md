# Using uv's Cache in CI Environments

Aggressive caching helps make `uv` fast by avoiding repeated downloads and builds of dependencies. In CI, however, transferring a cache between temporary *Hosted Runners* adds overhead, so preserving everything is not always worthwhile. [Astral's CI caching guidance](https://docs.astral.sh/uv/concepts/cache/#caching-in-continuous-integration) favors *Wheels Built from Source*, which can be costly to rebuild, over *Prebuilt Wheels*, which are usually quick to download and install. It does not cite a formal study quantifying these trade-offs; this section explains how to adopt the strategy and measure its benefits in your own CI workflow rather than assume a speedup.

## Used Project

This table lists the workflow and project files used in the examples.

| Component | Description |
| --- | --- |
| [`.github/workflows/uv-cache.yml`](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/.github/workflows/uv-cache.yml) | GitHub Actions workflow that compares cold, complete, and CI-pruned caches and records install time and local cache size. |
| [`notebooks/nb5_uv_cache_lab/pyproject.toml`](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/notebooks/nb5_uv_cache_lab/pyproject.toml) and [`uv.lock`](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/notebooks/nb5_uv_cache_lab/uv.lock) | Define the package build configuration and locked dependencies installed by the workflow. |

## GitHub Actions Caching Pattern

### Cache Layers

GitHub Actions provides an [***Integrated Cache Service***](https://docs.github.com/en/actions/reference/dependency-caching-reference) for storing and restoring files across workflow runs. It works alongside tools' own caches and the project's environment, so understanding the separate layers helps explain what persists and when it can be reused. Three distinct layers participate in this example.

1. **The GitHub Actions cache** stores a remote archive selected by an action-generated key and GitHub's access rules.
2. **Language and package-manager caches** hold tool-managed downloads and build artifacts on the runner. This pattern applies to tools such as Python's `uv`, Rust's `cargo`, and Node.js's `npm`
3. **The project `.venv`** contains installed packages. Each hosted runner creates it fresh, and it is not cached.

### Hosted Runner Cache Lifecycle

GitHub Actions offers long-lived self-hosted ***Persistent Runners*** and temporary ***(GitHub) Hosted Runners***. Hosted runners can reuse remote caches by restoring an archive at job start, using it during installs or builds, and saving an updated archive after success. Cache keys combine environment and project inputs; exact-key hits need no save because entries are immutable. Caches expire after seven days without access or sooner under storage pressure, and runs can generally restore caches only from their current or default branch ([retention](https://docs.github.com/en/actions/reference/dependency-caching-reference#usage-limits-and-eviction-policy) and [access rules](https://docs.github.com/en/actions/reference/dependency-caching-reference#restrictions-for-accessing-a-cache)). Use the same branch and revision for manual comparisons. After a cache miss, optionally prune local data before saving. A cold test skips restoration and saving without deleting the remote archive. The chart shows this workflow.

```mermaid
flowchart TD
    setup["Prepare hosted runner and project"] --> cold{"Cold-cache test requested?"}
    cold -->|Yes| install["Install dependencies and build project"]
    cold -->|No| restore["Restore cache or start without one"]
    restore --> install
    install --> run["Run workflow tasks and collect results"]
    run --> success{"Job successful?"}
    success -->|No| done["Finish without saving cache"]
    success -->|Yes| saveenabled{"Saving enabled?"}
    saveenabled -->|No| done
    saveenabled -->|Yes| hit{"Exact cache-key hit?"}
    hit -->|Yes| skip["Keep existing archive; skip saving"]
    hit -->|No| prune["Optionally prune local cache data"]
    prune --> save["Save archive for a future run"]
    save -. "Next workflow run" .-> setup
```

## Using uv's Cache in Docker Builds

Docker builds can reuse both **image layers** and a **BuildKit cache mount**. A reusable layer skips a build step entirely; a cache mount helps `uv` reuse downloaded or built packages when the step must run again. These caches are separate from the GitHub Actions cache used in the workflow example below.

### Separate Dependencies from Project Source

The following example assumes a single packaged project with a `pyproject.toml`, a committed `uv.lock`, and dependencies available without local source directories. Save this `Dockerfile` in the project root. It installs dependencies before copying the source, then validates the lockfile and installs the project:

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.11.1 /uv /uvx /bin/
WORKDIR /app

# Copy files from the cache mount into the environment.
ENV UV_LINK_MODE=copy

# Install locked dependencies in a reusable layer.
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-default-groups

# Add the project and verify its lockfile before installing it.
COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-default-groups --no-editable

# Replace this with the application's entry point.
CMD ["/app/.venv/bin/python", "--version"]
```

The first sync uses `--frozen` to skip the freshness check while project source files are unavailable. The final `--locked` sync checks `pyproject.toml` against the lockfile once the full project is present; `--no-editable` installs a regular project package. Both commands omit default dependency groups. See [Frozen Installs](./section-02.md#frozen-installs) for the distinction between frozen and locked syncs.

Add a `.dockerignore` in the project root so a host environment or Git metadata does not overwrite the environment created inside the image:

```text title=".dockerignore"
.venv/
.git/
__pycache__/
```

Build the image from the project root with BuildKit enabled:

```bash
DOCKER_BUILDKIT=1 docker build -t my-uv-app .
```

When only source code changes, Docker can reuse the dependency layer if its earlier inputs are unchanged. If a sync step must run again, BuildKit may reuse its cache mount; `UV_LINK_MODE=copy` handles the cache and environment residing on different filesystems. The cache mount is not included in the resulting image.

!!! info "Cache Persistence in CI"

    Cache mounts belong to the BuildKit builder and are reusable only while its cache is available. A fresh hosted runner does not automatically retain them across jobs; configure persistent builder storage or a supported cache backend when cross-run reuse is needed. Image-layer caching and cache-mount persistence depend on the CI builder and cache backend.

For workspaces or local path dependencies, include the required project metadata and source files in the appropriate build stages; `--no-install-workspace` can omit workspace packages during the initial sync. See [uv's Docker integration guide](https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers) for workspace and multi-stage examples.

## Using uv's Cache in GitHub Actions

The `uv cache demo` workflow in [`.github/workflows/uv-cache.yml`](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/.github/workflows/uv-cache.yml) is a streamlined example of using `uv`'s package cache in CI. It compares cold, complete, and CI-pruned caches to measure the potential installation-time savings from cache reuse.

### Workflow Triggers and Job Configuration

#### Workflow Triggers

GitHub Actions starts workflows from configured events, including *Pushes*, *Pull Requests*, *Manual (Workflow) Dispatches*, *Scheduled Runs*, and *Published Releases*. This workflow runs on pushes to `main` that match either listed path or manual dispatch from the **Actions** tab; both start the same job on a fresh *(GitHub-) Hosted (Ubuntu) Runner*. Manual runs select the `strategy` input: `cold`, `warm`, or `ci-pruned` (the default). Pushes use `ci-pruned`.

```mermaid
flowchart LR
    A["Push to main<br>matching paths"] -->|"strategy=ci-pruned"| W["GitHub Actions Workflow<br>(uv cache demo)"]
    B["Pull Request"] --> W
    C["Manual (Workflow) Dispatch"] -->|"strategy input<br>(default: ci-pruned)"| W
    D["Scheduled Run"] --> W
    E["Release Published"] --> W
    W --> J["analyze-embeddings job<br>CACHE_STRATEGY"]

    classDef unused fill:#eee,stroke:#bbb,color:#888
    class B,D,E unused
    linkStyle 1,3,4 stroke:#bbb,stroke-dasharray:4 4
```

> Grayed-out triggers indicate events not configured in this workflow.

#### Analysis Job and Steps

The `analyze-embeddings` job checks out the repository and sets up Python 3.12. The manual `fixture_size` choice selects a 16, 64, 256, 512, or 1024 MiB synthetic embedding matrix; it defaults to 256 MiB, as do push-triggered runs. The job generates the matrix, fingerprints the project's build inputs, and installs `uv` with optional package-cache restoration. After recording the pre-install cache size, it creates a fresh environment from the lockfile and times `uv sync`. Finally, it analyzes the installed embeddings and summarizes the selected size, cache sizes, restoration status, and installation time. The YAML below shows the workflow triggers and job configuration.

```yaml
name: uv cache demo

on:
  push:
    branches:
      - main
    paths:
      - "notebooks/nb5_uv_cache_lab/**"
      - ".github/workflows/uv-cache.yml"
  workflow_dispatch:
    inputs:
      strategy:
        description: "uv cache strategy"
        type: choice
        default: ci-pruned
        options:
          - cold
          - warm
          - ci-pruned
      fixture_size:
        description: "Embedding matrix size (MiB)"
        type: choice
        default: "256"
        options:
          - "16"
          - "64"
          - "256"
          - "512"
          - "1024"

permissions:
  contents: read

jobs:
  analyze-embeddings:
    runs-on: ubuntu-latest
    env:
      CACHE_STRATEGY: ${{ inputs.strategy || 'ci-pruned' }}
      fixture_size: ${{ inputs.fixture_size || '256' }}
```

### Step: Set up uv and Optionally Restore its Package Cache

The [`astral-sh/setup-uv`](https://github.com/astral-sh/setup-uv) GitHub Action is developed, released, and maintained by Astral, the company behind `uv`. It installs `uv`, adds it to the runner's `PATH`, and provides options to configure its setup and package-cache behavior, including cache restoration, pruning, and saving. Its remote cache key incorporates an internal cache version, architecture, platform, and detected Python version, along with a hash of matching files; the explicit patterns in this workflow cover dependencies and local build inputs, including generated data, so changes invalidate the remote cache.

After a successful job, the [post-action](https://github.com/astral-sh/setup-uv/blob/07a047e608db84b3d8c06cd9a7c7dcc9c355c18e/src/save-cache.ts) of `astral-sh/setup-uv` saves the remote cache when needed. An exact key hit skips pruning and saving; otherwise, the `ci-pruned` strategy runs `uv cache prune --ci` before saving, while `warm` saves without pruning. Because GitHub cache entries are immutable, the action creates a new entry instead of overwriting one. Cold experiments disable saving.

```yaml
- name: Set up uv and optionally restore its package cache
  id: uv
  uses: astral-sh/setup-uv@07a047e608db84b3d8c06cd9a7c7dcc9c355c18e # v10.3.2
  with:
    version: "0.11.1"
    enable-cache: true
    restore-cache: ${{ env.CACHE_STRATEGY != 'cold' }}
    save-cache: ${{ env.CACHE_STRATEGY == 'cold' && 'false' || 'auto' }}
    prune-cache: ${{ env.CACHE_STRATEGY == 'ci-pruned' }}
    cache-suffix: ${{ env.CACHE_STRATEGY == 'warm' && 'full-cache-demo' || '' }}
    cache-dependency-glob: |
      notebooks/nb5_uv_cache_lab/pyproject.toml
      notebooks/nb5_uv_cache_lab/uv.lock
      notebooks/nb5_uv_cache_lab/scripts/*.py
      notebooks/nb5_uv_cache_lab/src/**/*.py
      notebooks/nb5_uv_cache_lab/src/**/*.json
      notebooks/nb5_uv_cache_lab/src/**/*.bin
```

**Inputs**: (*excerpt*)

- `enable-cache` - Explicitly enables GitHub Actions caching; its `auto` default enables caching on GitHub-hosted runners for supported events.
- `restore-cache` - Restores matching artifacts for `warm` and `ci-pruned`. Selecting `cold` disables restoration, giving a cold installation without `uv cache clean`. This relies on fresh hosted runners. The action defaults to `"true"`.
- `save-cache` - Uses `"auto"` during normal runs and `"false"` during cold experiments, leaving remote archives unchanged. The `"auto"` default allows eligible saving except for `merge_group` events; it does not make installation cold.
- `prune-cache` - Enables `uv cache prune --ci` before a new cache is saved after a cache miss for the `ci-pruned` strategy; in v10.3.2, the default is `false`.
- `cache-suffix` - Separates the `warm` complete cache from the CI-pruned cache.
- `cache-dependency-glob` - Replaces the default lockfile and requirements patterns with the listed repository-relative paths, which are used to generate the remote cache key.

**Outputs**: (*excerpt*)

- `cache-hit` - Indicates whether restoration found an archive. When restoration is disabled, v10.3.2 leaves this output unset, so the summary explicitly reports `Skipped`.

=== "CI-pruned Cache"

    Select `ci-pruned` to enable restoration and automatic saving with pruning. On a cache miss, the action prunes before saving. Run once to populate the CI-pruned cache, then repeat with the same cache key to measure a warm restore.

    ```yaml
    with:
      enable-cache: true
      restore-cache: true
      save-cache: auto
      prune-cache: true
    ```

=== "Warm Cache"

    Select `warm` to enable restoration and automatic saving without pruning, using a separate cache suffix. Run once to populate this cache, then repeat with the same cache key.

    ```yaml
    with:
      enable-cache: true
      restore-cache: true
      save-cache: auto
      prune-cache: false
      cache-suffix: full-cache-demo
    ```

=== "Cold Cache"

    Select `cold` on a fresh GitHub-hosted runner to disable restoration and saving. The installation starts without a restored package cache, and the run leaves remote archives unchanged.

    ```yaml
    with:
      enable-cache: true
      restore-cache: false
      save-cache: false
    ```

### Step: Measure Restored Package Cache Size

Before installing dependencies, the workflow measures the package cache available on the runner so the report shows what was ready for reuse. It records the size in bytes and a readable unit such as MiB or GiB. It then exposes both values through `GITHUB_ENV` so the [final step](#step-show-cache-and-installation-time) can reuse them.

```yaml
- name: Measure restored package cache size
  run: |
    mkdir -p "$UV_CACHE_DIR"
    bytes=$(du -sb "$UV_CACHE_DIR" | cut -f1)
    echo "RESTORED_CACHE_BYTES=$bytes" >> "$GITHUB_ENV"
    echo "RESTORED_CACHE_SIZE=$(numfmt --to=iec-i --suffix=B "$bytes")" >> "$GITHUB_ENV"
```

### Step: Create a Fresh Environment from Locked Dependencies

As explained above, *GitHub Actions* can restore a remote package cache on a fresh *(Github-) Hosted Runner* and save cache updates after a run. Additionally, `uv` supports project-specific cache keys, that can be defined as `tool.uv.cache-keys` in `pyproject.toml` to fingerprint local wheel-cache entries, complementing the remote cache key.

```toml
[tool.uv]
cache-keys = [{ env = "CACHE_DEMO_KEY" }]
```

Earlier, the workflow generates a synthetic embedding matrix of the selected size (256 MiB by default) and exposes a fingerprint of the build inputs as `CACHE_DEMO_KEY`. With Python 3.12, `uv sync` creates the `.venv` and uses `--locked` to follow the committed `uv.lock` (and fail if it needs updating). The `--no-editable` option installs a regular project wheel containing the matrix rather than linking the source; the fingerprint lets `uv` reuse a cached wheel or rebuild it when inputs change. The step exposes the `uv sync` duration in milliseconds as `milliseconds` through *GitHub Outputs*, excluding fixture generation, cache transfers, pruning, and report execution.

```yaml
- name: Create a fresh environment from locked dependencies
  id: install
  shell: bash
  run: |
    start_ms=$(date +%s%3N)
    uv sync \
      --directory notebooks/nb5_uv_cache_lab \
      --locked \
      --no-editable \
      --python 3.12
    end_ms=$(date +%s%3N)
    echo "milliseconds=$((end_ms - start_ms))" >> "$GITHUB_OUTPUT"
```

### Step: Show Cache and Installation Time

The final job summary shows the selected strategy, whether a cache was restored, the cache sizes before and after installation, and the installation time. The previous step recorded the install duration of `uv sync` in milliseconds and exposed the value as `milliseconds` output, which the summary uses as `INSTALL_MS`. Cache sizes are measured on the *(GitHub-) Hosted Runner*, not from compressed remote archives; if restoration is skipped or misses, the pre-install size does not represent a restored cache.

```yaml
- name: Show cache and installation time
  env:
    RESTORE_STATUS: ${{ env.CACHE_STRATEGY == 'cold' && 'Skipped' || (steps.uv.outputs.cache-hit == 'true' && 'Restored' || 'Not restored') }}
    INSTALL_MS: ${{ steps.install.outputs.milliseconds }}
  run: |
    cache_bytes=$(du -sb "$UV_CACHE_DIR" | cut -f1)
    cache_size=$(numfmt --to=iec-i --suffix=B "$cache_bytes")
    echo "RESTORED_CACHE_SIZE=$RESTORED_CACHE_SIZE ($RESTORED_CACHE_BYTES bytes)"
    echo "CACHE_SIZE_AFTER_SYNC=$cache_size ($cache_bytes bytes; before setup-uv post-action pruning)"
    {
      echo '## uv cache demo'
      echo ''
      echo '| Measurement | Result |'
      echo '| --- | --- |'
      echo "| Embedding matrix size | ${fixture_size} MiB |"
      echo "| setup-uv cache restoration | $RESTORE_STATUS |"
      echo "| Cache strategy | $CACHE_STRATEGY |"
      echo "| Restored local uv cache | $RESTORED_CACHE_SIZE |"
      echo "| uv sync duration | ${INSTALL_MS} ms |"
      echo "| Local uv cache after sync, before post-action pruning | $cache_size |"
      echo ''
      echo 'Duration measures only uv sync; it excludes GitHub cache restoration and saving time.'
      echo 'Cold experiments skip cache restoration and saving; remote archives remain unchanged.'
      echo 'Only runs reporting Restored qualify as warm-cache measurements.'
      echo 'Compare multiple runs with unchanged dependencies and build inputs; no speedup is guaranteed.'
    } >> "$GITHUB_STEP_SUMMARY"
```

## Run the Workflow and Compare Cache Performance

### Execute the Cache Strategy Comparison

To test [uv's recommendation for caching in CI](https://docs.astral.sh/uv/concepts/cache/#caching-in-continuous-integration), the workflow was executed with different caching strategies and embedding-matrix sizes. The comparison examined whether retaining only costly source-built wheels could reduce cache size and overall job duration compared with keeping the complete cache or starting without one. The following conditions were varied:

- **Caching strategy:** The `setup-uv` input `prune-cache` controlled which artifacts were saved: `true` retained costly *Source-built Wheels* but removed *Downloaded Prebuilt Wheels* for the ***CI-pruned Cache***, while `false` retained both for the ***Warm (complete) cache***. The ***Cold (empty) cache*** baseline used `restore-cache: false` and `save-cache: false` on a fresh runner, skipping restoration and leaving remote archives unchanged.
- **Source-built wheel share:** Packaging matrices from 16 to 1,024 MiB into the source-built wheel changed its contribution to the overall cache. Each size used a distinct cache key; larger matrices also increased generation and analysis time.

The following table shows the runs for each estimated *source-built wheel share* and *caching strategy*, for **45 measurements** in total. Each combination was run three times because timings can vary; the middle result (the median) helps reduce the influence of an unusually fast or slow run. The [benchmark CSV](../../notebooks/nb5_uv_cache_lab/cache_benchmark_results.csv) provides the corresponding results and individual run links; cache-population runs are excluded.

| Estimated share of complete cache | Empty cache | CI-pruned cache | Complete cache |
| ---: | ---: | ---: | ---: |
| 3.60% | 3 runs | 3 runs | 3 runs |
| 11.85% | 3 runs | 3 runs | 3 runs |
| 27.70% | 3 runs | 3 runs | 3 runs |
| 35.65% | 3 runs | 3 runs | 3 runs |
| 41.63% | 3 runs | 3 runs | 3 runs |

### Results

The [benchmark CSV](../../notebooks/nb5_uv_cache_lab/cache_benchmark_results.csv) provides the per-strategy measurements and links to the individual runs. The chart compares total job duration with the estimated source-built wheel share:

- **X-axis — Estimated CI-pruned share of the complete cache (%):** For each workload, the median restored CI-pruned cache size divided by the median restored complete cache size, multiplied by 100. The CI-pruned cache is largely the source-built project wheel, making this a proxy for its share of the overall cache. It is not an exact wheel-size measurement: the pruned cache can also contain metadata and other retained artifacts, and the complete cache can contain different representations of the project.
- **Y-axis — Total job duration (seconds):** The time from job start to completion, including post-actions but excluding queue time. Lower values indicate faster jobs. The axis starts at 10 seconds, with 5-second intervals.

The three lines track the *Cold Caching Strategy*, *CI-pruned Strategy*, and *Warm Caching Strategy*. Each workload uses the same estimated reference share for all three lines, including cold runs that do not restore a cache. Each point represents the median of three successful runs, while the error bar spans that strategy's observed minimum and maximum. The separately measured `uv sync` times help distinguish installation time from cache transfers and other work. Comparing these timings with total job duration shows whether a faster installation offsets the cost of restoring a larger cache. Job-duration readings from the GitHub Jobs API have one-second resolution. Cache size is the uncompressed local cache before `uv sync`, not the compressed remote archive; the cold cache was about 1.4 KiB and rounds to 0.00 MiB.

![Total job duration versus estimated CI-pruned share of the complete cache for the cold, CI-pruned, and complete cache strategies, showing medians and ranges](../assets/images/chapter-03/uv-cache-job-duration.svg)

!!! hint "Benchmark Environment"
    The benchmark ran on GitHub-hosted `ubuntu-latest` runners with Python 3.12 and `uv` 0.11.

### Key findings and conclusions

These results illustrate the trade-offs described in [Astral's CI caching guidance](https://docs.astral.sh/uv/concepts/cache/#caching-in-continuous-integration). A larger cache can accelerate dependency installation, but its transfer overhead may outweigh the savings in total job duration.

- **Cache strategy matters:** The CI-pruned cache delivered the shortest median job duration in most larger workload scenarios, while the complete cache consistently provided the fastest `uv sync`.
- **Cache size vs. performance:** The complete cache restored substantially more data (up to 2,461 MiB), but faster dependency installation did not necessarily translate into faster overall jobs.
- **Workload dependency:** The complete cache was competitive at smaller estimated shares, where measurement ranges often overlapped. At the two largest estimated shares, the CI-pruned cache delivered the shortest median job duration.
- **Cache validation:** A restored archive did not always prevent a project rebuild. Stale caches were refreshed, and warm runs that rebuilt the project were excluded from the comparison.
- **Measurement limitations:** Each scenario includes only three runs. Runner performance, cache transfer, and workload execution introduce variability.

**Overall conclusion:** These findings provide a useful indication of how cache strategies can affect CI performance, but they are specific to this project, its dependencies, and the tested GitHub Actions environment. They should not be generalized into a universal ranking. Validate the results against your own workload before choosing a caching strategy.

*Note: Warm-cache measurements reused existing archives without saving new ones; the cold baseline skipped both cache restoration and saving.*
