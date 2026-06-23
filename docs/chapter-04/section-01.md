# Modern Python project management with uv

## Introduction

`uv` is a single self-contained binary written in **Rust**, developed by Astral — the same team behind the `ruff` linter. It was designed to unify Python packaging, dependency management, virtual environments, and tool execution under a single command-line interface. Instead of combining multiple tools such as `pip`, `venv`, `pip-tools`, and `pipx`, developers can use `uv` for the entire workflow.

Because it compiles down to native machine code, it carries no Python runtime dependency of its own and starts in milliseconds. Its rapid adoption is driven by exceptional performance and a streamlined developer experience. Written in Rust, uv executes common packaging operations dramatically faster than traditional Python tooling while remaining fully compatible with the Python packaging ecosystem.

=== "macOS and Linux"

    Download the standalone installer and execute the shell script

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

    It ships as two statically-linked binaries — **`uv`** (main CLI) and **`uvx`** (ephemeral tool runner, equivalent to `pipx run`) — with a total on-disk footprint of ~36 MB. There are no shared libraries, no interpreter bundles, and no background daemons. The global package cache (`~/.cache/uv`) is shared across all projects to avoid redundant downloads (see more about caching in [Section-03](./section-02.md)).

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

## Managing a Python Project

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

In a single step, the command resolves dependencies, creates a virtual environment if necessary, installs the packages, adds an entry of the dependency in the `pyproject.toml`, and generates/refreshes the `uv.lock` file (details about `uv.lock` are covered in [uv.lock](./section-02.md/#uvlock)).


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

### Build distributions

The `uv build` command compiles the project into a source distribution (`sdist`) and a wheel, placing both in the `dist/` directory:

```shell
uv build
```

```
dist/
├── my_project-0.1.0.tar.gz              ← source distribution
└── my_project-0.1.0-py3-none-any.whl   ← wheel
```

### Publish packages

The `uv publish` command uploads the distribution files from `dist/` to PyPI using the `--token` for authentication and the `--publish-url` to override the target registry:

```shell
uv publish --token pypi-<your-token> --publish-url https://test.pypi.org/legacy/
```

## Build and Publishing Packages

## Handling multiple projects with uv

### Introduction into uv workspaces

When multiple related projects must be developed and tested together, a consistent shared environment becomes essential. For scenarios like this, `uv` provides the concept of **[workspaces](https://docs.astral.sh/uv/concepts/projects/workspaces/)**. A workspace allows multiple related Python projects to coexist within a single repository while remaining independent packages. All workspace members share a common `uv.lock` file, ensuring a consistent dependency set across the entire workspace. At the same time, each member maintains its own `pyproject.toml`, allowing project-specific configuration and metadata.

### Structure and Members

A workspace consists of a root project that defines the workspace itself and one or more workspace members. In the following example, the plugin is the workspace root and the `depsight-dependency-manager` framework lives as a workspace member beneath it:

```text
depsight-third-party-plugin/
├── pyproject.toml
├── uv.lock
├── src/
│   └── depsight_third_party_plugin
│
└── depsight-dependency-manager/
    ├── pyproject.toml
    └── src/
        └── depsight_dependency_manager
```

The workspace root (`depsight-third-party-plugin`) owns the shared `uv.lock` and a `pyproject.toml` that both declares the framework as a workspace member and pins it as a local source, so `uv` resolves it from the workspace instead of PyPI.

```toml
[tool.uv.workspace]
members = [
    "depsight-dependency-manager",
]

[tool.uv.sources]
depsight-dependency-manager = { workspace = true }
```

To invoke dedicated workspace members such as the `depsight-dependency-manager` framework you can simply use the `uv run --package depsight-dependency-manager` command. 
