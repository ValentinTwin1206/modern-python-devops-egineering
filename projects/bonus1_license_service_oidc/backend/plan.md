# Cloudsmith Entitlement Token Integration Plan

The license service will act as a trusted broker: Keycloak authenticates users, while the backend uses a server-side Cloudsmith technical-user API key to create repository-scoped, time-limited Entitlement Tokens. End users will not need Cloudsmith membership.

## 1. Confirm the Cloudsmith contract

Implement a cloudsmith verification. This can be done during bootstrap of the application

Implementation started: the backend now verifies the configured repository during
FastAPI startup. Verification is skipped when Cloudsmith is not configured for
local development and fails fast when configuration is incomplete or the
technical user cannot read the repository.

- Confirm the Cloudsmith owner or namespace and repository slug.
- Confirm that the technical user can create entitlements for the target repository.
- Confirm the API response shape, expiration limits, and revocation behavior.
- Decide whether the service returns an entitlement token or a package-specific download URL.
- Use Cloudsmith Entitlement Tokens rather than Cloudsmith user API keys for user-facing access.


Step 1 is DONE

## 2. Add backend Cloudsmith configuration

Add backend-only configuration for:

- `CLOUDSMITH_API_KEY`
- `CLOUDSMITH_OWNER`
- `CLOUDSMITH_REPOSITORY`
- Cloudsmith API base URL
- Maximum allowed token duration

The technical-user API key must be supplied through deployment secrets. It must never be sent to the frontend, included in the Keycloak realm export, returned in an API response, or written to logs.

Step 2 is DONE: backend configuration now reads the Cloudsmith API key,
repository settings, request timeout, and maximum token duration from
environment variables. Docker Compose injects these values into the backend
only.

## 3. Implement a Cloudsmith client

Create a dedicated Cloudsmith service module instead of placing HTTP calls directly in the FastAPI route. The service should:

1. Authenticate with the technical-user API key.
2. Call `POST /v1/entitlements/{owner}/{repo}/`.
3. Set `limit_date_range_from` and `limit_date_range_to`.
4. Add a descriptive token name and optional Keycloak subject metadata.
5. Apply package, path, download, or client restrictions when configured.
6. Use an explicit request timeout.
7. Convert Cloudsmith errors into safe application errors without exposing raw responses or credentials.

Prefer a direct HTTP API client over executing the Cloudsmith CLI from a request handler.

Step 3 is DONE: `CloudsmithClient` now centralizes authenticated repository
verification and entitlement creation, including expiration limits, optional
package/path/download/client restrictions, request timeouts, and safe errors.

## 4. Add a protected token endpoint

Reuse the create_license method in [main.py](./main.py) for issuing Cloudsmith access, for example:

The endpoint should:

- Require a valid Keycloak JWT.
- Read the stable `sub` claim from `request.state.jwt_claims`.
- Reject requests without a valid `sub`.
- Accept only token options such as duration or package selection.
- Never accept the user identity, Cloudsmith owner, or repository from the request.
- Enforce a server-side maximum duration.
- Call the Cloudsmith service.
- Return only the minimum token or download information required by the client.

The existing `POST /licenses?user=...` route should not trust a client-supplied user value. Either derive its user identity from the JWT or introduce the new endpoint first and deprecate the old contract.

Step 4 is DONE: `POST /licenses` now derives the user from a validated Keycloak
JWT and includes a Cloudsmith entitlement token and expiration in its response.
The endpoint accepts only a duration option for Cloudsmith access and enforces
the configured duration limit. There is no separate entitlement route;
Cloudsmith issuance is part of license creation.

## 5. Persist entitlement metadata

Update [database.py](./database.py) with a migration-safe table for issued entitlements. Store at least:

- Local entitlement ID
- Keycloak subject
- Display username
- Expiration timestamp
- Active or revoked state

For now, you can store the token. Later we prefer not to store plaintext entitlement tokens. If later retrieval is required, use encrypted secret storage instead of plaintext SQLite.

If entitlement records must survive container replacement, add a persistent database volume in [docker-compose.yml](../docker-compose.yml).

Step 5 persistence is DONE for the current token-backed license model: the
SQLite database is mounted at `/app/data/licenses.db` through the named
`license_service_data` volume, so records survive backend container replacement.

The table now also stores the Keycloak subject and nullable `revoked_at`
metadata. The service uses the new schema directly; the obsolete key-based
schema is no longer migrated.

## 6. Add revocation support

Add a protected revoke operation that:

1. Verifies the authenticated user's ownership using the Keycloak `sub` claim.
2. Disables or deletes the corresponding Cloudsmith entitlement.
3. Marks the local entitlement as revoked.
4. Handles Cloudsmith and local database failures safely.
5. Requires an administrator role for cross-user revocation, if that capability is needed.

Step 6 is DONE: `DELETE /licenses/{cloudsmith_token}` now revokes the
Cloudsmith entitlement and marks the local record inactive. A JWT user may
revoke only a license whose stored Keycloak `sub` matches the token subject.
An administrator may revoke any license with the configured `X-API-Key`.
Cloudsmith revocation is completed before the local record is marked revoked;
failures return safe `502` or `500` responses without exposing credentials.

## 7. Update deployment configuration

Update [docker-compose.yml](../docker-compose.yml) to inject Cloudsmith configuration into the backend only. Do not add the technical-user key to frontend environment variables or browser-visible configuration.

Update [Dockerfile](./Dockerfile) if new Python modules or runtime dependencies are added. Update `pyproject.toml` and `uv.lock` when adding an HTTP client dependency.

Step 7 is DONE: Docker Compose injects all Cloudsmith settings into the backend
only, including the technical-user API key. The frontend receives no Cloudsmith
credentials. The backend Dockerfile copies the `license_service` package and
installs the locked runtime dependencies, including `requests` and the JWT
crypto dependencies. Cloudsmith configuration is loaded and verified during
FastAPI lifespan startup rather than per request.

## 8. Update the frontend if required

If the frontend requests Cloudsmith access:

- Send the existing Keycloak bearer token.
- Send only token options.
- Do not send the Cloudsmith technical-user key.
- Do not send a client-controlled user identity.
- Avoid logging or persisting the returned entitlement token unnecessarily.

## 9. Add automated tests

Add tests for:

- Successful entitlement creation.
- Expiration duration validation and maximum limits.
- Missing, malformed, expired, or invalid JWTs.
- JWTs without a `sub` claim.
- Rejection of client-supplied identity or repository overrides.
- Cloudsmith 401, 403, 404, 429, and 5xx responses.
- Cloudsmith timeouts and malformed responses.
- Persistence after successful creation.
- Cloudsmith success followed by local database failure.
- Ownership checks and revocation.
- Confirmation that technical credentials and tokens are not logged.
- A Keycloak-authenticated user who is not a Cloudsmith member can receive a valid entitlement.

Reuse the existing JWT fixtures in [test/test_jwt_auth.py](./test/test_jwt_auth.py), temporary database pattern in [test/test_license_service.py](./test/test_license_service.py), and PyGuard isolation in [test/conftest.py](./test/conftest.py).

## 10. Verification checklist

1. Mock Cloudsmith API calls and run the backend test suite.
2. Build the backend image and verify all new modules import successfully.
3. Start Compose with a secret-injected technical-user key.
4. Confirm that only the backend receives the Cloudsmith key.
5. Authenticate with Keycloak as a user who is not a Cloudsmith member.
6. Request a token and verify its repository scope and expiration.
7. Verify that expired or revoked entitlements cannot download packages.
8. Inspect logs and API responses to confirm that Cloudsmith credentials and tokens are not exposed.

## Recommended design decisions

- Keycloak authenticates the person.
- The license service authorizes the operation.
- The Cloudsmith technical user authorizes the backend to create entitlements.
- Cloudsmith enforces repository scope and expiration.
- The entitlement belongs locally to the validated Keycloak `sub`, not to a request-supplied username.
- End users need Keycloak access but do not need Cloudsmith membership.
