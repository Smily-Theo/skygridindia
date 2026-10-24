from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "SKYGRID INDIA"
    database_url: str = "sqlite:///./skygrid.db"
    cors_origins: str = "http://localhost:8000"
    sim_tick_seconds: float = 2.0
    default_city: str = "Coimbatore"
    max_simulated_vehicles: int = 100
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
