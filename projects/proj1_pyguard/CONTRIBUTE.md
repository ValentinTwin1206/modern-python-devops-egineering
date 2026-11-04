# Developer Guide

## Setup

``` bash
./build.sh build --path proj1_pyguard/Dockerfile.devEnv
```

``` bash
uv sync --all-groups
source .venv/bin/activate
```

## Lint

``` bash
ruff check .
```

## Build

``` bash
uv build --wheel --out-dir /build
```

## Publish

``` bash
uv publish
```

PyGuard is distributed as a pure-Python wheel and can be installed
directly from PyPI.
