#!/bin/bash
set -euxo pipefail

# libheisenblue is provided by the pin_subpackage() host dependency, so its
# shared library and headers are already installed under $PREFIX. The wheel
# build (driven by scikit-build-core) locates them through find_library /
# find_path against the Conda host prefix.
"${PYTHON}" -m pip install . --no-deps --no-build-isolation -vv
