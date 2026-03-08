#!/bin/bash
# Development startup script
# Usage: ./dev.sh

set -e

echo "Starting Quip-SharePoint development servers..."

# Backend
echo "Starting backend (FastAPI)..."
cd backend
uv run uvicorn src.app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Frontend
echo "Starting frontend (Vite)..."
cd frontend
bun dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo "API docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
