# License Service Dev Container

This project provides a **Dev Container** for developing and testing the License Service. The container includes the tools required for end-to-end UI and load testing, such as **Playwright** and **Artillery**.

The Dev Container is designed to work together with the existing **Docker Compose** setup of the License Service.

## Prerequisites

The development environment should be run from **WSL (Windows Subsystem for Linux)**.

Install the following tools:

* **WSL 2** – Linux environment for Windows
* **Docker Desktop** – provides the Docker Engine and Docker Compose
* **Visual Studio Code**
* **Dev Containers extension for VS Code** – `ms-vscode-remote.remote-containers`

Make sure Docker Desktop is running before starting the Dev Container.

Docker Desktop should also have **WSL 2 integration** enabled for the WSL distribution you are using.

## Start the Dev Container

Open the project in your **WSL terminal**:

```bash
cd /path/to/license-service
code .
```

VS Code should open the project using the WSL environment.

Then:

1. Open the Command Palette with `Ctrl+Shift+P`.
2. Select **Dev Containers: Reopen in Container**.
3. VS Code reads the `devcontainer.json` configuration and starts the `devcontainer` service.
4. The required Docker Compose services (`backend`, `frontend`, and `devcontainer`) are started together.

After the container has started, VS Code is connected directly to the development container.

## Testing

The Dev Container provides the required Node/Bun tooling and Playwright dependencies.

The available npm scripts are:

### Run Playwright UI tests

```bash
bun run test:gui
```

### Run the Artillery load test

```bash
bun run test:load:spike:gui
```

The frontend and backend are available through the ports configured in `devcontainer.json`:

* **8080** – Backend
* **8501** – Frontend
