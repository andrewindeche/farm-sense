import pytest

from app.services.crop_advice import crop_advice_service


@pytest.mark.asyncio
async def test_suggest_uses_hot_dry_recommendation():
    weather = {"current": {"temp_c": 33, "condition": {"text": "Sunny"}, "humidity": 35, "precip_mm": 0}}
    result = await crop_advice_service.suggest(weather)
    assert "sorghum" in result.lower()
    assert "dry" in result.lower()


@pytest.mark.asyncio
async def test_suggest_uses_cool_wet_recommendation():
    weather = {"current": {"temp_c": 16, "condition": {"text": "Rain"}, "humidity": 85, "precip_mm": 12}}
    result = await crop_advice_service.suggest(weather)
    assert "leafy greens" in result.lower() or "kale" in result.lower()
    assert "cool" in result.lower() or "wet" in result.lower()


@pytest.mark.asyncio
async def test_suggest_zero_temp_c_does_not_fall_through_to_temperature_fallback():
    weather = {"current": {"temp_c": 0, "temperature": 25, "condition": {"text": "Rain"}, "humidity": 80, "precip_mm": 5}}
    result = await crop_advice_service.suggest(weather)
    assert "leafy greens" in result.lower() or "kale" in result.lower()


@pytest.mark.asyncio
async def test_suggest_zero_humidity_does_not_fall_through_to_humid_fallback():
    weather = {"current": {"temp_c": 35, "humidity": 0, "humid": 50, "condition": {"text": "Sunny"}, "precip_mm": 0}}
    result = await crop_advice_service.suggest(weather)
    assert "sorghum" in result.lower()


@pytest.mark.asyncio
async def test_suggest_zero_precip_does_not_fall_through_to_rain_fallback():
    weather = {"current": {"temp_c": 22, "humidity": 70, "precip_mm": 0, "rain": 10, "condition": {"text": "Rain"}}}
    result = await crop_advice_service.suggest(weather)
    assert "tomatoes" in result.lower() or "pepper" in result.lower()


@pytest.mark.asyncio
async def test_suggest_missing_current_returns_default():
    result = await crop_advice_service.suggest({})
    assert "beans" in result.lower() or "sorghum" in result.lower()
