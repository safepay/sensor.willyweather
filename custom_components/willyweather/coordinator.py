"""DataUpdateCoordinator for WillyWeather."""
from __future__ import annotations

import asyncio
from datetime import timedelta
import logging
from typing import TYPE_CHECKING, Any

import aiohttp
import async_timeout

from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import (
    API_BASE_URL,
    API_TIMEOUT,
    CONF_FORECAST_DAYS,
    CONF_FORECAST_RAINFALL,
    CONF_FORECAST_SUNRISESUNSET,
    CONF_FORECAST_TIDES,
    CONF_FORECAST_UV,
    CONF_STATION_ID,
    DEFAULT_FORECAST_DAYS,
    DOMAIN,
    UPDATE_INTERVAL_OBSERVATION,
)

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry

_LOGGER = logging.getLogger(__name__)


class WillyWeatherDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching WillyWeather data from the API."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self.hass = hass
        self.entry = entry
        self.api_key = entry.data[CONF_API_KEY]
        self.station_id = entry.data[CONF_STATION_ID]
        self._session = aiohttp.ClientSession()

        _LOGGER.debug(
            "Initializing WillyWeather coordinator for station %s",
            self.station_id,
        )

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{self.station_id}",
            update_interval=timedelta(minutes=UPDATE_INTERVAL_OBSERVATION),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API."""
        _LOGGER.debug("Updating WillyWeather data for station %s", self.station_id)
        
        try:
            # Build forecast parameters based on enabled options
            forecast_types = ["weather"]  # Always include weather
            
            if self.entry.options.get(CONF_FORECAST_RAINFALL, False):
                forecast_types.append("rainfall")
            if self.entry.options.get(CONF_FORECAST_UV, False):
                forecast_types.append("uv")
            if self.entry.options.get(CONF_FORECAST_SUNRISESUNSET, False):
                forecast_types.append("sunrisesunset")
            if self.entry.options.get(CONF_FORECAST_TIDES, False):
                forecast_types.append("tides")
            
            # Get number of forecast days
            forecast_days = self.entry.options.get(CONF_FORECAST_DAYS, DEFAULT_FORECAST_DAYS)
            
            # Fetch observational and forecast data
            observational_data = await self._fetch_observational_data()
            forecast_data = await self._fetch_forecast_data(forecast_types, forecast_days)

            _LOGGER.debug("Successfully fetched data from WillyWeather API")

            return {
                "observational": observational_data,
                "forecast": forecast_data,
                "last_update": dt_util.utcnow(),
            }

        except aiohttp.ClientResponseError as err:
            _LOGGER.error(
                "HTTP error %s when fetching data: %s",
                err.status,
                err.message,
            )
            raise UpdateFailed(f"HTTP error {err.status}: {err.message}") from err
        except aiohttp.ClientError as err:
            _LOGGER.error("Network error when fetching data: %s", err)
            raise UpdateFailed(f"Network error: {err}") from err
        except Exception as err:
            _LOGGER.error("Unexpected error when fetching data: %s", err, exc_info=True)
            raise UpdateFailed(f"Unexpected error: {err}") from err

    async def _fetch_observational_data(self) -> dict[str, Any]:
        """Fetch observational weather data."""
        url = f"{API_BASE_URL}/{self.api_key}/locations/{self.station_id}/weather.json"
        params = {
            "observational": "true",
            "units": "distance:km,temperature:c,amount:mm,speed:km/h,pressure:hpa,tideHeight:m,swellHeight:m",
        }

        _LOGGER.debug("Fetching observational data from: %s with params: %s", url, params)

        try:
            async with async_timeout.timeout(API_TIMEOUT):
                async with self._session.get(url, params=params) as response:
                    response_text = await response.text()
                    
                    if response.status == 401:
                        _LOGGER.error("API key is invalid (401 Unauthorized)")
                        raise UpdateFailed("Invalid API key")
                    elif response.status == 403:
                        _LOGGER.error("API key doesn't have access (403 Forbidden)")
                        raise UpdateFailed("API key access denied")
                    elif response.status == 404:
                        _LOGGER.error("Station ID %s not found (404)", self.station_id)
                        raise UpdateFailed(f"Station ID {self.station_id} not found")
                    elif response.status == 400:
                        _LOGGER.error("Bad request (400): %s", response_text[:500])
                        raise UpdateFailed(f"Bad request: {response_text[:200]}")
                    elif response.status != 200:
                        _LOGGER.error(
                            "Error fetching observational data: HTTP %s - %s",
                            response.status,
                            response_text[:500],
                        )
                        raise UpdateFailed(f"HTTP error {response.status}")
                    
                    data = await response.json()
                    _LOGGER.debug("Observational data structure: %s", data.keys() if isinstance(data, dict) else type(data))
                    
                    obs_data = data.get("observational", {})
                    if not obs_data:
                        _LOGGER.warning("No observational data in response")
                    else:
                        _LOGGER.debug("Observational sub-keys: %s", obs_data.keys())
                    
                    return obs_data
                    
        except asyncio.TimeoutError as err:
            _LOGGER.error("Timeout fetching observational data")
            raise UpdateFailed("Request timeout") from err
        except aiohttp.ClientError as err:
            _LOGGER.error("Network error fetching observational data: %s", err)
            raise UpdateFailed(f"Network error: {err}") from err

    async def _fetch_forecast_data(self, forecast_types: list[str], days: int) -> dict[str, Any]:
        """Fetch forecast weather data."""
        url = f"{API_BASE_URL}/{self.api_key}/locations/{self.station_id}/weather.json"
        params = {
            "forecasts": ",".join(forecast_types),
            "days": str(days),
            "units": "distance:km,temperature:c,amount:mm,speed:km/h,pressure:hpa,tideHeight:m,swellHeight:m",
        }

        _LOGGER.debug("Fetching forecast data from: %s with params: %s", url, params)

        try:
            async with async_timeout.timeout(API_TIMEOUT):
                async with self._session.get(url, params=params) as response:
                    response_text = await response.text()
                    
                    if response.status == 401:
                        _LOGGER.error("API key is invalid (401 Unauthorized)")
                        raise UpdateFailed("Invalid API key")
                    elif response.status == 403:
                        _LOGGER.error("API key doesn't have access (403 Forbidden)")
                        raise UpdateFailed("API key access denied")
                    elif response.status == 404:
                        _LOGGER.error("Station ID %s not found (404)", self.station_id)
                        raise UpdateFailed(f"Station ID {self.station_id} not found")
                    elif response.status == 400:
                        _LOGGER.error("Bad request (400): %s", response_text[:500])
                        raise UpdateFailed(f"Bad request: {response_text[:200]}")
                    elif response.status != 200:
                        _LOGGER.error(
                            "Error fetching forecast data: HTTP %s - %s",
                            response.status,
                            response_text[:500],
                        )
                        raise UpdateFailed(f"HTTP error {response.status}")
                    
                    data = await response.json()
                    _LOGGER.debug("Forecast data structure: %s", data.keys() if isinstance(data, dict) else type(data))
                    
                    return {
                        "location": data.get("location", {}),
                        "forecasts": data.get("forecasts", {}),
                    }
                    
        except asyncio.TimeoutError as err:
            _LOGGER.error("Timeout fetching forecast data")
            raise UpdateFailed("Request timeout") from err
        except aiohttp.ClientError as err:
            _LOGGER.error("Network error fetching forecast data: %s", err)
            raise UpdateFailed(f"Network error: {err}") from err

    async def async_shutdown(self) -> None:
        """Close the aiohttp session."""
        await self._session.close()


async def async_get_station_id(
    hass: HomeAssistant, lat: float, lng: float, api_key: str
) -> str | None:
    """Get the closest station ID based on coordinates."""
    url = f"{API_BASE_URL}/{api_key}/search.json"
    params = {
        "lat": lat,
        "lng": lng,
        "units": "distance:km",
    }

    _LOGGER.debug("Searching for station at lat=%s, lng=%s", lat, lng)
    _LOGGER.debug("Search URL: %s?%s", url, "&".join(f"{k}={v}" for k, v in params.items()))

    try:
        async with async_timeout.timeout(API_TIMEOUT):
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    response_text = await response.text()
                    
                    _LOGGER.debug("Search response status: %s", response.status)
                    _LOGGER.debug("Search response body: %s", response_text[:1000])
                    
                    if response.status == 401:
                        _LOGGER.error("API key is invalid (401 Unauthorized)")
                        return None
                    elif response.status == 403:
                        _LOGGER.error("API key doesn't have access (403 Forbidden)")
                        return None
                    elif response.status != 200:
                        _LOGGER.error(
                            "Error finding closest station: HTTP %s - %s",
                            response.status,
                            response_text[:500],
                        )
                        return None
                    
                    data = await response.json()
                    _LOGGER.debug("Search response JSON structure: %s", data.keys() if isinstance(data, dict) else type(data))
                    
                    # WillyWeather API returns location directly
                    location = data.get("location")
                    if location:
                        station_id = str(location.get("id"))
                        station_name = location.get("name")
                        distance = location.get("distance")
                        _LOGGER.info(
                            "Found closest station: %s (ID: %s) at %.1f km",
                            station_name,
                            station_id,
                            distance if distance else 0,
                        )
                        return station_id
                    else:
                        _LOGGER.error("No location data in search response: %s", data)
                        return None
                        
    except asyncio.TimeoutError:
        _LOGGER.error("Timeout while searching for station")
        return None
    except aiohttp.ClientError as err:
        _LOGGER.error("Network error while searching for station: %s", err)
        return None
    except Exception as err:
        _LOGGER.error("Unexpected error finding closest station: %s", err, exc_info=True)
        return None


async def async_get_station_name(
    hass: HomeAssistant, station_id: str, api_key: str
) -> str | None:
    """Get the station name by fetching weather data (which includes location info)."""
    url = f"{API_BASE_URL}/{api_key}/locations/{station_id}/weather.json"
    params = {
        "observational": "true",
        "units": "distance:km,temperature:c,amount:mm,speed:km/h,pressure:hpa",
    }

    _LOGGER.debug("Fetching station name for ID: %s", station_id)
    _LOGGER.debug("Station info URL: %s?%s", url, "&".join(f"{k}={v}" for k, v in params.items()))

    try:
        async with async_timeout.timeout(API_TIMEOUT):
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    response_text = await response.text()
                    
                    _LOGGER.debug("Station info response status: %s", response.status)
                    _LOGGER.debug("Station info response body: %s", response_text[:1000])
                    
                    if response.status == 401:
                        _LOGGER.error("API key is invalid (401 Unauthorized)")
                        return None
                    elif response.status == 403:
                        _LOGGER.error("API key doesn't have access (403 Forbidden)")
                        return None
                    elif response.status == 404:
                        _LOGGER.error("Station ID %s not found (404)", station_id)
                        return None
                    elif response.status != 200:
                        _LOGGER.error(
                            "Error fetching station info: HTTP %s - %s",
                            response.status,
                            response_text[:500],
                        )
                        return None
                    
                    data = await response.json()
                    _LOGGER.debug("Station info JSON structure: %s", data.keys() if isinstance(data, dict) else type(data))
                    
                    # Location info is at the root level
                    location = data.get("location", {})
                    station_name = location.get("name")
                    
                    if station_name:
                        _LOGGER.info("Station name: %s", station_name)
                        return station_name
                    else:
                        _LOGGER.warning("No station name found in response. Location data: %s", location)
                        # Still return something so setup can continue
                        return f"Station {station_id}"
                    
    except asyncio.TimeoutError:
        _LOGGER.error("Timeout while fetching station info")
        return None
    except aiohttp.ClientError as err:
        _LOGGER.error("Network error while fetching station info: %s", err)
        return None
    except Exception as err:
        _LOGGER.error("Unexpected error fetching station info: %s", err, exc_info=True)
        return None