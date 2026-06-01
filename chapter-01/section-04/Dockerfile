# BUILD STAGE:
#   - uses python:3.12, matching the other Chapter 1 deploy images
#   - installs the native compiler/linker tools Nuitka needs and the
#     image libraries Pillow links against
#   - builds the project wheel with uv and installs that wheel into the builder
#   - compiles the installed CLI module into a one-file executable
# # # # # # # # # # #
FROM python:3.12 AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# install system tools and Pillow build dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        libjpeg-dev \
        libpng-dev \
        patchelf \
        zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy project metadata first so Docker can cache dependency installation
COPY pyproject.toml ./
COPY src ./src

# Build the wheel, then install that wheel and Nuitka into the builder.
RUN uv build --wheel \
    && pip install --no-cache-dir nuitka dist/*.whl

# Compile the installed CLI into one executable.
RUN python -m nuitka \
        --onefile \
        --output-dir=/out \
        --output-filename=pixelpack \
        --include-package=PIL \
        --include-package=click \
        "$(python -c 'import pixelpack.cli as m; print(m.__file__)')"

# RUNTIME STAGE:
#   - uses python:3.12-slim, matching the Chapter 1 deploy runtime pattern
#   - keeps the Pillow runtime libraries available for the compiled binary
# # # # # # # # # # #
FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libjpeg62-turbo \
        libpng16-16 \
        zlib1g \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only the compiled executable from the build stage into the runtime image.
COPY --from=builder /out/pixelpack /usr/local/bin/pixelpack

ENTRYPOINT ["/usr/local/bin/pixelpack"]
