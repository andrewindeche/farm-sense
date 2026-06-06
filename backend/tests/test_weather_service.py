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

        result = await service.get_current(-1.2921, 36.8219)

    assert result == {"current": {"temp_c": 25}}
    mock_client.assert_called_once_with(
        base_url=service.base_url,
        headers={"Authorization": f"Bearer {service.api_key}"},
    )
    mock_client.return_value.__aenter__.return_value.get.assert_called_once_with(
        "/current",
        params={"lat": -1.2921, "lon": 36.8219},
    )


@pytest.mark.asyncio
async def test_get_forecast_calls_correct_endpoint(service):
    with patch("app.services.weather.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get.return_value = (
            _mock_response({"forecast": {"forecastday": []}})
        )

        result = await service.get_forecast(-1.2921, 36.8219, days=5)

    assert result == {"forecast": {"forecastday": []}}
    mock_client.assert_called_once_with(
        base_url=service.base_url,
        headers={"Authorization": f"Bearer {service.api_key}"},
    )
    mock_client.return_value.__aenter__.return_value.get.assert_called_once_with(
        "/forecast",
        params={"lat": -1.2921, "lon": 36.8219, "days": 5},
    )


@pytest.mark.asyncio
async def test_get_forecast_defaults_to_3_days(service):
    with patch("app.services.weather.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get.return_value = (
            _mock_response({"forecast": {}})
        )

        await service.get_forecast(-1.2921, 36.8219)

    mock_client.assert_called_once_with(
        base_url=service.base_url,
        headers={"Authorization": f"Bearer {service.api_key}"},
    )
    mock_client.return_value.__aenter__.return_value.get.assert_called_once_with(
        "/forecast",
        params={"lat": -1.2921, "lon": 36.8219, "days": 3},
    )


@pytest.mark.asyncio
async def test_get_current_caches_same_coordinates(service):
    with patch("app.services.weather.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get.return_value = (
            _mock_response({"current": {"temp_c": 25}})
        )

        result1 = await service.get_current(-1.2921, 36.8219)
        assert result1 == {"current": {"temp_c": 25}}
        assert mock_client.return_value.__aenter__.return_value.get.call_count == 1

        result2 = await service.get_current(-1.2921, 36.8219)
        assert result2 == {"current": {"temp_c": 25}}
        assert mock_client.return_value.__aenter__.return_value.get.call_count == 1


@pytest.mark.asyncio
async def test_get_forecast_caches_same_coordinates_and_days(service):
    with patch("app.services.weather.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get.return_value = (
            _mock_response({"forecast": {}})
        )

        result1 = await service.get_forecast(-1.2921, 36.8219, days=3)
        assert result1 == {"forecast": {}}
        assert mock_client.return_value.__aenter__.return_value.get.call_count == 1

        result2 = await service.get_forecast(-1.2921, 36.8219, days=3)
        assert result2 == {"forecast": {}}
        assert mock_client.return_value.__aenter__.return_value.get.call_count == 1


@pytest.mark.asyncio
async def test_get_current_different_coordinates_do_not_share_cache(service):
    with patch("app.services.weather.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get.return_value = (
            _mock_response({"current": {"temp_c": 25}})
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
