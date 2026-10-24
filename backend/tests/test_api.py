from fastapi.testclient import TestClient
from app.main import app

def test_health():
    with TestClient(app) as client:
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

def test_spawn_and_reset():
    with TestClient(app) as client:
        client.post("/api/simulation/reset")
        response = client.post("/api/simulation/spawn", json={"count":3,"city":"Coimbatore"})
        assert response.status_code == 200
        assert response.json()["created"] == 3
        assert len(client.get("/api/vehicles").json()) == 3
        client.post("/api/simulation/reset")
