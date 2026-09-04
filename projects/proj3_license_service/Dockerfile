FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency metadata
COPY pyproject.toml uv.lock ./

# Install dependencies into a project-local virtual environment
RUN uv sync --frozen --no-dev
ENV PATH="/app/.venv/bin:${PATH}"

# Copy application source
COPY main.py database.py helpers.py ./

EXPOSE 8080

CMD ["python", "main.py"]