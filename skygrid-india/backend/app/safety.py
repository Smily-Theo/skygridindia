from math import radians, sin, cos, sqrt, atan2

# Heuristic demo thresholds only; these are NOT aviation separation standards.
HORIZONTAL_ALERT_M = 250.0
VERTICAL_ALERT_M = 30.0
PREDICTION_HORIZON_S = 60.0

def haversine_m(lat1, lon1, lat2, lon2):
    r = 6371000.0
    p1, p2 = radians(lat1), radians(lat2)
    dp, dl = radians(lat2-lat1), radians(lon2-lon1)
    a = sin(dp/2)**2 + cos(p1)*cos(p2)*sin(dl/2)**2
    return 2*r*atan2(sqrt(a), sqrt(max(0.0, 1-a)))

def _local_xy(lat, lon, lat0, lon0):
    # Local tangent-plane approximation for short-range demo predictions.
    return ((radians(lon-lon0) * 6371000.0 * cos(radians(lat0))),
            (radians(lat-lat0) * 6371000.0))

def _velocity(vehicle):
    # Simulator heading is degrees clockwise from north; speed is m/s.
    from math import sin, cos, radians
    heading, speed = radians(float(vehicle.get("heading_deg", 0))), float(vehicle.get("speed_mps", 0))
    return speed * sin(heading), speed * cos(heading)

def check_pair(a, b):
    horizontal = haversine_m(a["lat"], a["lon"], b["lat"], b["lon"])
    vertical = abs(a["altitude_m"] - b["altitude_m"])
    ax, ay = _local_xy(a["lat"], a["lon"], a["lat"], a["lon"])
    bx, by = _local_xy(b["lat"], b["lon"], a["lat"], a["lon"])
    avx, avy = _velocity(a); bvx, bvy = _velocity(b)
    rx, ry, vx, vy = bx-ax, by-ay, bvx-avx, bvy-avy
    vv = vx*vx + vy*vy
    t_cpa = max(0.0, min(PREDICTION_HORIZON_S, -(rx*vx+ry*vy)/vv)) if vv > 1e-6 else 0.0
    predicted = sqrt((rx+vx*t_cpa)**2 + (ry+vy*t_cpa)**2)
    predicted_vertical = vertical # Demo assumes altitude stays constant during prediction.
    current_conflict = horizontal < HORIZONTAL_ALERT_M and vertical < VERTICAL_ALERT_M
    predicted_conflict = predicted < HORIZONTAL_ALERT_M and predicted_vertical < VERTICAL_ALERT_M and t_cpa > 0
    conflict = current_conflict or predicted_conflict
    severity = "high" if conflict and min(horizontal, predicted) < 100 else ("medium" if conflict else "none")
    return {
        "vehicle_a": a["id"], "vehicle_b": b["id"],
        "horizontal_distance_m": round(horizontal, 1),
        "vertical_distance_m": round(vertical, 1),
        "predicted_closest_distance_m": round(predicted, 1),
        "time_to_closest_approach_s": round(t_cpa, 1),
        "conflict": conflict, "severity": severity,
        "prediction_horizon_s": PREDICTION_HORIZON_S,
        "note": "Heuristic trajectory projection for simulation only; not certified detect-and-avoid or flight guidance."
    }

def find_conflicts(vehicles):
    active = [v for v in vehicles if v.get("status") in ("enroute", "holding", "emergency")]
    results = []
    for i in range(len(active)):
        for j in range(i + 1, len(active)):
            item = check_pair(active[i], active[j])
            if item["conflict"]:
                results.append(item)
    return results
