from __future__ import annotations

from typing import Any


class HarvestReminderService:
    def suggest(self, weather: dict[str, Any]) -> str:
        current = weather.get("current", {})
        temp = current.get("temp_c") or current.get("temperature") or 0
        humidity = current.get("humidity") or current.get("humid") or 0
        precipitation = current.get("precip_mm") or current.get("rain") or 0
        condition = str(current.get("condition", {}).get("text", "")).lower()

        messages = []
        reasons = []

        if temp < 5:
            messages.append(
                "Frost risk detected — harvest all mature crops immediately "
                "to prevent frost damage."
            )
            reasons.append("freezing temperatures")
        elif temp >= 30 and humidity < 40:
            messages.append(
                "Hot and dry weather — crops may be ripening early. "
                "Check fields and harvest mature produce promptly."
            )
            reasons.append("hot and dry")
        elif temp >= 30 and humidity >= 60:
            messages.append(
                "Heat with high humidity — risk of spoilage. "
                "Harvest in the early morning and store in a cool, dry place."
            )
            reasons.append("hot and humid")
        elif precipitation >= 10:
            messages.append(
                "Heavy rain expected — delay harvest if possible. "
                "Harvested crops need proper drying and covered storage."
            )
            reasons.append("heavy rainfall")
        elif humidity >= 80:
            messages.append(
                "High humidity — avoid harvesting until conditions dry out. "
                "Wet crops are prone to fungal spoilage in storage."
            )
            reasons.append("very humid")
        elif temp >= 20 and humidity < 60 and precipitation < 3:
            messages.append(
                "Favorable harvest weather — dry and warm. "
                "Ideal window to bring in your crops."
            )
            reasons.append("warm and dry")
        elif temp >= 15 and precipitation < 3:
            messages.append(
                "Mild harvest conditions — good for most crops. "
                "Plan harvest during dry hours of the day."
            )
            reasons.append("mild weather")
        else:
            messages.append(
                "Monitor local conditions before harvesting. "
                "Delay if rain or high humidity is expected."
            )
            reasons.append("variable weather")

        if "rain" in condition and precipitation < 10:
            messages.append(
                "Rain in the forecast — aim to harvest before the next shower."
            )
            reasons.append("rain expected")

        if temp >= 35:
            messages.append(
                "Extreme heat warning — harvest early in the morning "
                "to avoid sun damage to produce."
            )
            reasons.append("extreme heat")

        reason_text = ", ".join(reasons)
        reminder = " ".join(messages)

        return (
            f"Harvest reminder ({reason_text}): {reminder} "
            "Store harvested crops away from direct sun and moisture."
        )


harvest_reminder_service = HarvestReminderService()
