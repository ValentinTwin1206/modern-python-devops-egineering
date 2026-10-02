# Keycloak OIDC Provider

Keycloak is the OpenID Connect (OIDC) identity provider for the License Service. It authenticates users for the Streamlit frontend and issues the ID and access tokens that the backend validates before allowing protected license operations.

This directory contains the realm definition imported by the Keycloak container. Keycloak itself is provided as a Docker image; there is no separate application source code to install in this directory.

## Basic Components

The Keycloak configuration for this project is defined in `realm-export.json`. This realm export describes the identity-provider components required by the application: the `license-service` realm, the `streamlit-frontend` OIDC client, and a development user. When the Keycloak container starts with `--import-realm`, it uses this file to create the realm configuration.

The following sections explain each component and its role in the authentication flow.

### Realm

A Keycloak realm is an isolated security domain containing users, clients, roles, and authentication settings. This project imports the `license-service` realm so the license application has its own identity configuration.

```json
{
  "realm": "license-service",
  "enabled": true,
  "displayName": "License Service"
}
```

### Client

The `streamlit-frontend` client represents the Streamlit application. It is a confidential OIDC client using the standard authorization-code flow.

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

The client secret is used by the frontend when exchanging the authorization result for tokens. It is a development value in the checked-in realm export and must be replaced or managed through a secret-management system in a production deployment.

### User

The realm export contains an `example-user` for local development. Production users should be created through Keycloak administration or an approved provisioning workflow, and passwords must not be committed to source control.

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

## Token Validation

The backend is responsible for deciding whether the token is valid. For protected license operations, it performs these checks:

1. Confirms that the `Authorization` header uses the `Bearer <token>` format.
2. Reads the token header and obtains the matching public signing key from
  Keycloak's JWKS endpoint.
3. Verifies the token signature using the `RS256` algorithm.
4. Verifies the issuer (`iss`) and expiration (`exp`) claims.
5. Verifies the audience (`aud`) claim when `OIDC_AUDIENCE` is configured.
6. Verifies a required realm role when `OIDC_REQUIRED_ROLE` is configured.

```python
def validate_bearer_token(authorization: str) -> dict:
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise TokenError(401, "Invalid authorization header")
    try:
        signing_key = _jwks_client.get_signing_key_from_jwt(token)
        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            issuer=OIDC_ISSUER_URL,
            audience=OIDC_AUDIENCE,
            options={"verify_aud": OIDC_AUDIENCE is not None},
        )
    except jwt.PyJWTError as exc:
        raise TokenError(401, f"Invalid token: {exc}") from exc
    if OIDC_REQUIRED_ROLE:
        roles = claims.get("realm_access", {}).get("roles", [])
        if OIDC_REQUIRED_ROLE not in roles:
            raise TokenError(403, "Insufficient role")
    return claims

```

The issuer, JWKS endpoint, audience, and required role are configured through the backend environment variables. The audience and required-role checks are optional because their checks are enabled only when the corresponding environment variable is non-empty.

In the Docker Compose configuration, Keycloak issues tokens with this host-facing issuer URL in the `iss` claim:

```text
http://keycloak.localhost:8081/realms/license-service
```

The backend runs inside the Compose network and therefore fetches the public signing keys through Keycloak's internal service address:

```text
http://keycloak:8080/realms/license-service/protocol/openid-connect/certs
```

## Frontend Configuration

The frontend configuation can be seen in the [README.md](./../frontend/README.md) file of the frontend.

The `client_id` must match the Keycloak client. The redirect URI must be registered in Keycloak, and `expose_tokens` makes the access token available to the frontend so it can call the protected backend API.

## Container Build

Build the keycloak image from the `bonus1_license_service_oidc` project root with `docker compose`:

```bash
docker compose up
```
