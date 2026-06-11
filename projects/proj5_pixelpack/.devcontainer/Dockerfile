# DEVELOPMENT IMAGE:
#   - uses the Ubuntu 24.04 Dev Containers base image
#   - installs CPython, PyPy, uv, and Nuitka tooling
#   - runs editor terminals and lifecycle commands as vscode
# # # # # # # # # # #
FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04

# Avoid interactive APT prompts during image build.
ENV DEBIAN_FRONTEND=noninteractive

# Put user-level tools installed by uv on PATH.
ENV PATH="/home/vscode/.local/bin:${PATH}"

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Install Python runtimes, the native tools Nuitka needs, and the system
# libraries Pillow links against for JPEG, PNG, and zlib support.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        curl \
        debhelper \
        dpkg-dev \
        git \
        libjpeg-dev \
        libpng-dev \
        patchelf \
        pypy3 \
        pypy3-venv \
        python3 \
        python3-dev \
        python3-pip \
        python3-venv \
        zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Install user-level tools as the same account VS Code uses.
USER vscode

# Install Nuitka as a user-level uv tool.
RUN uv tool install nuitka

# Keep the final image user aligned with devcontainer.json.
USER vscode
