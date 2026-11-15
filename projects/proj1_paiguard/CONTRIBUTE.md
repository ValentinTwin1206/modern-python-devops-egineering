# Developer Guide

## Setup

``` bash
./build.sh build --path proj1_paiguard/Dockerfile.devEnv
```

``` bash
uv sync --all-groups --all-extras
source .venv/bin/activate
```

## Lint

``` bash
ruff check .
```

## Test

``` bash
pytest
```

## Build

``` bash
uv build --wheel --out-dir /build
```

## Publish

``` bash
uv publish
```

PaiGuard is distributed as a pure-Python wheel and can be installed
directly from PyPI.
