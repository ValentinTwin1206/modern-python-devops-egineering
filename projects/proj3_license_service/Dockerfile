FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency metadata
COPY pyproject.toml uv.lock ./

# Make the lockfile's editable dependency available at /proj1_pyguard
# (uv.lock contains ../proj1_pyguard, resolved relative to /app).
COPY --from=pyguard . /proj1_pyguard

# Install dependencies into a project-local virtual environment
RUN uv sync --frozen --no-dev
ENV PATH="/app/.venv/bin:${PATH}"

# Copy application source
COPY main.py database.py helpers.py ./

EXPOSE 8080

CMD ["python", "main.py"]