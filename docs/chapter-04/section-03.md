# OIDC

This section extends the Compose orchestration from the previous section with an OpenID Connect (OIDC) authentication mechanism. It adds Keycloak as the identity provider and uses Streamlit's built-in OIDC support to authenticate users before they access the frontend application.

## Introduction

### OIDC

OpenID Connect (OIDC) is a standard for authenticating users on top of the OAuth 2.0 authorization framework. OAuth 2.0 allows an application to obtain permission to access protected resources, while OIDC adds information about the user's identity. After successful authentication, the OIDC provider returns an ID token containing claims such as the user's subject identifier, name, or email address.

The user starts at the client application, which redirects them to the OIDC provider. The provider authenticates the user and returns an authorization result to the client. The client then exchanges that result for tokens, validates the ID token, and creates an authenticated session for the user.


```text
  User                 OIDC client application        OIDC provider
   |                           |                           |
   |-- open application ------>|                           |
   |                           |-- redirect to login ----->|
   |<------------- login page / authenticate --------------|
   |-- credentials --------------------------------------->|
   |                           |                           |
   |                           |<------- exchange  ------->|
   |                           |                           |
   |<------ authenticated application ---------------------|
```

OIDC allows applications to delegate authentication to a trusted, centralized identity provider instead of managing passwords and login sessions themselves. This enables single sign-on and gives different applications a consistent way to identify users.

### OIDC Provider

Keycloak is the identity provider used by this application. A Keycloak **realm** is an isolated security domain that contains its users, roles, clients, and authentication settings. The application uses a dedicated realm for the license service so its identity configuration remains separate from other applications.

```json
{
  "realm": "license-service",
  "enabled": true,
  "displayName": "License Service"
}
```

### OIDC Client

An OIDC **client** represents an application that relies on Keycloak for authentication. It has a client ID and defines settings such as allowed redirect URIs, which tell Keycloak where to return the user after login. In this example, the Streamlit frontend is the OIDC client: it redirects users to Keycloak, receives the authentication result, and uses the returned identity information to establish the signed-in user session.

### OIDC Token

After the frontend authenticates the user, it sends the access token to the backend which must not trust the claims supplied by the frontend without verifying the token. In general, JWT verification performs the following checks:

1. It confirms that the header uses the `Bearer` scheme and contains a token.
2. It uses Keycloak's JSON Web Key Set (JWKS) endpoint to obtain the public key that matches the token's key ID (`kid`).
3. It verifies the token's RS256 signature, which proves that the token was issued by the holder of Keycloak's private signing key and has not been modified.
4. It verifies the `iss` claim against `OIDC_ISSUER_URL` and checks the token's expiry time.
5. If `OIDC_AUDIENCE` is configured, it also verifies the `aud` claim. If `OIDC_REQUIRED_ROLE` is configured, the required role must be present in the token's `realm_access.roles` claim.

`OIDC_ISSUER_URL` identifies the expected token issuer, while `OIDC_JWKS_URL` provides the backend with Keycloak's public signing keys. The backend validates tokens in middleware before using their claims. Invalid tokens return `401`; valid tokens without the required role return `403`. Decoding alone is not verification—the signature and claims must be checked before granting access.

## Applied Project

### docker-compose.yaml

The Compose configuration adds Keycloak as the OIDC provider alongside the existing backend and frontend services. It also supplies the services with the environment variables and mounted configuration files required for authentication and communication; the individual settings are explained below.

The backend receives `OIDC_ISSUER_URL` and `OIDC_JWKS_URL`, which identify the issuer and the public signing keys it uses to validate access tokens. 

The frontend receives `BACKEND_URL` so it can call the backend, while the Keycloak container receives bootstrap administrator credentials and its public hostname. The `ADMIN_API_KEY` is passed to the backend and frontend for their existing API authorization. 

Compose mounts the realm export into Keycloak as a read-only import file and mounts the frontend's `.streamlit/secrets.toml` file as read-only configuration.


```yaml
services:
  backend:
    build:
      context: ./backend
      additional_contexts:
        pyguard: ../proj1_pyguard
    ports:
      - "8080:8080"
    environment:
      ADMIN_API_KEY: ${ADMIN_API_KEY:-dev-secret}
      OIDC_ISSUER_URL: http://keycloak.localhost:8081/realms/license-service
      OIDC_JWKS_URL: http://keycloak:8080/realms/license-service/protocol/openid-connect/certs
    networks:
      license_service_network:
        ipv4_address: ${BACKEND_IP:-172.30.0.2}

  frontend:
    build: ./frontend
    depends_on:
      - backend
    ports:
      - "8501:8501"
    extra_hosts:
      - "keycloak.localhost:172.30.0.1"
    volumes:
      - ./frontend/.streamlit/secrets.toml:/app/.streamlit/secrets.toml:ro
    networks:
      license_service_network:
        ipv4_address: ${FRONTEND_IP:-172.30.0.3}
    environment:
      BACKEND_URL: http://backend:8080
      ADMIN_API_KEY: ${ADMIN_API_KEY:-dev-secret}

  keycloak:
    image: quay.io/keycloak/keycloak:26.3
    command: start-dev --import-realm
    environment:
      KC_BOOTSTRAP_ADMIN_USERNAME: ${KEYCLOAK_ADMIN:-admin}
      KC_BOOTSTRAP_ADMIN_PASSWORD: ${KEYCLOAK_ADMIN_PASSWORD:-admin}
      KC_HOSTNAME: http://keycloak.localhost:8081
    ports:
      - "8081:8080"
    volumes:
      - ./keycloak/realm-export.json:/opt/keycloak/data/import/realm-export.json:ro
    networks:
      license_service_network:
        ipv4_address: ${KEYCLOAK_IP:-172.30.0.4}


networks:
  license_service_network:
    ipam:
      config:
        - subnet: 172.30.0.0/24

```

