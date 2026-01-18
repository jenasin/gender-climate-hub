#!/bin/bash

# Gender & Climate Intelligence Hub - Start Script

echo "🌍 Starting Gender & Climate Intelligence Hub..."
echo ""

# Check for API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ ANTHROPIC_API_KEY not set!"
    echo "   Please run: export ANTHROPIC_API_KEY=your_key"
    exit 1
fi

echo "✅ API key found"

# Install backend dependencies
echo ""
echo "📦 Installing backend dependencies..."
cd backend
pip install -r requirements.txt -q

# Start backend in background
echo ""
echo "🚀 Starting backend server on http://localhost:8000"
python main.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Install frontend dependencies
echo ""
echo "📦 Installing frontend dependencies..."
cd ../frontend
npm install --silent

# Start frontend
echo ""
echo "🎨 Starting frontend on http://localhost:3000"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  🌍 Gender & Climate Intelligence Hub is running!"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "  Press Ctrl+C to stop"
echo ""

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait
