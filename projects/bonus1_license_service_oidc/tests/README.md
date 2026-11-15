# End-to-End Testing Scenarios

This directory contains browser-based end-to-end tests and Artillery tests for IrisLab. Run the tests from the project root inside the Dev Container, where the API and Keycloak are available on the Compose network.

## Structure

The following overview shows the folder and file structure of the test scenarios.

```text
project root/
├── package.json                Defines the test commands
└── tests/
    ├── e2e/
    │   └── app.spec.js         Playwright UI test: sign in through Keycloak
    └── load/
        ├── helpers/
        │   ├── performance-flow.cjs Browser-authenticated API performance journey
        │   └── test-helpers.cjs PyGuard token setup and response checks
        ├── performance.yml     Authenticated analysis and history workload
        └── spike.yml           API PyGuard brute-force scenario
```

The root `package.json` is the entry point for running tests: 

```json
"scripts": {
    "gui-test": "bunx playwright test",
    "spike-test": "artillery run tests/load/spike.yml",
    "performance-test": "artillery run tests/load/performance.yml"
}
```

`bun run gui-test` runs the Playwright tests, `bun run spike-test` runs the PyGuard scenario, and `bun run performance-test` runs the authenticated API performance scenario.

## Playwright

Run the test with:

```bash
bun run gui-test
```

The `gui-test` script in [package.json](../package.json) starts Playwright, which loads [playwright.config.js](../playwright.config.js) and runs [app.spec.js](e2e/app.spec.js). The test uses Chromium to verify the Streamlit–Keycloak login flow against the running Compose services and generates a test report.

```mermaid
flowchart TD
    Package["package.json: gui-test"] -->|starts| Runner["Playwright test runner"]
    Config["playwright.config.js"] -->|configures Chromium, URLs and reports| Runner
    Spec["tests/e2e/app.spec.js"] -->|defines login actions and assertions| Runner
    Compose["docker-compose.yml"] -->|provides services and gateway environment| Runner
    Runner -->|drives Chromium| Login["Streamlit → Keycloak → Streamlit callback"]
    Runner -->|writes| Report["HTML report and failure artifacts"]
```

**Configuration**

The [Playwright configuration](../playwright.config.js) sets Chromium as the browser target and uses `FRONTEND_URL` as its base URL.

The login flow of the example project uses two hostnames defined by the project:

1. `localhost:8501`: the default frontend URL in the [Playwright configuration](../playwright.config.js). The [secrets.toml](../frontend/.streamlit/secrets.toml) set `redirect_uri` to `http://localhost:8501/oauth2callback`, which the [Keycloak client configuration](../keycloak/realm-export.json) allows as a callback.
2. `keycloak.localhost:8081`: the public Keycloak address set by `KEYCLOAK_HOSTNAME` in the [environment configuration](../.env) and passed to Keycloak as `KC_HOSTNAME` by [Compose](../docker-compose.yml). Streamlit's `server_metadata_url` uses this address to discover the login endpoints.

The [Compose stack](../docker-compose.yml) runs Chromium in the Dev Container, separate from Streamlit and Keycloak. Chromium normally resolves both hostnames to loopback—the Dev Container itself, where neither service runs. Compose therefore sets `PLAYWRIGHT_HOST_GATEWAY=172.30.0.1`. The `browserArgs` resolver rules map both names to this network gateway to reach the host-published ports, preserving the configured URLs throughout login and callback.

These rules affect only Chromium. Compose's `extra_hosts` entries separately resolve `keycloak.localhost` for container-side clients such as Streamlit. For host-run tests, leave `PLAYWRIGHT_HOST_GATEWAY` unset. If the Compose subnet changes, update the gateway value and matching `extra_hosts` addresses together.

The configured reporters print a test list and generate an HTML report at `/tmp/playwright-artifacts/report`. Screenshots, videos, and traces are retained for failed tests in `/tmp/playwright-artifacts/results`.

**Test Case**

The GUI test verifies the login flow:

