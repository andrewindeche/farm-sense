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
async def test_get_current_calls_correct_endpoint(service):
    with patch("app.services.weather.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get.return_value = (
            _mock_response({"current": {"temp_c": 25}})
        )

        result = await service.get_current("Nairobi")

    assert result == {"current": {"temp_c": 25}}
    mock_client.return_value.__aenter__.return_value.get.assert_called_once_with(
        "/current.json", params={"key": service.api_key, "q": "Nairobi"}
    )


@pytest.mark.asyncio
async def test_get_forecast_calls_correct_endpoint(service):
    with patch("app.services.weather.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get.return_value = (
            _mock_response({"forecast": {"forecastday": []}})
        )

        result = await service.get_forecast("Nairobi", days=5)

    assert result == {"forecast": {"forecastday": []}}
    mock_client.return_value.__aenter__.return_value.get.assert_called_once_with(
        "/forecast.json",
        params={"key": service.api_key, "q": "Nairobi", "days": 5},
    )


@pytest.mark.asyncio
async def test_get_forecast_defaults_to_3_days(service):
    with patch("app.services.weather.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get.return_value = (
            _mock_response({"forecast": {}})
        )

        await service.get_forecast("Nairobi")

    mock_client.return_value.__aenter__.return_value.get.assert_called_once_with(
        "/forecast.json",
        params={"key": service.api_key, "q": "Nairobi", "days": 3},
    )


@pytest.mark.asyncio
async def test_raises_on_http_error(service):
    with patch("app.services.weather.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get.side_effect = Exception(
            "API error"
        )

        with pytest.raises(Exception, match="API error"):
            await service.get_current("Nairobi")
