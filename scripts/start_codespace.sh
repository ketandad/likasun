
#!/bin/bash
# RayBeam Codespaces startup script: launches backend (FastAPI/Uvicorn, SQLite) and frontend (Next.js)
set -e

ROOT="/workspaces/likasun"

# --- Backend setup ---
cd "$ROOT/apps/api"
if [ ! -d ".venv" ]; then
	python3 -m venv .venv
fi
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
export DATABASE_URL="sqlite:///$ROOT/alembic.db"
alembic upgrade head

# --- Frontend setup ---
cd "$ROOT/apps/web"
npm install


# --- Start backend (port 8000) ---
cd "$ROOT/apps/api"
source .venv/bin/activate
PYTHONPATH="$ROOT" nohup uvicorn main:app --host 0.0.0.0 --port 8000 &
API_PID=$!

# --- Start frontend (port 3000) ---
cd "$ROOT/apps/web"
nohup npm run dev -- --port 3000 &
WEB_PID=$!

cd "$ROOT"
echo "==> RayBeam API running at http://localhost:8000"
echo "==> RayBeam Web running at http://localhost:3000"
echo "==> Use 'ps aux' and 'kill' to manage background processes."

# Wait for both processes
wait $API_PID $WEB_PID
