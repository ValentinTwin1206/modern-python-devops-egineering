function setRolelessTestToken(requestParams, context, events, next) {
  const cachedToken = context.vars.rolelessTestToken;
  if (cachedToken) {
    requestParams.headers = { ...requestParams.headers, Authorization: `Bearer ${cachedToken}` };
    return next();
  }

  const username = process.env.KEYCLOAK_TEST_USERNAME;
  const password = process.env.KEYCLOAK_TEST_PASSWORD;
  if (!username || !password) {
    return next(new Error("Set KEYCLOAK_TEST_USERNAME and KEYCLOAK_TEST_PASSWORD in .env"));
  }

  const keycloakUrl = process.env.IRIS_KEYCLOAK_TOKEN_URL || process.env.IRIS_KEYCLOAK_URL || "http://keycloak:8080";
  const realm = process.env.IRIS_KEYCLOAK_REALM || "iris-analysis";
  const tokenUrl = `${keycloakUrl}/realms/${realm}/protocol/openid-connect/token`;
  const body = new URLSearchParams({
    grant_type: "password",
    client_id: "iris-analysis-load-test",
    username,
    password,
  });

  fetch(tokenUrl, {
    method: "POST",
    headers: { "content-type": "application/x-www-form-urlencoded" },
    body,
  })
    .then(async (response) => {
      if (!response.ok) {
        throw new Error(`Keycloak token request failed with HTTP ${response.status}`);
      }
      const tokenResponse = await response.json();
      if (!tokenResponse.access_token) {
        throw new Error("Keycloak response did not contain an access token");
      }
      context.vars.rolelessTestToken = tokenResponse.access_token;
      requestParams.headers = {
        ...requestParams.headers,
        Authorization: `Bearer ${tokenResponse.access_token}`,
      };
      next();
    })
    .catch((error) => next(error));
}

function checkPyGuard403Response(requestParams, response, context, events, next) {
  const maxAttempts = Number(process.env.PYGUARD_MAX_ATTEMPTS || 100);
  if (!Number.isInteger(maxAttempts) || maxAttempts < 1 || maxAttempts >= 120) {
    return next(new Error("PYGUARD_MAX_ATTEMPTS must be an integer from 1 to 119 for this 120-request test"));
  }

  const attempt = context.vars.authAttempt || 0;
  const expected = attempt < maxAttempts ? 403 : 429;
  context.vars.authAttempt = attempt + 1;

  if (response.statusCode !== expected) {
    return next(new Error(`Expected HTTP ${expected}, received ${response.statusCode}`));
  }
  console.log(`${requestParams.url} -> ${response.statusCode}`);
  return next();
}

module.exports = {
  setRolelessTestToken,
  checkPyGuard403Response,
};