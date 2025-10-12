"""DataUpdateCoordinator for WillyWeather."""
import logging
from datetime import timedelta
from typing import Any

import aiohttp
import async_timeout

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import API_BASE_URL, API_TIMEOUT, DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=30)


class WillyWeatherDataCoordinator(DataUpdateCoordinator):
    """Class to manage fetching WillyWeather observational data."""

    def __init__(self, hass: HomeAssistant, api_key: str, station_id: str):
        """Initialize."""
        self.api_key = api_key
        self.station_id = station_id
        
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_observational",
            update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API."""
        url = f"{API_BASE_URL}/{self.api_key}/locations/{self.station_id}/weather.json?observational=true"
        
        try:
            async with async_timeout.timeout(API_TIMEOUT):
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        if response.status != 200:
                            raise UpdateFailed(f"Error fetching data: {response.status}")
                        data = await response.json()
                        return data.get("observational", {})
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Unexpected error: {err}") from err


class WillyWeatherForecastCoordinator(DataUpdateCoordinator):
    """Class to manage fetching WillyWeather forecast data."""

    def __init__(self, hass: HomeAssistant, api_key: str, station_id: str, days: int):
        """Initialize."""
        self.api_key = api_key
        self.station_id = station_id
        self.days = days
        
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_forecast",
            update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API."""
        url = f"{API_BASE_URL}/{self.api_key}/locations/{self.station_id}/weather.json?observational=true&forecasts=weather,rainfall&days={self.days}"
        
        try:
            async with async_timeout.timeout(API_TIMEOUT):
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        if response.status != 200:
                            raise UpdateFailed(f"Error fetching data: {response.status}")
                        data = await response.json()
                        return data
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Unexpected error: {err}") from err


async def async_get_station_id(hass: HomeAssistant, lat: float, lng: float, api_key: str) -> str | None:
    """Get the closest station ID based on coordinates."""
    url = f"{API_BASE_URL}/{api_key}/search.json"
    params = {
        "lat": lat,
        "lng": lng,
        "units": "distance:km",
    }
    
    try:
        async with async_timeout.timeout(API_TIMEOUT):
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        _LOGGER.error("Error finding closest station: %s", response.status)
                        return None
                    data = await response.json()
                    return data.get("location", {}).get("id")
    except Exception as err:
        _LOGGER.error("Error finding closest station: %s", err)
        return None
