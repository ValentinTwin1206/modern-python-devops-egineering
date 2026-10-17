# Grafana

Grafana is used to visualize the collected API metrics of the used Influx Database. The examples below use the `api_metrics` bucket and the `api_requests` measurement. 

## Table of contents
- [Configure Grafana](#configure-grafana)
  - [Dashboards](#dashboards)
  - [Alerts](#alerts)
- [Reuse Grafana configurations](#reuse-grafana-configurations)
  - [Export Configurations](#export-configurations)
  - [Import Configurations](#import-configurations)
    - [Import via the Grafana UI](#import-via-the-grafana-ui)
    - [Import via Docker Compose](#import-via-docker-compose)
- [Docker Desktop MCP Gateway](#docker-desktop-mcp-gateway)
  - [Service Account](#service-account)
  - [Grafana Server](#grafana-server)

## Configure Grafana

### Connect InfluxDB

At first, define and connect the InfluxDB datasource for Grafana

* Open **Connections > Add new data source**
* Select **InfluxDB** and set **Flux** as the query language
* Use the following settings and confirm the with clicking on **Save & test**:
  * URL: `http://influxdb:8086`
  * Organization: `oidc_license_service`
  * Bucket: `api_metrics`
  * Token: `INFLUXDB_TOKEN` from `.env`


### Dashboards

A Grafana dashboard is a collection of panels that displays data from connected
data sources in one place, making it easier to monitor and explore metrics.

#### Re-create the API dashboard

Follow these steps to recreate the **OIDC License Service** dashboard in the
**General** folder:

1. In Grafana, open **Dashboards > New > New dashboard**.
2. Add a visualization, select the **influxdb** data source, and choose **Flux**
   as the query language.
3. Configure the first panel:
   - Set the title to **Request Latency by Endpoint and Method**.
   - Use a **Time series** visualization and this query to chart mean latency
     for each endpoint and HTTP method:

     ```flux
     from(bucket: "api_metrics")
       |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
       |> filter(fn: (r) =>
         r._measurement == "api_requests" and
         r._field == "duration_ms"
       )
       |> group(columns: ["endpoint", "method"])
       |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
       |> yield(name: "mean_latency_ms")
     ```

   - Under **Standard options**, set the unit to **milliseconds (ms)**. In
     **Axis**, set the label to **Latency (ms)**, then apply/save the panel.
4. Add a second visualization using the same **influxdb** data source and
   configure it as follows:
   - Set the title to **Request Counts by HTTP Status** and use **Time series**.
   - Paste this query to count requests per status code in one-minute windows:

     ```flux
     from(bucket: "api_metrics")
       |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
       |> filter(fn: (r) =>
         r._measurement == "api_requests" and
         r._field == "status_code"
       )
       |> map(fn: (r) => ({
         r with
         _field: "HTTP " + string(v: r._value)
       }))
       |> group(columns: ["_field"])
       |> aggregateWindow(every: 1m, fn: count, createEmpty: true)
       |> yield(name: "api_calls")
     ```

   - Under **Standard options**, use the **short** unit for count values. In
     **Axis**, set the label to **Requests (count)**, then apply/save the panel.

5. Optionally add a total request-volume panel instead of, or in addition to,
   the status-code breakdown. Use a **Time series** visualization and this query:

   ```flux
   from(bucket: "api_metrics")
     |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
     |> filter(fn: (r) => r._measurement == "api_requests")
     |> filter(fn: (r) => r._field == "status_code")
     |> aggregateWindow(every: 1m, fn: count, createEmpty: true)
     |> yield(name: "api_calls")
   ```

6. Save the dashboard as **OIDC License Service** in the **General** folder.
   Choose the dashboard time range you want to inspect; the panel queries use
   that range. Older records may not appear in the latency panel because they
   predate the `duration_ms` field.

Grafana supplies `v.timeRangeStart`, `v.timeRangeStop`, and `v.windowPeriod`
when it runs these queries in a dashboard. For Time series panels, Grafana
uses timestamps on the x-axis and formats them automatically for the selected
dashboard time range and timezone; there is no separate time unit to set.

### Alerts

An alert in Grafana monitors data for a defined condition, such as a metric
exceeding a threshold. When the condition is met, Grafana can notify configured
recipients so they can investigate.

#### PyGuard HTTP 429 alert

The `PyGuard HTTP 429 Alert` rule detects rate-limit blocks on PyGuard's
protected license endpoints. PyGuard protects `GET /licenses` and
`POST /licenses`; the backend records each response's status code, endpoint,
and method in the `api_requests` measurement.

The alert query counts matching 429 responses over the last five minutes:

```flux
from(bucket: "api_metrics")
  |> range(start: -5m)
  |> filter(fn: (r) =>
    r._measurement == "api_requests" and
    r._field == "status_code" and
    r._value == 429 and
    r.endpoint == "/licenses" and
    (r.method == "GET" or r.method == "POST")
  )
  |> group()
  |> aggregateWindow(every: 1m, fn: count, createEmpty: false)
  |> yield(name: "pyguard_429_blocks")
```

The rule reduces query `A` using **Max** and fires when the result is above
`0`. It evaluates every `1m` with a `0s` pending period, so a recorded PyGuard
429 is eligible to alert at the next evaluation. **No data** is treated as
**Normal**, as expected when no rate-limit blocks occurred during the query
window.

To deliver notifications, configure a working contact point and a notification
policy that routes this alert to it. The default email contact point requires
SMTP configuration before it can send messages.

#### Find the alert in Grafana

1. Open **Alerting > Alert rules** in the Grafana navigation.
2. Find the **PyGuard** folder and open **PyGuard HTTP 429 Alert**.
3. Check the rule state and its evaluation details. An active rate-limit event
  puts the rule into **Firing**; the alert details show its query/evaluation
  history and labels.
4. To see active alert instances across rules, open **Alerting > Alert groups**
  (called **Alert instances** in some Grafana versions) and locate
  **PyGuard HTTP 429 Alert**.

The rule is evaluated every minute over a rolling five-minute query window, so
allow up to one evaluation interval for a spike to appear. If the rule fires
but no notification arrives, check the notification policy and contact point;
the default email contact point needs SMTP configuration.

## Reuse Grafana configurations

### Export Configurations

Export dashboards and alert rules to reuse them in another Grafana instance or keep their configuration in version control. These exports contain configuration, not the metrics stored in InfluxDB.

- **Dashboard:** Open **OIDC License Service**, choose **Share > Export**, and download the JSON file. Save it as [oidc-license-service.dashboard.json](oidc-license-service.dashboard.json) in this directory. For Docker provisioning, export the regular dashboard JSON rather than the **Export for sharing externally** variant.
- **Alert rule:** In **Alerting > Alert rules**, find **PyGuard HTTP 429 Alert** and use its **Export** action. Select **YAML for file provisioning** and save it as [pyguard-http-429.alerting.yaml](pyguard-http-429.alerting.yaml) in this directory. The export includes the rule and its evaluation group.

### Import Configurations

Before importing, configure an InfluxDB data source connected to `api_metrics`. The supplied exports reference datasource UID `bg0kwzzxbw4xsc` and organization ID `1`. When using a different instance, update these references to match the target configuration; datasource names alone do not resolve UID references.

#### Import via the Grafana UI

**Dashboard:** Open **Dashboards > New > Import** and upload
[oidc-license-service.dashboard.json](oidc-license-service.dashboard.json).
Select the destination folder (this example uses **General**) and map the
InfluxDB data source if prompted. If no mapping prompt appears, ensure the
JSON's datasource UIDs match your data source before importing. Choose whether
to create a new dashboard or overwrite one with the same UID, then click
**Import**.

**Alert rule:** Grafana 10.4, used by this project, does not support uploading
the exported alert-provisioning YAML through the UI. To use only the UI, open
**Alerting > Alert rules > New alert rule** and recreate the query, condition,
evaluation settings, and no-data behavior described in
[PyGuard HTTP 429 alert](#pyguard-http-429-alert). To reuse the YAML directly,
use Docker Compose provisioning below.

#### Import via Docker Compose

Grafana can load both exports from files at startup. Dashboard provisioning
also needs a provider file that tells Grafana where to find the dashboard JSON.

1. Create a file named `dashboard-provider.yaml` in this directory with:

   ```yaml
   apiVersion: 1
   providers:
     - name: OIDC License Service
       orgId: 1
       folder: ""
       type: file
       disableDeletion: true
       allowUiUpdates: false
       options:
         path: /etc/grafana/dashboards
   ```

   An empty `folder` places the dashboard in **General**. Adjust `orgId` if
   needed, and ensure the alert's **PyGuard** folder exists in the target
   organization.

2. Add these read-only mounts under the `grafana` service's `volumes` in
   [docker-compose.yml](../docker-compose.yml), keeping the existing
   `grafana_data` volume:

   ```yaml
   - ./grafana/dashboard-provider.yaml:/etc/grafana/provisioning/dashboards/dashboard-provider.yaml:ro
   - ./grafana/oidc-license-service.dashboard.json:/etc/grafana/dashboards/oidc-license-service.dashboard.json:ro
   - ./grafana/pyguard-http-429.alerting.yaml:/etc/grafana/provisioning/alerting/pyguard-http-429.alerting.yaml:ro
   ```

3. Recreate Grafana from the project directory:

   ```shell
   docker compose up -d --force-recreate grafana
   ```

4. Check **Dashboards** and **Alerting > Alert rules** to confirm that both
   configurations loaded. If either is missing, inspect the startup logs with
   `docker compose logs grafana`.

With this setup, configuration files are the source of truth: update the
dashboard JSON or alert YAML rather than editing provisioned resources in the
UI. Recreate Grafana after changing the alert YAML. Contact points and
notification policies are configured separately; importing a rule alone does
not set up notification delivery.

## Docker Desktop MCP Gateway

The Docker Desktop MCP Gateway provides a central way to connect AI clients to
MCP servers. The Grafana MCP server exposes Grafana operations through that
connection, allowing an AI client to access dashboards and, when permitted,
manage alert rules.

### Service Account

Create a Grafana service account and token for the MCP server:

1. In Grafana, open **Administration > Users and access > Service accounts**.
2. Create a service account, for example `grafana-mcp`.
3. For read-only dashboard access, assign the **Viewer** role. If the MCP
   server must manage alert rules, also grant it the `alert.provisioning:read`
   and `alert.provisioning:write` permissions.
4. Create a service account token and store it securely. Do not commit the
   token to source control.


### Grafana Server

Add the Grafana server from the Docker Desktop MCP catalog and configure:

- `grafana.url`: the Grafana base URL reachable from the MCP server. In this
  Linux Docker setup, use `http://172.17.0.1:3001`.
- `grafana.api_key`: the service account token created above; store it as a
  secret.

Restart the Grafana MCP server after changing its configuration. Verify the
connection by listing dashboards before trying alert-rule management.

