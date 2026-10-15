# Project Scaffolding with uv

## Introduction

This section shows how to use `uv` to scaffold a multi-project workspace, initialize its backend and frontend components, and configure project metadata and shared workspace settings in `pyproject.toml` and `uv.lock`. The example pairs a Bottle backend with a Streamlit frontend.

## The Modern Python Standard

The `pyproject.toml` is the modern standard to describe a Python project. [PEP 518](https://peps.python.org/pep-0518/) established it for build-system requirements, [PEP 621](https://peps.python.org/pep-0621/) standardized project metadata, and [PEP 735](https://peps.python.org/pep-0735/) standardized dependency groups. Together with tool-specific settings, these entries bring project metadata, build configuration, and dependency declarations that were often scattered across `setup.py`, `setup.cfg`, and `requirements.txt` into one clear source of truth. Exact resolved versions belong in the lockfile, which helps keep installations consistent and reduces environment drift.

`uv` builds its project workflows around `pyproject.toml` and the lockfile. It writes project metadata and dependency declarations to the project file and uses the lockfile to keep environments consistent. A small web backend could keep these settings together in one file:

```toml
[build-system]
requires = ["uv_build>=0.11.8,<0.12"]
build-backend = "uv_build"

[project]
name = "example-web-app"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "bottle>=0.13",
]

[dependency-groups]
dev = [
    "pytest>=8.0",
    "ruff>=0.15",
]

[tool.ruff]
line-length = 88
```

## Install uv

`uv` is distributed as a single, self-contained static binary and can be installed without Python already present.

=== "macOS and Linux"

    Run the standalone installer in a terminal:

    ```shell
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

=== "Windows"

    Run the standalone installer in PowerShell:

    ```powershell
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

Check that the command is available:

```shell
uv --version
```

## Manage Python with uv

Like [`nvm`](https://github.com/nvm-sh/nvm) for Node.js and [`rustup`](https://rust-lang.github.io/rustup/) for Rust, `uv` can install and select interpreter versions without replacing the system interpreter. Use the `uv python` commands to manage interpreters. Install version 3.12 alongside the system interpreter:

```shell
uv python install 3.12
```

On Linux, `uv` stores managed interpreter files in `~/.local/share/uv/python` by default. Run `uv python dir` to see the configured installation directory. The home-directory path varies by user:

```shell
uv python dir
```

## Set Up an uv Workspace

### Create the Workspace

A [uv workspace](https://docs.astral.sh/uv/concepts/projects/workspaces/) groups related projects under one root. Each component keeps its own `pyproject.toml`, while the workspace shares one `uv.lock` and resolves dependencies together. Here the workspace contains an HTTP backend and a browser-facing frontend; neither component depends on the other yet.

Initialize the workspace root as a bare project using Python 3.12. The root project owns the workspace configuration and the shared lockfile:

```shell
uv init --bare --python 3.12 --vcs none uv-workspace
```

Create directories for the two workspace members:

```shell
mkdir -p uv-workspace/backend uv-workspace/frontend
```

After both components are initialized, the root `pyproject.toml` lists them as workspace members. Each member owns its project metadata, dependencies, and local interpreter pin. The first dependency resolution creates the single root `uv.lock`.

### Pin Python for the Components

Both workspace members use Python 3.12. A `.python-version` file selects the interpreter for local commands; `requires-python` in each `pyproject.toml` declares the versions supported by that project. Workspace members must have compatible `requires-python` requirements, and using the same pin here makes that relationship explicit.

=== "Backend"

    `--no-project` writes the pin before the member's `pyproject.toml` exists:

    ```shell
    uv --directory uv-workspace/backend python pin --no-project 3.12
    ```

=== "Frontend"

    Use the same Python version for the frontend member:

    ```shell
    uv --directory uv-workspace/frontend python pin --no-project 3.12
    ```

### Initialize the Workspace Components

Initialize each member as a packaged application. The template creates project metadata and starter package files; this section uses that generated scaffolding without implementing application modules.

=== "Backend"

    The backend is a Python application that will provide HTTP endpoints. Initialize it as a packaged application, disabling Git initialization because the workspace root is the repository:

    ```shell
    uv init --app --package --vcs none --author-from none uv-workspace/backend
    ```

    When run inside an existing project, `uv init` discovers the workspace and registers the new project as a member. Inspect the member configuration:

    ```shell
    cat uv-workspace/backend/pyproject.toml
    ```

=== "Frontend"

    The frontend will provide a small interactive UI with [Streamlit](https://streamlit.io/). Initialize it as a separate packaged application in the same workspace:

    ```shell
    uv init --app --package --vcs none --author-from none uv-workspace/frontend
    ```

    Inspect the generated project metadata:

    ```shell
    cat uv-workspace/frontend/pyproject.toml
    ```

Confirm that the root includes both projects as workspace members and that the lockfile is at the root:

```shell
cat uv-workspace/pyproject.toml
```

Each member has its own project metadata and Python pin, while the workspace has one lockfile at its root rather than one per component.

### Add a Workspace Dependency

The backend and frontend already share a workspace. Add a small library under `packages/` to see how another project joins it. Create the parent directory:

```shell
mkdir -p uv-workspace/packages
```

Initialize a library. Because it is created inside the workspace, `uv init` adds it to the root workspace members:

```shell
uv init --lib --vcs none --author-from none uv-workspace/packages/shared-components
```

Inspect the root workspace configuration:

```shell
cat uv-workspace/pyproject.toml
```

Make the backend depend on the local library. `--workspace` records the dependency as a workspace source instead of fetching a package from an index:

```shell
uv --directory uv-workspace/backend add --workspace shared-components
```

Inspect the backend's dependency and workspace source:

```shell
cat uv-workspace/backend/pyproject.toml
```

This adds the library as a third workspace member and resolves all members into the single root lockfile. Workspace dependencies are installed editably during development.

## Work in the Project Environment

### Add Dependencies and Run the Project

By default, `uv add` updates project metadata and the workspace lockfile, creates a virtual environment if needed, and installs dependencies. Run the commands from each member while addressing it explicitly with `--directory`.

=== "Backend"

    Add [Bottle](https://bottlepy.org/docs/dev/), a small web framework, to the backend with an exact version requirement:

    ```shell
    uv --directory uv-workspace/backend add "bottle==0.13.4"
    ```


=== "Frontend"

    Add Streamlit to the frontend:
    ```shell
    uv --directory uv-workspace/frontend add streamlit
    ```

The dependencies are recorded in each member's `pyproject.toml`, while `uv.lock` remains at the workspace root. The generated workspace tree now looks like this:

```text
uv-workspace/
├── pyproject.toml
├── uv.lock
├── backend/
│   ├── .python-version
│   ├── README.md
│   ├── pyproject.toml
│   └── src/
│       └── backend/
│           └── __init__.py
└── frontend/
    ├── .python-version
    ├── README.md
    ├── pyproject.toml
    └── src/
        └── frontend/
            └── __init__.py
```

Inspect the backend metadata:

```shell
cat uv-workspace/backend/pyproject.toml
```

Inspect the frontend metadata:

```shell
cat uv-workspace/frontend/pyproject.toml
```

Inspect the root lockfile location:

```shell
ls uv-workspace/uv.lock
```

The generated package files are scaffolding only. No Bottle routes or Streamlit UI are implemented in this section. Once application code is added, `uv run --directory uv-workspace/backend ...` and `uv run --directory uv-workspace/frontend ...` run commands in the corresponding workspace project.

Add [Ruff](https://docs.astral.sh/ruff/) for linting and [pytest](https://docs.pytest.org/en/stable/) for testing to the backend's `dev` dependency group, rather than its runtime requirements:

```shell
uv --directory uv-workspace/backend add --dev ruff pytest
```

Your Ruff and pytest versions may differ. `uv` writes compatible version ranges to project metadata and resolves exact versions in the shared `uv.lock`.

### Use the `[tool.*]` Table

Tools that support `pyproject.toml` can keep their settings alongside project metadata instead of using separate tool-specific configuration files. These tables configure tools but do not install them. Add Ruff and pytest settings to the backend project:

```toml title="uv-workspace/backend/pyproject.toml"
[tool.ruff]
line-length = 88

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra"
```

The workspace project files now hold component-specific metadata and settings, while dependency resolution is shared at the root. Put future backend tests in `tests/`; configuration alone does not create test files.

## Build a Package

Python packaging separates building into a **frontend** and a **backend**, with their interface defined by [PEP 517](https://peps.python.org/pep-0517/). The build frontend coordinates the build, while the build backend creates installable distributions. [PEP 518](https://peps.python.org/pep-0518/) defines how a project declares its build backend and requirements in `[build-system]`.

The frontend in that packaging terminology is distinct from the Streamlit UI component. Common build frontends include `python -m build`, `pip wheel`, and `uv build`; common build backends include `setuptools.build_meta`, `hatchling.build`, and `uv_build`. The packaged application templates use `uv_build` in their `[build-system]` table.

Build the backend distributions from its project directory:

```shell
uv build uv-workspace/backend --out-dir uv-workspace/backend/dist
```

Build the frontend distributions:

```shell
uv build uv-workspace/frontend --out-dir uv-workspace/frontend/dist
```

The output directory is selected explicitly so each component's distributions remain with that component. Inspect the backend output:

```shell
ls -lah uv-workspace/backend/dist/
```

## Publish a Package

Before uploading, check the project name, version, and package contents. Set a PyPI token in `UV_PUBLISH_TOKEN`, then pass a component's distribution files to `uv publish`:

```shell
uv publish uv-workspace/backend/dist/*.whl uv-workspace/backend/dist/*.tar.gz
```

For a first trial, use [TestPyPI](https://test.pypi.org/) with a TestPyPI token and its upload URL:

```shell
uv publish --publish-url https://test.pypi.org/legacy/ uv-workspace/backend/dist/*.whl uv-workspace/backend/dist/*.tar.gz
```

Repeat the publish command with `uv-workspace/frontend/dist/*.whl` and `uv-workspace/frontend/dist/*.tar.gz` when that component is ready to release. For more detail on wheel packaging and uploading distributions, see [Chapter 02, Section 01](../chapter-02/section-01.md).
