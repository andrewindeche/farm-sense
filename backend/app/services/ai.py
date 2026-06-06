from __future__ import annotations

import logging
from typing import Any

from httpx import AsyncClient

from app.config import settings

logger = logging.getLogger(__name__)

_GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

_CROP_PROMPT = (
    "You are an expert agricultural advisor for small-scale farmers in East Africa. "
    "Based on this weather data, recommend specific crops to plant. "
    "Weather: temp {temp}C, humidity {humidity}%, precipitation {precip}mm, conditions '{condition}'. "
    "Keep response under 300 characters. Be concise and practical."
)

_PEST_PROMPT = (
    "You are an expert agricultural advisor for small-scale farmers in East Africa. "
    "Based on this weather data, identify likely pest or disease threats. "
    "Weather: temp {temp}C, humidity {humidity}%, precipitation {precip}mm, conditions '{condition}'. "
    "Keep response under 300 characters. Include inspection and prevention tips."
)

_HARVEST_PROMPT = (
    "You are an expert agricultural advisor for small-scale farmers in East Africa. "
    "Based on this weather data, give harvest timing advice. "
    "Weather: temp {temp}C, humidity {humidity}%, precipitation {precip}mm, conditions '{condition}'. "
    "Keep response under 300 characters. Be concise and practical."
)


class AIService:
    def __init__(self) -> None:
        self.api_key = settings.gemini_api_key

    async def _generate(self, prompt: str) -> str | None:
        if not self.api_key:
            logger.debug("GEMINI_API_KEY not set — skipping AI call")
            return None

        url = f"{_GEMINI_URL}?key={self.api_key}"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}

        try:
            async with AsyncClient() as client:
                resp = await client.post(url, json=payload, timeout=30)
                resp.raise_for_status()
                data = resp.json()
        except Exception as e:
            logger.warning("Gemini API call failed: %s: %s", type(e).__name__, e)
            return None

        try:
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            return text.strip()
        except (KeyError, IndexError, TypeError) as e:
            logger.warning("Unexpected Gemini response format: %s", e)
            return None

    async def suggest_crop(self, weather: dict[str, Any]) -> str | None:
        current = weather.get("current", {})
        temp = current.get("temp_c") if "temp_c" in current else current.get("temperature", 0)
        humidity = current.get("humidity") if "humidity" in current else current.get("humid", 0)
        precip = current.get("precip_mm") if "precip_mm" in current else current.get("rain", 0)
        condition = str(current.get("condition", {}).get("text", ""))
        prompt = _CROP_PROMPT.format(temp=temp, humidity=humidity, precip=precip, condition=condition)
        return await self._generate(prompt)

    async def suggest_pest(self, weather: dict[str, Any]) -> str | None:
        current = weather.get("current", {})
        temp = current.get("temp_c") if "temp_c" in current else current.get("temperature", 0)
        humidity = current.get("humidity") if "humidity" in current else current.get("humid", 0)
        precip = current.get("precip_mm") if "precip_mm" in current else current.get("rain", 0)
        condition = str(current.get("condition", {}).get("text", ""))
        prompt = _PEST_PROMPT.format(temp=temp, humidity=humidity, precip=precip, condition=condition)
        return await self._generate(prompt)

    async def suggest_harvest(self, weather: dict[str, Any]) -> str | None:
        current = weather.get("current", {})
        temp = current.get("temp_c") if "temp_c" in current else current.get("temperature", 0)
        humidity = current.get("humidity") if "humidity" in current else current.get("humid", 0)
        precip = current.get("precip_mm") if "precip_mm" in current else current.get("rain", 0)
        condition = str(current.get("condition", {}).get("text", ""))
        prompt = _HARVEST_PROMPT.format(temp=temp, humidity=humidity, precip=precip, condition=condition)
        return await self._generate(prompt)


ai_service = AIService()
