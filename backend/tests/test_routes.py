from unittest.mock import AsyncMock, patch

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
async def test_pest_disease_endpoint_returns_alert_and_sends_sms(client):
    with patch(
        "app.services.weather.weather_service.get_current"
    ) as mock_weather, patch(
        "app.services.africastalking.africastalking_service.send_sms"
    ) as mock_send, patch(
        "app.services.africastalking.africastalking_service.get_sender_id"
    ) as mock_sender_id:
        mock_weather.return_value = {"current": {"temp_c": 30, "humidity": 85, "condition": {"text": "Overcast"}, "precip_mm": 0}}
        mock_send.return_value = {"status": "sent"}
        mock_sender_id.return_value = "FARMSENSE"

        resp = await client.post(
            "/api/advice/pest-disease",
            json={"lat": -1.2921, "lon": 36.8219},
        )

    assert resp.status_code == 200
    data = resp.json()
    assert "alert" in data
    assert "leaf spot" in data["alert"].lower()
    assert data["sent"] is True
    assert mock_send.called


@pytest.mark.asyncio
async def test_pest_disease_endpoint_returns_alert_even_when_sms_fails(client):
    with patch(
        "app.services.weather.weather_service.get_current"
    ) as mock_weather, patch(
        "app.services.africastalking.africastalking_service.send_sms"
    ) as mock_send:
        mock_weather.return_value = {"current": {"temp_c": 30, "humidity": 85, "condition": {"text": "Overcast"}, "precip_mm": 0}}
        mock_send.side_effect = RuntimeError("SMS gateway down")

        resp = await client.post(
            "/api/advice/pest-disease",
            json={"lat": -1.2921, "lon": 36.8219},
        )

    assert resp.status_code == 200
    data = resp.json()
    assert "alert" in data
    assert data["sent"] is False
    assert data["sms_error"] == "SMS gateway down"


@pytest.mark.asyncio
async def test_pest_disease_endpoint_returns_502_on_weather_error(client):
    with patch(
        "app.services.weather.weather_service.get_current"
    ) as mock_weather:
        mock_weather.side_effect = Exception("Weather API down")

        resp = await client.post(
            "/api/advice/pest-disease",
            json={"lat": -1.2921, "lon": 36.8219},
        )

    assert resp.status_code == 502


@pytest.mark.asyncio
async def test_harvest_reminder_endpoint_returns_reminder_and_sends_sms(client):
    with patch(
        "app.services.weather.weather_service.get_current"
    ) as mock_weather, patch(
        "app.services.africastalking.africastalking_service.send_sms"
    ) as mock_send, patch(
        "app.services.africastalking.africastalking_service.get_sender_id"
    ) as mock_sender_id:
        mock_weather.return_value = {"current": {"temp_c": 24, "humidity": 45, "condition": {"text": "Clear"}, "precip_mm": 0}}
        mock_send.return_value = {"status": "sent"}
        mock_sender_id.return_value = "FARMSENSE"

        resp = await client.post(
            "/api/advice/harvest-reminder",
            json={"lat": -1.2921, "lon": 36.8219},
        )

    assert resp.status_code == 200
    data = resp.json()
    assert "reminder" in data
    assert "favorable" in data["reminder"].lower()
    assert data["sent"] is True


@pytest.mark.asyncio
async def test_harvest_reminder_endpoint_returns_alert_even_when_sms_fails(client):
    with patch(
        "app.services.weather.weather_service.get_current"
    ) as mock_weather, patch(
        "app.services.africastalking.africastalking_service.send_sms"
    ) as mock_send:
        mock_weather.return_value = {"current": {"temp_c": 24, "humidity": 45, "condition": {"text": "Clear"}, "precip_mm": 0}}
        mock_send.side_effect = RuntimeError("SMS gateway down")

        resp = await client.post(
            "/api/advice/harvest-reminder",
            json={"lat": -1.2921, "lon": 36.8219},
        )

    assert resp.status_code == 200
    data = resp.json()
    assert "reminder" in data
    assert data["sent"] is False
    assert data["sms_error"] == "SMS gateway down"


@pytest.mark.asyncio
async def test_harvest_reminder_endpoint_returns_502_on_weather_error(client):
    with patch(
        "app.services.weather.weather_service.get_current"
    ) as mock_weather:
        mock_weather.side_effect = Exception("Weather API down")

        resp = await client.post(
            "/api/advice/harvest-reminder",
            json={"lat": -1.2921, "lon": 36.8219},
        )

    assert resp.status_code == 502


@pytest.mark.asyncio
async def test_scheduler_subscribe_and_list(client):
    resp = await client.post(
        "/api/scheduler/subscribe",
        json={"lat": -1.2921, "lon": 36.8219, "phone": "+254700000001"},
    )
    assert resp.status_code == 200
    assert resp.json() == {"lat": -1.2921, "lon": 36.8219, "phone": "+254700000001", "status": "subscribed"}

    list_resp = await client.get("/api/scheduler/subscribers")
    assert list_resp.status_code == 200
    phones = [s["phone"] for s in list_resp.json()["subscribers"]]
    assert "+254700000001" in phones


