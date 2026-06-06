from unittest.mock import AsyncMock, patch

import pytest

from app.services.scheduler import SchedulerService


def test_add_subscriber_adds_new():
    svc = SchedulerService()
    result = svc.add_subscriber(-1.29, 36.82, "+254700000001")
    assert result["status"] == "subscribed"
    assert len(svc.subscribers) == 1


def test_add_subscriber_updates_existing():
    svc = SchedulerService()
    svc.add_subscriber(-1.29, 36.82, "+254700000001")
    result = svc.add_subscriber(-1.30, 36.83, "+254700000001")
    assert result["status"] == "updated"
    assert len(svc.subscribers) == 1
    assert svc.subscribers[0]["lat"] == -1.30


def test_remove_subscriber_removes():
    svc = SchedulerService()
    svc.add_subscriber(-1.29, 36.82, "+254700000001")
    result = svc.remove_subscriber("+254700000001")
    assert result["status"] == "unsubscribed"
    assert len(svc.subscribers) == 0


def test_remove_subscriber_not_found():
    svc = SchedulerService()
    result = svc.remove_subscriber("+254700009999")
    assert result["status"] == "not_found"


def test_subscribers_returns_copy():
    svc = SchedulerService()
    svc.add_subscriber(-1.29, 36.82, "+254700000001")
    subs = svc.subscribers
    subs.clear()
    assert len(svc.subscribers) == 1


@pytest.mark.asyncio
async def test_deliver_all_no_subscribers():
    svc = SchedulerService()
    result = await svc.deliver_all()
    assert result == {"delivered": 0, "total": 0, "results": []}


@pytest.mark.asyncio
async def test_deliver_all_sends_sms_for_each_subscriber():
    svc = SchedulerService()
    svc.add_subscriber(-1.29, 36.82, "+254700000001")

    with patch(
        "app.services.scheduler.weather_service.get_current",
        new=AsyncMock(return_value={"current": {"temp_c": 25, "humidity": 60, "condition": {"text": "Clear"}, "precip_mm": 0}}),
    ), patch(
        "app.services.scheduler.crop_advice_service.suggest",
        return_value="Plant maize.",
    ), patch(
        "app.services.scheduler.pest_disease_service.suggest",
        return_value="Watch for aphids.",
    ), patch(
        "app.services.scheduler.harvest_reminder_service.suggest",
        return_value="Harvest now.",
    ), patch(
        "app.services.scheduler.africastalking_service.send_sms",
        return_value={"status": "sent"},
    ) as mock_sms:
        result = await svc.deliver_all()

    assert result["delivered"] == 1
    assert result["total"] == 1
    assert len(result["results"]) == 1
    r = result["results"][0]
    assert r["phone"] == "+254700000001"
    assert r["sms_status"] == "sent"
    assert "Plant maize." in r["crop_advice"]
    assert "Watch for aphids." in r["pest_alert"]
    assert "Harvest now." in r["harvest_reminder"]
    mock_sms.assert_called_once()
    args, kwargs = mock_sms.call_args
    assert kwargs["to"] == "+254700000001"
    assert "Plant maize." in args[0]
    assert "Watch for aphids." in args[0]
    assert "Harvest now." in args[0]
