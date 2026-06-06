from httpx import AsyncClient

from app.config import settings


class WeatherService:
    def __init__(self) -> None:
        self.base_url = settings.weather_api_base_url
        self.api_key = settings.weather_api_key
        if not self.api_key:
            raise RuntimeError("WeatherAI API key is missing. Set WEATHER_API_KEY in backend/.env.")
        if self.api_key.startswith("atsk_"):
            raise RuntimeError(
                "WeatherAI API key appears to be an Africa's Talking key. "
                "Use a valid WeatherAI key for WEATHER_API_KEY."
            )

    async def _get(self, path: str, params: dict | None = None) -> dict:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with AsyncClient(base_url=self.base_url, headers=headers) as client:
            resp = await client.get(path, params=params)
            resp.raise_for_status()
            return resp.json()

    async def get_current(self, lat: float, lon: float) -> dict:
        return await self._get("/current", {"lat": lat, "lon": lon})

    async def get_forecast(self, lat: float, lon: float, days: int = 3) -> dict:
        return await self._get("/forecast", {"lat": lat, "lon": lon, "days": days})


weather_service = WeatherService()
