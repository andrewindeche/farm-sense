from __future__ import annotations

from typing import Any

from app.services.ai import ai_service


class PestDiseaseService:
    async def suggest(self, weather: dict[str, Any], use_ai: bool = False) -> str:
        if use_ai:
            result = await ai_service.suggest_pest(weather)
            if result:
                return result
        return self._suggest_rules(weather)

    def _suggest_rules(self, weather: dict[str, Any]) -> str:
        current = weather.get("current", {})
        temp = current.get("temp_c") if "temp_c" in current else current.get("temperature", 0)
        humidity = current.get("humidity") if "humidity" in current else current.get("humid", 0)
        precipitation = current.get("precip_mm") if "precip_mm" in current else current.get("rain", 0)
        condition = str(current.get("condition", {}).get("text", "")).lower()

        issues = []
        reasons = []

        if humidity >= 80 and temp >= 25:
            issues = ["leaf spot and blight", "powdery mildew", "rust diseases"]
            reasons.append("very humid and warm")
        elif humidity >= 80 and temp < 25:
            issues = ["root rot", "bacterial wilt", "downy mildew"]
            reasons.append("very humid and cool")
        elif humidity >= 60 and temp >= 25:
            issues = ["aphids", "whiteflies", "armyworms"]
            reasons.append("warm and humid")
        elif humidity < 40 and temp >= 30:
            issues = ["spider mites", "thrips", "stem borers"]
            reasons.append("hot and dry")
        elif precipitation >= 5 and temp >= 20:
            issues = ["black sigatoka", "leaf rust", "downy mildew"]
            reasons.append("steady rain and warmth")
        else:
            issues = ["general leaf spot", "mild fungal diseases", "sap-sucking insects"]
            reasons.append("moderate weather conditions")

        if "rain" in condition or precipitation >= 3:
            reasons.append("rainy weather")

        if humidity >= 85:
            reasons.append("high humidity")
        elif humidity <= 35:
            reasons.append("low humidity")

        issues_text = ", ".join(issues)
        reason_text = ", ".join(reasons)

        return (
            f"Based on the current weather ({reason_text}), watch for {issues_text}. "
            "Inspect crops regularly, remove infected material, maintain good airflow, "
            "and use resistant varieties or approved treatments as needed."
        )


pest_disease_service = PestDiseaseService()
