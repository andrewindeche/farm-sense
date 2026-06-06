import logging

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from app.config import settings
from .services.authentication import auth_service
from .services.weather import weather_service
from .services.africastalking import africastalking_service
from .services.crop_advice import crop_advice_service
from .services.pest_disease import pest_disease_service
from .services.harvest_reminder import harvest_reminder_service

app = FastAPI(title="FarmSense API")


class AuthPayload(BaseModel):
    username: str
    password: str


class AdviceRequestPayload(BaseModel):
    lat: float
    lon: float
    use_ai: bool = False
    farmer_phone: str | None = None


def _get_bearer_token(authorization: str | None) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    return parts[1]

@app.get("/")
async def root():
    return {"message": "Fastapi is running!"}

@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/api/auth/register")
async def register(payload: AuthPayload):
    try:
        return auth_service.register(payload.username, payload.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/auth/login")
async def login(payload: AuthPayload):
    try:
        token = auth_service.authenticate(payload.username, payload.password)
        return {"access_token": token, "token_type": "bearer"}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@app.get("/api/auth/me")
async def me(authorization: str | None = Header(None)):
    try:
        token = _get_bearer_token(authorization)
        username = auth_service.validate_token(token)
        return {"username": username}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@app.post("/api/auth/logout")
async def logout(authorization: str | None = Header(None)):
    try:
        token = _get_bearer_token(authorization)
        return auth_service.logout(token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@app.get("/api/weather/current")
async def current_weather(lat: float, lon: float):
    try:
        return await weather_service.get_current(lat, lon)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.get("/api/weather/forecast")
async def weather_forecast(lat: float, lon: float, days: int = 3):
    try:
        return await weather_service.get_forecast(lat, lon, days)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.post("/api/advice/request")
async def request_advice(payload: AdviceRequestPayload):
    try:
        weather = await weather_service.get_current(payload.lat, payload.lon)
    except Exception as e:
        logger.error("Weather fetch failed: %s: %s", type(e).__name__, e)
        raise HTTPException(status_code=502, detail=f"Weather service error: {e}")

    try:
        recommendation = crop_advice_service.suggest(weather)
    except Exception as e:
        logger.error("Crop advice failed: %s: %s", type(e).__name__, e)
        raise HTTPException(status_code=502, detail=f"Crop advice error: {e}")

    try:
        sms_response = africastalking_service.send_sms(recommendation, to=payload.farmer_phone)
        return {
            "recommendation": recommendation,
            "sent": True,
            "sms_sender_id": settings.africastalking_sender_id,
            "sms_response": sms_response,
        }
    except Exception as e:
        logger.warning("SMS send failed (advice still returned): %s: %s", type(e).__name__, e)
        return {
            "recommendation": recommendation,
            "sent": False,
            "sms_error": str(e),
        }


@app.post("/api/advice/pest-disease")
async def pest_disease_advice(payload: AdviceRequestPayload):
    try:
        weather = await weather_service.get_current(payload.lat, payload.lon)
    except Exception as e:
        logger.error("Weather fetch failed: %s: %s", type(e).__name__, e)
        raise HTTPException(status_code=502, detail=f"Weather service error: {e}")

    try:
        alert = pest_disease_service.suggest(weather)
    except Exception as e:
        logger.error("Pest/disease advice failed: %s: %s", type(e).__name__, e)
        raise HTTPException(status_code=502, detail=f"Pest/disease advice error: {e}")

    try:
        sender_id = africastalking_service.get_sender_id()
        sms_response = africastalking_service.send_sms(alert, to=payload.farmer_phone)
        return {
            "alert": alert,
            "sent": True,
            "sms_sender_id": sender_id,
            "sms_response": sms_response,
        }
    except Exception as e:
        logger.warning("SMS send failed (alert still returned): %s: %s", type(e).__name__, e)
        return {
            "alert": alert,
            "sent": False,
            "sms_error": str(e),
        }


@app.post("/api/advice/harvest-reminder")
async def harvest_reminder(payload: AdviceRequestPayload):
    try:
        weather = await weather_service.get_current(payload.lat, payload.lon)
    except Exception as e:
        logger.error("Weather fetch failed: %s: %s", type(e).__name__, e)
        raise HTTPException(status_code=502, detail=f"Weather service error: {e}")

    try:
        reminder = harvest_reminder_service.suggest(weather)
    except Exception as e:
        logger.error("Harvest reminder failed: %s: %s", type(e).__name__, e)
        raise HTTPException(status_code=502, detail=f"Harvest reminder error: {e}")

    try:
        sender_id = africastalking_service.get_sender_id()
        sms_response = africastalking_service.send_sms(reminder, to=payload.farmer_phone)
        return {
            "reminder": reminder,
            "sent": True,
            "sms_sender_id": sender_id,
            "sms_response": sms_response,
        }
    except Exception as e:
        logger.warning("SMS send failed (reminder still returned): %s: %s", type(e).__name__, e)
        return {
            "reminder": reminder,
            "sent": False,
            "sms_error": str(e),
        }


@app.post("/api/notify/farmer")
async def notify_farmer(message: str):
    try:
        return africastalking_service.send_sms(message)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
