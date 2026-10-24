# SKYGRID INDIA
## AI-assisted lane-less air traffic management simulator

A simulation-first prototype for exploring future urban air mobility in Indian cities. It models flying vehicles, synthetic obstacles, restricted zones, route planning, predicted trajectory conflicts, emergency scenarios, and a live dashboard.

**Safety notice:** This is a research/demo simulator only. It is not certified aviation software, does not control real aircraft, and must not be used to plan or authorize real flights. All obstacle/cable data is synthetic demo data, not a survey of real infrastructure.

## Features
- FastAPI REST API and WebSocket event stream
- Responsive browser dashboard with CesiumJS 3D globe
- Up to 100 simulated vehicles
- Heuristic trajectory-projection conflict alerts with closest-approach estimates (not certified AI or aviation safety logic)
- Dedicated working dashboard pages: Airspace Overview, Traffic Monitor, Safety & Conflicts, Smart Route Planner, Vertiports, India Hazards, and Incident Log
- Configurable demo route planning and emergency landing-site recommendations
- Synthetic building, power-corridor and restricted-zone data
- Emergency scenario and persistent incident logs
- SQLite by default, Docker-ready
- Pytest tests

## Requirements
- Python 3.11+
- Optional: Docker Desktop

## Run on Windows / PowerShell
From the project folder:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

If PowerShell blocks activation, use:
```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000 for the dashboard and http://127.0.0.1:8000/docs for API docs.

## Run tests
From `backend`:
```powershell
pytest
```

## Docker
From project root:
```bash
docker compose up --build
```
Dashboard: http://localhost:8080  
API docs: http://localhost:8000/docs

## API
- `GET /api/health`
- `GET /api/overview`
- `GET /api/vehicles`
- `GET /api/obstacles`
- `GET /api/landing-sites`
- `GET /api/cities`
- `GET /api/conflicts`
- `POST /api/simulation/spawn`
- `POST /api/simulation/start`
- `POST /api/simulation/stop`
- `POST /api/simulation/step`
- `POST /api/simulation/reset`
- `POST /api/simulation/emergency/{vehicle_id}`
- `POST /api/routes/plan`
- `GET /api/incidents`
- `WS /ws/events`

## Important limitations
The demo uses simplified geographic movement and approximate horizontal/vertical alert thresholds. These are not aviation separation standards. Production use would require validated obstacle datasets, certified aircraft interfaces, formal hazard analysis, redundant systems, cybersecurity assurance, rigorous testing, and approvals from relevant authorities.
