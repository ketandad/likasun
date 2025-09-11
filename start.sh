#!/bin/bash
set -e

# Start PostgreSQL if not running
if ! pg_isready; then
    sudo service postgresql start
fi

# Run DB migrations
cd apps/api
alembic upgrade head

# Start API in background
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &

# Start web frontend
cd ../web
npm run dev &

wait
