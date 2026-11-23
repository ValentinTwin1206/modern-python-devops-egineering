# Testing

## Applied Project

This section builds on the previous [section](./section-02.md) by adding a Dev Container as another project component. Dev Containers were first introduced in [Chapter 01, Section 04](../../chapter-01/section-04.md) as a way to provide a reproducible development environment. Here, the container includes the heavier configuration and tooling needed to test the complete application stack in a more realistic, end-to-end environment. 

```mermaid
flowchart LR
    F["Frontend"] --> K["Keycloak OIDC"]
    K --> F
    K --> P["PostgreSQL"]
    F --> A["Backend"]
    A --> M["MongoDB"]
    A --> INFLUXDB["InfluxDB"]
    INFLUXDB --> GRAFANA["Grafana"]
    A -->|logs| ALLOY["Grafana Alloy"]
    ALLOY --> LOKI["Loki"]
    LOKI --> GRAFANA
    subgraph DEVCONTAINER["Dev Container"]
        PW["Playwright"]
        ART["Artillery"]
    end
    PW --> F
    ART --> PW
    ART --> A
```

!!! info "info"
	This section uses Playwright and Artillery, both JavaScript-based tools. Rather than covering them in depth, it focuses on the infrastructure and setup needed to integrate them into the development and testing workflow.

### Project Setup

**docker-compose.yaml**

The compose setup is extended with the new service `devcontainer` which provides the needed tools for our end-to-end testing chain. It reaches the published Keycloak port through the Compose gateway (`extra_hosts`) and receives the test credentials from `.env`.

```yaml
services:
  devcontainer:
    build:
      context: .
      dockerfile: .devcontainer/Dockerfile
    command: sleep infinity
    depends_on:
      - backend
      - frontend
    volumes:
      - .:/workspace:cached
    working_dir: /workspace
    extra_hosts:
      - "keycloak.localhost:172.30.0.1"
    environment:
      PLAYWRIGHT_HOST_GATEWAY: 172.30.0.1
      KEYCLOAK_TEST_USERNAME: ${KEYCLOAK_TEST_USERNAME}
      KEYCLOAK_TEST_PASSWORD: ${KEYCLOAK_TEST_PASSWORD}
      IRIS_PERF_CLIENT_SECRET: ${IRIS_PERF_CLIENT_SECRET:-}
      IRIS_PERF_UPLOADS: ${IRIS_PERF_UPLOADS:-50}
    networks:
      irislab_network:

	...

```

**Dockerfile**

The Dev Container image is based on Microsoft's JavaScript and Node.js development image and is stored in the required `.devcontainer/Dockerfile` path. It installs the command-line tools required by the project, including Bun, Playwright, and Artillery, and stores Playwright's browser binaries in a shared directory.

```dockerfile
FROM mcr.microsoft.com/devcontainers/javascript-node:24-bookworm

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

ARG HTTP_PROXY
ARG HTTPS_PROXY
ARG NO_PROXY
ENV HTTP_PROXY=${HTTP_PROXY}
ENV HTTPS_PROXY=${HTTPS_PROXY}
ENV NO_PROXY=${NO_PROXY}
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

USER root
RUN apt-get update && apt-get upgrade -y \
	&& apt-get install -y bats bats-support bats-assert bats-file dnsutils \
	&& rm -rf /var/lib/apt/lists/*

RUN curl -kfsSL https://bun.com/install \
	| sed 's/curl --fail/curl --insecure --fail/' \
	| bash \
	&& cp /root/.bun/bin/bun /usr/local/bin/bun \
	&& cp /root/.bun/bin/bunx /usr/local/bin/bunx

RUN mkdir -p /ms-playwright \
	&& npm install -g @playwright/test@1.58.0 artillery \
	&& apt-get update \
	&& npx playwright install --with-deps \
	&& chown -R node:node /ms-playwright

USER node
WORKDIR /workspace
ENV PATH=/workspace/node_modules/.bin:$PATH

EXPOSE 9323
CMD ["sleep", "infinity"]
```

