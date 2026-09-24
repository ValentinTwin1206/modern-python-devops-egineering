# Adding OIDC Login to a Streamlit and FastAPI License Service

A small license service is an excellent place to learn OpenID Connect (OIDC).
The application already has three useful building blocks:

- a Streamlit frontend,
- a FastAPI backend,
- a Keycloak container with an imported realm.

What it does not have yet is a complete trust chain between those components.
The frontend can eventually authenticate a person with Keycloak, but the backend
currently knows nothing about OIDC tokens. This guide explains how to extend the
existing project step by step.

The goal is not just to add a login button. The goal is to establish this flow:

```text
Browser
  │
  │ 1. Login with OIDC
  ▼
Streamlit ───────────────► Keycloak
  │                         │
  │ 2. Access token         │ 3. ID/access tokens
  │
  │ 4. Authorization: Bearer <access-token>
  ▼
FastAPI API ──────────────► Keycloak JWKS endpoint
             5. Validate signature, issuer, audience and claims
```

Once the flow is complete, Keycloak authenticates the user, Streamlit keeps the
login session, and FastAPI independently verifies the access token before
creating a license.

## Start with the Existing Application

The project is located in:

```text
projects/bonus1_license_service_oidc/
├── backend/
│   ├── main.py
│   ├── helpers.py
│   └── ...
├── frontend/
│   ├── app.py
│   ├── api.py
│   └── ...
├── keycloak/
│   └── realm-export.json
└── docker-compose.yml
```

The current frontend calls the backend through [frontend/api.py](frontend/api.py).
Creating a license sends an `X-API-Key` header:

```python
headers={"X-API-Key": ADMIN_API_KEY}
```

The backend applies the matching dependency in [backend/main.py](backend/main.py):

```python
@app.post(
    "/licenses",
    response_model=LicenseResponse,
    dependencies=[Depends(require_admin)],
)
def create_license(user: str):
    ...
```

The `require_admin` function in [backend/helpers.py](backend/helpers.py) compares
the request header with `ADMIN_API_KEY`. This is API-key authentication, not JWT
or OIDC authentication.

That distinction matters: adding a Keycloak login to Streamlit alone does not
secure the API. The backend must validate the token itself because request
headers can be forged by any client that can reach the API.

## Step 1: Understand the OIDC Vocabulary

OIDC builds on OAuth 2.0. The most important terms for this project are:

- **Realm**: the Keycloak security boundary. This project uses the
  `license-service` realm.
- **Client**: the application registered in Keycloak. The Streamlit frontend
  will be an OIDC client.
- **Client ID**: the public identifier of that client.
- **Client secret**: a credential used by a confidential client. It must not be
  committed to source control.
- **Redirect URI**: the URL Keycloak uses to return the browser after login.
- **Access token**: the token sent to the FastAPI API.
- **ID token**: identity information intended for the client application.
- **Issuer**: the realm URL that issued the token.
- **JWKS**: Keycloak's public signing keys. The API uses them to verify JWT
  signatures without receiving a private key.

For local development, the browser reaches Keycloak at:

```text
http://localhost:8081
```

Containers reach the same service at:

```text
http://keycloak:8080
```

These addresses are not interchangeable in every part of the configuration.
The redirect URI is used by the browser and therefore normally uses
`localhost`. Backend discovery and JWKS requests happen from inside the backend
container and normally use the Docker service name.

## Step 2: Register a Streamlit Client in Keycloak

The existing [keycloak/realm-export.json](keycloak/realm-export.json) defines the
realm and an example user, but it does not yet define an OIDC client for
Streamlit.

Add a client to the realm export, or create one through the Keycloak admin UI.
For a local Docker Compose setup, use values equivalent to these:

| Setting | Development value |
| --- | --- |
| Realm | `license-service` |
| Client ID | `streamlit-frontend` |
| Client type | OpenID Connect |
| Client authentication | On, for a confidential client |
| Valid redirect URI | `http://localhost:8501/oauth2callback` |
| Web origin | `http://localhost:8501` |
| Standard flow | Enabled |
| Direct access grants | Not required for browser login |

Add the following lines to the `realm-export.json`

```json
 "clients": [
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
  ],
```

The client secret generated by Keycloak belongs in a local secret file or an
external secret manager. Do not put it directly in the realm export if that
file is committed to Git.

After changing the realm export, recreate the Keycloak container when necessary.
Keycloak imports a realm during startup, and an already-created realm may not be
overwritten automatically on every restart.

## Step 3: Configure Streamlit Secrets

Streamlit reads authentication settings from `.streamlit/secrets.toml`. Create
this file beneath the frontend directory:

