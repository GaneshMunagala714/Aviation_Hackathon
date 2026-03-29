#!/bin/bash
# EcoFlight AI 3 — Startup Script
# Launches backend with all API keys pre-configured

BACKEND_DIR="$(cd "$(dirname "$0")/backend" && pwd)"
FRONTEND_DIR="$(cd "$(dirname "$0")/frontend" && pwd)"

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║        EcoFlight AI — Hackathon Launch Pad           ║"
echo "║        ARIA on 121.500 AI Universal Frequency        ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# Kill any existing backend on port 8000
echo "→ Clearing port 8000..."
lsof -ti:8000 | xargs kill -9 2>/dev/null
sleep 1

# Start backend with API keys
echo "→ Starting backend (FastAPI on port 8000)..."
cd "$BACKEND_DIR"

# Activate venv if available
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Launch with keys
ELEVENLABS_API_KEY="sk_1456c213d59ac750a4226882e49d203da059398edb66d970" \
ELEVENLABS_VOICE_ID="CwhRBWXzGAHq8TQ4Fs17" \
python main.py &

BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"
sleep 3

# Check backend is running
if curl -s "http://localhost:8000/radio/status" > /dev/null 2>&1; then
    echo "   ✅ Backend online"
else
    echo "   ⚠  Backend starting... (give it a moment)"
fi

# Open main UI
echo ""
echo "→ Opening EcoFlight AI..."
open "$FRONTEND_DIR/index.html"

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║  Main App  → $FRONTEND_DIR/index.html               ║"
echo "║  ARIA Radio → click '🎙 ARIA — 121.500 AI RADIO'   ║"
echo "║  Backend   → http://localhost:8000                   ║"
echo "║  API Docs  → http://localhost:8000/docs             ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""
echo "Press Ctrl+C to stop the backend."

wait $BACKEND_PID
