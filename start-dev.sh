#!/bin/bash

# CaseMatch Development Environment Startup Script
# This script starts both the React frontend and Flask backend

echo "🚀 Starting CaseMatch Development Environment"
echo "=============================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is required but not installed"
    exit 1
fi

# Check if Node.js is available
if ! command -v npm &> /dev/null; then
    echo "❌ Node.js/npm is required but not installed"
    exit 1
fi

# Function to kill background processes on script exit
cleanup() {
    echo "🛑 Shutting down servers..."
    kill $(jobs -p) 2>/dev/null
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start Flask backend
echo "📡 Starting Flask backend on port 5001..."
cd backend
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt > /dev/null 2>&1
python run.py &
FLASK_PID=$!
cd ..

# Wait a moment for Flask to start
sleep 3

# Start React frontend (Express server)
echo "⚛️  Starting React frontend on port 5000..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Development environment is running!"
echo "   Frontend: http://localhost:5000"
echo "   Backend:  http://localhost:5001"
echo ""
echo "📋 Available backend endpoints:"
echo "   POST /search - Search for similar cases"
echo "   GET /test-connection - Test SAS Viya connection"
echo "   GET /health - Health check"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for background processes
wait