1. [Read credentials](e2e/app.spec.js#L4-L9) from `KEYCLOAK_TEST_USERNAME` and `KEYCLOAK_TEST_PASSWORD`; fail if either is missing *(L4-L9)*.
2. [Open Streamlit](e2e/app.spec.js#L11-L15), check the logged-out UI, and click **Log in with Keycloak** *(L11-L15)*.
3. [Verify the Keycloak redirect and sign in](e2e/app.spec.js#L17-L22) with the supplied credentials *(L17-L22)*.
4. [Check the authenticated UI](e2e/app.spec.js#L24-L26): the username, **Get license** button, and **License Key** field must be visible *(L24-L26)*.

The test checks login and UI visibility; it does not create or validate a license. Use the development realm account (`example-user` / `example-password`) or set the credential variables to another test user. Recreate the Dev Container after Compose changes so its host mapping is applied. Set `FRONTEND_URL` to override the target URL, `HEADED=true` to run a visible browser, or `TEST_ROOT_DIR` to choose another test directory.

A passing run means these browser actions and assertions succeeded; failures are reported in the terminal.

View the report from the Dev Container with:

```bash
bunx playwright show-report /tmp/playwright-artifacts/report
```

## Artillery

### Authenticated API performance test

Run the separate one-virtual-user Artillery + Playwright scenario from the Dev Container:

```bash
bun run performance-test
```

**Test flow**

1. **Start one virtual user:** `bun run performance-test` invokes the script in [package.json](../package.json#L9). Artillery loads [performance.yml](load/performance.yml#L1-L14), which targets the API and schedules one virtual user; its Playwright scenario calls `runAnalysisJourney`.
2. **Sign in and obtain a token:** Compose supplies the Keycloak test username and password, plus the performance client settings ([docker-compose.yml](../docker-compose.yml#L37-L42)). The helper checks these values and creates a PKCE verifier, challenge, and state ([performance-flow.cjs](load/helpers/performance-flow.cjs#L14-L43)). It signs in through the browser, validates the callback state, then exchanges the authorization code for an access token ([performance-flow.cjs](load/helpers/performance-flow.cjs#L46-L83)). Set `IRIS_PERF_CLIENT_SECRET` to the confidential frontend client's secret; the helper fails if it is missing. `IRIS_PERF_CLIENT_ID` defaults to `iris-analysis-frontend` and `IRIS_PERF_UPLOADS` defaults to 50; the API and Keycloak base URLs can be overridden with `IRIS_API_URL` and `IRIS_KEYCLOAK_URL` ([performance-flow.cjs](load/helpers/performance-flow.cjs#L5-L11)).
3. **Upload sample images:** The helper loads PNGs from `tests/samples/`, then randomly selects one for each iteration ([performance-flow.cjs](load/helpers/performance-flow.cjs#L24-L27), [performance-flow.cjs](load/helpers/performance-flow.cjs#L88-L89)). Each image is sent with the bearer token to `POST /api/v1/analyses`; the response must contain the expected analysis fields ([performance-flow.cjs](load/helpers/performance-flow.cjs#L92-L109)). The API endpoint is defined in [analysis.py](../../proj3_irislab_api/src/irislab_api/api/routes/analysis.py#L30-L32).
4. **Read history after every upload:** After each POST, the test calls `GET /api/v1/analyses` and fails unless that upload's filename is present ([performance-flow.cjs](load/helpers/performance-flow.cjs#L112-L120)). The corresponding API route is in [analysis.py](../../proj3_irislab_api/src/irislab_api/api/routes/analysis.py#L19-L27).
5. **Compare step timings:** Artillery records the `keycloak_login`, `analysis_post`, and `analysis_history_get` steps separately ([performance-flow.cjs](load/helpers/performance-flow.cjs#L53-L53), [performance-flow.cjs](load/helpers/performance-flow.cjs#L92-L92), [performance-flow.cjs](load/helpers/performance-flow.cjs#L112-L112)).
6. **Account for retained data:** The API persists each successful image in GridFS and its analysis document in MongoDB ([analysis.py](../../proj3_irislab_api/src/irislab_api/services/analysis.py#L112-L139)). History reads the stored images and embeds them as Base64 ([analysis.py](../../proj3_irislab_api/src/irislab_api/services/analysis.py#L175-L205), [analysis.py](../../proj3_irislab_api/src/irislab_api/schemas/analysis.py#L33-L39)). Records intentionally accumulate, so later history responses grow and can take longer; clear test data manually when a clean baseline is needed. This scenario is separate from the PyGuard brute-force test below.

### PyGuard brute-force test

The example project provides one Artillery testcase `spike-test` under `tests/load/spike.yml`. The `package.json` already defines the entrypoint. Run the test with:

```bash
bun run spike-test
```

**Test Case**

The load test targets the Iris API's protected `GET /api/v1/analyses` endpoint:

1. **Prepare authentication:** Set `OIDC_REQUIRED_ROLE` to a role the test token
    does not have, and set `IRIS_FORBIDDEN_TEST_TOKEN` to a valid Keycloak access
    token with a `sub` claim but without that role. Compose passes the role to
    the backend ([docker-compose.yml](../docker-compose.yml#L51-L56)) and the
    token to the Dev Container ([docker-compose.yml](../docker-compose.yml#L34-L41)).
    Keep the token local. Restart both containers after changing these values.
2. **Configure the load:** The scenario targets `http://backend:8080` and uses
    one virtual user to send 120 sequential requests from the same source IP;
    the phase schedules that user during a 60-second arrival window
    ([spike.yml](load/spike.yml#L1-L10)).
3. **Send failed-auth requests:** The loop calls `GET /api/v1/analyses` first
    without a token (401), then with the roleless token (403), and repeats the
    pair 60 times ([spike.yml](load/spike.yml#L13-L25)). The
    `setForbiddenTestToken` helper adds the bearer header
    ([test-helpers.cjs](load/helpers/test-helpers.cjs#L1-L9)).
4. **Verify rate limiting:** Compose passes the configured attempt limit and
    time window to the API and test runner ([docker-compose.yml](../docker-compose.yml#L40-L41),
    [docker-compose.yml](../docker-compose.yml#L55-L59)). With the current limit
    of 100, the first 100 responses should alternate between 401 and 403; later
    requests should return 429. `checkPyGuardResponse` checks responses against
    the configured limit ([test-helpers.cjs](load/helpers/test-helpers.cjs#L11-L25)).
    This fixed scenario supports limits from 1 through 119; adjust the loop and
    helper validation if you change the attempt limit beyond that range.
5. **Reset before rerunning:** PyGuard keeps block state in memory. Restart the
    backend or wait for the block duration to expire before rerunning from the
    same source IP.

```mermaid
flowchart TD
    Package["package.json: spike-test"] -->|starts| Runner["Artillery"]
    Config["tests/load/spike.yml"] -->|defines target, load and requests| Runner
    Helpers["helpers/test-helpers.cjs"] -->|sets test token and logs statuses| Runner
    Compose["docker-compose.yml"] -->|provides backend and network| Runner
    Runner -->|sends HTTP requests| API["Backend API with PyGuard"]
    Runner -->|writes| Results["Terminal metrics and optional JSON / Cloud results"]
```

To save the detailed results locally and record the run in Artillery Cloud, provide an Artillery Cloud API key:

```bash
artillery run --output spike-report.json tests/load/spike.yml --record --key "$ARTILLERY_CLOUD_KEY"
```

Set `ARTILLERY_CLOUD_KEY` to your Artillery Cloud API key before running the command. Open [app.artillery.io](https://app.artillery.io/) to view and analyze the recorded test run, then share the run or create a report from the dashboard. To save a PDF copy, use the browser's **Print** option and choose **Save as PDF**. The JSON results are also saved locally as `spike-report.json`.

