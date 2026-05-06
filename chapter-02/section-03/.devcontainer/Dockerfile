FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04

# Avoid interactive APT prompts during image build.
ENV DEBIAN_FRONTEND=noninteractive

# The uv installer places the binary in the vscode user's local bin dir.
# Put that location on PATH so later lifecycle commands can call `uv`
# without an absolute path.
ENV PATH="/home/vscode/.local/bin:${PATH}"

# Install the system-level tools that define the container's Python base:
# - CPython (`python3`, `python3-pip`, `python3-venv`)
# - PyPy (`pypy3`, `pypy3-venv`)
# - basic transport/VCS tools needed in a development container
# The package index is cleaned afterward to keep the image smaller.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        git \
        pypy3 \
        pypy3-venv \
        python3 \
        python3-pip \
        python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Install uv as the non-root development user so it lives in the same
# account that VS Code uses when the Dev Container starts.
USER vscode

# Fetch and install uv into /home/vscode/.local/bin.
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Switch back to root so later image extensions or derived Dockerfiles can
# still add system packages without first changing users again.
USER root
