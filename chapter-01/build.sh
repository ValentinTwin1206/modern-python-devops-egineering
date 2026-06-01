#!/usr/bin/env bash
# build.sh
#
# Build, run, and remove Tiny Webserver container images for this chapter.
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
${CYAN}${BOLD}${SCRIPT_DISPLAY_NAME}${RESET} ${DIM}- manage 'Tiny Webserver' container images${RESET}

${BLUE}${BOLD}USAGE${RESET}
    ${GREEN}${SCRIPT_DISPLAY_NAME}${RESET} ${YELLOW}<command>${RESET} ${DIM}[options]${RESET}

${BLUE}${BOLD}COMMANDS${RESET}
    ${GREEN}build${RESET}                  Builds an image from a Dockerfile, then opens an
                           interactive Bash shell unless ${YELLOW}--build-only${RESET} is set.
                           ${CYAN}.devcontainer/Dockerfile${RESET} paths are handled by
                           the Dev Containers CLI instead of Docker/Podman.
    ${GREEN}remove${RESET}                 Remove local images whose full tag matches ${YELLOW}--regex${RESET}.

${BLUE}${BOLD}BUILD OPTIONS${RESET}
    ${YELLOW}-p${RESET}, ${YELLOW}--path${RESET} ${CYAN}<DOCKERFILE>${RESET}   Path to a Dockerfile inside this chapter
                              ${DIM}(e.g. section-02/Dockerfile.devEnv).${RESET}
        ${YELLOW}--port${RESET} ${CYAN}<HOST:CONT>${RESET}    Port mapping. Defaults to ${CYAN}8080:8080${RESET}.
        ${YELLOW}--build-only${RESET}          Build the image but do not start a container.
        ${YELLOW}--rebuild${RESET}             Force a fresh build (${YELLOW}--no-cache${RESET}).
        ${YELLOW}--${RESET}                    Pass everything after this flag to docker run.

${BLUE}${BOLD}REMOVE OPTIONS${RESET}
        ${YELLOW}--regex${RESET} ${CYAN}<REGEX>${RESET}       Extended regex matched against image tags, such as
                              ${CYAN}"chapter-01-.*"${RESET}.

${BLUE}${BOLD}EXAMPLES${RESET}
    ${DIM}${SCRIPT_DISPLAY_NAME}${RESET} ${GREEN}build${RESET} ${YELLOW}--path${RESET} ${CYAN}section-02/Dockerfile.devEnv${RESET}
    ${DIM}${SCRIPT_DISPLAY_NAME}${RESET} ${GREEN}build${RESET} ${YELLOW}--path${RESET} ${CYAN}section-03/Dockerfile${RESET} ${YELLOW}--port${RESET} ${CYAN}9090:8080${RESET}
    ${DIM}${SCRIPT_DISPLAY_NAME}${RESET} ${GREEN}build${RESET} ${YELLOW}-p${RESET} ${CYAN}section-04/.devcontainer/Dockerfile${RESET} ${YELLOW}--rebuild${RESET}
    ${DIM}${SCRIPT_DISPLAY_NAME}${RESET} ${GREEN}remove${RESET} ${YELLOW}--regex${RESET} ${CYAN}"chapter-01-.*"${RESET}

${BLUE}${BOLD}DEVCONTAINER CLI${RESET}
    Install Node.js/npm:  ${CYAN}sudo apt-get update && sudo apt-get install -y nodejs npm${RESET}
    Install globally:     ${CYAN}npm install -g @devcontainers/cli${RESET}
    Or run once with:     ${CYAN}npx @devcontainers/cli build --workspace-folder section-04${RESET}
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

detect_devcontainer_cli() {
    if command -v devcontainer >/dev/null 2>&1; then
        DEVCONTAINER_CLI="devcontainer"
    else
        die "devcontainer CLI is required for '.devcontainer/Dockerfile' paths. Install Node.js/npm first if needed, then run 'npm install -g @devcontainers/cli' or 'npx @devcontainers/cli'."
    fi
}

