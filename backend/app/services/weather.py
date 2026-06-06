from httpx import AsyncClient

from app.config import settings


class WeatherService:
    def __init__(self) -> None:
        self.base_url = settings.weather_api_base_url
        self.api_key = settings.weather_api_key

    async def _get(self, path: str, params: dict | None = None) -> dict:
        params = {"key": self.api_key, **(params or {})}
        async with AsyncClient(base_url=self.base_url) as client:
            resp = await client.get(path, params=params)
            resp.raise_for_status()
            return resp.json()

    async def get_current(self, location: str) -> dict:
        return await self._get("/current.json", {"q": location})

    async def get_forecast(self, location: str, days: int = 3) -> dict:
        return await self._get("/forecast.json", {"q": location, "days": days})


weather_service = WeatherService()
