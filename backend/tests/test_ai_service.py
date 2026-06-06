from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.ai import AIService

_WEATHER = {"current": {"temp_c": 28, "humidity": 70, "condition": {"text": "Rain"}, "precip_mm": 5}}


def _mock_response(text: str):
    mock = MagicMock()
    mock.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": text}]}}]
    }
    return mock


@pytest.fixture
def service(monkeypatch):
    monkeypatch.setattr("app.services.ai.settings.gemini_api_key", "test-key")
    return AIService()


@pytest.mark.asyncio
async def test_suggest_crop_returns_none_when_no_api_key():
    svc = AIService()
    result = await svc.suggest_crop(_WEATHER)
    assert result is None


@pytest.mark.asyncio
async def test_suggest_crop_returns_formatted_advice(service):
    with patch("app.services.ai.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post.return_value = (
            _mock_response("Plant maize and beans.")
        )
        result = await service.suggest_crop(_WEATHER)

    assert result == "Plant maize and beans."


@pytest.mark.asyncio
async def test_suggest_pest_returns_formatted_alert(service):
    with patch("app.services.ai.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post.return_value = (
            _mock_response("Watch for aphids.")
        )
        result = await service.suggest_pest(_WEATHER)

    assert result == "Watch for aphids."


@pytest.mark.asyncio
async def test_suggest_harvest_returns_formatted_reminder(service):
    with patch("app.services.ai.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post.return_value = (
            _mock_response("Harvest in the morning.")
        )
        result = await service.suggest_harvest(_WEATHER)

    assert result == "Harvest in the morning."


@pytest.mark.asyncio
async def test_returns_none_on_api_error(service):
    with patch("app.services.ai.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post.side_effect = Exception(
            "API down"
        )
        result = await service.suggest_crop(_WEATHER)

    assert result is None


@pytest.mark.asyncio
async def test_returns_none_on_invalid_response(service):
    mock = MagicMock()
    mock.json.return_value = {"unexpected": "format"}

    with patch("app.services.ai.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post.return_value = mock
        result = await service.suggest_crop(_WEATHER)

    assert result is None


@pytest.mark.asyncio
async def test_use_ai_flag_returns_ai_content(client):
    with patch(
        "app.services.weather.weather_service.get_current"
    ) as mock_weather, patch(
        "app.services.ai.ai_service.suggest_crop"
    ) as mock_ai, patch(
        "app.services.africastalking.africastalking_service.send_sms"
    ) as mock_sms:
        mock_weather.return_value = _WEATHER
        mock_ai.return_value = "AI says plant maize."
        mock_sms.return_value = {"status": "sent"}

        resp = await client.post(
            "/api/advice/request",
            json={"lat": -1.2921, "lon": 36.8219, "use_ai": True},
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["recommendation"] == "AI says plant maize."


@pytest.mark.asyncio
async def test_use_ai_flag_falls_back_to_rules_on_ai_failure(client):
    with patch(
        "app.services.weather.weather_service.get_current"
    ) as mock_weather, patch(
        "app.services.ai.ai_service.suggest_crop"
    ) as mock_ai, patch(
        "app.services.africastalking.africastalking_service.send_sms"
    ) as mock_sms:
        mock_weather.return_value = _WEATHER
        mock_ai.return_value = None
        mock_sms.return_value = {"status": "sent"}

        resp = await client.post(
            "/api/advice/request",
            json={"lat": -1.2921, "lon": 36.8219, "use_ai": True},
        )

    assert resp.status_code == 200
    data = resp.json()
    assert "recommendation" in data