confirm_devcontainer_cli() {
    local action="$1"
    local workspace_folder="$2"
    local answer=""

    warn ".devcontainer/Dockerfile must be handled by the Dev Containers CLI, not by docker build."
    warn "This will run: ${DEVCONTAINER_CLI} ${action} --workspace-folder ${workspace_folder}"

    if [[ ! -t 0 ]]; then
        die "interactive confirmation is required before running the Dev Containers CLI"
    fi

    printf '%sType %s to continue: %s' "${YELLOW}${BOLD}" "devcontainer" "${RESET}" >&2
    read -r answer
    [[ "${answer}" == "devcontainer" ]] || die "Dev Containers CLI run cancelled"
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
    PORT_MAPPING="8080:8080"
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
            --port)
                [[ $# -ge 2 ]] || die "--port requires a value"
                PORT_MAPPING="$2"
                shift 2
                ;;
            --port=*)
                PORT_MAPPING="${1#*=}"
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
    local is_devcontainer is_dev_image section_name mount_source mount_target

    dockerfile_abs="$(resolve_dockerfile_path "${DOCKERFILE_PATH}")"

    dockerfile_dir="$(cd -- "$(dirname -- "${dockerfile_abs}")" && pwd)"
    dockerfile_name="$(basename -- "${dockerfile_abs}")"

    is_devcontainer=0
    if [[ "${dockerfile_dir}" == */.devcontainer ]]; then
        build_context="$(cd -- "${dockerfile_dir}/.." && pwd)"
        is_devcontainer=1
    else
        build_context="${dockerfile_dir}"
    fi

    if [[ "${is_devcontainer}" -eq 1 ]]; then
        run_devcontainer_command "${build_context}"
        exit 0
    fi

    detect_container_engine

    is_dev_image=0
    if [[ "${dockerfile_name}" == *.devEnv ]] || [[ "${is_devcontainer}" -eq 1 ]]; then
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

    local run_cmd=("${CONTAINER_ENGINE}" run --rm -it --name "${container_name}" --entrypoint /bin/bash)

    if [[ "${is_dev_image}" -eq 1 ]]; then
        section_name="$(basename -- "${build_context}")"
        if [[ "${is_devcontainer}" -eq 1 ]]; then
            mount_source="${build_context}"
            mount_target="/workspaces/${section_name}"
        else
            mount_source="${build_context}/src"
            mount_target="/app/src"
        fi

        if [[ -d "${mount_source}" ]]; then
            log "Bind-mount:      ${mount_source} -> ${mount_target}"
            run_cmd+=(--volume "${mount_source}:${mount_target}")
        else
            warn "expected source path not found: ${mount_source} (running without bind mount)"
        fi
    fi

    run_cmd+=(--publish "${PORT_MAPPING}")

    if [[ ${#EXTRA_ARGS[@]} -gt 0 ]]; then
        run_cmd+=("${EXTRA_ARGS[@]}")
    fi

    run_cmd+=("${image_tag}")

    log "Opening interactive Bash shell..."
    printf '%s    %s%s\n' "${DIM}" "${run_cmd[*]}" "${RESET}"
    exec "${run_cmd[@]}"
}

run_devcontainer_command() {
    local workspace_folder="$1"
    local action="up"
    local devcontainer_cmd

    [[ ${#EXTRA_ARGS[@]} -eq 0 ]] || die "docker run passthrough args are not supported for .devcontainer/Dockerfile paths"

    detect_devcontainer_cli

    if [[ "${BUILD_ONLY}" -eq 1 ]]; then
        action="build"
    fi

    confirm_devcontainer_cli "${action}" "${workspace_folder}"

    devcontainer_cmd=("${DEVCONTAINER_CLI}" "${action}" --workspace-folder "${workspace_folder}")
    if [[ "${NO_CACHE}" -eq 1 && "${action}" == "build" ]]; then
        devcontainer_cmd+=(--no-cache)
    elif [[ "${NO_CACHE}" -eq 1 ]]; then
        warn "--rebuild is ignored for devcontainer up; use --build-only --rebuild to force a no-cache build"
    fi

    log "Running Dev Containers CLI..."
    printf '%s    %s%s\n' "${DIM}" "${devcontainer_cmd[*]}" "${RESET}"
    exec "${devcontainer_cmd[@]}"
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
