from contextlib import asynccontextmanager
from datetime import datetime, timezone
import asyncio
from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .config import settings
from .database import Base, engine, get_db
from .models import Incident
from .schemas import SpawnRequest, RouteRequest, EmergencyRequest
from .simulator import Simulator, OBSTACLES, LANDING_SITES, CITY_CENTERS
from .routing import plan_route
from .safety import find_conflicts

Base.metadata.create_all(bind=engine)
sim = Simulator(max_vehicles=settings.max_simulated_vehicles)

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await sim.stop()

app = FastAPI(title=settings.app_name, version="0.1.0",
              description="Simulation-only urban air mobility traffic intelligence API", lifespan=lifespan)
origins = [x.strip() for x in settings.cors_origins.split(",") if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins or ["*"],
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

def save_incident(db, kind, severity, vehicle_id, message, details=None):
    row = Incident(kind=kind, severity=severity, vehicle_id=vehicle_id,
                   message=message, details=details or {})
    db.add(row); db.commit(); db.refresh(row)
    return row

@app.get("/")
def root():
    from fastapi.responses import FileResponse
    from pathlib import Path
    return FileResponse(Path(__file__).parent / "static" / "index.html")

@app.get("/api/health")
def health():
    return {"status":"ok","service":"skygrid-api","simulation_running":sim.running,"vehicles":len(sim.vehicles)}

@app.get("/api/overview")
def overview():
    conflicts = find_conflicts(sim.vehicles)
    return {"city":sim.city,"running":sim.running,"tick":sim.tick,"vehicle_count":len(sim.vehicles),
            "active_count":sum(v["status"] in ("enroute","holding","emergency") for v in sim.vehicles),
            "landed_count":sum(v["status"]=="landed" for v in sim.vehicles),
            "conflict_count":len(conflicts),"obstacle_count":len(OBSTACLES),
            "landing_site_count":len(LANDING_SITES),"updated_at":datetime.now(timezone.utc).isoformat()}

@app.get("/api/vehicles")
def vehicles():
    return sim.vehicles

@app.get("/api/obstacles")
def obstacles():
    return {"items":OBSTACLES,"note":"Synthetic demo obstacles; not real surveyed infrastructure."}

@app.get("/api/landing-sites")
def landing_sites():
    return LANDING_SITES

@app.get("/api/cities")
def cities():
    return [{"name":name, **coords} for name, coords in CITY_CENTERS.items()]

@app.get("/api/conflicts")
def conflicts():
    return find_conflicts(sim.vehicles)

@app.post("/api/simulation/spawn")
def spawn(req: SpawnRequest):
    created = sim.spawn(req.count, req.city)
    return {"created":created,"vehicle_count":len(sim.vehicles),"city":sim.city,"vehicles":sim.vehicles}

@app.post("/api/simulation/start")
async def start():
    await sim.start(settings.sim_tick_seconds)
    return {"running":sim.running,"message":"Simulation started"}

@app.post("/api/simulation/stop")
async def stop():
    await sim.stop()
    return {"running":sim.running,"message":"Simulation stopped"}

@app.post("/api/simulation/step")
async def step():
    conflicts = sim.step()
    return {"tick":sim.tick,"conflicts":conflicts,"overview":overview()}

@app.post("/api/simulation/reset")
async def reset():
    await sim.stop()
    sim.reset()
    return {"message":"Simulation reset","vehicle_count":0}

@app.post("/api/routes/plan")
def route_plan(req: RouteRequest):
    origin = {"lat":req.origin_lat,"lon":req.origin_lon}
    destination = {"lat":req.destination_lat,"lon":req.destination_lon}
    midpoint_lat = (origin["lat"] + destination["lat"]) / 2
    midpoint_lon = (origin["lon"] + destination["lon"]) / 2
    blocked = any(abs(o["lat"]-midpoint_lat) < 0.002 and abs(o["lon"]-midpoint_lon) < 0.002 for o in OBSTACLES)
    return plan_route(origin, destination, req.altitude_m, blocked=blocked)

@app.post("/api/simulation/emergency/{vehicle_id}")
def emergency(vehicle_id: str, req: EmergencyRequest, db: Session = Depends(get_db)):
    vehicle = next((v for v in sim.vehicles if v["id"] == vehicle_id), None)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    vehicle["status"] = "emergency"
    pad = min(LANDING_SITES, key=lambda p: (p["lat"]-vehicle["lat"])**2 + (p["lon"]-vehicle["lon"])**2)
    row = save_incident(db, "vehicle_emergency", "high", vehicle_id,
                        f"Emergency scenario triggered: {req.reason}",
                        {"recommended_landing_site":pad["id"],"note":"Demo recommendation; not operational guidance."})
    return {"vehicle":vehicle,"recommended_landing_site":pad,"incident_id":row.id,
            "notice":"Simulation-only recommendation. Not for real aircraft use."}

@app.get("/api/incidents")
def incidents(limit: int = 50, db: Session = Depends(get_db)):
    limit = max(1, min(limit, 200))
    rows = db.query(Incident).order_by(Incident.id.desc()).limit(limit).all()
    return [{"id":r.id,"kind":r.kind,"severity":r.severity,"vehicle_id":r.vehicle_id,
             "message":r.message,"details":r.details,
             "created_at":r.created_at.isoformat() if r.created_at else None} for r in rows]

@app.websocket("/ws/events")
async def websocket_events(websocket: WebSocket):
    await websocket.accept()
    queue = asyncio.Queue(maxsize=20)
    async def callback(event):
        try:
            queue.put_nowait(event)
        except asyncio.QueueFull:
            try:
                queue.get_nowait(); queue.put_nowait(event)
            except Exception:
                pass
    sim.subscribe(callback)
    try:
        await websocket.send_json({"type":"connected","data":sim.snapshot()})
        while True:
            await websocket.send_json(await queue.get())
    except WebSocketDisconnect:
        pass
    finally:
        sim.unsubscribe(callback)
