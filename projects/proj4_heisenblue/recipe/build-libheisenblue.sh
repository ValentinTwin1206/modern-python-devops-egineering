#!/bin/bash
set -euxo pipefail

mkdir -p build-libheisenblue
cd build-libheisenblue

cmake "${SRC_DIR}/cpp" \
    -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX="${PREFIX}" \
    -DCMAKE_INSTALL_LIBDIR=lib

cmake --build . --target heisenblue --config Release
cmake --install . --component Unspecified
