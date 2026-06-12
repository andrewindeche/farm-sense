import logging
from typing import Any

from httpx import AsyncClient

from app.cache import cache
from app.config import settings

logger = logging.getLogger(__name__)

_CURRENT_TTL = 600
_FORECAST_TTL = 1800

_WMO_CODES: dict[int, str] = {
    0: "Clear",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


def _wmo_to_text(code: int) -> str:
    return _WMO_CODES.get(code, "Unknown")


def _map_current(current: dict[str, Any]) -> dict[str, Any]:
    return {
        "current": {
            "temp_c": current.get("temperature_2m"),
            "humidity": current.get("relative_humidity_2m"),
            "precip_mm": current.get("precipitation"),
            "wind_kph": current.get("wind_speed_10m"),
            "condition": {
                "text": _wmo_to_text(current.get("weather_code") or 0),
            },
        }
    }


def _map_forecast_daily(daily: dict[str, Any], days: int) -> dict[str, Any]:
    times = daily.get("time", [])
    forecastday = []
    for i in range(min(len(times), days)):
        forecastday.append(
            {
                "date": times[i],
                "day": {
                    "maxtemp_c": (
                        daily["temperature_2m_max"][i]
                        if daily.get("temperature_2m_max")
                        else None
                    ),
                    "mintemp_c": (
                        daily["temperature_2m_min"][i]
                        if daily.get("temperature_2m_min")
                        else None
                    ),
                    "totalprecip_mm": (
                        daily["precipitation_sum"][i]
                        if daily.get("precipitation_sum")
                        else None
                    ),
                    "condition": {
                        "text": _wmo_to_text(
                            daily["weather_code"][i]
                            if daily.get("weather_code")
                            else 0
                        ),
                    },
                },
            }
        )
    return {"forecast": {"forecastday": forecastday}}


class WeatherService:
    def __init__(self) -> None:
        self.base_url = settings.weather_api_base_url

    async def _get(self, path: str, params: dict | None = None) -> dict:
        async with AsyncClient(base_url=self.base_url) as client:
            resp = await client.get(path, params=params)
            resp.raise_for_status()
            return resp.json()

    async def get_current(self, lat: float, lon: float) -> dict:
        key = f"weather:current:{lat}:{lon}"
        cached = await cache.get(key)
        if cached is not None:
            logger.debug("Cache hit for %s", key)
            return cached
        data = await self._get(
            "/forecast",
            {
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,weather_code",
            },
        )
        result = _map_current(data.get("current") or {})
        await cache.set(key, result, ttl=_CURRENT_TTL)
        return result

    async def get_forecast(self, lat: float, lon: float, days: int = 3) -> dict:
        key = f"weather:forecast:{lat}:{lon}:{days}"
        cached = await cache.get(key)
        if cached is not None:
            logger.debug("Cache hit for %s", key)
            return cached
        data = await self._get(
            "/forecast",
            {
                "latitude": lat,
                "longitude": lon,
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code",
                "forecast_days": days,
            },
        )
        result = _map_forecast_daily(data.get("daily") or {}, days)
        await cache.set(key, result, ttl=_FORECAST_TTL)
        return result


weather_service = WeatherService()
