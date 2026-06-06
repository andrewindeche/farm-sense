from app.services.crop_advice import crop_advice_service


def test_suggest_uses_hot_dry_recommendation():
    weather = {"current": {"temp_c": 33, "condition": {"text": "Sunny"}, "humidity": 35, "precip_mm": 0}}
    result = crop_advice_service.suggest(weather)
    assert "sorghum" in result.lower()
    assert "dry" in result.lower()


def test_suggest_uses_cool_wet_recommendation():
    weather = {"current": {"temp_c": 16, "condition": {"text": "Rain"}, "humidity": 85, "precip_mm": 12}}
    result = crop_advice_service.suggest(weather)
    assert "leafy greens" in result.lower() or "kale" in result.lower()
    assert "cool" in result.lower() or "wet" in result.lower()
