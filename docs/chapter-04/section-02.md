# Monitoring
## Connecting Grafana to InfluxDB

The license service records API requests in InfluxDB. Each request is stored
in the `api_requests` measurement with the HTTP method, endpoint, and response
status code.

### Open Grafana

Start the monitoring stack with Docker Compose and open Grafana:

<http://localhost:3001>

Log in with the Grafana administrator credentials configured in the `.env`
file:

- **Username:** `admin`
- **Password:** `admin1234`

### Add InfluxDB as a data source

In Grafana, open **Connections** → **Data sources** → **Add new data source**
and select **InfluxDB**.

Use these settings:

- **Query language:** `Flux`
- **URL:** `http://influxdb:8086`
- **Organization:** `oidc_license_service`
- **Default bucket:** `api_metrics`
- **Token:** the value of `INFLUXDB_TOKEN` from `.env`

Use `http://influxdb:8086` rather than `http://localhost:8086`. Grafana runs
inside Docker, so `localhost` refers to the Grafana container. The name
`influxdb` resolves to the InfluxDB service on the Docker network.

Click **Save & test**. Grafana should confirm that the data source is working.

### Query API metrics

Create a dashboard and add a panel using the InfluxDB data source. A basic
Flux query for recent API calls is:

```flux
from(bucket: "api_metrics")
	|> range(start: -1h)
	|> filter(fn: (r) => r._measurement == "api_requests")
```

The stored data contains:

- `method` — the HTTP method, such as `GET` or `POST`.
- `endpoint` — the requested API path.
- `_field` — normally `status_code`.
- `_value` — the HTTP response status code.

The middleware writes the metric after the request completes. Successful
writes return no value; InfluxDB raises an exception when a synchronous write
fails. Monitoring errors are logged and do not cause an otherwise healthy API
request to fail.

### Count API calls over time

To create a dashboard panel that displays the number of API calls over time:

1. Open **Dashboards** → **New** → **New dashboard**.
2. Click **Add visualization**.
3. Select the InfluxDB data source.
4. Switch to **Code** mode and enter this Flux query:

```flux
from(bucket: "api_metrics")
	|> range(start: v.timeRangeStart, stop: v.timeRangeStop)
	|> filter(fn: (r) => r._measurement == "api_requests")
	|> filter(fn: (r) => r._field == "status_code")
	|> aggregateWindow(every: 1m, fn: count, createEmpty: true)
	|> yield(name: "api_calls")
```

5. Select the **Time series** visualization.
6. Set the panel title to **API Calls Over Time**.
7. Click **Apply** and save the dashboard.

The query counts the `status_code` field once for every recorded request and
groups the results into one-minute intervals. The dashboard time-range
selector controls which requests are included.

For a single total count, create a **Stat** visualization with this query:

```flux
from(bucket: "api_metrics")
	|> range(start: v.timeRangeStart, stop: v.timeRangeStop)
	|> filter(fn: (r) => r._measurement == "api_requests")
	|> filter(fn: (r) => r._field == "status_code")
	|> count()
```

### Show requester IPs and endpoints in a table

To list one row for each API request with its timestamp, requester IP,
endpoint, and response status code:

1. Add a new Grafana panel.
2. Select the InfluxDB data source.
3. Switch to **Code** mode.
4. Use this Flux query:

```flux
from(bucket: "api_metrics")
	|> range(start: v.timeRangeStart, stop: v.timeRangeStop)
	|> filter(fn: (r) => r._measurement == "api_requests")
	|> filter(fn: (r) => r._field == "status_code")
	|> group()
	|> keep(columns: ["_time", "client_ip", "endpoint", "_value"])
	|> rename(columns: {
		_time: "Time",
		client_ip: "Requester",
		endpoint: "Endpoint",
		_value: "StatusCode",
	})
	|> sort(columns: ["Time"], desc: true)
```

5. Set the query result format to **Table** in the query editor. Do not use
	**Time series** format, because Grafana displays tags as series labels in
	that mode.
6. Select the **Table** visualization.
7. In the table options, disable **Column filter** to remove the filter row at
	the bottom of the table.
8. Set the panel title to **API Calls by Requester**.
9. Apply and save the panel.

The resulting table contains one line per recorded request with these columns:

- `Time` — when the request was recorded.
- `Requester` — the requester IP address.
- `Endpoint` — the requested API path.
- `StatusCode` — the HTTP response status code.

The `group()` call combines the individual InfluxDB series into one table so
the tags remain normal columns instead of being rendered as a series label.
This query does not use `count()` or `pivot()`, so requests are not grouped
or aggregated. Each InfluxDB point remains a separate table row.

If the table does not update after adding the `client_ip` tag, restart the
backend container and generate new requests. Existing InfluxDB points do not
contain tags that were added later.