```toml
[auth]
redirect_uri = "http://localhost:8501/oauth2callback"
cookie_secret = "replace-with-a-long-random-development-secret"

[auth.keycloak]
client_id = "streamlit-frontend"
client_secret = "replace-with-the-keycloak-client-secret"
server_metadata_url = "http://localhost:8081/realms/license-service/.well-known/openid-configuration"
```

Use a strong random value for `cookie_secret`. It signs Streamlit's local login
cookie; it is not the Keycloak client secret.

Keep the file out of version control. A good teaching project should include a
safe template such as `.streamlit/secrets.toml.example`, while the real
`.streamlit/secrets.toml` remains local.

The metadata URL must be reachable by the component that performs discovery.
For Streamlit's browser-oriented login flow, `localhost:8081` is generally the
right local development value. If a deployment uses a reverse proxy or a public
hostname, use that public issuer consistently instead.

## Step 4: Mount the Configuration with Docker Compose

The frontend image currently copies `app.py`, `api.py`, and the startup script,
but it does not bake Streamlit secrets into the image. Extend the `frontend`
service in
[docker-compose.yml](docker-compose.yml) with a read-only bind mount:

```yaml
  frontend:
    build: ./frontend
    depends_on:
      - backend
    ports:
      - "8501:8501"
    volumes:
      - ./frontend/.streamlit/secrets.toml:/run/secrets/streamlit-secrets.toml:ro
    networks:
      license_service_network:
        ipv4_address: ${FRONTEND_IP:-172.30.0.3}
    environment:
      BACKEND_URL: http://backend:8080
```

Create the local secrets file from the example before starting Compose:

```text
projects/bonus1_license_service_oidc/frontend/.streamlit/secrets.toml
```

Do not bake this file into the image with a Dockerfile `COPY` instruction. A
Docker image can be inspected later, so baking credentials into it makes secret
rotation and safe sharing difficult.

The frontend startup script copies this template into Streamlit's configuration
directory and generates a new `cookie_secret` on every container start. This
invalidates the browser's previous Streamlit login cookie, so restarting the
Compose stack starts in the logged-out state.

For a team or CI environment, replace the bind mount with a deployment secret or
another secret-injection mechanism. The exact mechanism is platform-specific;
the security rule is the same: credentials should be supplied at runtime.

## Step 5: Add Login and Logout to Streamlit

The current [frontend/app.py](frontend/app.py) displays license forms
immediately. Wrap those forms in an authentication check.

The development guide uses Streamlit's authentication APIs in this shape:

```python

# ...

if not st.experimental_user.is_logged_in:
    st.write("You are not logged in.")

    if st.button("Log in with Keycloak"):
        st.login("keycloak")

    st.stop()

authenticated_user = st.experimental_user
user_name = authenticated_user.get("preferred_username", authenticated_user.name)

  st.write(f"Signed in as: {user_name}")
  st.write(f"Email: {authenticated_user.get('email', 'N/A')}")

if st.button("Log out"):
    st.logout()

  st.header("Create license")

user = st.text_input("Benutzer", value=user_name, disabled=True)

# ...
```

Use the API variant supported by the Streamlit version pinned in
[frontend/pyproject.toml](frontend/pyproject.toml). Newer Streamlit releases may
expose `st.user` instead of the experimental user API. Do not mix API examples
from different Streamlit versions without checking the installed version.

A practical implementation should also decide which claim becomes the license
owner. Common choices are:

- `preferred_username` for a human-readable login name,
- `email` when email is verified and unique,
- `sub` when a stable provider-specific identifier is required.

Do not trust a username typed into a public form when the authenticated identity
is already available in the token. Use the authenticated identity as the default
owner, or restrict the user field to an explicit administrator feature.

## Step 6: Forward the Access Token to FastAPI

Streamlit only exposes tokens when you opt in. Add this to the `[auth]` section
of `.streamlit/secrets.toml`:

```toml
expose_tokens = ["id", "access"]
```

In [frontend/app.py](frontend/app.py), read the access token after login and
pass it to the API wrapper:

```python
access_token = st.user.tokens["access"]
...
result = create_license(user, access_token)
```

In [frontend/api.py](frontend/api.py), attach it to the protected request:

```python
def create_license(user: str, access_token: str) -> dict:
    response = requests.post(
        f"{BACKEND_URL}/licenses",
        params={"user": user},
        headers={
            "Authorization": f"Bearer {access_token}",
            # Temporary: remove once the backend validates JWTs (Step 7).
            "X-API-Key": ADMIN_API_KEY,
        },
        timeout=10,
    )
    response.raise_for_status()
    return response.json()
```

> Note: the pinned Streamlit 1.63 exposes `st.user`, not `st.experimental_user`.
> Use the API that matches the version in
> [frontend/pyproject.toml](frontend/pyproject.toml).

The `GET /licenses/{license_key}` route is currently public, while
`POST /licenses` requires authentication. Preserve that distinction unless the
exercise intentionally changes the API policy.

