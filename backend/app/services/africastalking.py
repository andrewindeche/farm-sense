import logging
from typing import List, Optional

from app.config import settings

try:
    import africastalking
except Exception:  # pragma: no cover - optional dependency in tests
    africastalking = None

logger = logging.getLogger(__name__)

_MAX_SMS_LENGTH = 1600


class AfricasTalkingService:
    def __init__(self) -> None:
        self.username = settings.africastalking_username
        self.api_key = settings.africastalking_api_key
        self.sender_id = settings.africastalking_sender_id
        if africastalking:
            africastalking.initialize(self.username, self.api_key)
            self._sms = africastalking.SMS
        else:
            self._sms = None

    def get_sender_id(self) -> str | None:
        if settings.africastalking_username.lower() == "sandbox":
            return None
        return settings.africastalking_sender_id or None

    def send_sms(self, message: str, to: Optional[List[str] | str] = None) -> dict:
        if not message or not message.strip():
            raise ValueError("message is empty")

        if len(message) > _MAX_SMS_LENGTH:
            logger.warning(
                "Message length (%d chars) exceeds %d — may be truncated",
                len(message),
                _MAX_SMS_LENGTH,
            )

        recipients = []
        if isinstance(to, str):
            recipients = [to]
        elif isinstance(to, list):
            recipients = to
        else:
            recipients = [settings.farmer_phone] if settings.farmer_phone else []

        if not self._sms:
            raise RuntimeError(
                "AfricasTalking SDK not available. "
                "Install 'africastalking' package and configure credentials."
            )

        if not recipients:
            raise ValueError("No recipient phone numbers configured/provided")

        sender_id = self.get_sender_id()
        kwargs = {"sender_id": sender_id} if sender_id else {}
        resp = self._sms.send(message, recipients, **kwargs)
        return resp


africastalking_service = AfricasTalkingService()