!!! info "bats-core"
	[Bats-core](https://bats-core.readthedocs.io/en/stable/) is a Bash-based testing framework for writing and running automated tests. It is installed in the Dockerfile, but its use is outside the scope of this section.

**devcontainer.json**

The `devcontainer.json` file connects the development container to the existing Docker Compose application. It selects the `devcontainer` service and starts the other services alongside it, installs the relevant VS Code extensions, and forwards the application ports to the host.

```json
{
  "name": "Iris Analysis DevContainer",
  "dockerComposeFile": ["../docker-compose.yml"],
  "service": "devcontainer",
  "workspaceFolder": "/workspace",
  "postCreateCommand": "npm ci",
  "runServices": [
    "backend",
    "mongodb",
    "frontend",
    "devcontainer",
    "keycloak",
    "keycloak-db",
    "influxdb",
    "grafana",
    "alloy",
    "loki"
  ],
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-azuretools.vscode-docker",
        "ms-playwright.playwright"
      ]
    }
  },
  "forwardPorts": [
    8080,
    8501,
    8081,
    8086,
    3001
  ],
  "portsAttributes": {
    "8080": {
      "label": "Backend",
      "onAutoForward": "silent"
    },
    "8501": {
      "label": "Frontend",
      "onAutoForward": "silent"
    },
    "8081": {
      "label": "Keycloak",
      "onAutoForward": "silent"
    },
    "8086": {
      "label": "InfluxDB",
      "onAutoForward": "silent"
    },
    "3001": {
      "label": "Grafana",
      "onAutoForward": "silent"
    }
  },
  "remoteUser": "node",
  "overrideCommand": false
}
```

!!! info "Bootstrapping"
    Please check the below section about bootstrapping Iris Analysis through a devcontainer.

## End-To-End Testing 

### Playwright

[Playwright](https://playwright.dev/) is an end-to-end testing framework for automating browsers and verifying web applications from a user's perspective. It supports Chromium, Firefox, and WebKit through one consistent API.

All browser-testing tools are provided inside the Dev Container: its Dockerfile installs Bun and bunx *(L34-L38)*, then Playwright, Artillery, browser binaries, and required system dependencies *(L41-L46)*. 

The project's [browser test](https://github.com/ValentinTwin1206/irislab-compose-project/blob/main/tests/e2e/app.spec.js) verifies the OIDC login flow: it opens Streamlit, follows the redirect to Keycloak, signs in, checks the account menu, and signs out again.

```javascript
import { test, expect } from '@playwright/test';

test('signs in through Keycloak', async ({ page }) => {
  const username = process.env.KEYCLOAK_TEST_USERNAME;
  const password = process.env.KEYCLOAK_TEST_PASSWORD;

  if (!username || !password) {
    throw new Error('Set KEYCLOAK_TEST_USERNAME and KEYCLOAK_TEST_PASSWORD in .env');
  }

  // Not signed in yet: no account menu.
  await page.goto('/');
  await expect(page.getByText('IrisLab Analysis Platform')).toBeVisible();
  await expect(page.getByRole('button', { name: /Account/ })).toHaveCount(0);
  await page.getByRole('button', { name: 'Continue with Keycloak' }).click();

  // Sign in on the Keycloak login page.
  await expect(page).toHaveURL(
    /keycloak\.localhost:8081\/realms\/iris-analysis\/protocol\/openid-connect\/auth/,
  );
  await page.locator('#username').fill(username);
  await page.locator('#password').fill(password);
  await page.locator('#kc-login').click();

  // Back in Streamlit: dashboard and account menu are shown.
  await expect(page.getByText('Discover the details of the iris.')).toBeVisible();
  const accountButton = page.getByRole('button', { name: /Account/ });
  await accountButton.click();
  await expect(page.getByText(username, { exact: true })).toBeVisible();

  // Sign out returns to the login screen.
  await page.getByRole('button', { name: 'Sign out', exact: true }).click();
  await expect(page.getByRole('button', { name: /Account/ })).toHaveCount(0);
});
```

The `page` fixture provides an isolated browser page. `page.goto('/')` uses the frontend base URL from the [Playwright configuration](https://github.com/ValentinTwin1206/irislab-compose-project/blob/main/playwright.config.js). Compose supplies the test credentials through environment variables; missing credentials fail the test immediately. The snippet is shortened; the full test also checks that the account menu sits inside the page header.

!!! info "Playwright"
	See the [README](https://github.com/ValentinTwin1206/irislab-compose-project/blob/main/README.md) for more details about Playwright and the project configuration.

### Artillery

[Artillery](https://www.artillery.io/) is a load-testing tool for measuring how an application behaves when it receives requests from many concurrent users. It helps identify performance bottlenecks, high error rates, and slow response times before they affect users in production.

Artillery tests are configured in YAML. The `config` section sets the target and the load phases, while `scenarios` define what each virtual user does. With the Playwright engine, a virtual user runs a real browser journey written in JavaScript:

```yaml
config:
  target: "http://backend:8080"

  # Three virtual users start within 10 seconds; each runs the journey once.
  phases:
    - name: "Concurrent users"
      duration: 10
      arrivalCount: 3

  # Number of images each virtual user uploads.
  variables:
    uploads: 20

  engines:
    playwright:
      launchOptions:
        args:
          - --disable-dev-shm-usage
          # Artillery does not load playwright.config.js, so mirror its host mapping.
          - "--host-resolver-rules=MAP localhost 172.30.0.1, MAP keycloak.localhost 172.30.0.1"
  processor: "./helpers/performance-flow.cjs"

  # Fail the run if any virtual user fails.
  plugins:
    ensure:
      conditions:
        - expression: "vusers.failed == 0"

scenarios:
  - name: "Keycloak login, image analysis, and history"
    engine: playwright
    testFunction: runAnalysisJourney
```

Three virtual users each sign in through Keycloak and upload 20 iris images, reading the analysis history after every upload. Artillery reports the duration of the login, upload, and history steps, so slow requests become visible.

!!! info "Artillery"
	For more details on running and interpreting the tests, see the [README](https://github.com/ValentinTwin1206/irislab-compose-project/blob/main/tests/README.md).

## Development Workflow

### Create the Environment

The project can be started from VS Code using the `devcontainer.json` configuration. It builds the development container and starts it together with the backend and frontend services defined in Docker Compose.

1. **Install the prerequisites.** Install Docker and the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) for VS Code. Make sure Docker is running.

2. **Open the project.** In VS Code, select **File > Open Folder** and open the project folder. The folder contains `.devcontainer/devcontainer.json` and the referenced `docker-compose.yml` file.

3. **Start the container.** Open the Command Palette with **Ctrl+Shift+P** or **Cmd+Shift+P**, then run **Dev Containers: Reopen in Container**. VS Code builds the image and starts all services listed in `runServices`. The first build may take several minutes because Playwright browsers are installed.

4. **Use the application.** Open `http://localhost:8501` for the frontend or `http://localhost:8080` for the backend. To verify the tools, open a VS Code terminal and run:

	```bash
	bunx playwright --version
	artillery --version
	```

Use **Dev Containers: Reopen Folder Locally** to leave the container. After changing the Dockerfile or `devcontainer.json`, use **Dev Containers: Rebuild Container**.


### Run tests in the Dev Container

After opening the project in the Dev Container, run these commands from the project root. All services from `runServices` should be running.

Run the browser-based tests:

```bash
bun run gui-test
```

Run the performance test:

```bash
bun run performance-test
```

Run the pAIguard moderation test, which uploads violent pictures and expects the backend to reject each with `422`:

```bash
bun run moderation-test
```

!!! info "Further reading"
	For details about the test scenarios, configuration, generated reports, and result evaluation, see the [tests README](https://github.com/ValentinTwin1206/irislab-compose-project/blob/main/tests/README.md).

