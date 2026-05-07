# BUILD STAGE:
#   - uses python:3.12 to build the project wheel
#   - copies only metadata and source code needed for packaging
# # # # # # # # # # #
FROM python:3.12 AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /build

# Copy packaging inputs before building the wheel.
COPY pyproject.toml ./
COPY src ./src

RUN uv build --wheel

# RUNTIME STAGE:
#   - uses python:3.12-slim, matching the Chapter 1 deploy runtime pattern
#   - installs the wheel and starts the console entry point
# # # # # # # # # # #
FROM python:3.12-slim AS runtime

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy the built wheel without renaming it; installers validate wheel filenames.
COPY --from=builder /build/dist /tmp/dist

RUN uv pip install --system --no-cache /tmp/dist/tiny_webserver-*.whl \
    && rm -rf /tmp/dist

EXPOSE 8080

ENTRYPOINT ["tiny-webserver"]