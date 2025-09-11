#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# Default env (only for local runs, not for Docker Compose)
if [[ -z "${RUNNING_IN_DOCKER:-}" ]]; then
  export DATABASE_URL="${DATABASE_URL:-postgresql+psycopg2://raybeam:raybeam@172.18.0.2:5432/raybeam}"
fi
export METRICS_ENABLED="${METRICS_ENABLED:-true}"
export RB_ADMIN_EMAIL="${RB_ADMIN_EMAIL:-admin@local}"
export RB_ADMIN_PASSWORD="${RB_ADMIN_PASSWORD:-admin}"

prepare_only=false
if [[ "${1:-}" == "--prepare" ]]; then
  prepare_only=true
fi

echo "==> Installing deps (Python + Node)"
pip install --upgrade pip >/dev/null
pip install -r apps/api/requirements.txt >/dev/null
npm ci >/dev/null

echo "==> Starting Postgres via Docker Compose"
docker compose -f ops/docker-compose.yml up -d db

echo "==> Waiting for Postgres to be healthy"
for i in {1..30}; do
  if docker compose -f ops/docker-compose.yml ps db | grep -qi "healthy"; then
    echo "Postgres is healthy"
    break
  fi
  sleep 2
  if [[ $i -eq 30 ]]; then
    echo "Postgres failed to become healthy" >&2
    exit 1
  fi

done


echo "==> Starting API and Web containers"
docker compose -f ops/docker-compose.yml up -d api web

echo "==> Waiting for API (http://localhost:8000/health)"
for i in {1..30}; do
  if curl -sf http://localhost:8000/health >/dev/null; then
    echo "API is up"
    break
  fi
  sleep 2
  if [[ $i -eq 30 ]]; then
    echo "API failed to start" >&2
    exit 1
  fi
done

echo "==> Running Alembic migrations (in Docker)"
docker compose -f ops/docker-compose.yml exec -w /app api alembic upgrade head

if $prepare_only; then
  echo "Preparation done. Use VS Code Task 'Start RayBeam Demo' or run: bash scripts/start_demo.sh"
  exit 0
fi

echo "==> Starting API and Web containers"
docker compose -f ops/docker-compose.yml up -d api web

echo "==> Waiting for API (http://localhost:8000/health)"
for i in {1..30}; do
  if curl -sf http://localhost:8000/health >/dev/null; then
    echo "API is up"
    break
  fi
  sleep 2
  if [[ $i -eq 30 ]]; then
    echo "API failed to start" >&2
    exit 1
  fi

done

echo "==> Loading demo assets"
curl -sf -X POST http://localhost:8000/assets/load-demo >/dev/null || true

echo "==> Running evaluation"
curl -sf -X POST http://localhost:8000/evaluate/run >/dev/null || true

echo "==> Exporting artifacts"
mkdir -p artifacts
curl -sf "http://localhost:8000/results/export.csv?status=FAIL" -o artifacts/results_fail.csv || true
curl -sf "http://localhost:8000/compliance/evidence-pack?framework=FedRAMP-Moderate" -o artifacts/fedramp_moderate.pdf || true

echo "==> Done. Open the forwarded URLs:"
echo "    Web UI:    http://localhost:3000"
echo "    API Health: http://localhost:8000/health"
