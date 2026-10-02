FROM mcr.microsoft.com/devcontainers/javascript-node:24-bookworm

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Optional: proxy support for apt-get and npm during build
ARG HTTP_PROXY
ARG HTTPS_PROXY
ARG NO_PROXY
ENV HTTP_PROXY=${HTTP_PROXY}
ENV HTTPS_PROXY=${HTTPS_PROXY}
ENV NO_PROXY=${NO_PROXY}

# Set Playwright browsers path to shared location (outside node_modules)
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

#
# 1. SYSTEM PACKAGES
# # # # # # # # #
USER root
RUN apt-get update && apt-get upgrade -y \
    && apt-get install -y \
        bats \
        bats-support \
        bats-assert \
        bats-file \
        dnsutils \
    && rm -rf /var/lib/apt/lists/*

#
# 2. BUN + PLAYWRIGHT + ARTILLERY
# # # # # # # # #
# Install Bun and create symlinks for both bun and bunx in /usr/local/bin
# The development network intercepts TLS with a CA that is not in the base image.
RUN curl -kfsSL https://bun.com/install \
    | sed 's/curl --fail/curl --insecure --fail/' \
    | bash \
    && cp /root/.bun/bin/bun /usr/local/bin/bun \
    && cp /root/.bun/bin/bunx /usr/local/bin/bunx

# Install Playwright and Artillery globally
RUN mkdir -p /ms-playwright \
    && npm install -g @playwright/test@1.58.0 \
    artillery \
    && apt-get update \
    && npx playwright install --with-deps \
    && chown -R node:node /ms-playwright

#
# 3. SETUP WORKSPACE
# # # # # # # # #
USER node
WORKDIR /workspace

# Ensure local node_modules binaries are in the path
ENV PATH=/workspace/node_modules/.bin:$PATH

#
# 4. SANITY CHECKS
# # # # # # # # #
RUN bats --version \
    && bun --version \
    && bunx playwright --version \
    && artillery --version

EXPOSE 9323

CMD ["sleep", "infinity"]
