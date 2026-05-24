# Dependency Management with Python


## Dependency Management

### Dependency Hell

Modern Python applications are built on top of third-party packages. A web service might use `requests` for HTTP, `pydantic` for validation, and `sqlalchemy` for database access — none of which ship with Python itself. Managing these external libraries across different developers, machines, and deployment environments is called **dependency management**.

As covered in [Chapter 02](../chapter-02/index.md), today's standard for declaring project metadata and dependencies is `pyproject.toml`. A minimal project looks like this:

```toml
[project]
name = "myapp"
version = "1.0.0"
requires-python = ">=3.11"
dependencies = [
    "requests>=2.0",
    "old-sdk>=1.0",
]
```

On the surface the declarations look fine — until you look at what each library itself pulls in:

```
myapp
├── requests 2.31.0
│   └── urllib3 >=1.21.1, <2
└── old-sdk 1.0.0
    └── urllib3 >=2.0        ← conflict!
```

Both `requests` and `old-sdk` depend on `urllib3`, but require incompatible versions. They cannot be installed together, and `pip` will fail with:

```
ERROR: Cannot install requests and old-sdk because these package versions have conflicting dependencies.
```

This is **dependency hell** — conflicting version constraints between transitive dependencies that make it impossible to assemble a working environment.

The `requires-python` field has the same fundamental weakness. It sets a lower bound on the interpreter, but does not pin or manage it. On one developer's machine the project runs on Python 3.11, on another 3.13, and in the CI container something else entirely — each with different standard library behaviour and package compatibility.

Even without an outright conflict, the environment is still fragile. Version ranges like `requests>=2.0` resolve to whatever is newest at install time, meaning two developers a week apart may end up with different packages, on different interpreters, in different `site-packages` directories.

All three dimensions — package versions, interpreter version, and environment isolation — need to be controlled to guarantee a reproducible build.

### Lockfiles and Environment Isolation

A **lockfile** solves this by recording the exact resolved versions of every package — direct and transitive — along with a cryptographic hash for each. Anyone installing from that lockfile gets an identical environment, regardless of when they do it:

```
# lockfile (abstract)
requests              2.31.0    sha256:58cd2187...
urllib3               1.26.18   sha256:34b174d6...
certifi               2024.2.2  sha256:abc12345...
charset-normalizer    3.3.2     sha256:def67890...
```

There is also the problem of **environment isolation**. Without it, all Python projects on a machine share the same `site-packages` directory. Upgrading `requests` for one project can silently break another that relies on an older version. Virtual environments solve this by giving each project its own independent package directory:

```
project-a/
└── .venv/    ← requests 2.31.0, urllib3 1.26.18
project-b/
└── .venv/    ← requests 2.28.0, urllib3 1.26.14  (independent)
```

`pyproject.toml` alone provides none of this — no lockfile generation, no guaranteed resolution across time, no environment or interpreter management. That is where dependency managers come in.

### Dependency Management Tools

Each manager builds on `pyproject.toml` and adds the missing pieces — but not all of them to the same degree.

#### pip

Released in **2008**, `pip` became the standard way to install Python packages and remains bundled with every Python installation today. For a long time it was the only tool most projects needed: declare dependencies in `pyproject.toml` (or the older `setup.py`), run `pip install`, and get packages from PyPI.

To get reproducible installs, developers manually maintained a `requirements.txt` file with pinned versions:

```text
# requirements.txt
requests==2.31.0
urllib3==1.26.18
certifi==2024.2.2
```

This works for simple cases, but has significant gaps. The file is hand-maintained — there is no tooling to generate or verify it automatically. It captures only what the developer explicitly pins, not the full transitive graph. And `pip` installs everything into the active Python environment with no isolation, so dependencies bleed across projects.

**Drawbacks:** no automatic lockfile, no virtual environment management, no interpreter pinning — reproducibility depends entirely on developer discipline.

---

#### pipenv

Released in **2017**, `pipenv` was the first tool to unify package management and virtual environment handling. It introduced two dedicated files: `Pipfile` for human-readable declarations and `Pipfile.lock` as an automatically generated lockfile covering the full transitive dependency graph with cryptographic hashes.

Running `pipenv install` creates a project-scoped virtual environment automatically and writes the resolved graph to `Pipfile.lock`:

