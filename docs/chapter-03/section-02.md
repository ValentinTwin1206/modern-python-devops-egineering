# 03.02 – The uv Workflow for Modern Dependency Management

## Goal
Participants learn the complete modern workflow for Python projects using uv.

## Topics

### Modern project setup
- Example project structure:
  - `pyproject.toml`
  - `.venv`
  - `uv.lock`

### Dependency management with uv
- Runtime dependencies
- Development dependencies
- Dependency groups
- Optional dependencies / extras

### Working with dependencies (uv commands)
- `uv add`
- `uv remove`
- `uv sync`
- `uv lock`
- `uv tree`

### Dependency definitions in `pyproject.toml`
- Version constraints
- Dependency groups
- Tool configurations
- Project structure best practices

### Reproducible builds
- Role of `uv.lock`
- Deterministic environments
- Team workflows
- CI/CD relevance

Hands-on:
- Recreate environments
- Update lockfiles
- Perform dependency upgrades

### Best practices
- Minimal runtime dependencies
- Separation of dev/runtime dependencies
- Clean dependency structures
- Lockfile strategy
