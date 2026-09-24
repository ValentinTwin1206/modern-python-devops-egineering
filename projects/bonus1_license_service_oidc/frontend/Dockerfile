FROM python:3.12-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml .

RUN uv sync --no-dev

COPY app.py .
COPY api.py .
COPY entrypoint.sh .

EXPOSE 8501

CMD ["sh", "/app/entrypoint.sh"]