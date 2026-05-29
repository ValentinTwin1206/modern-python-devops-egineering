#!/usr/bin/env bash
# ============================================================
# build_and_analyze.sh — Build all dependency manager images,
# measure install time, and extract last layer for analysis.
# ============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# --- Configuration -----------------------------------------------------------
DEPS_FILE="${1:-dependencies.txt}"
MANAGERS=("pip" "uv" "poetry")
LAYERS_BASE_DIR="layers"
METRICS_DIR="metrics"
RESULTS_JSON="results.json"

# --- Colors & output helpers -------------------------------------------------
RED='\033[0;31m'; GREEN='\033[0;32m'; BLUE='\033[0;34m'
YELLOW='\033[1;33m'; BOLD='\033[1m'; NC='\033[0m'

info()  { printf '%b▸ %s%b\n' "$YELLOW" "$1" "$NC"; }
ok()    { printf '%b✔ %s%b\n' "$GREEN"  "$1" "$NC"; }
err()   { printf '%b✗ %s%b\n' "$RED"    "$1" "$NC" >&2; }
header(){ printf '\n%b════════════════════════════════════════════════════════════%b\n' "$BLUE" "$NC"
          printf '%b  %s%b\n' "$BOLD" "$1" "$NC"
          printf '%b════════════════════════════════════════════════════════════%b\n\n' "$BLUE" "$NC"; }

# --- Preflight ---------------------------------------------------------------
preflight_check() {
  for cmd in docker jq tar; do
    command -v "$cmd" &>/dev/null || { err "'$cmd' is required but not found."; exit 1; }
  done
  if [[ ! -f "$DEPS_FILE" ]]; then
    err "Dependencies file '$DEPS_FILE' not found."
    exit 1
  fi
}

# --- Extract last layer from a Docker image ----------------------------------
# Args: $1 = image tag, $2 = output directory for extracted layer
extract_last_layer() {
  local image="$1"
  local output_dir="$2"
  local tmpdir

  tmpdir="$(mktemp -d)"

  docker save "$image" -o "$tmpdir/image.tar"
  mkdir -p "$tmpdir/image"
  tar -xf "$tmpdir/image.tar" -C "$tmpdir/image"

  local manifest="$tmpdir/image/manifest.json"
  local last_layer
  last_layer=$(jq -r '.[0].Layers[-1]' "$manifest")

  mkdir -p "$output_dir"
  tar -xf "$tmpdir/image/${last_layer}" -C "$output_dir" 2>/dev/null || true

  rm -rf "$tmpdir"
}

# --- Show layer summary ------------------------------------------------------
show_layer_summary() {
  local layer_dir="$1"
  local tool="$2"
  local line_num="$3"

  local file_count layer_size_bytes layer_size_human
  file_count=$(find "$layer_dir" -type f 2>/dev/null | wc -l)
  layer_size_bytes=$(du -sb "$layer_dir" 2>/dev/null | cut -f1)
  layer_size_human=$(du -sh "$layer_dir" 2>/dev/null | cut -f1)

  echo "  Files:      ${file_count}"
  echo "  Layer size: ${layer_size_human} (${layer_size_bytes} bytes)"

  # Show cache breakdown
  local cache_dir=""
  if [[ -d "$layer_dir/root/.cache/uv" ]]; then
    cache_dir="$layer_dir/root/.cache/uv"
  elif [[ -d "$layer_dir/root/.cache/pip" ]]; then
    cache_dir="$layer_dir/root/.cache/pip"
  elif [[ -d "$layer_dir/root/.cache/pipenv" ]]; then
    cache_dir="$layer_dir/root/.cache/pipenv"
  fi

  if [[ -n "$cache_dir" ]]; then
    local cache_human
    cache_human=$(du -sh "$cache_dir" 2>/dev/null | cut -f1)
    echo "  Cache size: ${cache_human}"
  fi

  # Show site-packages
  local site_pkgs
  site_pkgs=$(find "$layer_dir" -type d -name "site-packages" | head -1)
  if [[ -n "$site_pkgs" ]]; then
    local site_human
    site_human=$(du -sh "$site_pkgs" 2>/dev/null | cut -f1)
    echo "  site-packages: ${site_human}"
  fi

  # Extract install metrics
  local metrics_file="$layer_dir/tmp/install_metrics.json"
  if [[ -f "$metrics_file" ]]; then
    local install_time
    install_time=$(jq -r '.install_time_ms' "$metrics_file")
    echo "  Install time: ${install_time} ms"
  fi
}

