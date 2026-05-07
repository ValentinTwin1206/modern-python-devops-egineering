#!/usr/bin/env bash
# build.sh
#
# Build, run, and remove Historic Calculator container images for this chapter.
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
${CYAN}${BOLD}${SCRIPT_DISPLAY_NAME}${RESET} ${DIM}- manage Historic Calculator container images${RESET}

${BLUE}${BOLD}USAGE${RESET}
    ${GREEN}${SCRIPT_DISPLAY_NAME}${RESET} ${YELLOW}<command>${RESET} ${DIM}[options]${RESET}

${BLUE}${BOLD}COMMANDS${RESET}
    ${GREEN}build${RESET}                  Builds and (optionally) runs an image from a Dockerfile
    ${GREEN}remove${RESET}                 Remove local images whose full tag matches ${YELLOW}--regex${RESET}.

${BLUE}${BOLD}BUILD OPTIONS${RESET}
    ${YELLOW}-p${RESET}, ${YELLOW}--path${RESET} ${CYAN}<DOCKERFILE>${RESET}   Path to a Dockerfile inside this chapter
                              ${DIM}(e.g. section-04/Dockerfile.devEnv).${RESET}
        ${YELLOW}--build-only${RESET}          Build the image but do not start a container.
        ${YELLOW}--rebuild${RESET}             Force a fresh build (${YELLOW}--no-cache${RESET}).
        ${YELLOW}--${RESET}                    Pass everything after this flag to docker run.

${BLUE}${BOLD}REMOVE OPTIONS${RESET}
        ${YELLOW}--regex${RESET} ${CYAN}<REGEX>${RESET}       Extended regex matched against image tags, such as
                              ${CYAN}"chapter-02-.*"${RESET}.

${BLUE}${BOLD}EXAMPLES${RESET}
    ${DIM}${SCRIPT_DISPLAY_NAME}${RESET} ${GREEN}build${RESET} ${YELLOW}--path${RESET} ${CYAN}section-04/Dockerfile.devEnv${RESET}
    ${DIM}${SCRIPT_DISPLAY_NAME}${RESET} ${GREEN}build${RESET} ${YELLOW}--path${RESET} ${CYAN}section-06/Dockerfile${RESET} ${YELLOW}--rebuild${RESET}
    ${DIM}${SCRIPT_DISPLAY_NAME}${RESET} ${GREEN}remove${RESET} ${YELLOW}--regex${RESET} ${CYAN}"chapter-02-.*"${RESET}
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
    local chapter_name rel_path slug

    chapter_name="$(basename -- "${CHAPTER_ROOT}")"
    rel_path="${dockerfile_abs#"${CHAPTER_ROOT}/"}"
    slug="$(printf '%s/%s' "${chapter_name}" "${rel_path}" \
        | tr '[:upper:]' '[:lower:]' \
        | sed -e 's|/|-|g' -e 's|\.|-|g')"
    printf 'mpe/%s:latest\n' "${slug}"
}

resolve_dockerfile_path() {
    local requested_path="$1"
    local cwd_path
    local resolved_path

    if [[ "${requested_path}" = /* ]]; then
        resolved_path="${requested_path}"
    else
        resolved_path="${CHAPTER_ROOT}/${requested_path}"
    fi

    if [[ ! -f "${resolved_path}" ]]; then
        if [[ "${requested_path}" != /* ]]; then
            cwd_path="$(pwd -P)/${requested_path}"
            if [[ -f "${cwd_path}" ]]; then
                cwd_path="$(cd -- "$(dirname -- "${cwd_path}")" && pwd -P)/$(basename -- "${cwd_path}")"
                die "cannot build Dockerfiles outside $(basename -- "${CHAPTER_ROOT}"): ${cwd_path}"
            fi
        fi
        die "Dockerfile not found inside $(basename -- "${CHAPTER_ROOT}"): ${resolved_path}"
    fi

    resolved_path="$(cd -- "$(dirname -- "${resolved_path}")" && pwd -P)/$(basename -- "${resolved_path}")"
    if [[ "${resolved_path}" != "${CHAPTER_ROOT}/"* ]]; then
        die "cannot build Dockerfiles outside $(basename -- "${CHAPTER_ROOT}"): ${resolved_path}"
    fi

    printf '%s\n' "${resolved_path}"
}

parse_build_args() {
    DOCKERFILE_PATH=""
    BUILD_ONLY=0
    NO_CACHE=0
    EXTRA_ARGS=()

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
            --build-only)
                BUILD_ONLY=1
                shift
                ;;
            --rebuild)
                NO_CACHE=1
                shift
                ;;
            --)
                shift
                EXTRA_ARGS+=("$@")
                break
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
    local is_dev_image

    dockerfile_abs="$(resolve_dockerfile_path "${DOCKERFILE_PATH}")"
    detect_container_engine

    dockerfile_dir="$(cd -- "$(dirname -- "${dockerfile_abs}")" && pwd)"
    dockerfile_name="$(basename -- "${dockerfile_abs}")"
    build_context="${dockerfile_dir}"

    is_dev_image=0
    if [[ "${dockerfile_name}" == *.devEnv ]]; then
        is_dev_image=1
    fi

    image_tag="$(image_tag_for "${dockerfile_abs}")"
    container_name="$(printf '%s' "${image_tag}" \
        | sed -e 's|[^a-zA-Z0-9_.-]|-|g' -e 's|^-*||' -e 's|-*$||')"

    local build_cmd=("${CONTAINER_ENGINE}" build)
    [[ "${NO_CACHE}" -eq 1 ]] && build_cmd+=(--no-cache)
    build_cmd+=(--file "${dockerfile_abs}" --tag "${image_tag}" "${build_context}")

    log "Image tag:       ${BOLD}${image_tag}${RESET}"
    log "Dockerfile:      ${dockerfile_abs}"
    log "Build context:   ${build_context}"
    if [[ "${is_dev_image}" -eq 1 ]]; then
        log "Image type:      ${GREEN}development${RESET}"
    else
        log "Image type:      ${GREEN}deployment${RESET}"
    fi

    log "Building image..."
    "${build_cmd[@]}"

    if [[ "${BUILD_ONLY}" -eq 1 ]]; then
        log "${GREEN}Build complete.${RESET} (skipping run because --build-only was set)"
        exit 0
    fi

    local run_cmd=("${CONTAINER_ENGINE}" run --rm -it --name "${container_name}" "${image_tag}")

    if [[ ${#EXTRA_ARGS[@]} -gt 0 ]]; then
        run_cmd+=("${EXTRA_ARGS[@]}")
    fi

    log "Running container..."
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

CHAPTER_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
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
