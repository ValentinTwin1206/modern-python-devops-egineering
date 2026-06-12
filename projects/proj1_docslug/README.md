# Docslug

This section introduces *Docslug* as a small Python library that turns headings, titles, and filenames into stable slugs for URLs, documentation pages, and generated files, while demonstrating how a pure-Python package can be developed with `venv` and `uv`, distributed as a wheel, and published to PyPI.

## Project Components

The table below lists the main files that support the `venv` example project.

| Component | Description |
| --------- | ----------- |
| [Dockerfile.devEnv](Dockerfile.devEnv) | This development image installs `uv`, syncs the `dev` dependency group, and opens an interactive shell with the project virtual environment on `PATH`. It provides a reproducible containerized setup for the library workflow. |
| [pyproject.toml](pyproject.toml) | This file defines the package metadata, the `uv_build` build backend, and the development dependency group for Karva and Ruff. It is the main configuration file for the library-style project layout. |
| [src/docslug/](src/docslug/) | This source package holds the reusable slug helpers that end users import from their own applications. The `src` layout keeps imports honest by ensuring tests exercise the installed package shape rather than the repository root. |
| [tests/](tests/) | This directory contains the automated tests for the pure-Python slug helpers. It gives Karva a small but realistic library test surface without introducing any runtime dependencies. |

## End-User Guide

This section shows how an end user installs and uses `docslug` as a published Python library from PyPI.

### Requirements

- Python 3.12 or newer.
- `uv` if you install from `pyproject.toml`.
- `pip`, or another installer that reads `requirements.txt` files.

### Installation

Add `docslug` to your project metadata when you manage dependencies with `uv`:

```toml
[project]
dependencies = [
	"docslug==1.0.0",
]
```

Sync the environment with `uv`:

```bash
uv sync
```

If your project uses a `requirements.txt` file instead, add the published package there:

```text
docslug==1.0.0
```

Install the requirements with `pip`:

```bash
python -m pip install -r requirements.txt
```

### Usage

Create a filesystem-safe slug from a document title:

```python
from docslug import slugify

print(slugify("Release Notes: Summer 2026"))
```

Create a unique slug when a name already exists:

```python
from docslug import unique_slug

existing = {"release-notes-summer-2026", "release-notes-summer-2026-2"}
print(unique_slug("Release Notes: Summer 2026", existing))
```

Build a nested slug path for generated documentation:

```python
from docslug import slug_path

print(slug_path("Guides", "API Reference"))
```

## Developer Guide

### Setup Environment

Use the development image in [Dockerfile.devEnv](Dockerfile.devEnv) to open an interactive shell with `uv` and the project environment already prepared. Run the following command from the `projects/` directory through the shared helper:

```bash
../build.sh build --path proj1_docslug/Dockerfile.devEnv
```

### Sync Environment

Within the running container, you can sync the project environment with `uv`:

```bash
uv sync --all-groups
```

Then source the virtual environment so the installed tools are on `PATH`:

```bash
source .venv/bin/activate
```

### Run Tests

Within the active virtual environment, you can run the test suite with Karva:

```bash
karva test tests/
```

### Lint

Within the active virtual environment, you can run Ruff against the source tree:

```bash
ruff check .
```

### Build Guide

The project is shipped as a pure-Python wheel so that end users can install it directly from PyPI through `pyproject.toml` or `requirements.txt` without building from source.

#### Build the Wheel

Build the wheel artifact from the project root:

```bash
uv build --wheel --out-dir /build
```

The wheel is written inside the container to `/build` and appears on the host at:

```text
.build/docslug-1.0.0-py3-none-any.whl
```

#### Upload to PyPI

Upload the built distribution to PyPI with `uv`:

```bash
uv publish
```

`uv publish` reads the PyPI authentication settings from your environment or your configured credential store, so no extra publishing dependency is needed inside the project itself.