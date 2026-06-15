# Dependency Caching with uv

## Introduction

`uv` uses **aggressive caching** to avoid redundant network requests and wheel builds.
Every resolution, download, and install operation feeds a structured, on-disk cache so that
subsequent runs can skip work that has already been done.

---

## Cache footprint on Linux

Before exploring the cache layout itself, it is important to understand **what gets written
to disk** when you install a package. This section gives a brief overview of the artifacts
and libraries that end up on the system.

The following comparison installs a single, dependency-free library — `click` — and
examines the resulting footprint for three installation routines: 

* `pip`
* `uv pip install`
* `uv sync`

!!! note "Cache directory"
    By default, `uv` stores its cache in `$HOME/.cache/uv`. This can be changed with the
    `--cache-dir` flag or the `tool.uv.cache-dir` setting in `pyproject.toml`.

For the sake of comparison each of the three commands had been executed inside the `python:3.12-slim` 
container image. The resulting last layer, produced by the install command, was
then exported and inspected to extract file counts, sizes, and artifacts.

The general approach starts by exporting the finished image into a tar archive and
unpacking it:

```bash
docker save "$IMAGE" -o image.tar
tar -xf image.tar -C image/
```

This produces a directory containing one tar per layer plus a `manifest.json` that
lists them in order. The last entry in that list corresponds to the install command,
so it can be read directly:

```bash
LAST_LAYER=$(jq -r '.[0].Layers[-1]' image/manifest.json)
```

Extracting that single layer into an empty directory and measuring it gives the
file count and total size attributable to the install step alone:

```bash
tar -xf "image/${LAST_LAYER}" -C layers/
find layers/ -type f | wc -l        # file count
du -sh layers/                       # total size on disk
```

Because each Dockerfile instruction creates exactly one layer, this isolates
the files written by `pip install`, `uv pip install`, or `uv sync` — making
a direct, apples-to-apples comparison possible.

### Using pip install

As already mentioned in [Section 04](../chapter-03/section-04.md), `pip` is the traditional Python package 
manager and is itself a Python package. 
The installation of `click` is straight forward and the installation command inside ``Dockerfile`` looks like
the following

```Dockerfile
RUN pip install click
```

The extracted layer reveals two distinct areas that were written to disk:

```
└─ root/.cache/pip/                       # pip's own HTTP cache
    ├── http-v2/                          # cached PyPI responses
    └── selfcheck/                        # pip version check data
└─ usr/local/lib/python3.12/
    ├── __pycache__/                      # top-level stdlib .pyc files
    ├── collections/, email/, encodings/  # stdlib packages touched at runtime
    ├── html/, ..., urllib/               # ...
    └── site-packages/
        ├── click/                        # target package (~892 KB)
        ├── click-8.3.3.dist-info/
        └── pip/                          # pip itself (~4.8 MB)
```

`root/.cache/pip/` is pip's **HTTP response cache**. Every request to PyPI is stored here
so that repeated installs can serve responses locally. Unlike `uv`, pip does not hard-link 
installed packages from this cache — it is purely a download artefact.

`usr/local/lib/python3.12/` contains two categories of new files. First, the stdlib
`.pyc` bytecode — 158 compiled modules across packages like `http`, `email`, `urllib`,
`json`, and `re` — totalling ~4.3 MB. Second, `site-packages/` holds both the target package
`click` (~892 KB) and `pip` itself (~4.8 MB), which ships pre-installed in the image but
gets modified during the install.

!!! note "`.pyc` files"
    When `pip` runs, the CPython interpreter imports dozens of stdlib modules (http.client, urllib, email, hashlib, zipfile, …) to handle HTTP requests, checksum verification, and wheel unpacking. Each first-time import compiles the module and writes a `.pyc` bytecode file into `__pycache__/`. 

### Using uv pip install

`uv` provides a `pip`-compatible interface that installs packages directly into the system
`site-packages`:

```Dockerfile
RUN uv pip install --system click  # skips installation inside a venv 
```

The extracted layer reveals two areas:

```
└─ root/.cache/uv/                                 # uv structured cache (~584 KB)
    ├── archive-v0/                                # unpacked wheel archive (~452 KB)
    │   └── click/    
    ├── wheels-v1/pypi/click/                      # downloaded wheel + HTTP metadata
    ├── simple-v12/pypi/                           # cached PyPI Simple API index
    └── interpreter-v2/                            # interpreter discovery metadata
└─ usr/local/lib/python3.12/site-packages/
    ├── click/                                     # target package (~420 KB)
    └── click-8.3.3.dist-info/
```

`root/.cache/uv/` is uv's **structured cache** with purpose-specific buckets that will be explored in detail in the [Cache organisation](#cache-organisation) section below.

