#!/bin/bash
set -euxo pipefail

cmake -S "${SRC_DIR}/cpp" \
    -B build-tools \
    -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DIRISLAB_BUILD_BINDINGS=ON \
    -DCMAKE_PREFIX_PATH="${PREFIX}"

cmake --build build-tools

mkdir -p "${SP_DIR}/irislab"
cp "${SRC_DIR}"/src/irislab/*.py "${SP_DIR}/irislab/"
cp build-tools/_native*.so "${SP_DIR}/irislab/"
