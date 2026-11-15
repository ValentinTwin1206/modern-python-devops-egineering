function setForbiddenTestToken(requestParams, context, events, next) {
  const token = process.env.IRIS_FORBIDDEN_TEST_TOKEN;
  if (!token) {
    return next(new Error("Set IRIS_FORBIDDEN_TEST_TOKEN to a valid token without the required role"));
  }

  requestParams.headers = { ...requestParams.headers, Authorization: `Bearer ${token}` };
  return next();
}

function checkPyGuardResponse(requestParams, response, context, events, next) {
  const maxAttempts = Number(process.env.PYGUARD_MAX_ATTEMPTS || 100);
  if (!Number.isInteger(maxAttempts) || maxAttempts < 1 || maxAttempts >= 120) {
    return next(new Error("PYGUARD_MAX_ATTEMPTS must be an integer from 1 to 119 for this 120-request test"));
  }

  const attempt = context.vars.authAttempt || 0;
  const expected = attempt < maxAttempts
    ? (attempt % 2 === 0 ? 401 : 403)
    : 429;
  context.vars.authAttempt = attempt + 1;

  if (response.statusCode !== expected) {
    return next(new Error(`Expected HTTP ${expected}, received ${response.statusCode}`));
  }
  console.log(`${requestParams.url} -> ${response.statusCode}`);
  return next();
}

module.exports = {
  setForbiddenTestToken,
  checkPyGuardResponse,
};