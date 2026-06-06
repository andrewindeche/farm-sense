from unittest.mock import patch

import pytest


@pytest.mark.asyncio
async def test_health_returns_ok(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_current_weather_defaults_to_nairobi(client):
    with patch(
        "app.services.weather.weather_service.get_current"
    ) as mock_get:
        mock_get.return_value = {"current": {"temp_c": 22}}

        resp = await client.get("/api/weather/current")

    assert resp.status_code == 200
    assert resp.json() == {"current": {"temp_c": 22}}
    mock_get.assert_called_once_with("Nairobi")


@pytest.mark.asyncio
async def test_current_weather_passes_location(client):
    with patch(
        "app.services.weather.weather_service.get_current"
    ) as mock_get:
        mock_get.return_value = {"current": {"temp_c": 30}}

        resp = await client.get("/api/weather/current?location=Mombasa")

    assert resp.status_code == 200
    mock_get.assert_called_once_with("Mombasa")


@pytest.mark.asyncio
async def test_forecast_defaults(client):
    with patch(
        "app.services.weather.weather_service.get_forecast"
    ) as mock_get:
        mock_get.return_value = {"forecast": {"forecastday": []}}

        resp = await client.get("/api/weather/forecast")

    assert resp.status_code == 200
    mock_get.assert_called_once_with("Nairobi", 3)


@pytest.mark.asyncio
async def test_forecast_passes_location_and_days(client):
    with patch(
        "app.services.weather.weather_service.get_forecast"
    ) as mock_get:
        mock_get.return_value = {"forecast": {"forecastday": []}}

        resp = await client.get(
            "/api/weather/forecast?location=Kisumu&days=7"
        )

    assert resp.status_code == 200
    mock_get.assert_called_once_with("Kisumu", 7)


@pytest.mark.asyncio
async def test_weather_returns_502_on_service_error(client):
    with patch(
        "app.services.weather.weather_service.get_current"
    ) as mock_get:
        mock_get.side_effect = Exception("API unavailable")

        resp = await client.get("/api/weather/current")

    assert resp.status_code == 502
    assert resp.json() == {"detail": "API unavailable"}
