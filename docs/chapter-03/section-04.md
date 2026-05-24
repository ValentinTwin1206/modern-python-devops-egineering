# 03.04 – Migrating pip-Based Projects to uv

## Goal
Migrate existing pip-based projects to modern uv workflows.

## Topics

### Legacy project analysis
- `requirements.txt` structures
- Missing lockfiles
- Manual dependency workflows

### uv pip interface
- Compatibility with pip workflows
- Using:
  - `requirements.txt`
  - `constraints.txt`

Commands:
- `uv pip install`
- `uv pip compile`
- `uv pip sync`

### Modern project scaffolding
- Introducing `pyproject.toml`
- Introducing `uv.lock`
- Defining dependency groups
- Setting Python versions

### Dependency migration
- Importing legacy requirements
- Generating lockfiles
- Ensuring reproducible builds
- Detecting conflicts early

### From scaffolding to publishing
- Packaging structure
- Build workflows with uv
- Creating distributable artifacts
- Publishing preparation (PyPI / internal registries)

### CI/CD migration
- Updating pipelines
- Integrating uv
- Cache optimization
- Reproducible deployments