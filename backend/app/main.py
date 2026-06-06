from fastapi import FastAPI, HTTPException

from .services.weather import weather_service
from .services.africastalking import africastalking_service

app = FastAPI(title="FarmSense API")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/api/weather/current")
async def current_weather(location: str = "Nairobi"):
    try:
        return await weather_service.get_current(location)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.get("/api/weather/forecast")
async def weather_forecast(location: str = "Nairobi", days: int = 3):
    try:
        return await weather_service.get_forecast(location, days)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.post("/api/notify/farmer")
async def notify_farmer(message: str):
    try:
        return africastalking_service.send_sms(message)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
