# `virtualenv` Example

This folder shows how to use the third-party **`virtualenv`** tool to
create an isolated environment for a project.

## What Is `virtualenv`?

`virtualenv` is the older, third-party tool that originally inspired
the standard library's [`venv`](../venv/) module. It does the same
core thing — create a private folder with its own Python interpreter
and `site-packages` — but it is its own project on PyPI, with extra
features and a faster creation step.

You install it with `pip` like any other library.

## How It Works

1. You run `pip install virtualenv` once, into either your system Python
   or another environment.
2. `virtualenv .venv` creates a folder named `.venv/` with its own
   `python`, its own `pip`, and an empty `site-packages/` directory.
3. Activating the environment puts `.venv/bin/` at the front of your
   shell's `PATH`, so `python` and `pip` resolve to the ones inside
   `.venv/`.
4. Anything you install with that `pip` lands inside `.venv/`, leaving
   your system Python alone.

## Create The Environment

From this folder:

```sh
pip install virtualenv
virtualenv .venv
```

Activate it:

```sh
# Linux / macOS
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

Your prompt should show `(.venv)` and `which python` should point inside
`.venv/`.

## Manage Dependencies

Install the pinned packages from [`requirements.txt`](requirements.txt):

```sh
pip install -r requirements.txt
```

To save the current environment's exact versions back to a file:

```sh
pip freeze > requirements.txt
```

To leave the environment:

```sh
deactivate
```

## Run The Example

After installing the project itself with `pip install .` (it picks up
[`pyproject.toml`](pyproject.toml)):

```sh
python -m my_package.main
```

You should see `Hello from virtualenv environment`.

## Run It With Docker

A working [`Dockerfile`](Dockerfile) is included:

```sh
docker build -t pyenv-virtualenv .
docker run --rm pyenv-virtualenv
```

## Pros

- **Faster creation** than `venv` because it ships pre-built copies of
  `pip` and `setuptools` instead of bootstrapping them every time.
- **Works with older Python versions** (2.7, 3.4, …) that do not have
  `venv` in the standard library.
- **More options** — custom prompts, alternative seeders, plugin
  system.

## Cons

- **Extra install** — you have to install `virtualenv` itself before
  you can use it.
- **No lockfile** — same as `venv`, `requirements.txt` only pins what
  you explicitly add to it.
- **PyPI only** — cannot manage non-Python system libraries.

## When To Use It

Use `virtualenv` when:

- You need to support Python versions older than 3.3.
- You create a lot of environments and want the speed boost.
- You want one of its specific features, such as custom seed packages.

For modern projects on Python 3.8+, the built-in [`venv`](../venv/)
module is usually the simpler choice.
