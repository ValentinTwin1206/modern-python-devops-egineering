# DEPLOYMENT IMAGE:
#   - uses ubuntu:24.04 to keep the APT package `python3-systemd` available
#   - installs the journal-admin wheel into the system Python
#   - reads the journal from a mounted host path at runtime
# # # # # # # # # # #
FROM ubuntu:24.04 AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        python3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Copy packaging inputs before building the wheel.
COPY pyproject.toml ./
COPY src ./src

RUN uv build --wheel

# RUNTIME STAGE:
#   - uses ubuntu:24.04 so the APT-managed `python3-systemd` binding is available
#   - installs the wheel into the system interpreter under /usr
# # # # # # # # # # #
FROM ubuntu:24.04 AS runtime

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        python3 \
        python3-systemd \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /build/dist /tmp/dist

RUN uv pip install --system --break-system-packages --no-cache /tmp/dist/journal_admin-*.whl \
    && rm -rf /tmp/dist

# At runtime, mount the host journal (and machine-id) read-only. systemd does
# not need to be PID 1: `systemd.journal.Reader` opens the journal files
# directly through libsystemd.
#   docker run --rm \
#     -v /etc/machine-id:/etc/machine-id:ro \
#     -v /var/log/journal:/var/log/journal:ro \
#     -v /run/log/journal:/run/log/journal:ro \
#     journal-admin --since-minutes 30
ENTRYPOINT ["journal-admin"]
