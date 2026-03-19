#!/usr/bin/env bash
# Medixa AI — Local development launcher
# Starts backend (Flask) and frontend (Vite) in parallel.
# Prerequisites: Python 3.10+, Node 18+, npm. Run setup first (see README).

set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

echo "🩺 Medixa AI — Starting development servers..."
echo "   Backend:  http://localhost:5001"
echo "   Frontend: http://localhost:5173"
echo ""

(cd server && python app.py) &
API_PID=$!
sleep 2

(cd client && npm run dev) &
CLIENT_PID=$!

cleanup() {
  echo ""; echo "🛑 Shutting down..."; kill $API_PID $CLIENT_PID 2>/dev/null; exit 0
}
trap cleanup SIGINT SIGTERM
wait