`usr/local/lib/python3.12/site-packages/` contains **only** the `click` package and its
dist-info. Because uv is a compiled Rust binary, the Python interpreter is never 
invoked during the install, so no bytecode compilation takes place.

The click sources appear in both `archive-v0/` (the cache) and `site-packages/` (the
install target), but uv does not copy the files — it creates **hard-links**, meaning
both paths point to the **same inode** on disk.

### Using uv sync

The `uv sync` command is a **project-aware** workflow command that reads dependencies from a `pyproject.toml`, resolves
them into a universal lockfile (`uv.lock`), and installs everything into a project-local
`.venv`. The `pyproject.toml` used here declares a single dependency:

```toml
[project]
name = "uv-cache-demo"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["click"]
```

The install command:

```Dockerfile
RUN uv sync
```

The extracted layer reveals two areas:

```
└─ root/.cache/uv/                                 # uv structured cache (~668 KB)
    ├── archive-v0/                                # unpacked wheel archive (~452 KB)
    │   └── click/
    ├── wheels-v1/pypi/                            # downloaded wheels + HTTP metadata
    │   ├── click/
    │   └── colorama/                              # resolved for universal lock
    ├── ...
└─ app/
    ├── uv.lock                                    # universal lockfile (~4 KB)
    └── .venv/                                     # project-local virtual environment
        ├── ...
        └── lib/python3.12/site-packages/
            ├── click/                             # target package (~420 KB)
            ├── click-8.3.3.dist-info/
            └── _virtualenv.py
```

`root/.cache/uv/` follows the same bucket layout as the previous section. Two differences
stand out: `simple-v12/` now caches index data for both `click` and `colorama`,
and `built-wheels-v3/` contains build metadata for the project root itself.

`app/` holds the project-level artefacts like the `uv.lock` file that pins the
full dependency graph across all platforms. The `.venv/` directory is a standard virtual
environment created by uv containing the `site-packages/` with the installed packages. Also the 
click files in `.venv/site-packages/` are **hard-linked** from `archive-v0/` in the cache, 
so no bytes are duplicated on disk.

!!! note "Why is colorama in the cache but not in `.venv`?"
    The universal lockfile resolves `colorama` because it is a click dependency on Windows.
    uv downloads and caches the wheel metadata (`wheels-v1/` and `simple-v12/`), but since
    the install runs on Linux, `colorama` is never actually unpacked into `archive-v0/` or
    installed into `.venv/site-packages/`.

### Summary

The table below condenses the three layer extractions into a side-by-side comparison.
The contrast is stark: `pip` pulls in its own runtime, compiles stdlib bytecode, and
bloats the layer by an order of magnitude, while both `uv` approaches keep the footprint
close to the size of the target package itself.

| Metric | pip | uv pip install | uv sync |
|---|---|---|---|
| Install time | ~7 482 ms | ~346 ms | ~4 192 ms |
| Layer size | ~11 MB | ~640 KB | ~800 KB |
| File count | 518 | 56 | 74 |
| site-packages size | ~5.7 MB | ~452 KB | ~464 KB |

--- 

## Cache organisation

The cache lives under `~/.cache/uv/` (or the path set via `UV_CACHE_DIR`) and is split
into **typed, versioned buckets**. Each bucket handles one kind of artifact; the version
suffix (e.g. `-v5`) is bumped whenever the on-disk format changes, so different uv
versions can share the same cache root safely.

```
~/.cache/uv/
├── archive-v0/       ← unpacked wheel trees (hard-link source)
├── builds-v0/        ← temporary build workspace
├── git-v0/           ← bare git clones + checkouts
├── interpreter-v4/   ← Python interpreter metadata
├── sdists-v9/        ← source distributions & source-built wheels
├── simple-v16/       ← PyPI Simple API index responses
└── wheels-v5/        ← downloaded pre-built wheels
```

Which buckets are populated depends entirely on **where the dependency comes from**.
The following examples each install a single package from a different source and show
the resulting cache tree.

**Git source with setuptools backend**

The legacy build backend forces uv to pull setuptools as a build dependency, inflating `archive-v0/`:

```Dockerfile
RUN uv pip install --system \
  "markupsafe @ git+https://github.com/pallets/markupsafe.git@3.0.2"
```

