FROM ubuntu:24.04

# install the required packages and dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    ca-certificates \
    gnupg \
    lsb-release \
    && rm -rf /var/lib/apt/lists/*

# extend the sources list to include the deadsnakes PPA for Python 3.9 and install it afterwards
COPY ./etc/apt/sources.list.d/python-ppa.list /etc/apt/sources.list.d/python-ppa.list

RUN curl -fsSL "https://keyserver.ubuntu.com/pks/lookup?op=get&search=0xF23C5A6CF475977595C89F51BA6932366A755776" | gpg --dearmor | tee /etc/apt/keyrings/deadsnakes.gpg \
    && apt update \
    && apt install -y python3.9 python3.9-venv python3.9-dev

WORKDIR /app

# create a non-root user and group for running the server
RUN groupadd --system bob && \
    useradd --system --gid bob --create-home --home-dir /home/bob --shell /usr/sbin/nologin bob


# setup bobs server
COPY ./server/* /app/server
COPY ./../secrets /app/secrets

RUN ls -la /app/secrets
RUN python3.9 -m venv /opt/venv  \
    && /opt/venv/bin/python3 -m pip install -r /app/server/requirements.txt \
    && chown -R bob:bob /app /opt/venv \
    && chmod -R 755 /app /opt/venv

USER bob

EXPOSE 8000

ENTRYPOINT ["/opt/venv/bin/python3", "/app/server/main.py"]
