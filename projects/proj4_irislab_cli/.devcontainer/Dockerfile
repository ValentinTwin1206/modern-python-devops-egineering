# DEVELOPMENT IMAGE:
#   - uses the Ubuntu 24.04 Dev Containers base image
#   - installs uv, Nuitka, and the native build prerequisites Nuitka needs
#   - installs the Debian packaging tools used by scripts/build-deb.sh
#   - includes ELF inspection tools used to inspect compiled binary artifacts
#   - runs editor terminals and lifecycle commands as bob
# # # # # # # # # # #
FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04

# Avoid interactive APT prompts during image build.
ENV DEBIAN_FRONTEND=noninteractive

# Put user-level tools installed by uv on PATH.
ENV PATH="/home/bob/.local/bin:${PATH}" \
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
        devscripts \
        dpkg-dev \
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
    && groupmod --new-name bob vscode \
    && echo 'bob:c3po' | chpasswd

# Install user-level tools as the same account the container uses.
USER bob

# Install Nuitka as a user-level uv tool. It is intentionally not a project
# dependency: it is only needed to compile the executable.
RUN uv tool install nuitka

# Keep the final image user aligned with devcontainer.json.
USER bob
