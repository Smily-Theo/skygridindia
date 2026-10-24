import asyncio, random, uuid, math
from datetime import datetime, timezone
from .safety import find_conflicts

CITY_CENTERS = {
    "Coimbatore": {"lat": 11.0168, "lon": 76.9558},
    "Chennai": {"lat": 13.0827, "lon": 80.2707},
    "Bengaluru": {"lat": 12.9716, "lon": 77.5946},
}
# Synthetic demo features, not surveyed infrastructure.
OBSTACLES = [
    {"id":"BLD-001","type":"building","name":"Demo high-rise A","lat":11.0220,"lon":76.9630,"height_m":85,"radius_m":90},
    {"id":"PWR-001","type":"power_line","name":"Synthetic power corridor","lat":11.0190,"lon":76.9740,"height_m":35,"radius_m":140},
    {"id":"BLD-002","type":"building","name":"Demo high-rise B","lat":11.0110,"lon":76.9480,"height_m":62,"radius_m":70},
    {"id":"RZ-001","type":"restricted_zone","name":"Demo restricted zone","lat":11.0270,"lon":76.9460,"height_m":300,"radius_m":250},
]
LANDING_SITES = [
    {"id":"PAD-01","name":"Demo Central Vertiport","lat":11.0168,"lon":76.9558,"capacity":8,"available":True},
    {"id":"PAD-02","name":"Demo North Landing Site","lat":11.0340,"lon":76.9630,"capacity":4,"available":True},
    {"id":"PAD-03","name":"Demo East Landing Site","lat":11.0180,"lon":76.9920,"capacity":4,"available":True},
]

class Simulator:
    def __init__(self, max_vehicles=100):
        self.max_vehicles = max_vehicles
        self.vehicles = []
        self.running = False
        self.tick = 0
        self.city = "Coimbatore"
        self.events = []
        self._task = None
        self._callbacks = set()

    def subscribe(self, callback):
        self._callbacks.add(callback)

    def unsubscribe(self, callback):
        self._callbacks.discard(callback)

    async def emit(self, event):
        self.events.append(event)
        self.events = self.events[-100:]
        dead = []
        for callback in list(self._callbacks):
            try:
                await callback(event)
            except Exception:
                dead.append(callback)
        for callback in dead:
            self._callbacks.discard(callback)

    def snapshot(self):
        return {"running": self.running, "tick": self.tick, "city": self.city,
                "vehicles": self.vehicles, "conflicts": find_conflicts(self.vehicles),
                "updated_at": datetime.now(timezone.utc).isoformat()}

    def spawn(self, count=10, city="Coimbatore"):
        self.city = city if city in CITY_CENTERS else "Coimbatore"
        center = CITY_CENTERS[self.city]
        count = max(0, min(count, self.max_vehicles - len(self.vehicles)))
        for _ in range(count):
            origin = {"lat": center["lat"] + random.uniform(-0.025, 0.025),
                      "lon": center["lon"] + random.uniform(-0.03, 0.03)}
            destination = {"lat": center["lat"] + random.uniform(-0.025, 0.025),
                           "lon": center["lon"] + random.uniform(-0.03, 0.03)}
            self.vehicles.append({
                "id": f"FC-{uuid.uuid4().hex[:6].upper()}",
                "city": self.city, "lat": origin["lat"], "lon": origin["lon"],
                "altitude_m": random.choice([90, 120, 150, 180, 210]),
                "speed_mps": random.randint(18, 35), "destination": destination,
                "route": [origin, destination], "waypoint_index": 0,
                "status": "enroute", "battery_pct": random.randint(55, 100),
                "priority": "emergency" if random.random() < 0.04 else "normal",
                "heading_deg": random.randint(0, 359),
                "created_at": datetime.now(timezone.utc).isoformat()
            })
        return count

    def reset(self):
        self.vehicles = []
        self.tick = 0
        self.events = []
        self.running = False

    def step(self):
        self.tick += 1
        for v in self.vehicles:
            if v["status"] not in ("enroute", "holding"):
                continue
            target = v["destination"]
            dlat = target["lat"] - v["lat"]
            dlon = target["lon"] - v["lon"]
            if math.sqrt(dlat*dlat + dlon*dlon) < 0.0012:
                v["status"] = "landed"
                continue
            # Tiny coordinate step for visual demo; not a physical flight model.
            v["lat"] += dlat * 0.035
            v["lon"] += dlon * 0.035
            v["battery_pct"] = max(0, v["battery_pct"] - 0.01)
            v["heading_deg"] = (math.degrees(math.atan2(dlon, dlat)) + 360) % 360
        return find_conflicts(self.vehicles)

    async def run_loop(self, tick_seconds=2.0):
        while self.running:
            conflicts = self.step()
            await self.emit({"type":"simulation_tick","data":self.snapshot()})
            for conflict in conflicts:
                await self.emit({"type":"conflict_alert","data":conflict})
            await asyncio.sleep(tick_seconds)

    async def start(self, tick_seconds=2.0):
        if self.running:
            return
        self.running = True
        self._task = asyncio.create_task(self.run_loop(tick_seconds))

    async def stop(self):
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
