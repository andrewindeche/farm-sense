from unittest.mock import MagicMock, patch

import pytest

from app.config import settings
from app.services.africastalking import AfricasTalkingService


def test_send_sms_raises_when_sdk_is_missing(monkeypatch):
    monkeypatch.setattr(
        "app.services.africastalking.africastalking",
        None,
    )
    service = AfricasTalkingService()

    with pytest.raises(RuntimeError, match="AfricasTalking SDK not available"):
        service.send_sms("Hello")


def test_send_sms_raises_when_no_recipient_is_available(monkeypatch):
    fake_sdk = MagicMock()
    fake_sms = MagicMock()
    fake_sdk.SMS = fake_sms
    monkeypatch.setattr("app.services.africastalking.africastalking", fake_sdk)
    monkeypatch.setattr(settings, "farmer_phone", "")

    service = AfricasTalkingService()

    with pytest.raises(ValueError, match="No recipient phone numbers configured/provided"):
        service.send_sms("Hello")


def test_send_sms_uses_configured_sender_and_string_recipient(monkeypatch):
    fake_sdk = MagicMock()
    fake_sms = MagicMock()
    fake_sdk.SMS = fake_sms
    monkeypatch.setattr("app.services.africastalking.africastalking", fake_sdk)
    monkeypatch.setattr(settings, "africastalking_username", "live_user")
    monkeypatch.setattr(settings, "farmer_phone", "+254700000000")

    service = AfricasTalkingService()
    result = service.send_sms("Hello world", to="+254711111111")

    fake_sms.send.assert_called_once_with(
        "Hello world",
        ["+254711111111"],
        sender_id=service.sender_id,
    )
    assert result == fake_sms.send.return_value


def test_send_sms_omits_sender_id_when_using_sandbox_username(monkeypatch):
    fake_sdk = MagicMock()
    fake_sms = MagicMock()
    fake_sdk.SMS = fake_sms
    monkeypatch.setattr("app.services.africastalking.africastalking", fake_sdk)
    monkeypatch.setattr(settings, "africastalking_username", "sandbox")
    monkeypatch.setattr(settings, "africastalking_sender_id", "FARMSENSE")
    monkeypatch.setattr(settings, "farmer_phone", "+254700000000")

    service = AfricasTalkingService()
    result = service.send_sms("Hello sandbox", to="+254711111111")

    fake_sms.send.assert_called_once_with(
        "Hello sandbox",
        ["+254711111111"],
    )
    assert result == fake_sms.send.return_value


def test_send_sms_uses_recipient_list(monkeypatch):
    fake_sdk = MagicMock()
    fake_sms = MagicMock()
    fake_sdk.SMS = fake_sms
    monkeypatch.setattr("app.services.africastalking.africastalking", fake_sdk)
    monkeypatch.setattr(settings, "africastalking_username", "live_user")
    monkeypatch.setattr(settings, "farmer_phone", "+254700000000")

    service = AfricasTalkingService()
    result = service.send_sms(
        "Hello farmers",
        to=["+254711111111", "+254722222222"],
    )

    fake_sms.send.assert_called_once_with(
        "Hello farmers",
        ["+254711111111", "+254722222222"],
        sender_id=service.sender_id,
    )
    assert result == fake_sms.send.return_value
