# BUILD STAGE:
#   - uses python:3.12, matching the other Chapter 1 deploy images
#   - installs the native compiler/linker tools Nuitka needs
#   - builds the project wheel with uv and installs that wheel into the builder
#   - compiles the installed app module into a one-file executable
# # # # # # # # # # #
FROM python:3.12 AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# install system tools
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        patchelf \
    && rm -rf /var/lib/apt/lists/*

# Copy project metadata first so Docker can cache dependency installation
COPY pyproject.toml ./
COPY src ./src

# Build the wheel, then install that wheel and Nuitka into the builder.
RUN uv build --wheel \
    && pip install --no-cache-dir nuitka dist/*.whl

# Compile the installed app into one executable.
RUN python -m nuitka \
        --onefile \
        --output-dir=/out \
        --output-filename=tiny-webserver \
        --include-package=bottle \
        "$(python -c 'import tiny_webserver.app as app; print(app.__file__)')"

# RUNTIME STAGE:
#   - uses python:3.12-slim, matching the Chapter 1 deploy runtime pattern
#   - exposes port 8080 and starts the binary directly
# # # # # # # # # # #
FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy only the compiled executable from the build stage into the runtime image.
COPY --from=builder /out/tiny-webserver ./tiny-webserver

EXPOSE 8080

ENTRYPOINT ["/app/tiny-webserver"]