```
~/.cache/uv/
├── git-v0/
│   ├── db/<hash>/                   # bare clone of pallets/markupsafe
│   ├── checkouts/<hash>/28ace20/    # working tree at the pinned commit
│   └── locks/
├── sdists-v9/git/                   # wheel built from git source
├── wheels-v5/pypi/setuptools/       # setuptools fetched from PyPI (build dep)
├── simple-v16/pypi/                 # PyPI index for setuptools resolution
├── archive-v0/
│   ├── <hash-a>/markupsafe/         # unpacked target wheel (~68 KB)
│   └── <hash-b>/setuptools/         # unpacked build dep (~4.6 MB)
└── builds-v0/                       # empty after build
```

**Git source with modern backend (flit)**

No setuptools needed, so `archive-v0/` stays small:

```Dockerfile
RUN uv pip install --system \
  "tomli @ git+https://github.com/hukkin/tomli.git@2.2.1"
```

```
~/.cache/uv/
├── git-v0/
│   ├── db/<hash>/
│   ├── checkouts/<hash>/73c3d10/
│   └── locks/
├── sdists-v9/git/                   # wheel built from git source
├── wheels-v5/pypi/flit-core/        # flit-core from PyPI (build dep)
├── simple-v16/pypi/
├── archive-v0/
│   ├── <hash-a>/tomli/              # unpacked target wheel
│   └── <hash-b>/flit_core/          # unpacked build dep (~284 KB)
└── builds-v0/
```

!!! note "Takeaway"
    Packages with modern build backends (`flit`, `hatchling`, `maturin`) keep the
    build-dependency footprint in `archive-v0/` minimal compared to setuptools.

**Default index vs explicit `--index-url`**

uv keys cache entries by index URL. Using the built-in default *and* an explicit `--index-url` pointing to the same PyPI creates **duplicate** entries:

```Dockerfile
RUN uv pip install --system click \
  && uv pip install --system --reinstall \
     --index-url https://pypi.org/simple/ click
```

```
~/.cache/uv/
├── wheels-v5/
│   ├── pypi/click/                       # from default index
│   └── index/<digest>/click/             # from explicit --index-url (same PyPI!)
├── simple-v16/
│   ├── pypi/                             # default index metadata
│   └── index/                            # duplicate index metadata
└── archive-v0/
    ├── <hash-a>/click/                   # unpacked wheel (default)
    └── <hash-b>/click/                   # unpacked wheel (duplicate)
```

!!! warning "Avoid mixing index styles"
    Stick to **one** way of referencing each index. Mixing the default PyPI with an
    explicit `--index-url https://pypi.org/simple/` doubles cache usage for no benefit.

**Direct URL**

A wheel fetched from a URL is cached under `wheels-v5/url/`, keyed
by a hash of the URL. No `simple-v16/` entry is created because there is no index
to query:

```Dockerfile
RUN uv pip install --system \
  "click @ https://files.pythonhosted.org/packages/7e/d4/...click-8.1.8-py3-none-any.whl"
```

```
~/.cache/uv/
├── wheels-v5/
│   └── url/<digest>/click/               # wheel metadata + HTTP cache
└── archive-v0/
    └── <hash>/click/                     # unpacked wheel
```

!!! note "Direct URLs vs index installs"
    uv cannot de-duplicate a direct-URL wheel against the same version fetched from
    an index — they live in separate namespaces and are cached independently.

---

## Cache versioning across uv upgrades

Each bucket name includes a version suffix (e.g. `wheels-v5`). When a new uv release
changes the internal format of a bucket, it increments the suffix and writes to a new
directory. The old one remains on disk untouched.

There are two possible outcomes when upgrading uv, depending on whether bucket versions
changed:

**Breaking upgrade (e.g. 0.4.0 → 0.7.8)** — bucket versions differ. The new uv
ignores the old buckets and re-downloads everything from the network. After the
install, both old and new bucket directories coexist on disk, effectively doubling
cache usage.

**Compatible upgrade (e.g. 0.4.11 → 0.4.12)** — bucket versions are identical.
The cache built by the older version is fully readable by the newer one. This can be
proven by copying the old cache into a fresh environment and installing without any
network access:

```Dockerfile
COPY --from=cache-builder /root/.cache/uv /root/.cache/uv

RUN --network=none uv pip install --offline --system click
```

The install succeeds entirely from cache — no duplicated buckets, no re-download.

---

## Cache maintenance

uv ships two commands to manage cache disk usage:

```bash
uv cache clean
```

This wipes the entire cache. Every bucket is deleted, regardless of
version. Subsequent installs must re-download and rebuild everything from scratch.

```
Clearing cache at: /home/user/.cache/uv
Removed 31 files (463.2KiB)
```

```bash
uv cache prune
```

This removes only stale bucket directories that the running uv
version can no longer read. Current-version buckets and valid `archive-v0/` entries
are left intact.

```
Pruning cache at: /home/user/.cache/uv
Removed 12 files (148.8KiB)
```
