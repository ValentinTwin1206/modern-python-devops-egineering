# DEVELOPMENT IMAGE:
#   - uses the Ubuntu 24.04 Dev Containers base image
#   - installs CPython, uv, and Nuitka tooling
#   - includes ELF inspection tools used to inspect compiled binary artifacts
#   - includes Debian packaging tools used to build the .deb artifact
#   - runs editor terminals and lifecycle commands as vscode
# # # # # # # # # # #
FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04

# Avoid interactive APT prompts during image build.
ENV DEBIAN_FRONTEND=noninteractive

# Put user-level tools installed by uv on PATH.
ENV PATH="/home/vscode/.local/bin:${PATH}" \
    CLOUDSMITH_REPOSITORY=""

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Install Python, the native tools Nuitka needs, and Debian packaging tools.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        binutils \
        ca-certificates \
        coreutils \
        curl \
        debhelper \
        dpkg-dev \
        devscripts \
        file \
        git \
        libc-bin \
        patchelf \
        python3 \
        python3-dev \
        python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Install user-level tools as the same account VS Code uses.
USER vscode

# Install Nuitka as a container-level build tool. It intentionally does not
# belong to the project's Python dependency metadata.
RUN uv tool install nuitka

# Keep the final image user aligned with devcontainer.json.
USER vscode
