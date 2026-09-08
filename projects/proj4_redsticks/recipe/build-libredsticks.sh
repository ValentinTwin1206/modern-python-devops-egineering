#!/bin/bash
set -euxo pipefail

mkdir -p build-libredsticks
cd build-libredsticks

cmake "${SRC_DIR}/cpp" \
    -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX="${PREFIX}" \
    -DCMAKE_INSTALL_LIBDIR=lib

cmake --build . --target redsticks --config Release
cmake --install . --component Unspecified
