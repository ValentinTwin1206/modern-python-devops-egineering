const { createHash, randomBytes } = require("node:crypto");
const { readFileSync, readdirSync } = require("node:fs");
const path = require("node:path");

const API_URL = process.env.IRIS_API_URL || "http://backend:8080";
const KEYCLOAK_URL = process.env.IRIS_KEYCLOAK_URL || "http://keycloak.localhost:8081";
const REALM = process.env.IRIS_KEYCLOAK_REALM || "iris-analysis";
const CLIENT_ID = process.env.IRIS_PERF_CLIENT_ID || "iris-analysis-frontend";
const REDIRECT_URI = "http://localhost:8501/oauth2callback";
const UPLOAD_COUNT = Number(process.env.IRIS_PERF_UPLOADS || 50);
const SAMPLE_DIR = path.resolve(__dirname, "../../samples");

async function runAnalysisJourney(page, vuContext, events, test) {
  const username = process.env.KEYCLOAK_TEST_USERNAME;
  const password = process.env.KEYCLOAK_TEST_PASSWORD;
  const clientSecret = process.env.IRIS_PERF_CLIENT_SECRET;
  if (!username || !password || !clientSecret) {
    throw new Error("Set KEYCLOAK_TEST_USERNAME, KEYCLOAK_TEST_PASSWORD, and IRIS_PERF_CLIENT_SECRET");
  }
  if (!Number.isInteger(UPLOAD_COUNT) || UPLOAD_COUNT < 1) {
    throw new Error("IRIS_PERF_UPLOADS must be a positive integer");
  }

  // Read samples once, outside the measured upload steps.
  const samples = readdirSync(SAMPLE_DIR)
    .filter((name) => name.toLowerCase().endsWith(".png"))
    .map((name) => ({ name, buffer: readFileSync(path.join(SAMPLE_DIR, name)) }));
  if (!samples.length) throw new Error(`No PNG samples found in ${SAMPLE_DIR}`);

  // PKCE binds the authorization code to this browser-generated verifier.
  const verifier = randomBytes(32).toString("base64url");
  const challenge = createHash("sha256").update(verifier).digest("base64url");
  // Reject callbacks that do not belong to this login attempt.
  const state = randomBytes(24).toString("base64url");
  let accessToken;
  const authorizationUrl = new URL(`${KEYCLOAK_URL}/realms/${REALM}/protocol/openid-connect/auth`);
  authorizationUrl.search = new URLSearchParams({
    client_id: CLIENT_ID,
    response_type: "code",
    scope: "openid",
    redirect_uri: REDIRECT_URI,
    state,
    code_challenge: challenge,
    code_challenge_method: "S256",
  }).toString();

  let callbackUrl;
  // Install interception before navigation; capture Streamlit's redirect without running the frontend.
  const callbackCaptured = new Promise((resolve, reject) => {
    page.route(`${REDIRECT_URI}**`, async (route) => {
      callbackUrl = new URL(route.request().url());
      await route.fulfill({ status: 200, contentType: "text/html", body: "Sign-in complete" });
      resolve(callbackUrl);
    }).catch(reject);
  });

  await test.step("keycloak_login", async () => {
    await page.goto(authorizationUrl.toString());
    await page.locator("#username").fill(username);
    await page.locator("#password").fill(password);
    await page.locator("#kc-login").click();
    await callbackCaptured;
    if (callbackUrl.searchParams.get("state") !== state) {
      throw new Error("Keycloak callback state did not match");
    }
    const code = callbackUrl.searchParams.get("code");
    if (!code) throw new Error("Keycloak did not return an authorization code");

    const tokenResponse = await page.request.post(
      `${KEYCLOAK_URL}/realms/${REALM}/protocol/openid-connect/token`,
      {
        form: {
          grant_type: "authorization_code",
          client_id: CLIENT_ID,
          client_secret: clientSecret,
          code,
          redirect_uri: REDIRECT_URI,
          code_verifier: verifier,
        },
      },
    );
    if (!tokenResponse.ok()) {
      throw new Error(`Keycloak token exchange failed with HTTP ${tokenResponse.status()}`);
    }
    const tokenBody = await tokenResponse.json();
    if (!tokenBody.access_token) throw new Error("Keycloak token response has no access_token");
    accessToken = tokenBody.access_token;
  });

  const headers = { Authorization: `Bearer ${accessToken}` };
  // Keep persisted filenames identifiable and unique across test runs.
  const runId = randomBytes(8).toString("hex");
  for (let index = 0; index < UPLOAD_COUNT; index += 1) {
    // Vary the input image on every request.
    const sample = samples[Math.floor(Math.random() * samples.length)];
    const filename = `artillery-${runId}-${index}-${sample.name}`;

    await test.step("analysis_post", async () => {
      const response = await page.request.post(`${API_URL}/api/v1/analyses`, {
        headers,
        multipart: {
          image: {
            name: filename,
            mimeType: "image/png",
            buffer: sample.buffer,
          },
        },
      });
      if (response.status() !== 200) {
        throw new Error(`Analysis upload ${index + 1} failed with HTTP ${response.status()}`);
      }
      const result = await response.json();
      if (!result.eye_color || !result.closest_profile) {
        throw new Error(`Analysis upload ${index + 1} returned an incomplete result`);
      }
    });

    // Read history after every upload to exercise its growing response payload.
    await test.step("analysis_history_get", async () => {
      const response = await page.request.get(`${API_URL}/api/v1/analyses`, { headers });
      if (response.status() !== 200) {
        throw new Error(`History request ${index + 1} failed with HTTP ${response.status()}`);
      }
      const history = await response.json();
      if (!Array.isArray(history) || !history.some((item) => item.filename === filename)) {
        throw new Error(`History did not include newly uploaded image ${filename}`);
      }
    });
  }
}

module.exports = { runAnalysisJourney };
