# Teaching image: a shared Linux machine with two real users.
# Bob is the admin (sudo, passwordless for demos). Alice is an unprivileged user.
# The system Python interpreter comes pre-loaded with Bob's legacy dependency
# (requests==2.0.0) so the notebook can demonstrate dependency conflicts.
FROM ubuntu:26.04

ARG DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PIP_ROOT_USER_ACTION=ignore \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

# Minimal OS tooling required for the demonstration.
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-venv \
        python3-dev \
        sudo \
        passwd \
        procps \
        util-linux \
        curl \
        ca-certificates \
        git \
    && rm -rf /var/lib/apt/lists/*

# Ubuntu 24.04+ marks the system interpreter as an externally-managed
# environment (PEP 668). The teaching scenario deliberately installs into
# the system interpreter, so we allow that behaviour system-wide.
RUN printf '[global]\nbreak-system-packages = true\n' > /etc/pip.conf

# Notebook stack for the system Python interpreter plus Bob's legacy
# dependency. Everything is installed system-wide on purpose so the
# notebook can demonstrate conflicts later.
RUN python3 -m pip install --no-cache-dir \
    jupyterlab \
    notebook \
    ipykernel \
    ipywidgets \
    "requests==2.0.0"

# Register a clearly named kernel that targets /usr/bin/python3.
RUN python3 -m ipykernel install \
    --name system-python3 \
    --display-name "Python 3 — Ubuntu System"

# Bob: administrator, passwordless sudo so the notebook can demonstrate
# elevated actions without ever surfacing his password.
RUN useradd --create-home --shell /bin/bash --groups sudo bob \
    && echo 'bob:bar' | chpasswd \
    && echo 'bob ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/90-bob \
    && chmod 0440 /etc/sudoers.d/90-bob

# Alice: unprivileged user with her own home directory.
RUN useradd --create-home --shell /bin/bash alice \
    && echo 'alice:foo' | chpasswd

# Seed Alice's user site with application-level dependencies only. Requests
# stays untouched here so the shared system copy remains the source of the
# cross-user conflict demonstrated in the notebook.
RUN su - alice -c 'python3 -m pip install --user "fastapi==0.68.2" "pydantic<2"'

# Alice needs to be able to shell in via `su` from Bob's sessions for
# ipywidgets demos. `su` itself only asks for a password when the caller
# is not root, so the notebook always routes user switches through sudo.

# Workspace that Dev Containers will bind-mount over.
RUN mkdir -p /workspace && chown bob:bob /workspace

USER bob
WORKDIR /workspace

# Default: start an interactive shell. The devcontainer.json overrides
# this when VS Code attaches; the README documents the manual `docker run`.
CMD ["/bin/bash"]
