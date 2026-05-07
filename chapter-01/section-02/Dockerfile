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
#   - uses python:3.12-slim with a dedicated virtual environment
#   - installs the wheel and starts the console entry point
# # # # # # # # # # #
FROM python:3.12-slim AS runtime

WORKDIR /app

# Create the runtime virtual environment.
RUN python -m venv /opt/venv

ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY --from=builder /build/dist /tmp/dist

# Install the wheel into the virtual environment.
RUN pip install --upgrade pip \
    && pip install --no-cache-dir /tmp/dist/tiny_webserver-*.whl \
    && rm -rf /tmp/dist

EXPOSE 8080

ENTRYPOINT ["tiny-webserver"]