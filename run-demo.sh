#!/usr/bin/env bash
set -e

echo "Starting IS-Assist Demo..."
cd "$(dirname "$0")"

(cd backend && .venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000) &
BACKEND_PID=$!

(cd frontend && npm run dev -- --host 127.0.0.1 --port 5173) &
FRONTEND_PID=$!

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true" EXIT

echo "Backend running at: http://127.0.0.1:8000"
echo "Frontend running at: http://localhost:5173"
wait
