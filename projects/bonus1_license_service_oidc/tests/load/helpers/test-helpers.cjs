function checkResponse(requestParams, response, context, ee, next) {
  context.vars.tokenCaptured = false;

  if (response.statusCode === 429) {
    console.log(
      `429 Too Many Requests - ${response.body}`
    );
  } else if (response.statusCode === 200) {
    try {
      const body = JSON.parse(response.body);

      if (typeof body.cloudsmith_token !== "string" || !body.cloudsmith_token) {
        console.error("GET /licenses returned no cloudsmith_token");
      } else {
        context.vars.cloudsmithToken = body.cloudsmith_token;
        context.vars.tokenCaptured = true;
        context.vars.licenseUser = body.user;
      }
    } catch (error) {
      console.error(`Failed to parse GET /licenses response: ${error.message}`);
    }
  } else if (response.statusCode >= 400) {
    console.log(
      `${response.statusCode} - ${response.body}`
    );
  }

  return next();
}

function checkTokenResponse(requestParams, response, context, ee, next) {
  if (response.statusCode !== 200) {
    console.error(
      `GET /licenses/{cloudsmith_token} returned ${response.statusCode} - ${response.body}`
    );
  } else {
    try {
      const body = JSON.parse(response.body);
      if (body.valid !== true) {
        console.error("GET /licenses/{cloudsmith_token} returned valid=false");
      }
    } catch (error) {
      console.error(
        `Failed to parse token validation response: ${error.message}`
      );
    }
  }

  return next();
}

module.exports = {
  checkResponse,
  checkTokenResponse,
};