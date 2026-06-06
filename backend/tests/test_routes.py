from unittest.mock import patch

import pytest


@pytest.mark.asyncio
async def test_root_returns_running_message(client):
    resp = await client.get("/")
    assert resp.status_code == 200
    assert resp.json() == {"message": "Fastapi is running!"}


@pytest.mark.asyncio
async def test_health_returns_ok(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_current_weather_requires_lat_lon(client):
    with patch(
        "app.services.weather.weather_service.get_current"
    ) as mock_get:
        mock_get.return_value = {"current": {"temp_c": 22}}

        resp = await client.get("/api/weather/current?lat=-1.2921&lon=36.8219")

    assert resp.status_code == 200
    assert resp.json() == {"current": {"temp_c": 22}}
    mock_get.assert_called_once_with(-1.2921, 36.8219)


@pytest.mark.asyncio
async def test_forecast_passes_lat_lon_and_days(client):
    with patch(
        "app.services.weather.weather_service.get_forecast"
    ) as mock_get:
        mock_get.return_value = {"forecast": {"forecastday": []}}

        resp = await client.get(
            "/api/weather/forecast?lat=-1.2921&lon=36.8219&days=7"
        )

    assert resp.status_code == 200
    mock_get.assert_called_once_with(-1.2921, 36.8219, 7)


@pytest.mark.asyncio
async def test_weather_returns_502_on_service_error(client):
    with patch(
        "app.services.weather.weather_service.get_current"
    ) as mock_get:
        mock_get.side_effect = Exception("API unavailable")

        resp = await client.get("/api/weather/current?lat=-1.2921&lon=36.8219")

    assert resp.status_code == 502
    assert resp.json() == {"detail": "API unavailable"}


@pytest.mark.asyncio
async def test_notify_farmer_route_sends_message(client):
    with patch(
        "app.services.africastalking.africastalking_service.send_sms"
    ) as mock_send:
        mock_send.return_value = {"status": "sent"}

        resp = await client.post("/api/notify/farmer?message=Hello")

    assert resp.status_code == 200
    assert resp.json() == {"status": "sent"}
    mock_send.assert_called_once_with("Hello")


@pytest.mark.asyncio
async def test_notify_farmer_route_returns_502_on_error(client):
    with patch(
        "app.services.africastalking.africastalking_service.send_sms"
    ) as mock_send:
        mock_send.side_effect = Exception("SMS failed")

        resp = await client.post("/api/notify/farmer?message=Hello")

    assert resp.status_code == 502
    assert resp.json() == {"detail": "SMS failed"}
