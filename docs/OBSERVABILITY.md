# Observability

## Metrics

Set `METRICS_ENABLED=true` to expose Prometheus metrics at `/metrics`:

```bash
curl http://localhost:8000/metrics
```

Example Grafana panels:

- Rate of HTTP requests: `rate(raybeam_http_requests_total[5m])`
- Request latency: `histogram_quantile(0.95, sum(rate(raybeam_request_duration_seconds_bucket[5m])) by (le, route))`
- Evaluation duration: `histogram_quantile(0.95, sum(rate(raybeam_evaluate_duration_seconds_bucket[5m])) by (le))`
- Results by status: `raybeam_results_total`

## Logging

The API logs to stdout in JSON format with request ids. Configure a log forwarder or mount `/var/log/raybeam` to retain logs.

## Dashboards

Import the sample Grafana dashboards from `ops/grafana/` for API and evaluation metrics.
