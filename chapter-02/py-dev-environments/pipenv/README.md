# `pipenv` Example

This folder shows how to use **`pipenv`** to create and manage an
isolated environment for a project.

## What Is `pipenv`?

`pipenv` combines two tools you already know — `pip` (installer) and
`virtualenv` (environment isolator) — and adds a **real lockfile**.
Instead of writing a `requirements.txt` by hand, you describe your
direct dependencies in a [`Pipfile`](Pipfile), and `pipenv` resolves
the entire transitive tree, pins every version with a cryptographic
hash, and writes the result to [`Pipfile.lock`](Pipfile.lock).

That lockfile is what makes installs deterministic and verifiable.

## How It Works

1. You install `pipenv` once with `pip install pipenv`.
2. You declare your direct dependencies in [`Pipfile`](Pipfile)
   (TOML-like format).
3. `pipenv install` does three things in one step: creates a virtual
   environment, installs the dependencies into it, and writes
   [`Pipfile.lock`](Pipfile.lock) with the fully resolved tree and
   SHA-256 hashes for every package.
4. `pipenv sync` reinstalls the locked tree exactly. This is what
   teammates and CI run.

## Create The Environment

From this folder:

```sh
pip install pipenv
pipenv install
```

That single `pipenv install` reads `Pipfile`, creates a venv (by default
under `~/.local/share/virtualenvs/...`, or alongside the project if
`PIPENV_VENV_IN_PROJECT=1` is set), and writes `Pipfile.lock`.

Open a shell inside the environment:

```sh
pipenv shell
```

Or run a single command without entering a shell:

```sh
pipenv run python -m my_package.main
```

## Manage Dependencies

Add a runtime dependency:

```sh
pipenv install <package>
```

Add a development-only dependency (test runner, formatter, …):

```sh
pipenv install --dev <package>
```

Refresh the lockfile after editing `Pipfile`:

```sh
pipenv lock
```

Reinstall exactly what is in the lockfile (production / CI):

```sh
pipenv sync
```

To leave the environment shell:

```sh
exit
```

## Run The Example

```sh
pipenv run python -m my_package.main
```

You should see `Hello from pipenv environment`.

## Run It With Docker

A working [`Dockerfile`](Dockerfile) is included. It uses
`pipenv sync --deploy`, which fails the build if `Pipfile.lock` is
out of sync with `Pipfile` — exactly the safety net you want in CI:

```sh
docker build -t pyenv-pipenv .
docker run --rm pyenv-pipenv
```

## Pros

- **Real lockfile** with SHA-256 hashes, not just `==` pins.
- **Single tool** — replaces `pip install`, `pip freeze`,
  `virtualenv`, and `requirements*.txt` juggling.
- **Two-tier dependencies** — runtime vs. development packages, with
  the same lockfile.

## Cons

- **Slower** than plain `pip install` because of the resolver and hash
  computation.
- **One more dependency** — `pipenv` itself has to be installed.
- **Less momentum** today than newer project managers like
  [Poetry](https://python-poetry.org/), [PDM](https://pdm-project.org/),
  or [uv](https://docs.astral.sh/uv/).

## When To Use It

Use `pipenv` when:

- You want a deterministic, hash-verified install for an application,
  not just a library.
- You like the workflow but do not want to step up to a full project
  manager (Poetry / PDM / uv).
- Your team already uses it and is comfortable with the toolchain.

For library packaging, look at modern tools that follow PEP 621 such as
[Poetry](https://python-poetry.org/), [PDM](https://pdm-project.org/),
or [uv](https://docs.astral.sh/uv/).
