#!/bin/bash
# START_HERE.sh - One-command project startup (Unix/macOS)

echo "🚀 Football Predictor - One-Command Startup"
echo "==========================================="
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3.11+ not found. Install from https://www.python.org/"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js 18+ not found. Install from https://nodejs.org/"
    exit 1
fi

echo "✅ Python: $(python3 --version)"
echo "✅ Node.js: $(node --version)"
echo ""

# Backend setup
echo "📦 Setting up backend..."
cd backend || exit 1

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install -q -r requirements.txt

# Start backend in background
echo "🟢 Starting backend on http://localhost:8000"
nohup python3 -m uvicorn app.main:app --reload > backend.log 2>&1 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"

# Sleep to let backend start
sleep 3

# Frontend setup
echo "📦 Setting up frontend..."
cd ../frontend || exit 1

if [ ! -d "node_modules" ]; then
    npm install -q
fi

echo "🟢 Starting frontend on http://localhost:5173"
npm run dev &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"

echo ""
echo "✅ Project started!"
echo "==========================================="
echo "📱 Frontend: http://localhost:5173"
echo "🔌 Backend:  http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop servers"
echo ""

# Wait for all background processes
wait