The `X-API-Key` header is kept only as a temporary migration path so the app
keeps working until the backend validates JWTs. Remove it once Step 7 is
verified; do not rely on a hard-coded admin key in production.


## Step 7: Teach FastAPI to Validate JWTs

The backend currently accepts only `X-API-Key`; it does not accept incoming JWT
bearer tokens. Add PyJWT to [backend/pyproject.toml](backend/pyproject.toml):

```toml
"pyjwt[crypto]>=2.9.0",
```

Add a validator in [backend/helpers.py](backend/helpers.py) that verifies the
signature against Keycloak's JWKS, the issuer, and the expiry. `PyJWKClient`
fetches and caches the signing keys:

```python
_jwks_client = PyJWKClient(OIDC_JWKS_URL)


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

Wire it as middleware in [backend/main.py](backend/main.py), reusing the
existing `PROTECTED_PATHS` set:

```python
@app.middleware("http")
async def jwt_auth_middleware(request: FastAPIRequest, call_next):
    if (request.method, request.url.path) in PROTECTED_PATHS:
        authorization = request.headers.get("Authorization")
        # Migration: validate the JWT only when present; X-API-Key still
        # enforces access until Step 8 makes the token mandatory.
        if authorization:
            try:
                validate_bearer_token(authorization)
            except TokenError as exc:
                return responses.JSONResponse(
                    status_code=exc.status_code,
                    content={"detail": exc.detail},
                )
    return await call_next(request)
```

Pass the OIDC settings through [docker-compose.yml](docker-compose.yml):

```yaml
  backend:
    environment:
      OIDC_ISSUER_URL: http://localhost:8081/realms/license-service
      OIDC_JWKS_URL: http://keycloak:8080/realms/license-service/protocol/openid-connect/certs
```

There is an important networking detail here. A token's `iss` claim must match
the issuer expected by the validator. Keycloak issues browser-facing tokens with
`iss` set to `localhost:8081`, but the backend must fetch the JWKS from inside
the Docker network at `keycloak:8080`. That is why the issuer and JWKS URLs are
configured **independently** above: the signing keys are identical regardless of
hostname, so JWKS from `keycloak:8080` validates a token whose `iss` is
`localhost:8081`.

> Audience and role are enforced only when `OIDC_AUDIENCE` / `OIDC_REQUIRED_ROLE`
> are set. Step 8 turns them into mandatory authorization checks. During this
> migration the JWT is validated when present while `X-API-Key` remains the
> enforced credential, so existing API-key tests keep passing. Never log the
> complete token.

## Step 8: Decide How Authorization Works

Authentication answers “Who is this?” Authorization answers “May this user
create a license?”

For this exercise we widen the policy: `POST /licenses` may be called by an
**admin** (valid `X-API-Key`) **or** by **any authenticated user** (valid JWT).
The middleware from Step 7 authenticates the token; a small dependency then
authorizes either credential. Replace the old key-only `require_admin` with:

```python
def require_admin_or_user(
    request: Request,
    x_api_key: str | None = Header(default=None),
):
    if is_admin(x_api_key):
        return
    if getattr(request.state, "jwt_claims", None) is not None:
        return
    raise HTTPException(status_code=401, detail="Authentication required")
```

Have the middleware publish the validated claims so the dependency can see them:

```python
request.state.jwt_claims = claims
```

and point the endpoint at the new dependency:

```python
@app.post("/licenses", response_model=LicenseResponse,
          dependencies=[Depends(require_admin_or_user)])
```

Now a request is authorized when it carries a valid admin key **or** a valid
token; a request with neither is rejected with `401`. An invalid or expired
token is still rejected by the middleware before it reaches this check.

> Test isolation note: PyGuard's brute-force rule keeps per-source state in a
> module-level singleton. In tests, reset it between cases (an autouse
> `conftest.py` fixture that replaces `main.guard`) so the shared `testclient`
> source does not accumulate attempts and trip the limiter.

### Tightening later: require a role or scope

If you later need admin-only or scoped access, keep the same structure and add a
check on the token claims:

- **A Keycloak realm or client role** — create a role such as `license-admin`,
  assign it to the user, and set `OIDC_REQUIRED_ROLE` so the validator enforces
  it (returns `403` when missing).
- **A dedicated API audience and scope** — register the API as a resource and
  require a scope such as `licenses:create`. This is more precise when several
  clients or APIs share the realm.

Do not rely on a frontend button being hidden. Authorization belongs in the
backend dependency because clients can call FastAPI directly.

## Step 9: Update Docker Compose Environment Variables

Pass the non-secret OIDC settings to the backend through Compose. The issuer and
JWKS URLs are configured independently (see Step 7), and the admin key is shared
with the frontend so the `X-API-Key` path keeps working:

```yaml
  backend:
    environment:
      ADMIN_API_KEY: ${ADMIN_API_KEY:-dev-secret}
      OIDC_ISSUER_URL: http://localhost:8081/realms/license-service
      OIDC_JWKS_URL: http://keycloak:8080/realms/license-service/protocol/openid-connect/certs

  frontend:
    environment:
      BACKEND_URL: http://backend:8080
      ADMIN_API_KEY: ${ADMIN_API_KEY:-dev-secret}
