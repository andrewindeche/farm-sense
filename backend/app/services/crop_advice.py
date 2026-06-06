from __future__ import annotations

from typing import Any


class CropAdviceService:
    def suggest(self, weather: dict[str, Any]) -> str:
        current = weather.get("current", {})
        temp = current.get("temp_c") if "temp_c" in current else current.get("temperature", 0)
        condition = str(current.get("condition", {}).get("text", "")).lower()
        humidity = current.get("humidity") if "humidity" in current else current.get("humid", 0)
        precipitation = current.get("precip_mm") if "precip_mm" in current else current.get("rain", 0)

        crops = []
        reasons = []

        if temp >= 30 and precipitation < 2:
            crops = ["sorghum", "millet", "cassava"]
            reasons.append("hot and dry")
        elif temp >= 25 and "rain" in condition:
            crops = ["maize", "beans", "sweet potatoes"]
            reasons.append("warm with rain")
        elif temp >= 20 and humidity >= 60:
            crops = ["tomatoes", "pepper", "okra"]
            reasons.append("warm and humid")
        elif temp < 20 and "rain" in condition:
            crops = ["leafy greens", "kale", "spinach"]
            reasons.append("cool and wet")
        else:
            crops = ["beans", "sorghum", "groundnuts"]
            reasons.append("moderate conditions")

        if precipitation >= 10:
            reasons.append("heavy rainfall")
        elif precipitation >= 3:
            reasons.append("steady rainfall")

        reason_text = ", ".join(reasons) if reasons else "current weather conditions"
        crop_list = ", ".join(crops)

        return (
            f"Based on the current weather ({reason_text}), we recommend planting {crop_list}. "
            "Use rain-tolerant crops and maintain moisture with mulching."
        )


crop_advice_service = CropAdviceService()
