from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    weather_api_key: str = ""
    weather_api_base_url: str = "https://api.weatherapi.com/v1"

    africastalking_username: str = "sandbox"
    africastalking_api_key: str = ""
    africastalking_sender_id: str = "FARMSENSE"
    farmer_phone: str = ""


settings = Settings()
