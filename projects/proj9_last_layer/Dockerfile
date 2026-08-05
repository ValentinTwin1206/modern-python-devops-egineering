FROM python:3.12-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends curl \
 && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/0.11.28/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /workspace

# Create a new project
RUN uv init demo

WORKDIR /workspace/demo

# Create a virtual environment
RUN uv venv

# Install the project (without a CLI entry point)
RUN uv pip install -e .

# ------------------------------------------------------------------
# LAST LAYER
# Add a console entry point and reinstall
# ------------------------------------------------------------------
RUN printf '\n[project.scripts]\ndemo = "main:main"\n' >> pyproject.toml

RUN uv pip install --no-cache -e .