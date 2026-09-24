#!/usr/bin/env bash
# build.sh
#
# Build, run, and remove container images for the projects in this directory.
set -euo pipefail

if [[ -t 1 ]]; then
    BOLD=$'\e[1m'
    DIM=$'\e[2m'
    RED=$'\e[31m'
    GREEN=$'\e[32m'
    YELLOW=$'\e[33m'
    BLUE=$'\e[34m'
    CYAN=$'\e[36m'
    RESET=$'\e[0m'
else
    BOLD=""; DIM=""; RED=""; GREEN=""; YELLOW=""; BLUE=""; CYAN=""; RESET=""
fi

log()   { printf '%s==>%s %s\n' "${BLUE}${BOLD}" "${RESET}" "$*"; }
warn()  { printf '%swarn:%s %s\n' "${YELLOW}${BOLD}" "${RESET}" "$*" >&2; }
error() { printf '%serror:%s %s\n' "${RED}${BOLD}" "${RESET}" "$*" >&2; }
die()   { error "$*"; exit 1; }

usage() {
    cat <<EOF
${CYAN}${BOLD}${SCRIPT_DISPLAY_NAME}${RESET} ${DIM}- manage container images for the projects in this directory${RESET}

${BLUE}${BOLD}USAGE${RESET}
    ${GREEN}${SCRIPT_DISPLAY_NAME}${RESET} ${YELLOW}<command>${RESET} ${DIM}[options]${RESET}

${BLUE}${BOLD}COMMANDS${RESET}
    ${GREEN}build${RESET}                  Builds an image from a Dockerfile, then opens an
                           interactive Bash shell unless ${YELLOW}--build-only${RESET} is set.
    ${GREEN}remove${RESET}                 Remove local images whose full tag matches ${YELLOW}--regex${RESET}.

${BLUE}${BOLD}BUILD OPTIONS${RESET}
    ${YELLOW}-p${RESET}, ${YELLOW}--path${RESET} ${CYAN}<DOCKERFILE>${RESET}   Path to a Dockerfile inside this projects directory
                              ${DIM}(e.g. proj3_license_service/Dockerfile).${RESET}
        ${YELLOW}--port${RESET} ${CYAN}<HOST:CONT>${RESET}    Port mapping. Defaults to ${CYAN}8080:8080${RESET}.
        ${YELLOW}--gpus${RESET} ${CYAN}<GPU_REQUEST>${RESET}       GPU access passed to the container runtime, such as ${CYAN}all${RESET}.
        ${YELLOW}--build-only${RESET}          Build the image but do not start a container.
        ${YELLOW}--rebuild${RESET}             Force a fresh build (${YELLOW}--no-cache${RESET}).
        ${YELLOW}--rm-container${RESET}       Remove the container automatically after it exits.
        ${YELLOW}--cloudsmith-workspace${RESET} ${CYAN}<WORKSPACE>${RESET}
                              Forward ${CYAN}CLOUDSMITH_REPOSITORY${RESET} into the container.
        ${YELLOW}--cloudsmith-api-key${RESET} ${CYAN}<API_KEY>${RESET}
                              Forward ${CYAN}CLOUDSMITH_API_KEY${RESET} into the container.

    Each container run also bind-mounts the project's ${CYAN}.build/${RESET} directory at
    ${CYAN}/build${RESET} inside the container so wheels, compiled binaries, and other build
    artifacts produced inside the container land back on the host. The directory is
    created automatically next to the Dockerfile if it does not yet exist.

${BLUE}${BOLD}REMOVE OPTIONS${RESET}
        ${YELLOW}--regex${RESET} ${CYAN}<REGEX>${RESET}       Extended regex matched against image tags, such as
                              ${CYAN}"projects-.*"${RESET}.

${BLUE}${BOLD}EXAMPLES${RESET}
    ${DIM}${SCRIPT_DISPLAY_NAME}${RESET} ${GREEN}build${RESET} ${YELLOW}--path${RESET} ${CYAN}proj4_redsticks/Dockerfile.devEnv${RESET} ${YELLOW}--port${RESET} ${CYAN}9090:8080${RESET}
    ${DIM}${SCRIPT_DISPLAY_NAME}${RESET} ${GREEN}build${RESET} ${YELLOW}--path${RESET} ${CYAN}proj6_historic_calculator/2022/Dockerfile${RESET}
    ${DIM}${SCRIPT_DISPLAY_NAME}${RESET} ${GREEN}build${RESET} ${YELLOW}--path${RESET} ${CYAN}proj1_pyguard/Dockerfile.devEnv${RESET} ${YELLOW}--cloudsmith-workspace${RESET} ${CYAN}_YOUR_CLOUDSMITH_REPO_${RESET} ${YELLOW}--cloudsmith-api-key${RESET} ${CYAN}_YOUR_API_KEY_${RESET}
    ${DIM}${SCRIPT_DISPLAY_NAME}${RESET} ${GREEN}remove${RESET} ${YELLOW}--regex${RESET} ${CYAN}"projects-.*"${RESET}
EOF
}

