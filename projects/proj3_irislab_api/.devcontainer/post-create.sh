#!/usr/bin/env bash
set -euo pipefail

# Create a uv environment with the image's Conda Python and packages available.
uv venv --clear \
    --python "${CONDA_DIR}/envs/irislab-api/bin/python" \
    --system-site-packages
# Keep the lockfile unchanged while installing editable code and dev dependencies.
uv sync --locked
.venv/bin/python -m pip check
