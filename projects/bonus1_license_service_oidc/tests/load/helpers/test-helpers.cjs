function checkResponse(requestParams, response, context, ee, next) {
  if (response.statusCode === 429) {
    console.log(
      `429 Too Many Requests - ${response.body}`
    );
  } else if (response.statusCode >= 400) {
    console.log(
      `${response.statusCode} - ${response.body}`
    );
  }

  return next();
}

module.exports = {
  checkResponse,
};