# --- Write metrics to file ---------------------------------------------------
write_metrics() {
  local layer_dir="$1"
  local tool="$2"
  local line_num="$3"
  local packages="$4"
  local image="$5"
  local dep_label="$6"

  mkdir -p "$METRICS_DIR"

  local image_size_bytes layer_count file_count layer_size_bytes
  local cache_size_bytes=0 site_size_bytes=0 install_time_ms=0 installed_size_bytes=0

  image_size_bytes=$(docker inspect "$image" 2>/dev/null | jq -r '.[0].Size' || echo "0")
  layer_count=$(docker inspect "$image" 2>/dev/null | jq -r '.[0].RootFS.Layers | length' || echo "0")
  file_count=$(find "$layer_dir" -type f 2>/dev/null | wc -l)
  layer_size_bytes=$(du -sb "$layer_dir" 2>/dev/null | cut -f1)

  # Cache size
  local cache_dir=""
  if [[ -d "$layer_dir/root/.cache/uv" ]]; then
    cache_dir="$layer_dir/root/.cache/uv"
  elif [[ -d "$layer_dir/root/.cache/pip" ]]; then
    cache_dir="$layer_dir/root/.cache/pip"
  fi
  if [[ -n "$cache_dir" ]]; then
    cache_size_bytes=$(du -sb "$cache_dir" 2>/dev/null | cut -f1)
  fi

  # Site-packages size
  local site_pkgs
  site_pkgs=$(find "$layer_dir" -type d -name "site-packages" | head -1)
  if [[ -n "$site_pkgs" ]]; then
    site_size_bytes=$(du -sb "$site_pkgs" 2>/dev/null | cut -f1)
  fi

  # Install time from container metrics
  local metrics_file="$layer_dir/tmp/install_metrics.json"
  if [[ -f "$metrics_file" ]]; then
    install_time_ms=$(jq -r '.install_time_ms' "$metrics_file")
  fi

  # Measure installed size as the full last-layer size (from extracted blob)
  installed_size_bytes="$layer_size_bytes"

  # Patch the layer size back into the metrics JSON for downstream consumers
  if [[ -f "$metrics_file" ]]; then
    local tmp_patched
    tmp_patched=$(jq --argjson size "$installed_size_bytes" '. + {installed_size_bytes: $size}' "$metrics_file")
    echo "$tmp_patched" > "$metrics_file"
  fi

  local timestamp_ns
  timestamp_ns=$(date +%s%N)

  cat >> "$METRICS_DIR/metrics_line${line_num}.log" <<EOF
docker_layer_analysis,tool=${tool},packages="${packages}",image=${image},line=${line_num} install_time_ms=${install_time_ms}i,image_size_bytes=${image_size_bytes}i,layer_count=${layer_count}i,last_layer_size_bytes=${layer_size_bytes}i,last_layer_file_count=${file_count}i,cache_size_bytes=${cache_size_bytes}i,site_packages_size_bytes=${site_size_bytes}i,installed_size_bytes=${installed_size_bytes}i ${timestamp_ns}
EOF

  # Append to results.json (JSONL — one JSON object per line)
  printf '{"line":%d,"dep_set":"%s","tool":"%s","install_time_ms":%s,"installed_size_bytes":%s,"layer_size_bytes":%s,"image_size_bytes":%s,"cache_size_bytes":%s,"site_packages_size_bytes":%s}\n' \
    "$line_num" "$dep_label" "$tool" "$install_time_ms" "$installed_size_bytes" \
    "$layer_size_bytes" "$image_size_bytes" "$cache_size_bytes" "$site_size_bytes" \
    >> "$RESULTS_JSON"
}

