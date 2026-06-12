from pathlib import Path
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

env_path = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(env_path),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/farmsense"

    def model_post_init(self, __context: object) -> None:
        # Railway provides DATABASE_URL as `postgresql://...` (the sync scheme).
        # SQLAlchemy's async engine requires `postgresql+asyncpg://...`, so we
        # rewrite the scheme here to avoid a ModuleNotFoundError for psycopg2.
        if self.database_url.startswith("postgresql://") or self.database_url.startswith("postgres://"):
            object.__setattr__(
                self,
                "database_url",
                self.database_url.replace("://", "+asyncpg://", 1),
            )

    frontend_url: str = "http://localhost:5173"

    weather_api_base_url: str = "https://api.open-meteo.com/v1"

    africastalking_username: str = "sandbox"
    africastalking_api_key: str = ""
    africastalking_sender_id: str = "FARMSENSE"
    farmer_phone: str = ""
    scheduler_cron: str = "0 6 * * *"
    farmer_lat: float = -1.2921
    farmer_lon: float = 36.8219


settings = Settings()
