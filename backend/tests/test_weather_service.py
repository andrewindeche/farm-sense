from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.weather import WeatherService


@pytest.fixture
def service():
    return WeatherService()


def _mock_response(json_data):
    mock = MagicMock()
    mock.json.return_value = json_data
    return mock


@pytest.mark.asyncio
async def test_get_current_returns_mapped_open_meteo_response(service):
    om_response = {
        "current": {
            "temperature_2m": 25.0,
            "relative_humidity_2m": 60,
            "precipitation": 0.0,
            "wind_speed_10m": 15.0,
            "weather_code": 0,
        }
    }
    with patch("app.services.weather.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get.return_value = (
            _mock_response(om_response)
        )

        result = await service.get_current(-1.2921, 36.8219)

    assert result == {
        "current": {
            "temp_c": 25.0,
            "humidity": 60,
            "precip_mm": 0.0,
            "wind_kph": 15.0,
            "condition": {"text": "Clear"},
        }
    }
    mock_client.assert_called_once_with(base_url=service.base_url)
    mock_client.return_value.__aenter__.return_value.get.assert_called_once_with(
        "/forecast",
        params={
            "latitude": -1.2921,
            "longitude": 36.8219,
            "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,weather_code",
        },
    )


@pytest.mark.asyncio
async def test_get_forecast_maps_daily_to_forecastday(service):
    om_response = {
        "daily": {
            "time": ["2025-01-01", "2025-01-02"],
            "temperature_2m_max": [28.0, 26.0],
            "temperature_2m_min": [18.0, 17.0],
            "precipitation_sum": [0.0, 2.5],
            "weather_code": [0, 61],
        }
    }
    with patch("app.services.weather.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get.return_value = (
            _mock_response(om_response)
        )

        result = await service.get_forecast(-1.2921, 36.8219, days=5)

    assert result == {
        "forecast": {
            "forecastday": [
                {
                    "date": "2025-01-01",
                    "day": {
                        "maxtemp_c": 28.0,
                        "mintemp_c": 18.0,
                        "totalprecip_mm": 0.0,
                        "condition": {"text": "Clear"},
                    },
                },
                {
                    "date": "2025-01-02",
                    "day": {
                        "maxtemp_c": 26.0,
                        "mintemp_c": 17.0,
                        "totalprecip_mm": 2.5,
                        "condition": {"text": "Slight rain"},
                    },
                },
            ]
        }
    }
    mock_client.assert_called_once_with(base_url=service.base_url)
    mock_client.return_value.__aenter__.return_value.get.assert_called_once_with(
        "/forecast",
        params={
            "latitude": -1.2921,
            "longitude": 36.8219,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code",
            "forecast_days": 5,
        },
    )


@pytest.mark.asyncio
async def test_get_forecast_defaults_to_3_days(service):
    om_response = {"daily": {"time": [], "temperature_2m_max": [], "temperature_2m_min": [], "precipitation_sum": [], "weather_code": []}}
    with patch("app.services.weather.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get.return_value = (
            _mock_response(om_response)
        )

        await service.get_forecast(-1.2921, 36.8219)

    mock_client.assert_called_once_with(base_url=service.base_url)
    mock_client.return_value.__aenter__.return_value.get.assert_called_once_with(
        "/forecast",
        params={
            "latitude": -1.2921,
            "longitude": 36.8219,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code",
            "forecast_days": 3,
        },
    )


@pytest.mark.asyncio
async def test_get_current_caches_same_coordinates(service):
    om_response = {
        "current": {
            "temperature_2m": 25.0,
            "relative_humidity_2m": 60,
            "precipitation": 0.0,
            "wind_speed_10m": 15.0,
            "weather_code": 0,
        }
    }
    expected = {
        "current": {
            "temp_c": 25.0,
            "humidity": 60,
            "precip_mm": 0.0,
            "wind_kph": 15.0,
            "condition": {"text": "Clear"},
        }
    }
    with patch("app.services.weather.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get.return_value = (
            _mock_response(om_response)
        )

        result1 = await service.get_current(-1.2921, 36.8219)
        assert result1 == expected
        assert mock_client.return_value.__aenter__.return_value.get.call_count == 1

        result2 = await service.get_current(-1.2921, 36.8219)
        assert result2 == expected
        assert mock_client.return_value.__aenter__.return_value.get.call_count == 1


@pytest.mark.asyncio
async def test_get_forecast_caches_same_coordinates_and_days(service):
    om_response = {"daily": {"time": [], "temperature_2m_max": [], "temperature_2m_min": [], "precipitation_sum": [], "weather_code": []}}
    with patch("app.services.weather.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get.return_value = (
            _mock_response(om_response)
        )

        result1 = await service.get_forecast(-1.2921, 36.8219, days=3)
        assert result1 == {"forecast": {"forecastday": []}}
        assert mock_client.return_value.__aenter__.return_value.get.call_count == 1

        result2 = await service.get_forecast(-1.2921, 36.8219, days=3)
        assert result2 == {"forecast": {"forecastday": []}}
        assert mock_client.return_value.__aenter__.return_value.get.call_count == 1


@pytest.mark.asyncio
async def test_get_current_different_coordinates_do_not_share_cache(service):
    om_response = {
        "current": {
            "temperature_2m": 25.0,
            "relative_humidity_2m": 60,
            "precipitation": 0.0,
            "wind_speed_10m": 15.0,
            "weather_code": 0,
        }
    }
    with patch("app.services.weather.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get.return_value = (
            _mock_response(om_response)
        )

        await service.get_current(-1.2921, 36.8219)
        await service.get_current(-1.3000, 36.8000)

        assert mock_client.return_value.__aenter__.return_value.get.call_count == 2


@pytest.mark.asyncio
async def test_raises_on_http_error(service):
    with patch("app.services.weather.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get.side_effect = Exception(
            "API error"
        )

        with pytest.raises(Exception, match="API error"):
            await service.get_current(-1.2921, 36.8219)
