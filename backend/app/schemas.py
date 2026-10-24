from pydantic import BaseModel, Field

class SpawnRequest(BaseModel):
    count: int = Field(default=10, ge=1, le=100)
    city: str = Field(default="Coimbatore", min_length=2, max_length=80)

class RouteRequest(BaseModel):
    origin_lat: float = 11.0168
    origin_lon: float = 76.9558
    destination_lat: float = 11.0300
    destination_lon: float = 77.0000
    altitude_m: float = Field(default=120, ge=30, le=300)

class EmergencyRequest(BaseModel):
    reason: str = Field(default="Simulated vehicle system failure", max_length=300)
