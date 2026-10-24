from math import radians, sin, cos, sqrt, atan2

def distance_m(a, b):
    r = 6371000.0
    p1, p2 = radians(a["lat"]), radians(b["lat"])
    dp = radians(b["lat"]-a["lat"])
    dl = radians(b["lon"]-a["lon"])
    h = sin(dp/2)**2 + cos(p1)*cos(p2)*sin(dl/2)**2
    return 2*r*atan2(sqrt(h), sqrt(max(0, 1-h)))

def plan_route(origin, destination, altitude_m=120, blocked=False):
    # Illustrative route planner only; not for real flight navigation.
    if not blocked:
        points = [origin, destination]
        strategy = "direct_demo"
    else:
        mid = {
            "lat": (origin["lat"] + destination["lat"]) / 2 + 0.006,
            "lon": (origin["lon"] + destination["lon"]) / 2 - 0.004
        }
        points = [origin, mid, destination]
        strategy = "lateral_detour_demo"
    dist = sum(distance_m(points[i], points[i+1]) for i in range(len(points)-1))
    return {
        "waypoints": points, "distance_m": round(dist, 1),
        "strategy": strategy, "status": "planned",
        "altitude_m": altitude_m,
        "warning": "Demo route only; never use for real aircraft."
    }
