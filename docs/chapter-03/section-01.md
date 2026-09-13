# Python project management with uv

## Introduction

`uv` is a single self-contained binary written in **Rust**, developed by Astral — the same team behind the `ruff` linter. It was designed to unify Python packaging, dependency management, virtual environments, and tool execution under a single command-line interface. Instead of combining multiple tools such as `pip`, `venv`, `pip-tools`, and `pipx`, developers can use `uv` for the entire workflow.

Because it compiles down to native machine code, it carries no Python runtime dependency of its own and starts in milliseconds. Its rapid adoption is driven by exceptional performance and a streamlined developer experience. Written in Rust, uv executes common packaging operations dramatically faster than traditional Python tooling while remaining fully compatible with the Python packaging ecosystem.

=== "macOS and Linux"

    Download the standalone installer and execute the shell script

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

    It ships as two statically-linked binaries — **`uv`** (main CLI) and **`uvx`** (ephemeral tool runner, equivalent to `pipx run`) — with a total on-disk footprint of ~36 MB. There are no shared libraries, no interpreter bundles, and no background daemons. The global package cache (`~/.cache/uv`) is shared across all projects to avoid redundant downloads (see more about caching in [Section 04](./section-04.md)).

    ```
    /usr/local/bin/
    ├── uv       36 MB   ← main CLI binary (statically linked Rust)
    └── uvx     343 KB   ← tool runner (thin wrapper)
    ```

=== "Windows"

    Download the standalone installer and execute the powershell script

    ```powershell
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

---

Alternatively, `uv` can also be installed from PyPi using `pip`.

```shell
pip install uv
```

This might be more convenient for many developers, however, when installed via `pip`, the wheel format requires a `site-packages` entry. In addition to the two binaries, pip therefore creates `site-packages/uv/` (a Python shim) and `site-packages/uv-<version>.dist-info/` (package metadata). The curl installer produces only the two binaries with no Python packaging overhead.

## Managing legacy Python Projects with the pip interface

Not every code base is a modern, `pyproject.toml`-based project. Legacy projects often still rely on a `requirements.txt` together with `pip` and `venv`. For these cases `uv` exposes a **pip-compatible interface** that mirrors the familiar commands while keeping uv's speed.

Take [*Bob's server*](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/projXY_bobs_webserver/README.md), a small internal web service whose dependencies are pinned in a `requirements.txt`. Setting it up with uv only takes two commands:

```shell
uv venv                            # create a virtual environment (.venv)
uv pip install -r requirements.txt # install the pinned dependencies
```

The service can then be started through uv:

```shell
uv run main.py
```

!!! warning "The pip interface does not manage dependencies"
    `uv pip install` installs packages **into the environment only** — it does not touch `pyproject.toml` or `uv.lock`. uv therefore keeps no record of what was installed and cannot resolve, lock, or verify these dependencies. Installing another package later (for example `uv pip install requests==2.0.0`) can silently downgrade or break an already-installed dependency, and uv has no way to detect the drift. The pip interface is meant for *interacting* with legacy projects, not for *managing* them.

## Managing a modern Python Project

The following commands cover usual tasks during the lifecycle of a Python project.

### Initialize a Project

Create a new project with a default `pyproject.toml`.

```shell
cd ~ && uv init my-project
cd my-project
```

This creates the project structure and initializes Python package metadata.


```shell
/project-folder
└── app
    ├── README.md
    ├── main.py
    └── pyproject.toml
```

The command also sets up an initial cache structure under `/home/user/.cache/uv`. 

### Add Dependencies

`uv` simplifies the integration of dependencies to your project.

```shell
uv add click==1.0.0
```

After the first dependency is added, the project structure looks similar to:

```shell
/project-folder
└── app
    ├── .venv
    ├── README.md
    ├── main.py
    ├── pyproject.toml
    └── uv.lock
```

In a single step, the command resolves dependencies, creates a virtual environment if necessary, installs the packages, adds an entry of the dependency in the `pyproject.toml`, and generates/refreshes the `uv.lock` file (details about `uv.lock` are covered in [Locking](./section-03.md/#locking)).


Dependencies can be added to specific groups, such as development dependencies or to a custom group

```shell
uv add --dev pytest && uv add --group docs mkdocs
```

This adds the dependency to the corresponding section in the `pyproject.toml`:

```toml
[dependency-groups]
dev = [
    "pytest>=7.0.0",
]

docs = [
    "mkdocs>=1.6.0",
]
```

Dependencies can also be installed directly from Git repositories:

```shell
uv add "httpx @ git+https://github.com/encode/httpx"
```

The dependency is added to project.dependencies, while the source information is stored separately:

```toml
[project]
dependencies = [
    "httpx",
]

[tool.uv.sources]
httpx = { git = "https://github.com/encode/httpx" }
```

This allows `uv` to install packages directly from version control systems instead of package registries.

### Remove Dependencies

Remove a dependency from the project.

```shell
uv remove requests
```

This command removes the package from the `pyproject.toml` and updates `uv.lock` to reflect the change. It does not modify the virtual environment — run `uv sync` afterward to clean up the `.venv`.

### Synchronize the Environment

When setting up a project the first time or after pulling dependencies, the `uv sync` command can be used to synchronize the project's virtual environment.

```shell
uv sync
```

This command installs all locked dependencies and ensures that the local environment exactly matches the state described in `uv.lock`. If a virtual environment does not exist, `uv` creates it automatically. It ensures full reproducibility of the project environment and generates the exact same project structure as above.

```shell
/project-folder
└── app
    ├── .venv
    ├── README.md
    ├── main.py
    ├── pyproject.toml
    └── uv.lock
```


### Update the Lock File

Generate or refresh the project's lock file.

```shell
uv lock
```

The command resolves all dependencies defined in `pyproject.toml` and writes the result to `uv.lock` without installing packages into the virtual environment.

During resolution, `uv` may download metadata/wheels into `~/.cache/uv` and create temporary lock files, but it does not install packages into `.venv` or `site-packages`.

This is useful when dependencies have changed and you want to refresh the lock file separately from installation.

### Change the Python version

`uv` can manage Python interpreters directly and integrates it smoothly with the current project context. At first the needed Python version is going to be installed

```bash
uv python install 3.10
```

This downloads a standalone CPython 3.10 build into uv's shared install directory `~/.local/share/uv/python` without replacing the system Python. Afterwards the Python interpreter can be pinned to the project context

```bash
uv python pin 3.10
```

This writes the selected version to a `.python-version` file in the project root. From this point on, every `uv` command run inside the project (`uv sync`, `uv run`, `uv add`, …) will use Python 3.10. The next `uv sync` recreates `.venv` against the pinned interpreter.


### Run commands

`uv` can execute Python scripts and tools directly, without manually activating a virtual environment.

```shell
uv run main.py
```

Before running the command, `uv` ensures the project is ready: it creates the `.venv` if it does not exist, installs or updates dependencies to match `uv.lock`, and uses the pinned Python interpreter. The script is then executed inside that environment.


!!! note "Command invocation"
    The same principle applies to any command, whether it's an installed CLI entry point or a `python -m` invocation