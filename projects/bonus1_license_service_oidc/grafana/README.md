## Grafana Dashboard

Flux is InfluxDB's query language, sent through its HTTP API. `from` selects a
bucket, `range` selects the time period, and `filter` selects data. For
example, this query counts requests in one-minute windows:

```flux
from(bucket: "api_metrics")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "api_requests")
  |> filter(fn: (r) => r._field == "status_code")
  |> aggregateWindow(every: 1m, fn: count, createEmpty: true)
  |> yield(name: "api_calls")
```

Grafana provides `v.timeRangeStart` and `v.timeRangeStop` when it runs the
query in a dashboard. The `aggregateWindow` function groups the points and
`count` counts the `status_code` field.
