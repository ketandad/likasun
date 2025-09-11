# Observability

The API exposes Prometheus metrics when `METRICS_ENABLED=true`.

```bash
curl http://localhost:8000/metrics
```

Configure Prometheus to scrape the endpoint:

```
scrape_configs:
  - job_name: raybeam
    static_configs:
      - targets: ['api:8000']
```

Useful Grafana panels:

- Rate of HTTP requests: `rate(raybeam_http_requests_total[5m])`
- Request latency: `histogram_quantile(0.95, sum(rate(raybeam_request_duration_seconds_bucket[5m])) by (le, route))`
- Evaluation duration: `histogram_quantile(0.95, sum(rate(raybeam_evaluate_duration_seconds_bucket[5m])) by (le))`
- Results by status: `raybeam_results_total`
