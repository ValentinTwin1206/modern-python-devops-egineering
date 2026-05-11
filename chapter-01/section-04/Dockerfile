# BUILD STAGE:
#   - uses python:3.12 to build the project wheel
#   - copies only metadata and source code needed for packaging
# # # # # # # # # # #
FROM python:3.12 AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /build

COPY pyproject.toml ./
COPY src ./src

RUN uv build --wheel

# RUNTIME STAGE:
#   - uses python:3.12-slim with a pipenv-managed virtual environment
#   - installs the wheel and starts the FastAPI app via the console entry point
# # # # # # # # # # #
FROM python:3.12-slim AS runtime

WORKDIR /app

RUN pip install --no-cache-dir pipenv==2024.4.0

COPY Pipfile Pipfile.lock* ./

ENV PIPENV_VENV_IN_PROJECT=1
RUN if [ ! -f Pipfile.lock ]; then pipenv lock; fi \
    && pipenv install --deploy

ENV VIRTUAL_ENV=/app/.venv
ENV PATH=/app/.venv/bin:$PATH

COPY --from=builder /build/dist /tmp/dist

RUN /app/.venv/bin/pip install --no-cache-dir /tmp/dist/fastapi_crud-*.whl \
    && rm -rf /tmp/dist

EXPOSE 8080

ENTRYPOINT ["fastapi-crud"]
