## This Dockerfile is intentionally structured for teaching purposes.
## It demonstrates APT-managed, user-level, and system-level Python
## package installation side by side, which is useful for inspection but
## deliberately does not reflect container packaging best practices.
FROM ubuntu:26.04

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/root/.local/bin:$PATH"
ENV PYTHONPATH=/app/src

WORKDIR /app

# `python3` is the standard Ubuntu interpreter name, but the minimal
# ubuntu:26.04 base image does not ship it by default.
# Unlike the official `python:*` images, this Ubuntu base installs the
# interpreter under `/usr` via APT rather than shipping Python from
# `/usr/local`.
# `python3-pip` is also installed with APT so the image can contrast
# Debian-managed Python files under `/usr/lib/python3/dist-packages`
# with user installs under `/root/.local` and system-level installs
# performed by `uv`.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        python3 \
        python3-pip \
        tree \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | sh

# User installs land under `/root/.local/lib/python3.14/site-packages`
# and their console scripts land under `/root/.local/bin`.
RUN pip3 install --user karva ruff

# Ubuntu marks its APT-managed interpreter as externally managed, so
# `uv` needs the explicit override to install into the system Python
# by providing the `--system` and `--break-system-packages` flags. 
RUN uv pip install --system --break-system-packages bottle

EXPOSE 8080

# Drop into an interactive shell. Source files are expected to be
# bind-mounted into `/app` at runtime.
ENTRYPOINT ["/bin/bash"]