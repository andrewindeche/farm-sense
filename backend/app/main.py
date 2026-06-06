import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from .services.authentication import auth_service
from .services.weather import weather_service
from .services.africastalking import africastalking_service
from .services.crop_advice import crop_advice_service
from .services.pest_disease import pest_disease_service
from .services.harvest_reminder import harvest_reminder_service
from .database import init_db
from .services.scheduler import scheduler_service


limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app):
    await init_db()
    await scheduler_service.start()
    yield
    scheduler_service.stop()


app = FastAPI(title="FarmSense API", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)


class AuthPayload(BaseModel):
    username: str
    password: str


class AdviceRequestPayload(BaseModel):
    lat: float
    lon: float
    use_ai: bool = False
    farmer_phone: str | None = None


class SubscribePayload(BaseModel):
    lat: float
    lon: float
    phone: str


class UnsubscribePayload(BaseModel):
    phone: str


def _get_bearer_token(authorization: str | None) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    return parts[1]

@app.get("/")
@limiter.limit("100/minute")
async def root(request: Request):
    return {"message": "Fastapi is running!"}


@app.get("/health")
@limiter.limit("100/minute")
async def health(request: Request):
    return {"status": "ok"}


@app.post("/api/auth/register")
@limiter.limit("10/minute")
async def register(request: Request, payload: AuthPayload):
    try:
        return await auth_service.register(payload.username, payload.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/auth/login")
@limiter.limit("20/minute")
async def login(request: Request, payload: AuthPayload):
    try:
        token = await auth_service.authenticate(payload.username, payload.password)
        return {"access_token": token, "token_type": "bearer"}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@app.get("/api/auth/me")
@limiter.limit("30/minute")
async def me(request: Request, authorization: str | None = Header(None)):
    try:
        token = _get_bearer_token(authorization)
        username = await auth_service.validate_token(token)
        return {"username": username}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@app.post("/api/auth/logout")
@limiter.limit("30/minute")
async def logout(request: Request, authorization: str | None = Header(None)):
    try:
        token = _get_bearer_token(authorization)
        return await auth_service.logout(token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@app.get("/api/weather/current")
@limiter.limit("30/minute")
async def current_weather(request: Request, lat: float, lon: float):
    try:
        return await weather_service.get_current(lat, lon)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.get("/api/weather/forecast")
@limiter.limit("30/minute")
async def weather_forecast(request: Request, lat: float, lon: float, days: int = 3):
    try:
        return await weather_service.get_forecast(lat, lon, days)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.post("/api/advice/request")
@limiter.limit("10/minute")
async def request_advice(request: Request, payload: AdviceRequestPayload):
    try:
        weather = await weather_service.get_current(payload.lat, payload.lon)
    except Exception as e:
        logger.error("Weather fetch failed: %s: %s", type(e).__name__, e)
        raise HTTPException(status_code=502, detail=f"Weather service error: {e}")

    recommendation = await crop_advice_service.suggest(weather, use_ai=payload.use_ai)

    try:
        sender_id = africastalking_service.get_sender_id()
        sms_response = africastalking_service.send_sms(recommendation, to=payload.farmer_phone)
        return {
            "recommendation": recommendation,
            "sent": True,
            "sms_sender_id": sender_id,
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
@limiter.limit("10/minute")
async def pest_disease_advice(request: Request, payload: AdviceRequestPayload):
    try:
        weather = await weather_service.get_current(payload.lat, payload.lon)
    except Exception as e:
        logger.error("Weather fetch failed: %s: %s", type(e).__name__, e)
        raise HTTPException(status_code=502, detail=f"Weather service error: {e}")

    alert = await pest_disease_service.suggest(weather, use_ai=payload.use_ai)

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
@limiter.limit("10/minute")
async def harvest_reminder(request: Request, payload: AdviceRequestPayload):
    try:
        weather = await weather_service.get_current(payload.lat, payload.lon)
    except Exception as e:
        logger.error("Weather fetch failed: %s: %s", type(e).__name__, e)
        raise HTTPException(status_code=502, detail=f"Weather service error: {e}")

    reminder = await harvest_reminder_service.suggest(weather, use_ai=payload.use_ai)

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


@app.get("/api/scheduler/subscribers")
@limiter.limit("30/minute")
async def list_subscribers(request: Request):
    return {"subscribers": await scheduler_service.get_subscribers()}


@app.post("/api/scheduler/subscribe")
@limiter.limit("20/minute")
async def subscribe(request: Request, payload: SubscribePayload):
    try:
        return await scheduler_service.add_subscriber(payload.lat, payload.lon, payload.phone)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/scheduler/unsubscribe")
@limiter.limit("10/minute")
async def unsubscribe(request: Request, payload: UnsubscribePayload):
    try:
        return await scheduler_service.remove_subscriber(payload.phone)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/scheduler/deliver-now")
@limiter.limit("3/minute")
async def deliver_now(request: Request):
    try:
        return await scheduler_service.deliver_all()
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.post("/api/notify/farmer")
@limiter.limit("5/minute")
async def notify_farmer(request: Request, message: str):
    try:
        return africastalking_service.send_sms(message)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
