# UV Cache Fundamentals

## Introduction

`uv` uses **aggressive caching** to avoid redundant network requests and wheel builds.
Every resolution, download, and install operation feeds a structured, on-disk cache so that
subsequent runs can skip work that has already been done.

---

## Footprint on Linux

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

### Layer extraction analysis

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

As already mentioned in [Section 04](../chapter-02/section-04.md), `pip` is the traditional Python package 
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
`site-packages` — the same target as `pip install`, but powered by uv's native Rust resolver.
The `--system` flag tells uv to skip virtual-environment creation and write straight into
the interpreter's package directory:

```Dockerfile
RUN uv pip install --system click
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

`root/.cache/uv/` is uv's **structured cache**. Unlike pip's flat HTTP cache, uv organises
artefacts into purpose-specific buckets that will be explored in detail in the [Cache organisation](#cache-organisation) 
section below.

`usr/local/lib/python3.12/site-packages/` contains **only** the `click` package and its
dist-info — no pip binary, no stdlib `.pyc` files. Because uv is a compiled Rust binary,
the Python interpreter is never invoked during the install, so no bytecode compilation
takes place.

The click sources appear in both `archive-v0/` (the cache) and `site-packages/` (the
install target), but uv does not copy the files — it creates **hard-links**, meaning
both paths point to the **same inode** on disk. This can be verified with `ls -li`:

!!! note "Hard-links"
    
    ```
    $ ls -li root/.cache/uv/archive-v0/.../click/core.py \
             usr/local/lib/python3.12/site-packages/click/core.py

    437854 -rw-r--r-- 2 ... 134478 click/core.py   # cache
    437854 -rw-r--r-- 2 ... 134478 click/core.py   # site-packages
    ```
    Both entries share inode `437854` and the link count is `2`. As a result,
    `du` reports the actual disk usage of `site-packages/click/` as **0 bytes** —
    the blocks are already counted under the cache directory.

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
    ├── simple-v12/pypi/                           # cached PyPI index (click + colorama)
    ├── built-wheels-v3/                           # build metadata for the project itself
    └── interpreter-v2/                            # interpreter discovery metadata
└─ app/
    ├── uv.lock                                    # universal lockfile (~4 KB)
    └── .venv/                                     # project-local virtual environment
        ├── bin/                                   # activation scripts (activate, python, …)
        ├── pyvenv.cfg
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