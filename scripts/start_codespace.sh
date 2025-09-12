#!/bin/bash#!/usr/bin/env bash

# Codespaces startup script: launches backend (FastAPI/Uvicorn) and frontend (Next.js) for manual testingset -euo pipefail

# Uses SQLite, ensures Playwright browsers are installed, and fixes permissions

# RayBeam local dev launcher for Codespaces (no Docker)

set -eROOT="$(cd "$(dirname "$0")/.." && pwd)"

cd "$ROOT"

# Backend setup

cd /workspaces/likasun/apps/api# 1. Ensure Python venv for API

python3 -m venv .venvif [ ! -d ".venv-raybeam-api" ]; then

source .venv/bin/activate  python3 -m venv .venv-raybeam-api

pip install --upgrade pipfi

pip install -r requirements.txtsource .venv-raybeam-api/bin/activate

alembic upgrade headpip install --upgrade pip

pip install -r apps/api/requirements.txt

# Patch LICENSE_FILE and upload/data paths for Codespaces (if not already patched)

# (Manual patching required in code, see next steps)# 2. Run Alembic migrations (SQLite)

export DATABASE_URL="sqlite:///$ROOT/alembic.db"

# Frontend setupcd apps/api

cd /workspaces/likasun/apps/webalembic upgrade head

npm installcd "$ROOT"

npx playwright install --with-deps

echo "==> Starting RayBeam API (FastAPI, SQLite) on :8000"

# Start backend (port 8000) and frontend (port 3000) in background# Start API in background

cd /workspaces/likasun/apps/api

source .venv/bin/activatecd apps/api

nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 &PYTHONPATH="$ROOT" DATABASE_URL="sqlite:///$ROOT/alembic.db" uvicorn main:app --reload --port 8000 &

API_PID=$!

cd /workspaces/likasun/apps/webcd "$ROOT"

nohup npm run dev -- --port 3000 &

# 3. Start Next.js frontend

cd /workspaces/likasun

cd apps/web

echo "Backend running at http://localhost:8000"npm install

echo "Frontend running at http://localhost:3000"# Set Playwright browser path to user-writable directory

echo "Use 'ps aux' and 'kill' to manage background processes."export PLAYWRIGHT_BROWSERS_PATH="$ROOT/.pw-browsers"

mkdir -p "$PLAYWRIGHT_BROWSERS_PATH"
sudo npx playwright install --with-deps || true
PORT=3000 npm run dev &
WEB_PID=$!
cd "$ROOT"

echo "==> RayBeam API running at http://localhost:8000"
echo "==> RayBeam Web running at http://localhost:3000"
echo "==> Press Ctrl+C to stop both."

# Wait for both processes
wait $API_PID $WEB_PID
