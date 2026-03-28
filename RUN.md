# EcoFlight AI - Hackathon Run Instructions

## ⚡ Quick Start (5 minutes)

### Terminal 1 - Backend
```bash
cd ~/Desktop/EcoFlight_AI/backend

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start server
python main.py
```

Backend will start on `http://localhost:8000`

You should see: `Uvicorn running on http://0.0.0.0:8000`

### Primary UI (recommended): 3D globe + 4D paths

After the backend is running:

```bash
open ~/Desktop/EcoFlight_AI/frontend/index.html
```

Or from Finder: open `Desktop/EcoFlight_AI/frontend/index.html` in Chrome or Safari.

**Important:** Restart `python main.py` after pulling code changes so `/optimize` includes `trajectory_4d` and waypoint times.

Optional: `GET http://localhost:8000/research` returns the bibliography JSON for judges.

### Optional - Streamlit (older cockpit UI)

```bash
cd ~/Desktop/EcoFlight_AI/frontend
source venv/bin/activate
streamlit run app.py
```

Opens at `http://localhost:8501`

---

## 🧪 Testing the API

Once backend is running, test with:

```bash
# Test airports endpoint
curl http://localhost:8000/airports

# Test optimization
curl -X POST http://localhost:8000/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "KJFK",
    "destination": "KLAX",
    "aircraft_type": "B737",
    "priority": "balanced"
  }'
```

---

## 🐛 Troubleshooting

### Port already in use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or run on different port
python main.py --port 8001
```

### Frontend can't connect to backend
Make sure backend is running before starting frontend.

If using different ports, update `API_URL` in `frontend/app.py`:
```python
API_URL = "http://localhost:8001"  # match your backend port
```

### Missing dependencies
```bash
# Reinstall all packages
pip install --force-reinstall -r requirements.txt
```

---

## 🎯 Demo Script for Judges

1. **Start both services** (follow quick start above)

2. **Open browser** to `http://localhost:8501`

3. **Demo flow**:
   - Select route: KJFK → KLAX (New York to LA)
   - Aircraft: B737
   - Priority: Balanced
   - Click "Optimize Route"

4. **Point out**:
   - Green optimized route vs red direct route
   - Altitude profile with CDO descent
   - Fuel savings: ~350kg
   - CO₂ reduction: ~1,100kg
   - Cost savings: ~$280

5. **Show weather impact**:
   - Expand "Weather Factors"
   - Mention jet stream exploitation
   - Explain headwind avoidance

6. **Environmental scale**:
   - Bottom section shows if all US flights used this
   - 1.2M tons CO₂ avoided annually
   - Equivalent to 253K cars off road

7. **Differentiation slide** (scroll down in welcome view)
   - 4D vs 2D optimization
   - CDO integration
   - Real weather API

---

## 📦 Deployment (Optional)

### Deploy Backend (Render)
1. Push code to GitHub
2. Connect Render.com
3. Set build command: `pip install -r requirements.txt`
4. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Deploy Frontend (Streamlit Cloud)
1. Push code to GitHub
2. Connect to share.streamlit.io
3. Select repo and branch

---

## 🔥 Emergency Fallback

If everything breaks during demo:

1. **Show the code** - judges can see the architecture
2. **Reference the README** - shows research foundation
3. **Explain the algorithm** - A* with 4D optimization
4. **Emphasize the impact** - 3.67% fuel savings is validated

---

## 📞 Commands Quick Reference

```bash
# Start backend
cd backend && source venv/bin/activate && python main.py

# Start frontend (new terminal)
cd frontend && source venv/bin/activate && streamlit run app.py

# Test API
curl http://localhost:8000/airports

# Kill processes
lsof -ti:8000 | xargs kill -9
lsof -ti:8501 | xargs kill -9
```

---

**Good luck! You've got this! 🚀**
