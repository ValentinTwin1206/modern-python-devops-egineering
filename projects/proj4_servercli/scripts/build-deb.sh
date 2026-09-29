#!/usr/bin/env bash

set -euo pipefail

PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
ARTIFACT_DIR="${ARTIFACT_DIR:-${PROJECT_ROOT}/.build}"
WORK_ROOT="$(mktemp -d)"
SOURCE_COPY="${WORK_ROOT}/server-cli"

cleanup() {
    rm -rf "${WORK_ROOT}"
}

trap cleanup EXIT

binary="${ARTIFACT_DIR}/server-cli"
if [[ ! -x "${binary}" ]]; then
    printf 'error: executable not found or not executable: %s\n' "${binary}" >&2
    printf 'Build it first with scripts/build-executable.sh\n' >&2
    exit 1
fi

mkdir -p "${SOURCE_COPY}" "${ARTIFACT_DIR}"

tar -C "${PROJECT_ROOT}" \
    --exclude='.git' \
    --exclude='.venv' \
    --exclude='.build' \
    --exclude='.pytest_cache' \
    --exclude='.ruff_cache' \
    --exclude='.karva_cache' \
    --exclude='.coverage' \
    -cf - . | tar -C "${SOURCE_COPY}" -xf -

mkdir -p "${SOURCE_COPY}/.build"
cp -p "${binary}" "${SOURCE_COPY}/.build/server-cli"

cd "${SOURCE_COPY}"
dpkg-buildpackage -us -uc -b

find "${WORK_ROOT}" -maxdepth 1 -type f -name '*.deb' -exec cp -f {} "${ARTIFACT_DIR}/" \;
printf 'Built Debian package in %s\n' "${ARTIFACT_DIR}"
