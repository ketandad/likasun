# Manual Test Playbook

## Setup

```bash
docker compose -f ops/docker-compose.yml up -d db
cd apps/api
alembic upgrade head
export RB_ADMIN_EMAIL=admin@local RB_ADMIN_PASSWORD=admin
```

## Ingest Demo

```bash
make demo-pack
```

1. Visit `/ingest` in the web UI.
2. Upload files from `tests/fixtures/ingest/`.
3. Navigate to `/assets` and verify more than ten assets exist.

## Evaluate

```bash
curl -X POST http://localhost:8000/evaluate/run
```

Check `/results/summary` for counts.

## Compliance

```bash
curl http://localhost:8000/compliance/summary?framework=FedRAMP-Moderate
curl -o evidence.pdf http://localhost:8000/compliance/evidence-pack?framework=PCI-DSS
curl -o export.csv http://localhost:8000/compliance/export.csv?framework=PCI-DSS
```

## Exceptions

1. Add a waiver via `/exceptions`.
2. Run evaluation again. A previous `FAIL` should become `WAIVED`.

## License

1. Upload the dev license at `/settings/license`.
2. Attempt a premium feature with a community license – expect HTTP 402.

## Security

1. Call an outbound URL not in the allowlist – request should be blocked.
2. Inspect a web response header for `CSP` and `X-Frame-Options`.

## Observability

If `METRICS_ENABLED=true`:

```bash
curl http://localhost:8000/metrics
```
