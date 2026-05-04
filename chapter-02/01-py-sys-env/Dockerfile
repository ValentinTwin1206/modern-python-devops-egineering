FROM ubuntu:26.04

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/root/.local/bin:$PATH"
ENV PYTHONPATH=/app/src

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        python3 \
        python3-pip \
        tree \
    && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

RUN uv pip install --system --break-system-packages bottle karva ruff

COPY pyproject.toml uv.lock ./
COPY src ./src
COPY tests ./tests

RUN echo "Python executable from PATH:" \
    && which python3 \
    && python3 --version \
    && echo \
    && echo "Python site configuration:" \
    && python3 -m site \
    && echo \
    && echo "sys.path:" \
    && python3 -c "import sys; [print(path) for path in sys.path]" \
    && echo \
    && echo "sysconfig package directories:" \
    && python3 -c "import sysconfig; print('purelib =', sysconfig.get_path('purelib')); print('platlib =', sysconfig.get_path('platlib'))" \
    && echo \
    && echo "Installed package locations:" \
    && python3 -c "import bottle, karva, ruff; print('bottle =', bottle.__file__); print('karva =', karva.__file__); print('ruff =', ruff.__file__)" \
    && echo \
    && echo "Project directory structure:" \
    && tree -L 4 /app

EXPOSE 8080

CMD ["python3", "-m", "tiny_webserver.app"]