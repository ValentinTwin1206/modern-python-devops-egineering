# Project Scaffolding with uv

## Introduction

`uv` manages a Python project from its first files to a published package. Its central configuration file is `pyproject.toml`: it describes the project, its dependencies, and, when needed, how to build it. This section follows one project through that workflow. For dependency versions and lockfiles, see [Dependency Management with uv](./section-02.md).

## Install uv

Choose the installer for your operating system. You only need to install `uv` once.

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

## Initialize a Project

### Choose a Project Type

`uv init` creates the initial files. Choose a template according to what you want to make. The examples below show complete, *illustrative* `pyproject.toml` files; the exact generated fields and backend version depend on your uv version.

=== "Simple application"

    Create an application that you run locally without building it as a package:

    ```shell
    uv init --app --no-package hello-app
    ```

    The initial files include a script at the project root:

    ```text
    hello-app/
    ├── .python-version
    ├── README.md
    ├── main.py
    └── pyproject.toml
    ```

    Its complete `pyproject.toml` can look like this:

    ```toml
    [project]
    name = "hello-app"
    version = "0.1.0"
    description = "A small Python application"
    readme = "README.md"
    requires-python = ">=3.12"
    dependencies = []
    ```

=== "Packaged application"

    Create an application with an installable package and a command-line entry point:

    ```shell
    uv init --app --package hello-app
    ```

    Its source code lives in a package under `src/`:

    ```text
    hello-app/
    ├── .python-version
    ├── README.md
    ├── pyproject.toml
    └── src/
        └── hello_app/
            └── __init__.py
    ```

    Its complete `pyproject.toml` can look like this (with a `main` function in `hello_app`):

    ```toml
    [project]
    name = "hello-app"
    version = "0.1.0"
    description = "A packaged Python application"
    readme = "README.md"
    requires-python = ">=3.12"
    dependencies = []

    [project.scripts]
    hello-app = "hello_app:main"

    [build-system]
    requires = ["uv_build>=0.11,<0.12"]
    build-backend = "uv_build"
    ```

=== "Library"

    Create a reusable package for other projects to import:

    ```shell
    uv init --lib hello-library
    ```

    The library has a package under `src/`:

    ```text
    hello-library/
    ├── .python-version
    ├── README.md
    ├── pyproject.toml
    └── src/
        └── hello_library/
            ├── __init__.py
            └── py.typed
    ```

    Its complete `pyproject.toml` can look like this:

    ```toml
    [project]
    name = "hello-library"
    version = "0.1.0"
    description = "A reusable Python library"
    readme = "README.md"
    requires-python = ">=3.12"
    dependencies = []

    [build-system]
    requires = ["uv_build>=0.11,<0.12"]
    build-backend = "uv_build"
    ```

For a file-only starting point, `--bare` creates just `pyproject.toml` and leaves the project layout to you:

```shell
uv init --bare hello-project
```

### Understand `pyproject.toml`

`[project]` holds metadata and runtime requirements. `[project.scripts]` names commands users can run, while `[build-system]` says how to package the code. This one standard file can grow with the project; there is no need to scatter these settings across several setup files. See [Declaring Dependencies](./section-02.md#declaring-dependencies) for how to change requirements safely.

The rest of this section follows the **packaged application**. Run its commands from inside `hello-app/`.

## Choose a Python Version

### Install and Pin Python

Install the interpreter you want to use without replacing your system Python:

```shell
uv python install 3.12
```

Pin it for this project:

```shell
uv python pin 3.12
```

The pin lives in `.python-version` and selects the interpreter for local development. The `requires-python` value in `pyproject.toml` instead tells installers which Python versions the project supports; keep it consistent with the code you write.

## Work in the Project Environment

### Create and Use `.venv`

Prepare the project's virtual environment:

```shell
uv sync
```

`uv` creates `.venv` if needed. You do not have to activate it: `uv run` uses it automatically. To create an environment manually outside a managed project, see [Standalone Environments and Tools](./section-04.md#create-a-standalone-environment).

### Add Dependencies and Run the Project

Add a library your application needs:

```shell
uv add rich
```

This updates `pyproject.toml`, `uv.lock`, and `.venv`. [Section 02](./section-02.md) explains dependency groups, removing packages, and synchronizing a team environment.

Run the packaged app's entry point (the `main` function shown in its configuration):

```shell
uv run hello-app
```

## Configure Project Tools

### Use `[tool.*]` Tables

Many tools can read settings from `pyproject.toml`, reducing the need for separate configuration files. For example, add this table to the packaged app's existing `pyproject.toml` to configure Ruff:

```toml
[tool.ruff]
line-length = 88
```

Each tool defines its own supported settings; `[tool.uv]` is for uv settings, while `[tool.ruff]` is for Ruff. This configures Ruff but does not install it. Running standalone tools is covered in [Section 04](./section-04.md#run-command-line-tools).

## Build a Package

### Understand the `uv_build` Backend

The packaged templates include `[build-system]`. Here, `uv_build` is the **build backend**: it turns source files into installable distributions. `uv` is the command-line tool that invokes the backend. The simple `--no-package` app has no build system; choose a packaged template when you intend to distribute your code.

### Create Distributions

Build the package from the project root:

```shell
uv build
```

The `dist/` directory contains a wheel (`.whl`) for installation and a source archive (`.tar.gz`) that can be built elsewhere. Both use the version declared in `pyproject.toml`.

## Publish a Package

### Upload to a Package Index

Before uploading, check the project name, version, and package contents. Set a PyPI token in `UV_PUBLISH_TOKEN`, then publish the files in `dist/`:

```shell
uv publish
```

By default, this publishes to PyPI. For a first trial, use [TestPyPI](https://test.pypi.org/) with a TestPyPI token and its upload URL:

```shell
uv publish --publish-url https://test.pypi.org/legacy/
```

## Manage Related Projects

### Introduce Workspaces

When several related packages live in one repository, a [uv workspace](https://docs.astral.sh/uv/concepts/projects/workspaces/) lets each keep its own `pyproject.toml` while sharing one `uv.lock`. For example, a root project can include packages under `packages/`:

```toml
[tool.uv.workspace]
members = ["packages/*"]
```

When the root depends on a member called `hello-library`, add it to the existing `[project]` dependencies and point uv to the local source:

```toml
[tool.uv.sources]
hello-library = { workspace = true }
```

The resulting `[project]` table includes `dependencies = ["hello-library"]`. Start with one project; introduce a workspace when you need to develop related packages together.
