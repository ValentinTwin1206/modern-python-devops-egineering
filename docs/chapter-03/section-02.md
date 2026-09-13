# Project Scaffolding

## Execute third party tools

During development you frequently reach for command-line tools such as `ruff`, `black`, or `httpie`. Installing them into the project environment would mix tool dependencies with the project's own dependencies and lead to exactly the conflicts described above. To keep them isolated, `uv` provides a dedicated **tool interface**.

To test Bob's server endpoints with `httpie`, install it once as a globally available tool:

```shell
uv tool install httpie
```

uv installs the tool into its own isolated environment under `~/.local/share/uv/tools` and exposes the executable on the `PATH`, completely separate from any project `.venv`.

If a tool is only needed once, `uvx` (an alias for `uv tool run`) runs it ephemerally without a permanent installation:

```shell
uvx --from httpie http GET http://127.0.0.1:8000/health
```

!!! note "`uv tool` vs. `uvx`"
    Use `uv tool install` for tools you rely on regularly and `uvx` for one-off invocations that should leave no trace on the system.


## Build and Publishing Packages

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

## Handling multiple projects with uv

### Introduction into uv workspaces

When multiple related projects must be developed and tested together, a consistent shared environment becomes essential. For scenarios like this, `uv` provides the concept of **[workspaces](https://docs.astral.sh/uv/concepts/projects/workspaces/)**. A workspace allows multiple related Python projects to coexist within a single repository while remaining independent packages. All workspace members share a common `uv.lock` file, ensuring a consistent dependency set across the entire workspace. At the same time, each member maintains its own `pyproject.toml`, allowing project-specific configuration and metadata.

### Structure and Members

A workspace consists of a *root project* that defines the workspace itself and one or more *workspace members*. There is no single correct layout: members may live side by side in a dedicated `packages/` directory underneath a standalone root, or a library can simply be nested inside the application that consumes it. What actually turns a set of folders into a workspace is not the directory layout but the referencing inside the `pyproject.toml` files.

Take the [license service](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/proj3_license_service/README.md) and the [PyGuard](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/proj1_pyguard/README.md) middleware. The license service is the application that depends on `PyGuard`, so it becomes the workspace root and `PyGuard` is nested underneath it as a member:

```text
license-service/
├── pyproject.toml          ← workspace root
├── uv.lock                 ← shared lock file
├── main.py
└── packages/
    └── pyguard/
        └── pyproject.toml  ← member, keeps its own metadata
```

The root `pyproject.toml` does two things: it declares which folders are members via `[tool.uv.workspace]`, and it pins `pyguard` as a workspace source so that `uv` resolves it from the workspace instead of PyPI:

```toml
[tool.uv.workspace]
members = ["packages/*"]

[tool.uv.sources]
pyguard = { workspace = true }
```

The member (`packages/pyguard/pyproject.toml`) needs no workspace-specific configuration at all — it stays a normal package with its own dependencies and metadata.

!!! note "The layout is flexible, the referencing is not"
    You are free to organise members however you like — nested under the root as shown above, or side by side in a dedicated `packages/` directory with a standalone root. Regardless of the chosen layout, a workspace only comes to life through the `[tool.uv.workspace]` members and the `{ workspace = true }` sources declared in the `pyproject.toml` files.

To invoke a dedicated workspace member such as the `pyguard` package you can simply use the `uv run --package pyguard` command. 
