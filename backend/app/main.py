from fastapi import FastAPI, HTTPException

from .services.weather import weather_service

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
