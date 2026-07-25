#!/usr/bin/env bash

set -euo pipefail

# Define constants
PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
ARTIFACT_DIR="${ARTIFACT_DIR:-/build}"
WORK_ROOT="$(mktemp -d)"
SOURCE_COPY="${WORK_ROOT}/source"

# Exit handling routine
cleanup() {
    rm -rf "${WORK_ROOT}"
}

trap cleanup EXIT

mkdir -p "${ARTIFACT_DIR}" "${SOURCE_COPY}" "${SOURCE_COPY}/.build"

# Exclude certain repo artifacts from package build
tar -C "${PROJECT_ROOT}" \
    --exclude='.git' \
    --exclude='.venv' \
    --exclude='.build' \
    --exclude='.pytest_cache' \
    --exclude='.ruff_cache' \
    --exclude='.karva_cache' \
    --exclude='.coverage' \
    -cf - . | tar -C "${SOURCE_COPY}" -xf -

# Terminate if the *.whl is not packaged
wheel="$(find "${ARTIFACT_DIR}" -maxdepth 1 -type f -name 'simply_journal_admin-*.whl' | sort | tail -n 1)"
if [[ -z "${wheel}" ]]; then
    printf 'error: no wheel found in %s\n' "${ARTIFACT_DIR}" >&2
    exit 1
fi

cp "${wheel}" "${SOURCE_COPY}/.build/"

cd "${SOURCE_COPY}"

# Build the Debian package
dpkg-buildpackage -us -uc -b

find "${WORK_ROOT}" -maxdepth 1 -type f -name '*.deb' -exec cp -f {} "${ARTIFACT_DIR}/" \;