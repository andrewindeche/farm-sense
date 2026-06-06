from fastapi import FastAPI, HTTPException

from .services.weather import weather_service
from .services.africastalking import africastalking_service

app = FastAPI(title="FarmSense API")

@app.get("/")
async def root():
    return {"message": "Fastapi is running!"}

@app.get("/health")
async def health():
    return {"status": "ok"}


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


@app.post("/api/notify/farmer")
async def notify_farmer(message: str):
    try:
        return africastalking_service.send_sms(message)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
