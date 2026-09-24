# Frontend

This section introduces the frontend of the integrated license service. The
frontend is implemented with [Streamlit](https://streamlit.io/), a Python
framework for building small interactive web applications.

The focus of the section is deliberately limited to the frontend itself and its connection
to the backend. 

## Introduction

### Streamlit components

A Streamlit works as ordinary Python scripts. It executes the
script from top to bottom and reruns it whenever the user interacts with a
widget. Following script can be an example `app.py` with the most common building blocks:

```python
import streamlit as st

st.title("License Service")
st.write("Create and verify licenses.")

license_key = st.text_input("License key")

if st.button("Verify") and license_key:
	st.success(f"Verification requested for {license_key}")
```

!!! info
	* `st.title()` and `st.header()` provide page structure
	* `st.write()` displays text or Python values
	* `st.text_input()` collects user input
	* `st.button()` triggers an action during a script rerun
	* `st.success()`, `st.error()`, and `st.code()` act as result helpers and provide visual feedback.

### Run a Streamlit application

Start the application from the directory containing `app.py`:

```shell
uv run streamlit run app.py
```

By default, Streamlit listens on port `8501`. To make the application
reachable from a container or another machine, bind it to all interfaces:

```shell
uv run streamlit run app.py \
	--server.address=0.0.0.0 \
	--server.port=8501
```

The application is then available at `http://localhost:8501`.

## Applied project

The applied frontend contains the Streamlit interface, the small HTTP client used by that interface, and the Dockerfile
used to package both files.

The project metadata includes `streamlit` and `requests`.

### app.py

`app.py` defines the Streamlit user interface and provides buttons for creating and checking licenses.

The application imports the API functions and handles the license-creation
request as follows:

```python
from api import check_license, create_license

if not st.user.is_logged_in:
	if st.button("Log in with Keycloak"):
		st.login("keycloak")
	st.stop()

user_name = st.user.get("preferred_username", st.user.name)
access_token = st.user.tokens["access"]

if st.button("License erzeugen"):
	result = create_license(user_name, access_token)
	st.code(result["license_key"])
```

### api.py

`api.py` keeps HTTP communication out of the interface by reading the
backend URL and temporary API key from environment variables and exposing
small functions for creating and checking licenses.

```python
def create_license(user: str, access_token: str) -> dict:
	response = requests.post(
		f"{BACKEND_URL}/licenses",
		params={"user": user},
		headers={
			"Authorization": f"Bearer {access_token}",
			"X-API-Key": ADMIN_API_KEY,
		},
		timeout=10,
	)
	response.raise_for_status()
	return response.json()
```

### Dockerfile

The `Dockerfile` builds a small Python 3.12 image, installs the project with
`uv`, copies `app.py` and `api.py`, exposes port `8501`, and starts Streamlit
on all network interfaces.

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY pyproject.toml .

RUN uv sync --no-dev

COPY app.py api.py ./

EXPOSE 8501

CMD ["uv", "run", "streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
```

The image installs only runtime dependencies, copies the two application
modules, documents port `8501`, and starts Streamlit on all network
interfaces. Build it from the frontend directory:

```shell
docker build -t license-service-frontend .
```

## Bootstrap the license-service

Before using Docker Compose, both services can be started with independent
`docker run` commands. Create a shared Docker network first so the frontend
can reach the backend by its container name:

```shell
docker network create license-service-network
```

Build the backend image from the project root and provide the local PyGuard
project as the additional build context expected by the backend Dockerfile.
Then start it on the shared network:

```shell
docker build \
	--build-context pyguard=../proj1_pyguard \
	-t license-service-backend \
	./backend

docker run --rm \
	--name license-service-backend \
	--network license-service-network \
	-p 8080:8080 \
	-e ADMIN_API_KEY=dev-secret \
	license-service-backend
```

Start the frontend as a second container. Inside the Docker network, the
backend is addressed by its container name, not by `localhost`:

```shell
docker run --rm \
	--name license-service-frontend \
	--network license-service-network \
	-p 8501:8501 \
	-e BACKEND_URL=http://license-service-backend:8080 \
	-e ADMIN_API_KEY=dev-secret \
	license-service-frontend
```

The frontend is available at `http://localhost:8501`, and its requests are
forwarded to the backend through the shared Docker network. These commands
demonstrate the individual containers and their network dependency. The next
section replaces this manual setup with Docker Compose orchestration.