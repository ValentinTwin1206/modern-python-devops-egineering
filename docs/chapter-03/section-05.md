# 03.05 – Practical Project: Troubleshooting & Modernizing a Legacy Python Project

## Goal
Fix and modernize a broken Python project using uv.

## Scenario
The project:
- uses outdated Python versions
- relies on pip-based workflows
- has dependency conflicts
- lacks reproducible builds
- contains outdated packages
- has slow CI/CD pipelines

## Project analysis
- Inspect project structure
- Identify dependency issues
- Analyze Python compatibility
- Detect outdated packages

## Migration to uv
- Introduce:
  - `pyproject.toml`
  - `uv.lock`
- Upgrade Python version
- Rebuild environment

## Resolving dependency conflicts
- Resolver conflict analysis
- Fix incompatible dependencies
- Apply correct version constraints
- Stabilize dependency graph

## Build & pipeline optimization
- Integrate uv caching
- Optimize Docker builds
- Modernize CI/CD pipelines

## Final result
A modernized project:
- uses uv
- has reproducible builds
- runs on modern Python versions
- has resolved dependency conflicts
- is CI/CD ready
- is production-grade