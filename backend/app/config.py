from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

env_path = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(env_path),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    weather_api_key: str = ""
    weather_api_base_url: str = "https://api.weather-ai.co/v1"

    africastalking_username: str = "sandbox"
    africastalking_api_key: str = ""
    africastalking_sender_id: str = "FARMSENSE"
    farmer_phone: str = ""
    scheduler_cron: str = "0 6 * * *"
    farmer_lat: float = -1.2921
    farmer_lon: float = 36.8219


settings = Settings()
