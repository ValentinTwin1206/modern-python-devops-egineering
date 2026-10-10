#!/usr/bin/env bash
# Measure allocated disk space without running uv or creating a missing cache.
# GitHub supplies GITHUB_OUTPUT; all workflow steps share UV_CACHE_DIR.
set -euo pipefail

kib=0
if [[ -d "$UV_CACHE_DIR" ]]; then
  kib=$(du -sk "$UV_CACHE_DIR" | cut -f1)
fi
echo "${1}: ${kib} KiB"
echo "kib=$kib" >> "$GITHUB_OUTPUT"
