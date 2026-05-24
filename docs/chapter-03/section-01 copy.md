# Dependency Management with Python

## Goal
Participants understand the role of uv in the modern Python ecosystem and why it is becoming the new standard for dependency management.

## Topics

### Why uv?
- Problems with traditional Python workflows
- Slow dependency resolution
- Non-reproducible environments
- Tooling fragmentation in the Python ecosystem

### The intention behind uv
- Unified modern Python tooling
- Focus on:
  - Performance
  - Reproducibility
  - Developer experience
  - DevOps integration

### uv architecture
- Rust-based architecture
- Dependency resolver
- Global cache
- Locking mechanism
- Environment management
- Integration with `pyproject.toml`

### Comparison with other tools
- pip
- pip-tools
- poetry
- pipenv

Key aspects:
- Workflow differences
- Lockfile handling
- Performance
- Reproducibility
- Tooling complexity

### Performance comparison
- Installation speed
- Resolver performance
- Cache utilization
- Cold vs warm installs