detect_container_engine() {
    if command -v docker >/dev/null 2>&1; then
        CONTAINER_ENGINE="docker"
    elif command -v podman >/dev/null 2>&1; then
        CONTAINER_ENGINE="podman"
    else
        die "neither docker nor podman is installed"
    fi
}

image_tag_for() {
    local dockerfile_abs="$1"
    local rel_path project_name

    rel_path="${dockerfile_abs#"${PROJECTS_ROOT}/"}"
    project_name="${rel_path%%/*}"
    project_name="$(printf '%s' "${project_name}" | tr '[:upper:]' '[:lower:]')"
    printf 'mpe/%s\n' "${project_name}"
}

resolve_dockerfile_path() {
    local requested_path="$1"
    local cwd_path
    local resolved_path

    if [[ "${requested_path}" = /* ]]; then
        resolved_path="${requested_path}"
    else
        resolved_path="${PROJECTS_ROOT}/${requested_path}"
    fi

    if [[ ! -f "${resolved_path}" ]]; then
        if [[ "${requested_path}" != /* ]]; then
            cwd_path="$(pwd -P)/${requested_path}"
            if [[ -f "${cwd_path}" ]]; then
                cwd_path="$(cd -- "$(dirname -- "${cwd_path}")" && pwd -P)/$(basename -- "${cwd_path}")"
                die "cannot build Dockerfiles outside $(basename -- "${PROJECTS_ROOT}"): ${cwd_path}"
            fi
        fi
        die "Dockerfile not found inside $(basename -- "${PROJECTS_ROOT}"): ${resolved_path}"
    fi

    resolved_path="$(cd -- "$(dirname -- "${resolved_path}")" && pwd -P)/$(basename -- "${resolved_path}")"
    if [[ "${resolved_path}" != "${PROJECTS_ROOT}/"* ]]; then
        die "cannot build Dockerfiles outside $(basename -- "${PROJECTS_ROOT}"): ${resolved_path}"
    fi

    printf '%s\n' "${resolved_path}"
}

parse_build_args() {
    DOCKERFILE_PATH=""
    PORT_MAPPING="8080:8080"
    GPU_REQUEST=""
    BUILD_ONLY=0
    NO_CACHE=0
    RM_CONTAINER=0
    CLOUDSMITH_WORKSPACE=""
    CLOUDSMITH_API_KEY=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -h|--help)
                usage
                exit 0
                ;;
            -p|--path)
                [[ $# -ge 2 ]] || die "--path requires a value"
                DOCKERFILE_PATH="$2"
                shift 2
                ;;
            --path=*)
                DOCKERFILE_PATH="${1#*=}"
                shift
                ;;
            --port)
                [[ $# -ge 2 ]] || die "--port requires a value"
                PORT_MAPPING="$2"
                shift 2
                ;;
            --port=*)
                PORT_MAPPING="${1#*=}"
                shift
                ;;
            --gpus)
                [[ $# -ge 2 ]] || die "--gpus requires a value"
                GPU_REQUEST="$2"
                shift 2
                ;;
            --gpus=*)
                GPU_REQUEST="${1#*=}"
                shift
                ;;
            --build-only)
                BUILD_ONLY=1
                shift
                ;;
            --rebuild)
                NO_CACHE=1
                shift
                ;;
            --rm-container)
                RM_CONTAINER=1
                shift
                ;;
            --cloudsmith-workspace)
                [[ $# -ge 2 ]] || die "--cloudsmith-workspace requires a value"
                CLOUDSMITH_WORKSPACE="$2"
                shift 2
                ;;
            --cloudsmith-workspace=*)
                CLOUDSMITH_WORKSPACE="${1#*=}"
                shift
                ;;
            --cloudsmith-api-key)
                [[ $# -ge 2 ]] || die "--cloudsmith-api-key requires a value"
                CLOUDSMITH_API_KEY="$2"
                shift 2
                ;;
            --cloudsmith-api-key=*)
                CLOUDSMITH_API_KEY="${1#*=}"
                shift
                ;;
            -*)
                die "unknown build option: $1 (try --help)"
                ;;
            *)
                die "unexpected build argument: $1 (try --help)"
                ;;
        esac
    done

    [[ -n "${DOCKERFILE_PATH}" ]] || die "build requires --path (try --help)"
}

build_command() {
    parse_build_args "$@"

    local dockerfile_abs dockerfile_dir dockerfile_name build_context image_tag container_name
    local is_dev_image mount_source mount_target

    dockerfile_abs="$(resolve_dockerfile_path "${DOCKERFILE_PATH}")"

    dockerfile_dir="$(cd -- "$(dirname -- "${dockerfile_abs}")" && pwd)"
    dockerfile_name="$(basename -- "${dockerfile_abs}")"

    if [[ "${dockerfile_dir}" == */.devcontainer ]]; then
        die "building .devcontainer/Dockerfile images is not supported; pass a project Dockerfile or Dockerfile.devEnv instead"
    fi
    build_context="${dockerfile_dir}"

    detect_container_engine

    is_dev_image=0
    if [[ "${dockerfile_name}" == *.devEnv ]]; then
        is_dev_image=1
    fi

    image_tag="$(image_tag_for "${dockerfile_abs}")"
    container_name="$(printf '%s' "${image_tag}" \
        | sed -e 's|[^a-zA-Z0-9_.-]|-|g' -e 's|^-*||' -e 's|-*$||')"

    local host_uid host_gid
    local build_cmd=("${CONTAINER_ENGINE}" build)
    [[ "${NO_CACHE}" -eq 1 ]] && build_cmd+=(--no-cache)
    build_cmd+=(--file "${dockerfile_abs}" --tag "${image_tag}")

    if [[ "${is_dev_image}" -eq 1 ]]; then
        host_uid="$(id -u)"
        host_gid="$(id -g)"
        build_cmd+=(--build-arg "HOST_UID=${host_uid}" --build-arg "HOST_GID=${host_gid}")
    fi

    build_cmd+=("${build_context}")

    log "Image tag:       ${BOLD}${image_tag}${RESET}"
    log "Dockerfile:      ${dockerfile_abs}"
    log "Build context:   ${build_context}"
    if [[ "${is_dev_image}" -eq 1 ]]; then
        log "Image type:      ${GREEN}development${RESET}"
    else
        log "Image type:      ${GREEN}deployment${RESET}"
    fi

    log "Building image..."
    if [[ "${is_dev_image}" -eq 1 ]]; then
        log "Build user:      UID ${host_uid}, GID ${host_gid}"
    fi
    "${build_cmd[@]}"

    if [[ "${BUILD_ONLY}" -eq 1 ]]; then
        log "${GREEN}Build complete.${RESET} (skipping run because --build-only was set)"
        exit 0
    fi

    local run_cmd=("${CONTAINER_ENGINE}" run -it --name "${container_name}")
    local container_cmd=("/bin/bash")

    if [[ "${RM_CONTAINER}" -eq 1 ]]; then
        run_cmd+=(--rm)
    fi

    if [[ "${is_dev_image}" -eq 1 ]]; then
        mount_source="${build_context}"
        mount_target="/app"

        if [[ -d "${mount_source}" ]]; then
            log "Bind-mount:      ${mount_source} -> ${mount_target}"
            run_cmd+=(--volume "${mount_source}:${mount_target}")
        else
            warn "expected source path not found: ${mount_source} (running without bind mount)"
        fi
    fi

    # Every run mounts the project's .build/ directory at Conda's build root so
    # Conda packages and other build artifacts surface on the host.
    local build_artifact_dir="${build_context}/.build"
    mkdir -p "${build_artifact_dir}"
    log "Bind-mount:      ${build_artifact_dir} -> /opt/conda/conda-bld"
    run_cmd+=(--volume "${build_artifact_dir}:/opt/conda/conda-bld")

    run_cmd+=(--publish "${PORT_MAPPING}")

    if [[ -n "${GPU_REQUEST}" ]]; then
        run_cmd+=(--gpus "${GPU_REQUEST}")
    fi

    # --cloudsmith-workspace maps to CLOUDSMITH_REPOSITORY, which the container tooling reads.
    if [[ -n "${CLOUDSMITH_WORKSPACE}" ]]; then
        log "Cloudsmith:      forwarding CLOUDSMITH_REPOSITORY"
        run_cmd+=(--env "CLOUDSMITH_REPOSITORY=${CLOUDSMITH_WORKSPACE}")
    fi

    if [[ -n "${CLOUDSMITH_API_KEY}" ]]; then
        log "Cloudsmith:      forwarding CLOUDSMITH_API_KEY"
        run_cmd+=(--env "CLOUDSMITH_API_KEY=${CLOUDSMITH_API_KEY}")
    fi

    run_cmd+=("${image_tag}" "${container_cmd[@]}")

    log "Opening interactive Bash shell..."
    printf '%s    %s%s\n' "${DIM}" "${run_cmd[*]}" "${RESET}"
    exec "${run_cmd[@]}"
}

