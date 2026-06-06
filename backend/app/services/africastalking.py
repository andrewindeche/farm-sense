from typing import List, Optional

from app.config import settings

try:
    import africastalking
except Exception:  # pragma: no cover - optional dependency in tests
    africastalking = None


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

    def send_sms(self, message: str, to: Optional[List[str] | str] = None) -> dict:
        recipients = []
        if isinstance(to, str):
            recipients = [to]
        elif isinstance(to, list):
            recipients = to
        else:
            recipients = [settings.farmer_phone] if settings.farmer_phone else []

        if not self._sms:
            raise RuntimeError("AfricasTalking SDK not available. Install 'africastalking' package and configure credentials.")

        if not recipients:
            raise ValueError("No recipient phone numbers configured/provided")

        if settings.africastalking_username.lower() == "sandbox":
            resp = self._sms.send(message, recipients)
        else:
            resp = self._sms.send(message, recipients, sender_id=settings.africastalking_sender_id)
        return resp


africastalking_service = AfricasTalkingService()
