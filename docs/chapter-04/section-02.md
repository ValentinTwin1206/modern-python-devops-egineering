# Python Service Orchestration

In the previous [section](./section-01.mds), we introduced the frontend and started the frontend
and backend separately with two `docker run` commands. 

In this section, we replace that manual setup with [Docker Compose](https://docs.docker.com/compose/). Compose starts the components together and configures the shared network they use to communicate. This provides a simple way to showcase multi-component application startup, networking, and service discovery in one repeatable configuration.

## Introduction

Docker Compose is a tool for defining and running applications made up of multiple containers. A Compose file describes each service, its image or build configuration, ports, environment variables, dependencies, and networks. The [docker-compose.yaml](#applied-project) used in this section serves as the basis for the following explanations, which refer to its core components: 

  * services
  * networking
  * service discovery

### Services

Each entry under `services` describes one container role. Compose also gives each service a network identity that other services can use.

In the Compose file, the `depends_on` setting in the `frontend` service expresses startup order, but it does not prove that the `backend` dependency is ready to accept requests. Applications that need readiness guarantees should use health checks, retries, or an explicit readiness check.

The `backend` service exposes port `8080`, and the `frontend` service exposes port `8501`. The frontend declares a dependency on the backend so Compose starts the backend first.

### Networking

In the Compose file, both services join the `license_service_network` network. The network uses the `172.20.0.0/24` subnet and assigns predictable addresses through the `BACKEND_IP` and `FRONTEND_IP` environment variables.

The Compose file configures services to communicate by service name rather than by `localhost`. Therefore, the frontend uses `http://backend:8080` as its backend URL.

The published ports are different from the internal service address: port `8501` makes the frontend available to the host, while port `8080` makes the backend available to the host. Container-to-container traffic uses the internal Compose network.

### Service Discovery

The Compose configuration provides internal DNS-based service discovery. A container can resolve another service using the service name from the Compose file, for example:

`http://backend:8080`

The name is resolved to the backend container's current private IP address. This is more stable than hard-coding an IP address because containers may be recreated and receive different addresses.

## Applied Project

**docker-compose.yaml**

The `docker-compose.yml` file describes the complete application as a group of services. Docker Compose reads this file and uses it to create the containers, network, port mappings, and environment configuration.

```yaml
services:
  
  backend:
    container_name: backend
    image: license-service-backend:latest
    ports:
      - "8080:8080"
    networks:
      license_service_network:
        ipv4_address: ${BACKEND_IP:-172.20.0.2}

  frontend:
    build: .
    container_name: frontend
    depends_on:
      - backend
    ports:
      - "8501:8501"
    networks:
      license_service_network:
        ipv4_address: ${FRONTEND_IP:-172.20.0.3}
    environment:
      BACKEND_URL: http://backend:8080


networks:
  license_service_network:
    ipam:
      config:
        - subnet: 172.20.0.0/24

```

The most important configuration keys are:

- `services` — Defines the containers that make up the application.
- `image` — Selects an existing container image for a service.
- `build` — Builds a service image from a local Dockerfile.
- `container_name` — Assigns a readable name to the container.
- `depends_on` — Defines service startup order.
- `ports` — Maps host ports to container ports.
- `networks` — Connects services to a shared Docker network.
- `ipv4_address` — Assigns a fixed address within a configured network.
- `environment` — Passes configuration values into the container.
- `ipam` and `subnet` — Configure the address range of a Docker network.

## Bootstrap the license-service

The complete application can be started from the `projects/proj10_license_service_frontend` directory. The Compose file expects the backend image to be available locally, so build that image first from the backend project. The additional PyGuard build context is required by the backend Dockerfile:

```shell
cd projects/proj10_license_service_frontend

docker build \
  --build-context pyguard=../proj1_pyguard \
  -t license-service-backend:latest \
  ../proj3_license_service
```

Then start the frontend and backend together with Docker Compose. The `--build` option builds the frontend image from its Dockerfile before starting both services:

```shell
docker compose up --build
```

After the containers have started, open the frontend at `http://localhost:8501`. The frontend reaches the backend through the Compose network at `http://backend:8080`, while the backend is also available from the host at `http://localhost:8080`.

Stop and remove the containers and network with:

```shell
docker compose down
```
