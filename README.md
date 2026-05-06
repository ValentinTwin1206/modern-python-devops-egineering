# Modern Python Engineering

This repository collects small, self-contained examples for teaching how
modern Python projects are packaged and how their development environments
are managed.

## Chapters

### Chapter 1: Packaging History

- [Chapter 1 index](./chapter-01/README.md)
- [Python Packaging History](./chapter-01/section-01/README.md)

This chapter walks through the same small package across multiple packaging
eras, from early `distutils` through a `pyproject.toml`-based workflow.

### Chapter 2: Development Environments

- [Chapter 2 index](./chapter-02/README.md)
- [Python System Environment](./chapter-02/section-01/README.md)
- [Python Virtual Environments](./chapter-02/section-02/README.md)
- [Python Dev Containers](./chapter-02/section-03/README.md)

This chapter compares common environment-management approaches, including
system-level Python, `venv`, `conda`, `pipenv`, and Dev Containers.

## Using uv At The Repository Root

If you want a modern local workflow, `uv` is a good default choice for
creating an isolated environment and running tools from the repository root:

```bash
uv venv
source .venv/bin/activate
uv pip install -r chapter-01/section-01/05-py35/requirements-dev.txt
```

The chapter directories remain intentionally independent so each example can
demonstrate its own packaging or environment style without relying on a shared
root project configuration.