# --- Build, analyze, and clean up one image ----------------------------------
process_image() {
  local tool="$1"
  local line_num="$2"
  local packages="$3"

  local image_tag="depmanager-analysis-${tool}:line${line_num}"
  local dockerfile="Dockerfile_${tool}"
  local layer_output="${LAYERS_BASE_DIR}/${line_num}/${tool}"

  if [[ ! -f "$dockerfile" ]]; then
    err "Dockerfile '$dockerfile' not found. Skipping ${tool}."
    return 1
  fi

  info "Building ${image_tag} with packages: ${packages}"

  sleep 3

  # Build the image
  if ! DOCKER_BUILDKIT=1 docker build \
    --no-cache \
    --build-arg "PACKAGES=${packages}" \
    -t "$image_tag" \
    -f "$dockerfile" \
    . 2>&1; then
    err "Build failed for ${tool} (line ${line_num})"
    return 1
  fi
  ok "Image built: ${image_tag}"

  # Run container to show metrics
  info "Container CMD output:"
  docker run --rm "$image_tag" 2>&1 || true
  echo ""

  # Extract last layer
  info "Extracting last layer to ${layer_output}/ ..."
  rm -rf "$layer_output"
  extract_last_layer "$image_tag" "$layer_output"
  ok "Layer extracted"

  # Show summary
  info "Layer summary for ${tool} (line ${line_num}):"
  show_layer_summary "$layer_output" "$tool" "$line_num"
  echo ""

  # Write metrics
  write_metrics "$layer_output" "$tool" "$line_num" "$packages" "$image_tag" "$packages"

  # Clean up image
  info "Removing image ${image_tag} ..."
  docker rmi "$image_tag" >/dev/null 2>&1 || true
  ok "Image removed"
  echo ""
}

# --- Main --------------------------------------------------------------------
main() {
  header "Dependency Manager Layer Analysis"
  preflight_check

  # Clean previous runs
  rm -rf "$LAYERS_BASE_DIR" "$METRICS_DIR" "$RESULTS_JSON"
  mkdir -p "$LAYERS_BASE_DIR" "$METRICS_DIR"

  local line_num=0

  while IFS= read -r line || [[ -n "$line" ]]; do
    # Skip empty lines and comments
    [[ -z "$line" || "$line" =~ ^# ]] && continue

    line_num=$((line_num + 1))

    # Replace commas with spaces for package list
    local packages
    packages=$(echo "$line" | tr ',' ' ' | xargs)

    header "Line ${line_num}: ${packages}"

    for tool in "${MANAGERS[@]}"; do
      header "${tool} — Line ${line_num}"
      process_image "$tool" "$line_num" "$packages" || true
    done

  done < "$DEPS_FILE"

  # Final summary
  header "Analysis Complete"
  ok "Layer data stored in: ${LAYERS_BASE_DIR}/"
  ok "Metrics stored in:    ${METRICS_DIR}/"
  echo ""
  info "Results per line:"
  for f in "$METRICS_DIR"/metrics_line*.log; do
    [[ -f "$f" ]] || continue
    echo "  $(basename "$f"):"
    cat "$f" | sed 's/^/    /'
    echo ""
  done

  # Prune build cache
  docker builder prune -f >/dev/null 2>&1 || true
  ok "Build cache pruned. Done."

  # Generate visualization
  if command -v python3 &>/dev/null && [[ -f "$RESULTS_JSON" ]]; then
    header "Generating Charts"
    python3 "$SCRIPT_DIR/visualize.py" "$RESULTS_JSON" || err "Visualization failed (matplotlib installed?)"
  fi
}

main "$@"