remove_command() {
    local regex=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -h|--help)
                usage
                exit 0
                ;;
            --regex)
                [[ $# -ge 2 ]] || die "--regex requires a value"
                regex="$2"
                shift 2
                ;;
            --regex=*)
                regex="${1#*=}"
                shift
                ;;
            -*)
                die "unknown remove option: $1 (try --help)"
                ;;
            *)
                die "unexpected remove argument: $1 (try --help)"
                ;;
        esac
    done

    [[ -n "${regex}" ]] || die "remove requires --regex (try --help)"
    detect_container_engine

    mapfile -t matched_images < <(
        "${CONTAINER_ENGINE}" image ls --format '{{.Repository}}:{{.Tag}}' \
            | grep -v '<none>' \
            | grep -E "${regex}" \
            | sort -u || true
    )

    if [[ ${#matched_images[@]} -eq 0 ]]; then
        warn "no local images matched regex: ${regex}"
        exit 0
    fi

    log "Removing ${#matched_images[@]} image(s) matching regex: ${regex}"
    printf '%s\n' "${matched_images[@]}"
    "${CONTAINER_ENGINE}" rmi "${matched_images[@]}"
}

PROJECTS_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
SCRIPT_DISPLAY_NAME="${0:-${BASH_SOURCE[0]}}"

if [[ $# -eq 0 ]]; then
    usage
    exit 1
fi

COMMAND="$1"
shift

case "${COMMAND}" in
    build)
        build_command "$@"
        ;;
    remove)
        remove_command "$@"
        ;;
    -h|--help)
        usage
        ;;
    *)
        die "unknown command: ${COMMAND} (expected build or remove)"
        ;;
esac
