# Standalone Environments and Tools with uv

## Introduction

Not every task needs a `pyproject.toml` project. `uv` can also work with an existing `requirements.txt`, run a single script, or provide a command-line tool. For the project-managed workflow, start with [Project Scaffolding with uv](./section-01.md).

## Work with Legacy Projects

### Create a Standalone Environment

In a directory containing a `requirements.txt`, create a virtual environment manually:

```shell
uv venv
```

This creates `.venv` in the current directory. To choose an interpreter explicitly, use this form instead:

```shell
uv venv --python 3.12
```

In a managed project, `uv sync` creates and maintains `.venv` for you; `uv venv` is most useful when you are managing an environment yourself.

### Install from `requirements.txt`

Install the existing requirements into `.venv`:

```shell
uv pip install -r requirements.txt
```

To inspect what was installed, list the packages:

```shell
uv pip list
```

`uv pip` works directly on the environment: it does **not** update `pyproject.toml` or `uv.lock`. For a managed project, use [`uv add`](./section-02.md#add-and-remove) instead.

## Run Standalone Scripts

### Run a Script with `uv run`

Run a small script without creating a project:

```shell
uv run --no-project report.py
```

`--no-project` keeps the script independent even if you happen to run it inside a project directory.

### Declare Inline Dependencies

Initialize a script with metadata for its Python version and dependencies:

```shell
uv init --script report.py --python 3.12
```

Add a package needed by that script:

```shell
uv add --script report.py rich
```

`uv` writes the requirement into a small metadata block at the top of the file, so the script carries its own setup instructions. Run it without managing a `.venv` yourself:

```shell
uv run report.py
```

## Run Command-Line Tools

### Run a Tool Once with `uvx`

Try Ruff without adding it to the project:

```shell
uvx ruff check .
```

`uvx` is shorthand for `uv tool run`; the equivalent command is:

```shell
uv tool run ruff check .
```

Both use an isolated tool environment. If a tool needs your project's dependencies, add it to the project and use `uv run` instead.

### Install and Maintain Tools with `uv tool`

Install a frequently used tool for your user account:

```shell
uv tool install ruff
```

See which tools are installed:

```shell
uv tool list
```

Upgrade a tool when needed:

```shell
uv tool upgrade ruff
```

Remove it when you no longer need it:

```shell
uv tool uninstall ruff
```

## Choose the Right Workflow

| Need | Start with |
| --- | --- |
| Develop a `pyproject.toml` project | `uv sync`, `uv add`, `uv run` |
| Use an existing `requirements.txt` | `uv venv`, `uv pip install -r requirements.txt` |
| Run a self-contained script | `uv run --no-project` or inline script dependencies |
| Try a CLI tool once | `uvx` |
| Keep a CLI tool available | `uv tool install` |

If another workflow needs a `requirements.txt` **from a managed project**, see [Export Dependencies](./section-02.md#export-dependencies).
