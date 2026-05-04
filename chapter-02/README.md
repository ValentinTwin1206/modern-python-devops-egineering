# Chapter 2: Python Development Environments

This chapter collects teaching examples about Python runtime and project
environments. The examples focus on where Python is installed, where
packages are written, how command lookup and import lookup differ, and
how environment tools isolate dependencies from the operating system.

The runnable example across this chapter is `tiny_webserver`: a minimal
Bottle application with one JSON endpoint. It is intentionally small so
the environment layout remains the main subject.

## Folder Index

| Folder | Topic | Focus | Details |
| ------ | ----- | ----- | ------- |
| [`01-py-sys-env/`](./01-py-sys-env/) | Python system environment | APT-managed Linux Python, system package installs, `PATH`, `sys.path`, `site-packages`, and `dist-packages` | [README](./01-py-sys-env/README.md) |
| [`02-py-virt-env/`](./02-py-virt-env/) | Python virtual environments | `venv`, `virtualenv`, `conda`, and `pipenv` isolation patterns | [README](./02-py-virt-env/README.md) |
| [`03-py-dev-containers/`](./03-py-dev-containers/) | Python dev containers | containerized development environments | README |

## Tiny Webserver

`tiny_webserver` is the shared project used by every Chapter 2 example.
It is a dependency-light Bottle application with one route, `/`, that
returns a JSON message. There is no database, template layer, background
worker, or application framework beyond Bottle; that keeps the project
small enough for the surrounding Python environment to remain visible.

The development stack is intentionally consistent across the chapter:

- `uv` provides the build backend through `uv_build` and manages the
  locked development workflow in the system-environment example.
- `ruff` is the linting tool.
- `karva` is the test runner.

The virtual-environment examples still use their own environment tools
to teach isolation mechanics, but their `pyproject.toml` files share the
same `uv_build` backend and declare the same Karva/Ruff development
tooling.

Boot the canonical system-environment project:

```sh
cd chapter-02/01-py-sys-env
uv sync
uv run tiny-webserver
```

Run tests and linting:

```sh
uv run karva test tests/
uv run ruff check .
```

Build a wheel with the `uv_build` backend:

```sh
uv build --wheel
```

For a virtual-environment subproject, use the same project metadata and
development group directly:

```sh
uv sync --group dev
uv run tiny-webserver
uv run karva test tests/
uv run ruff check .
uv build --wheel
```
