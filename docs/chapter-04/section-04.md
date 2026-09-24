# Python Dev Containers

This section builds on the previous [section](./section-03.md) by adding a Dev Container as another project component. Dev Containers were first introduced in [Chapter 01, Section 04](../../chapter-01/section-04.md) as a way to provide a reproducible development environment. Here, the container includes the heavier configuration and tooling needed to test the complete application stack in a more realistic, end-to-end environment. Although Playwright and Artillery are used in the project, the focus is not to introduce these tools in detail; it is to explain the infrastructure and setup required to integrate them into the complete development and testing workflow.

## Introduction

### Playwright

[Playwright](https://playwright.dev/) is an end-to-end testing framework for automating browsers and verifying web applications from a user's perspective. It supports Chromium, Firefox, and WebKit through one consistent API.

Playwright tests usually create a browser context, open a page, perform user actions, and assert the expected result. A simple test can verify that the application displays the expected heading after navigation:

```javascript
import { test, expect } from "@playwright/test";

test("the home page displays its heading", async ({ page }) => {
	await page.goto("http://localhost:8501");
	await expect(page.locator("h1")).toContainText("License Service");
});
```

The `page` fixture provides an isolated browser page for the test. `page.goto()` opens the application, while the assertion confirms that the rendered UI behaves as expected.

### Artillery

[Artillery](https://www.artillery.io/) is a load-testing tool for measuring how an application behaves when it receives requests from many concurrent users. It helps identify performance bottlenecks, high error rates, and slow response times before they affect users in production.

An Artillery test is usually described in a YAML file. The `config` section defines the target and load phases, while `scenarios` describe the requests performed by each virtual user. A simple test can send repeated `GET` requests to the license service:

```yaml
config:
	target: "http://localhost:8080"
	phases:
		- duration: 10
			arrivalRate: 1

scenarios:
	- flow:
		- get:
			url: "/"
```

This test starts one virtual user per second for ten seconds. Each virtual user requests the service's root endpoint, allowing Artillery to record response times, throughput, and errors.

## Applied Project

### Dockerfile

The Dev Container image is based on Microsoft's JavaScript and Node.js development image. It installs the command-line tools required by the project, including Bats, Bun, Playwright, and Artillery, and stores Playwright's browser binaries in a shared directory. The final sanity checks confirm that the tools are available before the container is used.

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
	&& apt-get install -y \
		bats \
		bats-support \
		bats-assert \
		bats-file \
		dnsutils \
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

RUN bats --version \
	&& bun --version \
	&& bunx playwright --version \
	&& artillery --version

EXPOSE 9323
CMD ["sleep", "infinity"]
```

### devcontainer.json

The `devcontainer.json` file connects the development container to the existing Docker Compose application. It selects the `devcontainer` service, starts the backend and frontend alongside it, installs the relevant VS Code extensions, and forwards the application ports to the host.

```json
{
	"name": "License Service DevContainer",
	"dockerComposeFile": ["../docker-compose.yml"],
	"service": "devcontainer",
	"workspaceFolder": "/workspace",
	"runServices": [
		"backend",
		"frontend",
		"devcontainer"
	],
	"customizations": {
		"vscode": {
			"extensions": [
				"ms-azuretools.vscode-docker",
				"ms-playwright.playwright"
			]
		}
	},
	"forwardPorts": [8080, 8501],
	"portsAttributes": {
		"8080": {
			"label": "Backend",
			"onAutoForward": "silent"
		},
		"8501": {
			"label": "Frontend",
			"onAutoForward": "silent"
		}
	},
	"remoteUser": "node",
	"overrideCommand": false
}
```

### spike.yml

## Bootstrap the License Service

The project can be started from VS Code using the `devcontainer.json` configuration. It builds the development container and starts it together with the backend and frontend services defined in Docker Compose.

1. **Install the prerequisites.** Install Docker and the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) for VS Code. Make sure Docker is running.

2. **Open the project.** In VS Code, select **File > Open Folder** and open:

	```text
	projects/proj11_license_service_devcontainer
	```

	The folder contains `.devcontainer/devcontainer.json` and the referenced `docker-compose.yml` file.

3. **Start the container.** Open the Command Palette with **Ctrl+Shift+P** or **Cmd+Shift+P**, then run **Dev Containers: Reopen in Container**. VS Code builds the image and starts the `backend`, `frontend`, and `devcontainer` services. The first build may take several minutes because Playwright browsers are installed.

4. **Use the application.** Open `http://localhost:8501` for the frontend or `http://localhost:8080` for the backend. To verify the tools, open a VS Code terminal and run:

	```bash
	bunx playwright --version
	artillery --version
	```

Use **Dev Containers: Reopen Folder Locally** to leave the container. After changing the Dockerfile or `devcontainer.json`, use **Dev Containers: Rebuild Container**.
