#!/usr/bin/env bash

set -euo pipefail

PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
BUILD_DIR="${BUILD_DIR:-${PROJECT_ROOT}/.build}"

mkdir -p "${BUILD_DIR}"
rm -f "${BUILD_DIR}/server-cli"

cd "${PROJECT_ROOT}"
site_packages="$(uv run python -c 'import site; print(site.getsitepackages()[0])')"
PYTHONPATH="${PROJECT_ROOT}/src:${site_packages}" nuitka \
    --onefile \
    --output-dir="${BUILD_DIR}" \
    --output-filename=server-cli \
    --include-package=server_cli \
    src/server_cli/cli.py

chmod 0755 "${BUILD_DIR}/server-cli"
printf 'Built %s\n' "${BUILD_DIR}/server-cli"
