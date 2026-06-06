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
async def test_auth_register_login_and_me(client):
    register_resp = await client.post(
        "/api/auth/register",
        json={"username": "farmer1", "password": "strongpass"},
    )
    assert register_resp.status_code == 200
    assert register_resp.json() == {"username": "farmer1", "status": "registered"}

    login_resp = await client.post(
        "/api/auth/login",
        json={"username": "farmer1", "password": "strongpass"},
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    assert login_resp.json()["token_type"] == "bearer"

    me_resp = await client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_resp.status_code == 200
    assert me_resp.json() == {"username": "farmer1"}


@pytest.mark.asyncio
async def test_auth_logout(client):
    await client.post(
        "/api/auth/register",
        json={"username": "farmer2", "password": "pass123"},
    )
    login_resp = await client.post(
        "/api/auth/login",
        json={"username": "farmer2", "password": "pass123"},
    )
    token = login_resp.json()["access_token"]

    logout_resp = await client.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert logout_resp.status_code == 200
    assert logout_resp.json() == {"status": "logged_out"}

    me_resp = await client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_resp.status_code == 401


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
async def test_advice_request_sends_fallback_recommendation(client):
    with patch(
        "app.services.weather.weather_service.get_current"
    ) as mock_weather, patch(
        "app.services.africastalking.africastalking_service.send_sms"
    ) as mock_send:
        mock_weather.return_value = {"current": {"temp_c": 30, "condition": {"text": "Sunny"}, "humidity": 25, "precip_mm": 0}}
        mock_send.return_value = {"status": "sent"}

        resp = await client.post(
            "/api/advice/request",
            json={"lat": -1.2921, "lon": 36.8219},
        )

    assert resp.status_code == 200
    assert resp.json()["sent"] is True
    assert "recommendation" in resp.json()
    assert mock_send.called


@pytest.mark.asyncio
async def test_advice_request_returns_advice_even_when_sms_fails(client):
    with patch(
        "app.services.weather.weather_service.get_current"
    ) as mock_weather, patch(
        "app.services.africastalking.africastalking_service.send_sms"
    ) as mock_send:
        mock_weather.return_value = {"current": {"temp_c": 22, "condition": {"text": "Rain"}, "humidity": 70, "precip_mm": 5}}
        mock_send.side_effect = RuntimeError("SMS gateway down")

        resp = await client.post(
            "/api/advice/request",
            json={"lat": -1.2921, "lon": 36.8219},
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["sent"] is False
    assert "recommendation" in data
    assert data["sms_error"] == "SMS gateway down"


@pytest.mark.asyncio
async def test_notify_farmer_route_returns_502_on_error(client):
    with patch(
        "app.services.africastalking.africastalking_service.send_sms"
    ) as mock_send:
        mock_send.side_effect = Exception("SMS failed")

        resp = await client.post("/api/notify/farmer?message=Hello")

    assert resp.status_code == 502
    assert resp.json() == {"detail": "SMS failed"}