@pytest.mark.asyncio
async def test_scheduler_subscribe_update_existing(client):
    await client.post(
        "/api/scheduler/subscribe",
        json={"lat": -1.29, "lon": 36.82, "phone": "+254700000001"},
    )
    resp = await client.post(
        "/api/scheduler/subscribe",
        json={"lat": -1.30, "lon": 36.83, "phone": "+254700000001"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "updated"


@pytest.mark.asyncio
async def test_scheduler_unsubscribe(client):
    await client.post(
        "/api/scheduler/subscribe",
        json={"lat": -1.2921, "lon": 36.8219, "phone": "+254700000001"},
    )
    resp = await client.post(
        "/api/scheduler/unsubscribe",
        json={"phone": "+254700000001"},
    )
    assert resp.status_code == 200
    assert resp.json() == {"phone": "+254700000001", "status": "unsubscribed"}


@pytest.mark.asyncio
async def test_scheduler_unsubscribe_not_found(client):
    resp = await client.post(
        "/api/scheduler/unsubscribe",
        json={"phone": "+254700009999"},
    )
    assert resp.status_code == 200
    assert resp.json() == {"phone": "+254700009999", "status": "not_found"}


@pytest.mark.asyncio
async def test_scheduler_deliver_now(client):
    await client.post(
        "/api/scheduler/subscribe",
        json={"lat": -1.2921, "lon": 36.8219, "phone": "+254700000001"},
    )
    with patch(
        "app.services.scheduler.weather_service.get_current",
        new=AsyncMock(return_value={"current": {"temp_c": 25, "humidity": 60, "condition": {"text": "Clear"}, "precip_mm": 0}}),
    ), patch(
        "app.services.scheduler.crop_advice_service.suggest",
        return_value="Crop advice.",
    ), patch(
        "app.services.scheduler.pest_disease_service.suggest",
        return_value="Pest alert.",
    ), patch(
        "app.services.scheduler.harvest_reminder_service.suggest",
        return_value="Harvest reminder.",
    ), patch(
        "app.services.scheduler.africastalking_service.send_sms",
        return_value={"status": "sent"},
    ):
        resp = await client.post("/api/scheduler/deliver-now")

    assert resp.status_code == 200
    data = resp.json()
    assert data["delivered"] == 1
    assert data["total"] == 1
    assert len(data["results"]) == 1
    assert data["results"][0]["phone"] == "+254700000001"
    assert data["results"][0]["sms_status"] == "sent"


@pytest.mark.asyncio
async def test_notify_farmer_route_returns_502_on_error(client):
    with patch(
        "app.services.africastalking.africastalking_service.send_sms"
    ) as mock_send:
        mock_send.side_effect = Exception("SMS failed")

        resp = await client.post("/api/notify/farmer?message=Hello")

    assert resp.status_code == 502
    assert resp.json() == {"detail": "SMS failed"}


@pytest.mark.asyncio
async def test_auth_register_empty_username(client):
    resp = await client.post(
        "/api/auth/register",
        json={"username": "", "password": "strongpass"},
    )
    assert resp.status_code == 400
    assert "required" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_auth_register_whitespace_username(client):
    resp = await client.post(
        "/api/auth/register",
        json={"username": "   ", "password": "strongpass"},
    )
    assert resp.status_code == 400
    assert "required" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_auth_register_empty_password(client):
    resp = await client.post(
        "/api/auth/register",
        json={"username": "farmer99", "password": ""},
    )
    assert resp.status_code == 400
    assert "required" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_auth_login_empty_credentials(client):
    resp = await client.post(
        "/api/auth/login",
        json={"username": "", "password": ""},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_auth_me_missing_token(client):
    resp = await client.get("/api/auth/me")
    assert resp.status_code == 401
    assert "missing" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_auth_me_invalid_token(client):
    resp = await client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalidtoken123"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_subscribe_invalid_phone(client):
    resp = await client.post(
        "/api/scheduler/subscribe",
        json={"lat": -1.29, "lon": 36.82, "phone": "not-a-phone"},
    )
    assert resp.status_code == 400
    assert "phone" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_subscribe_empty_phone(client):
    resp = await client.post(
        "/api/scheduler/subscribe",
        json={"lat": -1.29, "lon": 36.82, "phone": ""},
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_subscribe_invalid_lat(client):
    resp = await client.post(
        "/api/scheduler/subscribe",
        json={"lat": 200, "lon": 36.82, "phone": "+254700000001"},
    )
    assert resp.status_code == 400
    assert "lat" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_subscribe_invalid_lon(client):
    resp = await client.post(
        "/api/scheduler/subscribe",
        json={"lat": -1.29, "lon": 500, "phone": "+254700000001"},
    )
    assert resp.status_code == 400
    assert "lon" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_subscribe_duplicate_phone(client):
    resp1 = await client.post(
        "/api/scheduler/subscribe",
        json={"lat": -1.29, "lon": 36.82, "phone": "+254700000001"},
    )
    assert resp1.status_code == 200

    resp2 = await client.post(
        "/api/scheduler/subscribe",
        json={"lat": -1.29, "lon": 36.82, "phone": "+254700000001"},
    )
    assert resp2.status_code == 200
    assert resp2.json()["status"] == "updated"


@pytest.mark.asyncio
async def test_rate_limit_exceeded_returns_429(client):
    for _ in range(4):
        resp = await client.post("/api/scheduler/deliver-now")
        if resp.status_code == 429:
            assert "limit" in resp.text.lower()
            return
    pytest.fail("Expected 429 after exceeding rate limit")
