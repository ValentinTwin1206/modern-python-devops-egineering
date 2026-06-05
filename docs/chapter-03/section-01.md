# Common Dependency Management
## Dependency Management
### Dependency Hell

Modern Python applications are built on top of third-party packages that are not shipped with Python itself. Managing these external libraries across different developers, machines, and deployment environments is called **dependency management**.

As covered in [Chapter 02](../chapter-02/index.md), today's standard for declaring project metadata and dependencies is the `pyproject.toml`. A minimal project looks like this:

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
├── requests 2.28.0
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
requests              2.28.0    sha256:58cd2187...
urllib3               2.0.0     sha256:34b174d6...
charset-normalizer    3.3.2     sha256:def67890...
```

There is also the problem of **environment isolation**. Without it, all Python projects on a machine share the same `site-packages` directory. Upgrading `requests` for one project can silently break another that relies on an older version. Virtual environments solve this by giving each project its own independent package directory:

```
project-a/
└── .venv/    ← requests 2.28.0, urllib3 2.0.0
project-b/
└── .venv/    ← requests 2.25.0, urllib3 1.26.14  (independent)
```

`pyproject.toml` alone provides none of this — no lockfile generation, no guaranteed resolution across time, no environment or interpreter management. That is where dependency managers come in.

### Dependency Management Tools

Each manager builds on `pyproject.toml` and adds the missing pieces — but not all of them to the same degree.

#### pip

Released in **2008**, `pip` became the standard way to install Python packages and remains bundled with every Python installation today. It covers the basics but provides no lockfile generation, no virtual environment management, and no interpreter pinning. Reproducibility depends entirely on developer discipline.

To get reproducible installs, developers manually maintained a `requirements.txt` file with pinned versions:

```text
# requirements.txt
requests==2.28.0
urllib3==2.0.0
```

These two versions are already inconsistent: `requests 2.28.0` requires `urllib3<1.27`, but `urllib3==2.0.0` is pinned — `pip` will not catch this until installation. This file is hand-maintained: there is no tooling to generate or verify it automatically, and it captures only what the developer explicitly pins — not the full transitive graph.

In **2019**, `pip` introduced `pip check`, which validates that all installed packages have their dependencies satisfied in the current environment:

```bash
$ pip check
requests 2.28.0 has requirement urllib3<1.27,>=1.21.1, but you have urllib3 2.0.0.
```

However, `pip check` only detects inconsistencies after the fact — it does not prevent them. Existing environments in an inconsistent state are not repaired automatically.

With **pip 20.3** (released **2020**), `pip` gained a backtracking resolver that warns about conflicts at install time. However, it still installs the conflicting package and leaves the environment broken:

```bash
$ pip install "urllib3==2.0.0"
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed.
requests 2.28.0 requires urllib3<1.27,>=1.21.1, but you have urllib3 2.0.0 which is incompatible.
Successfully installed urllib3-2.0.0
```

#### pipenv

Released in **2017**, `pipenv` was the first tool to unify package management and virtual environment handling. It introduced two dedicated files: `Pipfile` for human-readable declarations and `Pipfile.lock` as an automatically generated lockfile covering the full transitive dependency graph with cryptographic hashes.

Running `pipenv install` creates a project-scoped virtual environment automatically and writes the resolved graph to `Pipfile.lock`:

```json
{
    "default": {
        "requests": {
            "version": "==2.28.0",
            "hashes": ["sha256:58cd2187..."]
        },
        "urllib3": {
            "version": "==2.0.0",
            "hashes": ["sha256:34b174d6..."]
        }
    }
}
```

In contrast, when the same conflicting packages are specified, `pipenv` refuses to lock rather than creating a broken environment:

```bash
$ pipenv install -r requirements.txt
✘ Locking Failed!
The conflict is caused by:
    The user requested urllib3==2.0.0
    requests 2.28.0 depends on urllib3<1.27 and >=1.21.1
ERROR: ResolutionImpossible
```

`pipenv` solved the reproducibility and isolation problems that `pip` left open, but introduced its own limitations: its dependency resolver was notoriously slow on larger projects, and the workflow stops at dependency management — building and publishing packages are out of scope. These gaps drove adoption towards `poetry`, which aimed to cover the full project lifecycle in a single tool.

#### poetry

Released in **2018**, `poetry` unified the entire Python project workflow — dependency resolution, virtual environment management, building, and publishing — in a single tool backed by `pyproject.toml`. Its resolver is significantly faster than `pipenv`'s and generates a `poetry.lock` file in a structured TOML format that captures the full dependency graph with per-file hashes:

```toml
[[package]]
name = "requests"
version = "2.28.0"
description = "Python HTTP for Humans."
files = [
    {file = "requests-2.28.0-py3-none-any.whl", hash = "sha256:58cd2187..."},
]

[package.dependencies]
urllib3 = ">=1.21.1,<3"
certifi = ">=2017.4.17"

[[package]]
name = "urllib3"
version = "2.0.0"
files = [
    {file = "urllib3-2.0.0-py3-none-any.whl", hash = "sha256:34b174d6..."},
]
```

`poetry` builds a complete dependency graph before installing, resolving the full transitive tree and detecting conflicts upfront — not just for direct dependencies.

**Drawbacks:** `poetry` still relies on an external tool (e.g. `pyenv`) to manage the Python interpreter itself, and its resolver — while better than `pipenv`'s — is written in Python and becomes a bottleneck on large dependency trees. These gaps motivated `uv`.
