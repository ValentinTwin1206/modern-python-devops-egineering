# Teaching image: a shared Linux machine with two real users.
#
# Bob is the administrator (sudo, passwordless for demos).
# Alice is an unprivileged user.
#
# The system Python interpreter deliberately contains Bob's legacy
# dependency (requests==2.25.1) so the notebook can demonstrate
# dependency conflicts and progressively solve them.
FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive

ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

# ----------------------------------------------------------------------
# Base operating-system tooling
# ----------------------------------------------------------------------
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        git \
        passwd \
        procps \
        python3 \
        python3-dev \
        python3-pip \
        python3-systemd \
        python3-venv \
        sudo \
        util-linux \
    && rm -rf /var/lib/apt/lists/*

# ----------------------------------------------------------------------
# Create users
#
# Bob:
#   - administrator
#   - password: bar
#   - passwordless sudo for the demonstration
#
# Alice:
#   - unprivileged
#   - password: foo
# ----------------------------------------------------------------------
RUN useradd \
        --create-home \
        --shell /bin/bash \
        --groups sudo \
        bob \
    && echo 'bob:bar' | chpasswd \
    && echo 'bob ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/90-bob \
    && chmod 0440 /etc/sudoers.d/90-bob \
    && useradd \
        --create-home \
        --shell /bin/bash \
        alice \
    && echo 'alice:foo' | chpasswd

# ----------------------------------------------------------------------
# System Python
#
# Ubuntu 22.04 ships an older pip than the notebook demonstration uses.
# Upgrade pip first so later cells can keep --break-system-packages
# explicit when they intentionally modify the shared interpreter.
# ----------------------------------------------------------------------
RUN python3 -m pip install \
    --no-cache-dir \
    --upgrade pip \
    && python3 -m pip install \
    --break-system-packages \
    --no-cache-dir \
    jupyterlab \
    notebook \
    ipykernel \
    ipywidgets \
    "requests==2.25.1"

# Register the system Python as a clearly named Jupyter kernel.
RUN python3 -m ipykernel install \
        --sys-prefix \
        --name system-python3 \
        --display-name "Python 3 — Ubuntu System"

# ----------------------------------------------------------------------
# Alice's initial user environment
#
# These packages deliberately live in Alice's ~/.local directory.
# They do not modify the system Python installation.
#
# Keep requests out of this installation initially: the notebook should
# demonstrate the conflict with Bob's system-level requests==2.25.1.
# ----------------------------------------------------------------------
RUN su - alice -c \
    'python3 -m pip install --user --no-cache-dir fastapi==0.68.2 "pydantic<2"'

# ----------------------------------------------------------------------
# Workspace
# ----------------------------------------------------------------------
RUN install -d -o bob -g bob /workspace

USER bob

WORKDIR /workspace

CMD ["/bin/bash"]
