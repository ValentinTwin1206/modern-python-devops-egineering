# Python Service Orchestration

## Applied Project

The applied project is an integrated iris lab analyzation for analyzing incoming pictures of the iris. It consists of four main application components:

* A [Streamlit](https://streamlit.io/) frontend provides the browser-based user interface. Users sign in through the frontend and upload images for iris analysation. 
* A [Keycloak](https://www.keycloak.org/) provides the OpenID Connect (OIDC) identity service. It authenticates users, manages the configured realm and client, and issues tokens for authenticated requests.
* A [FastAPI](https://fastapi.tiangolo.com/) backend analyzes incoming pictures of the iris, authorizes protected operations, stores the data in MongoDB, and returns the response.
* The [PyGuard](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/proj1_pyguard/README.md) library provides brute-force protection middleware for the backend. It tracks requests to protected endpoints and can temporarily block suspicious clients that exceed the configured attempt threshold.

```mermaid
flowchart LR
    B["Browser"] --> F["Streamlit frontend"]
    F --> K["Keycloak OIDC"]
    K -->|access token| F
    F -->|Bearer token| A["FastAPI backend"]
    A --> D["MongoDB/GridFS"]
```

!!! info "For more information"
    The individual components are documented in their own README files:

    * [Frontend README](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/bonus1_license_service_oidc/frontend/README.md)
    * [Backend README](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/bonus1_license_service_oidc/backend/README.md)
    * [Keycloak README](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/bonus1_license_service_oidc/keycloak/README.md)

### Project Setup

Docker Compose starts the frontend, backend, MongoDB, and Keycloak services on a shared network. 

The Compose configuration is stored in `projects/bonus1_license_service_oidc/docker-compose.yml`. 

```yaml
services:
  backend:
    image: irislab-api:0.0.1
    depends_on:
      mongodb:
        condition: service_healthy
    ports:
      - "8080:8080"
    environment:
      MONGODB_URI: mongodb://${MONGODB_ROOT_USERNAME}:${MONGODB_ROOT_PASSWORD}@mongodb:27017/?authSource=admin
      MONGODB_DATABASE: ${MONGODB_DATABASE}
      OIDC_ISSUER_URL: ${OIDC_ISSUER_URL}
      OIDC_JWKS_URL: ${OIDC_JWKS_URL}
    networks:
      irislab_network:
        ipv4_address: ${IRIS_API_IP}

  mongodb:
    image: mongo:8.0
    environment:
      MONGO_INITDB_ROOT_USERNAME: ${MONGODB_ROOT_USERNAME}
      MONGO_INITDB_ROOT_PASSWORD: ${MONGODB_ROOT_PASSWORD}
    ports:
      - "127.0.0.1:${MONGODB_HOST_PORT}:27017"
    volumes:
      - mongodb_data:/data/db
    healthcheck:
      test:
        - CMD-SHELL
        - mongosh --quiet --eval 'db.adminCommand("ping").ok' --username "$$MONGO_INITDB_ROOT_USERNAME" --password "$$MONGO_INITDB_ROOT_PASSWORD" --authenticationDatabase admin
      interval: 5s
      timeout: 5s
      retries: 20
    networks:
      irislab_network:
        ipv4_address: ${MONGODB_IP}

  frontend:
    build: ./frontend
    depends_on:
      backend:
        condition: service_started
      keycloak:
        condition: service_healthy
    ports:
      - "8501:8501"
    extra_hosts:
      - "keycloak.localhost:172.30.0.1"
    volumes:
      - ./frontend/.streamlit/secrets.toml:/run/secrets/streamlit-secrets.toml:ro
    networks:
      irislab_network:
        ipv4_address: ${FRONTEND_IP}
    environment:
      IRIS_API_URL: http://backend:8080

  keycloak:
    image: quay.io/keycloak/keycloak:26.3
    command: start-dev --import-realm
    healthcheck:
      test: ["CMD", "bash", "-c", ":</dev/tcp/127.0.0.1/8080"]
      interval: 5s
      timeout: 3s
      retries: 20
      start_period: 15s
    environment:
      KC_BOOTSTRAP_ADMIN_USERNAME: ${KEYCLOAK_ADMIN}
      KC_BOOTSTRAP_ADMIN_PASSWORD: ${KEYCLOAK_ADMIN_PASSWORD}
      KC_HOSTNAME: ${KEYCLOAK_HOSTNAME}
    ports:
      - "8081:8080"
    volumes:
      - ./keycloak/realm-export.json:/opt/keycloak/data/import/realm-export.json:ro
    networks:
      irislab_network:
        ipv4_address: ${KEYCLOAK_IP}

networks:
  irislab_network:
    ipam:
      config:
        - subnet: 172.30.0.0/24

volumes:
  mongodb_data:
```

The most important Compose configuration keys are:

| Key | Purpose |
| --- | --- |
| `services` | Defines the containers that make up the application. |
| `image` and `build` | Use a prebuilt image or build a service image from a local Dockerfile. |
| `depends_on` | Defines service startup order. |
| `ports` | Maps host ports to container ports. |
| `environment` | Passes configuration values into a container. |
| `volumes` | Mounts the Keycloak realm and Streamlit secrets. |
| `networks` | Connects services to a shared Docker network. |
| `ipam` and `subnet` | Configure the address range of that network. |

The project-level `.env` file supplies values for Compose variable substitution.
Only variables listed under a service's `environment` section are passed into
that container.



## Orchestration with Compose

### Services

Each entry under `services` describes one container role. Compose also gives each service a network identity that other services can use.

The `backend` service exposes port `8080`, the `frontend` service exposes port `8501`, and Keycloak exposes port `8081` to the host. The frontend declares a dependency on the backend so Compose starts the backend first. The Keycloak service imports the realm definition from `keycloak/realm-export.json`.

`depends_on` expresses startup order, but it does not prove that a dependency is ready to accept requests. Applications that need readiness guarantees should use health checks, retries, or an explicit readiness check.

### Networking

The frontend, backend, MongoDB, and Keycloak services join the
`irislab_network` network. The network uses the `172.30.0.0/24` subnet, with
configurable addresses for the services.

Published ports are different from internal service addresses. Port `8501`
makes the frontend available to the host, while port `8080` makes the backend
available to the host. Container-to-container traffic uses service names on
the internal Compose network.

### Discovery

Compose provides internal DNS-based service discovery. A container can resolve
another service using the service name from the Compose file:

```text
http://backend:8080
http://keycloak:8080
```

This is more stable than hard-coding an IP address because containers may be
recreated and receive different private addresses.

## Development Workflow
### Create the Environment

Start the complete application from the project directory:

```shell
cd projects/bonus1_license_service_oidc
docker compose up --build
```

The `--build` option builds the frontend image before starting the stack. The
backend uses the prebuilt `irislab-api:0.0.1` image. Keycloak imports the realm
export during startup, and the frontend uses the mounted Streamlit OIDC
configuration.

Run the services in the background with `-d`:

```shell
docker compose up --build -d
docker compose ps
```

Stop and remove the containers and network with:

```shell
docker compose down
```

The application is then available at `http://localhost:8501`. Keycloak is
available at `http://localhost:8081`, and the backend API is available at
`http://localhost:8080`.

### Inspect the Environment

Inspect service output with:

```shell
docker compose logs -f frontend
docker compose logs -f backend
docker compose logs -f keycloak
```
