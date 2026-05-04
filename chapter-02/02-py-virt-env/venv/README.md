# `venv` Example

This folder shows how to use Python's built-in **`venv`** module to
create an isolated environment for a project.

## What Is `venv`?

`venv` is a module that ships with Python itself (since version 3.3).
It creates a *virtual environment*: a private folder that contains its
own copy of the Python interpreter and its own `site-packages`
directory. Anything you install while that environment is active goes
into the private folder, not into your system Python.

You do not have to install `venv` separately — if you have a recent
Python, you already have it.

## How It Works

1. You ask `python -m venv .venv` to create a folder named `.venv/`.
2. That folder gets its own `python` executable and an empty
   `site-packages/` directory.
3. When you "activate" the environment, your shell's `PATH` is
   adjusted so that typing `python` or `pip` uses the ones inside
   `.venv/`.
4. `pip install` then writes packages into `.venv/lib/.../site-packages`,
   leaving the system Python untouched.

## Create The Environment

From this folder, on a machine with Python 3.8 or newer:

```sh
python -m venv .venv
```

Activate it:

```sh
# Linux / macOS
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

You will know it worked because your shell prompt is prefixed with
`(.venv)` and `which python` points inside the `.venv/` folder.

## Manage Dependencies

Install the project and its pinned dependencies from [`pyproject.toml`](pyproject.toml):

```sh
pip install .
```

To inspect the exact versions currently installed in the environment:

```sh
pip freeze
```

To leave the environment when you are done:

```sh
deactivate
```

## Run The Example

After installing the project with `pip install .`:

```sh
python -m tiny_webserver.app
```

The Bottle development server should listen on port `8080`.

## Run It With Docker

A working [`Dockerfile`](Dockerfile) is included:

```sh
docker build -t pyenv-venv .
docker run --rm pyenv-venv
```

## Pros

- **Zero install** — comes bundled with Python.
- **Lightweight** — the environment is just a folder you can delete.
- **Standard** — every Python developer recognises it.

## Cons

- **No lockfile** — `pyproject.toml` records direct dependency
   constraints, not the full resolved tree of indirect dependencies.
- **PyPI only** — cannot install non-Python system libraries.
- **Does not manage Python itself** — you need a separately installed
  Python interpreter of the version you want.

## When To Use It

Use `venv` when:

- Your project only needs Python packages from PyPI.
- You already have the Python version you want installed.
- You want the simplest possible setup with no extra tooling.

For projects that need a stronger lockfile, look at [`pipenv/`](../pipenv/).
For projects that need non-Python libraries (BLAS, CUDA, GDAL, …), look
at [`conda/`](../conda/).
