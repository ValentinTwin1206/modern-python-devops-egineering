# DEVELOPMENT IMAGE:
#   - uses the Ubuntu 24.04 Dev Containers base image
#   - installs uv and native Nuitka build prerequisites
#   - includes ELF inspection tools used to inspect compiled binary artifacts
#   - includes native build prerequisites used by Nuitka
#   - runs editor terminals and lifecycle commands as bob
# # # # # # # # # # #
FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04

# Avoid interactive APT prompts during image build.
ENV DEBIAN_FRONTEND=noninteractive

# Put user-level tools installed by uv on PATH.
ENV PATH="/home/bob/.local/bin:${PATH}" \
    CLOUDSMITH_REPOSITORY=""

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Install Python and the native tools Nuitka needs.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        binutils \
        ca-certificates \
        coreutils \
        curl \
        file \
        git \
        libc-bin \
        patchelf \
        python3 \
        python3-dev \
        python3-venv \
        sudo \
    && rm -rf /var/lib/apt/lists/*

# Keep the base image's host-mapped UID/GID while using the project's bob name.
USER root
RUN usermod --login bob --home /home/bob --move-home vscode \
    && groupmod --new-name bob vscode

# Install user-level tools as the same account the container uses.
USER bob

# Keep the final image user aligned with devcontainer.json.
USER bob