```json
{
    "default": {
        "requests": {
            "version": "==2.31.0",
            "hashes": ["sha256:58cd2187..."]
        },
        "urllib3": {
            "version": "==1.26.18",
            "hashes": ["sha256:34b174d6..."]
        },
        "certifi": {
            "version": "==2024.2.2",
            "hashes": ["sha256:abc12345..."]
        }
    }
}
```

This solved the reproducibility and isolation problems that `pip` left open.

**Drawbacks:** `pipenv`'s dependency resolver was notoriously slow on larger projects, and it does not support building or publishing packages — the workflow stops at dependency management. These limitations drove adoption towards `poetry`.

---

#### poetry

Released in **2018**, `poetry` unified the entire Python project workflow — dependency resolution, virtual environment management, building, and publishing — in a single tool backed by `pyproject.toml`. Its resolver is significantly faster than `pipenv`'s and generates a `poetry.lock` file in a structured TOML format that captures the full dependency graph with per-file hashes:

```toml
[[package]]
name = "requests"
version = "2.31.0"
description = "Python HTTP for Humans."
files = [
    {file = "requests-2.31.0-py3-none-any.whl", hash = "sha256:58cd2187..."},
]

[package.dependencies]
urllib3 = ">=1.21.1,<3"
certifi = ">=2017.4.17"

[[package]]
name = "urllib3"
version = "1.26.18"
files = [
    {file = "urllib3-1.26.18-py2.py3-none-any.whl", hash = "sha256:34b174d6..."},
]
```

**Drawbacks:** `poetry` still relies on an external tool (e.g. `pyenv`) to manage the Python interpreter itself, and its resolver — while better than `pipenv`'s — is written in Python and becomes a bottleneck on large dependency trees. These gaps motivated `uv`.

---

#### Summary

| Tool | Introduced | Lockfile | Env Isolation | Interpreter Mgmt | Full Lifecycle |
|------|------------|:--------:|:-------------:|:----------------:|:--------------:|
| `pip` | 2008 | ✗ | ✗ | ✗ | ✗ |
| `pipenv` | 2017 | ✓ | ✓ | ✗ | ✗ |
| `poetry` | 2018 | ✓ | ✓ | ✗ | ✓ |
| `uv` | 2024 | ✓ | ✓ | ✓ | ✓ |

---

## uv

> Introduced: **2024**

`uv` was built to solve the performance bottleneck that affected all previous Python dependency resolvers. Written in Rust by the team behind Ruff, it resolves and installs packages dramatically faster than `pip` or `poetry`, while maintaining a global cache that avoids redundant downloads across projects.

Beyond raw speed, `uv` consolidates the entire Python project lifecycle: it manages Python interpreter versions, creates virtual environments, resolves and locks dependencies, and runs scripts — replacing `pyenv`, `virtualenv`, `pip`, and `poetry` with a single binary. It is fully compatible with `pyproject.toml` and can also consume `requirements.txt` files, making migration straightforward.

| | |
|---|---|
| **Strengths** | Extremely fast resolution and installation, unified single-tool workflow, global dependency cache, strong CI/CD integration |
| **Weaknesses** | Younger ecosystem, some advanced features still stabilising |

**Key files:**

| Filename | Description |
|----------|-------------|
| `pyproject.toml` | Project metadata and dependency declarations |
| `uv.lock` | Fully resolved dependency versions and hashes for reproducible installs |
| `.venv` | Virtual environment created and managed by `uv` |

Dependencies are declared in the standard `[project]` table of `pyproject.toml`:

```toml
[project]
name = "myapp"
version = "1.0.0"
requires-python = ">=3.11"
dependencies = [
    "requests>=2.31.0",
]

[dependency-groups]
dev = [
    "pytest>=7.4.0",
]
```

`uv.lock` uses a structured TOML format and records every resolved package with its source and hashes:

```toml
version = 1
requires-python = ">=3.11"

[[package]]
name = "requests"
version = "2.31.0"
source = { registry = "https://pypi.org/simple" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/.../requests-2.31.0-py3-none-any.whl", hash = "sha256:58cd2187..." },
]
```

---

## Summary

The Python dependency management landscape evolved from manual `pip` installs and hand-maintained `requirements.txt` files, through `pipenv`'s introduction of true lockfiles, to the unified workflows of `poetry` and the high-performance tooling of `uv`. Each tool raised the bar for reproducibility and developer experience — the common thread running through all of them is `pyproject.toml` as the shared project declaration format.