```

For the Step 8 policy (admin **or** any authenticated user), leave
`OIDC_AUDIENCE` and `OIDC_REQUIRED_ROLE` unset: Keycloak's default access token
carries `aud: account`, so enforcing an audience would reject it unless you add
an audience mapper, and no role is required. Set them only when you tighten the
policy to a specific audience or role.

`ADMIN_API_KEY` is retained as a separate admin authentication mechanism. Keep
the two services in sync and use a strong value outside local development.

It is also useful to add service health checks and startup ordering once the
basic flow works. `depends_on` starts containers in order, but it does not
necessarily mean that Keycloak is ready to answer discovery requests.

## Step 10: Test the Flow in Small Increments

Test each boundary independently instead of debugging the whole stack at once.

### Keycloak

1. Open `http://localhost:8081`.
2. Confirm that the `license-service` realm exists.
3. Confirm that the Streamlit client exists.
4. Confirm that the example user can log in.
5. Confirm that the redirect URI exactly matches the Streamlit callback.

### Streamlit

1. Start the services with Docker Compose.
2. Open `http://localhost:8501`.
3. Confirm that unauthenticated users see only the login action.
4. Complete login in Keycloak.
5. Confirm that the authenticated username and email are displayed.
6. Confirm that logout returns the user to the login state.

### FastAPI

1. Call the public health endpoint.
2. Call `POST /licenses` without credentials and expect `401`.
3. Call it with an invalid bearer token and expect `401`.
4. Call it with a valid token lacking the required role and expect `403`.
5. Call it with a valid authorized token and expect license creation.
6. Confirm that an expired token is rejected.

### Regression tests

Run the existing backend tests after changing the dependency:

```bash
cd projects/bonus1_license_service_oidc/backend
uv run pytest
```

If the old tests still use `X-API-Key`, either update them to create representative
JWT claims or deliberately retain and test the compatibility path. Tests should
reflect the security policy that the application is supposed to enforce, not just
make the old implementation pass.

## Common Problems

### Redirect URI mismatch

Keycloak compares redirect URIs strictly. A difference in scheme, port, path, or
trailing slash can cause login to fail. Use exactly:

```text
http://localhost:8501/oauth2callback
```

for this local setup.

### Keycloak works in the browser but not in the backend

`localhost` inside the backend container means the backend container itself, not
the host and not the Keycloak container. Use `keycloak:8080` for container-to-
container traffic.

### Discovery succeeds but JWKS fails

Inspect the URLs returned by the discovery document. Keycloak may advertise a
hostname that is not resolvable from the backend container. The issuer, discovery
URL, and JWKS URL must be reachable from where they are used.

### The token is valid but the audience check fails

The `aud` claim may not contain the Streamlit client ID. Configure the Keycloak
client and token mappers deliberately, then validate the audience expected by the
API. Do not disable audience validation just to make the first request work.

### The login works but license creation returns 401

Inspect the request headers at the frontend boundary without logging the token
value. Verify that `Authorization: Bearer ...` is present and that the token has
not expired before the request reaches FastAPI.

### A valid user receives 403

The token is probably authenticated but lacks the role or scope required by the
API. Check whether the role is in `realm_access.roles`, `resource_access`, or a
custom claim, and make the backend authorization rule match the Keycloak client
configuration.

## A Secure Completion Checklist

The exercise is complete when all of the following are true:

- [ ] The Streamlit client exists in the `license-service` realm.
- [ ] The redirect URI is configured exactly.
- [ ] Streamlit secrets are mounted at runtime and excluded from Git.
- [ ] Unauthenticated users cannot use protected frontend actions.
- [ ] The frontend sends an access token, not an ID token, to FastAPI.
- [ ] FastAPI validates the JWT signature using Keycloak's JWKS.
- [ ] FastAPI validates issuer, audience, and expiration.
- [ ] The backend enforces a role or scope for license creation.
- [ ] Tokens and client secrets are never written to logs.
- [ ] Invalid, expired, and unauthorized tokens have automated tests.
- [ ] The old API-key path is either removed or clearly documented as temporary.

OIDC is finished when the backend can independently answer two questions: “Was
this token issued by the expected identity provider?” and “Does this identity
have permission to perform this operation?” The Streamlit login is only the first
half of that responsibility.