### realm-export.json

The realm export combines the realm metadata, OIDC client configuration, and user definitions. The client entry below registers the Streamlit frontend as a confidential OIDC client. Its redirect URI is the endpoint to which Keycloak sends the browser after login. The client secret shown here is intended only for local development and should be replaced or managed securely in a production deployment.

```json
{
  "clientId": "streamlit-frontend",
  "name": "Streamlit Frontend",
  "description": "OIDC client for the license-service Streamlit application",
  "enabled": true,
  "protocol": "openid-connect",
  "publicClient": false,
  "clientAuthenticatorType": "client-secret",
  "secret": "streamlit-dev-secret",
  "standardFlowEnabled": true,
  "implicitFlowEnabled": false,
  "directAccessGrantsEnabled": false,
  "serviceAccountsEnabled": false,
  "redirectUris": [
    "http://localhost:8501/oauth2callback"
  ],
  "webOrigins": [
    "http://localhost:8501"
  ]
}
```

Users are also defined in the realm export. The following development user can sign in through Keycloak. In a real deployment, do not commit passwords to the realm export; use a secret-management solution or create users through an administrative workflow instead.

```json
{
  "username": "example-user",
  "enabled": true,
  "email": "example-user@example.com",
  "emailVerified": true,
  "firstName": "Example",
  "lastName": "User",
  "credentials": [
    {
      "type": "password",
      "value": "example-password",
      "temporary": false
    }
  ]
}
```

### secrets.toml

Streamlit provides built-in support for OIDC login and redirects the user to the configured OIDC provider, processes the callback, and exposes the authenticated user's claims through `st.user`.

A minimal Streamlit application can protect its content as follows:

```python
import streamlit as st

st.title("OIDC example")

if not st.user.is_logged_in:
  st.write("You are not logged in.")
  if st.button("Log in"):
    st.login("keycloak")
  st.stop()

st.write(f"Signed in as {st.user.get('preferred_username', st.user.name)}")

if st.button("Log out"):
  st.logout()
```

The provider-specific settings are configured separately in `.streamlit/secrets.toml`. This file contains the redirect URI, the client credentials, and the provider's discovery document URL. The discovery document allows Streamlit to learn the provider's authorization, token, and user-information endpoints.

```toml
# Copy this file to secrets.toml for local development.
# Never commit secrets.toml or real credentials to source control.

[auth]
redirect_uri = "http://localhost:8501/oauth2callback"
cookie_secret = "replace-with-a-random-secret"
expose_tokens = ["id", "access"]

[auth.keycloak]
client_id = "streamlit-frontend"
client_secret = "streamlit-dev-secret"
server_metadata_url = "http://keycloak.localhost:8081/realms/license-service/.well-known/openid-configuration"
```

The `client_id` must match the client configured in the realm export. The `client_secret` authenticates the confidential client and must be kept private. The `redirect_uri` must also be registered for that client; otherwise, the provider rejects the callback. The `expose_tokens` setting makes the ID and access tokens available through `st.user.tokens`, which the frontend uses when calling the protected backend API.


!!! info
    The backend must validate the ID token before trusting the user's identity or granting access to protected API endpoints.

## Bootstrap the license-service

The complete stack can be started with Docker Compose from the project directory:

```bash
cd projects/bonus1_license_service_oidc
docker compose up --build -d
```

The `--build` option rebuilds the backend and frontend images, while `-d` starts the services in the background. During startup, Compose creates the shared network and starts the backend, frontend, and Keycloak containers. Keycloak imports `keycloak/realm-export.json`, and the frontend reads its OIDC settings from the mounted `.streamlit/secrets.toml` file.

Use the following command to verify that the containers are running:

```bash
docker compose ps
```

The application is then available at `http://localhost:8501`. Select **Log in** to begin the OIDC flow. Keycloak can be accessed at `http://localhost:8081`, and the backend API is exposed at `http://localhost:8080`. If a service does not start correctly, inspect its output with:

```bash
docker compose logs -f frontend
docker compose logs -f keycloak
```

To stop the stack without removing its images, run:

```bash
docker compose down
```
