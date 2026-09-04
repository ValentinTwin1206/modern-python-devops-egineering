FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency metadata
COPY pyproject.toml uv.lock ./

# Install dependencies into the system Python environment
RUN uv sync --frozen --no-dev

# Copy application source
COPY main.py database.py helpers.py ./

EXPOSE 8080

CMD ["python", "main.py"]