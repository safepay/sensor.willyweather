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
    CONF_STATION_ID,
    CONF_INCLUDE_OBSERVATIONAL,
    CONF_INCLUDE_UV,
    CONF_INCLUDE_TIDES,
    CONF_INCLUDE_WIND,
    CONF_INCLUDE_WARNINGS,
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
            forecast_types = [
                "weather",
                "precis", 
                "sunrisesunset",
                "moonphases",
                "rainfall",
            ]
            
            include_tides = self.entry.options.get(CONF_INCLUDE_TIDES, False)
            include_uv = self.entry.options.get(CONF_INCLUDE_UV, False)
            include_wind = self.entry.options.get(CONF_INCLUDE_WIND, False)
            
            _LOGGER.debug("Options - Tides: %s, UV: %s, Wind: %s", 
                         include_tides, include_uv, include_wind)
            
            if include_tides:
                forecast_types.append("tides")
                _LOGGER.debug("Added tides to forecast types")
            if include_uv:
                forecast_types.append("uv")
            if include_wind:
                forecast_types.append("wind")
            
            _LOGGER.debug("Final forecast types: %s", forecast_types)
            
            # Fetch observational and forecast data
            observational_data = await self._fetch_observational_data()
            forecast_data = await self._fetch_forecast_data(forecast_types)
            
            # Log what we got back
            if forecast_data and "forecasts" in forecast_data:
                available_forecasts = list(forecast_data["forecasts"].keys())
                _LOGGER.debug("Available forecasts in response: %s", available_forecasts)
            
            # Fetch warning data if enabled
            warning_data = None
            if self.entry.options.get(CONF_INCLUDE_WARNINGS, False):
                warning_data = await self._fetch_warning_data()

            _LOGGER.debug("Successfully fetched data from WillyWeather API")

            return {
                "observational": observational_data,
                "forecast": forecast_data,
                "warnings": warning_data,
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

        _LOGGER.debug("Fetching observational data from: %s", url)

        try:
            async with async_timeout.timeout(API_TIMEOUT):
                async with self._session.get(url, params=params) as response:
                    response_text = await response.text()
                    
                    if response.status == 401:
                        _LOGGER.error("API key is invalid (401 Unauthorized)")
                        raise UpdateFailed("Invalid API key")
                    elif response.status == 403:
                        _LOGGER.error("API key does not have access (403 Forbidden)")
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
                    obs_data = data.get("observational", {})
                    if not obs_data:
                        _LOGGER.warning("No observational data in response")
                    
                    return obs_data
                    
        except asyncio.TimeoutError as err:
            _LOGGER.error("Timeout fetching observational data")
            raise UpdateFailed("Request timeout") from err
        except aiohttp.ClientError as err:
            _LOGGER.error("Network error fetching observational data: %s", err)
            raise UpdateFailed(f"Network error: {err}") from err

    async def _fetch_forecast_data(self, forecast_types: list[str]) -> dict[str, Any]:
        """Fetch forecast weather data."""
        url = f"{API_BASE_URL}/{self.api_key}/locations/{self.station_id}/weather.json"
        params = {
            "forecasts": ",".join(forecast_types),
            "days": "7",
            "units": "distance:km,temperature:c,amount:mm,speed:km/h,pressure:hpa,tideHeight:m,swellHeight:m",
        }

        _LOGGER.debug("Fetching forecast data with types: %s", forecast_types)

        try:
            async with async_timeout.timeout(API_TIMEOUT):
                async with self._session.get(url, params=params) as response:
                    response_text = await response.text()
                    
                    if response.status == 401:
                        _LOGGER.error("API key is invalid (401 Unauthorized)")
                        raise UpdateFailed("Invalid API key")
                    elif response.status == 403:
                        _LOGGER.error("API key does not have access (403 Forbidden)")
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

    async def _fetch_warning_data(self) -> dict[str, Any]:
        """Fetch warning data for location."""
        url = f"{API_BASE_URL}/{self.api_key}/locations/{self.station_id}/warnings.json"
        params = {
            "area": "location",
        }

        _LOGGER.debug("Fetching warning data")

        try:
            async with async_timeout.timeout(API_TIMEOUT):
                async with self._session.get(url, params=params) as response:
                    if response.status == 401:
                        _LOGGER.error("API key is invalid (401 Unauthorized)")
                        return {}
                    elif response.status == 403:
                        _LOGGER.error("API key does not have access (403 Forbidden)")
                        return {}
                    elif response.status == 404:
                        _LOGGER.debug("No warnings available for this location")
                        return {}
                    elif response.status != 200:
                        _LOGGER.debug(
                            "Warning data not available: HTTP %s",
                            response.status,
                        )
                        return {}
                    
                    data = await response.json()
                    return {"warnings": data if isinstance(data, list) else []}
                    
        except asyncio.TimeoutError:
            _LOGGER.debug("Timeout fetching warning data")
            return {}
        except aiohttp.ClientError as err:
            _LOGGER.debug("Network error fetching warning data: %s", err)
            return {}

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

    try:
        async with async_timeout.timeout(API_TIMEOUT):
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 401:
                        _LOGGER.error("API key is invalid (401 Unauthorized)")
                        return None
                    elif response.status == 403:
                        _LOGGER.error("API key does not have access (403 Forbidden)")
                        return None
                    elif response.status != 200:
                        _LOGGER.error(
                            "Error finding closest station: HTTP %s",
                            response.status,
                        )
                        return None
                    
                    data = await response.json()
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
                        _LOGGER.error("No location data in search response")
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
    """Get the station name by fetching weather data."""
    url = f"{API_BASE_URL}/{api_key}/locations/{station_id}/weather.json"
    params = {
        "observational": "true",
        "units": "distance:km,temperature:c,amount:mm,speed:km/h,pressure:hpa",
    }

    _LOGGER.debug("Fetching station name for ID: %s", station_id)

    try:
        async with async_timeout.timeout(API_TIMEOUT):
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 401:
                        _LOGGER.error("API key is invalid (401 Unauthorized)")
                        return None
                    elif response.status == 403:
                        _LOGGER.error("API key does not have access (403 Forbidden)")
                        return None
                    elif response.status == 404:
                        _LOGGER.error("Station ID %s not found (404)", station_id)
                        return None
                    elif response.status != 200:
                        _LOGGER.error(
                            "Error fetching station info: HTTP %s",
                            response.status,
                        )
                        return None
                    
                    data = await response.json()
                    location = data.get("location", {})
                    station_name = location.get("name")
                    
                    if station_name:
                        _LOGGER.info("Station name: %s", station_name)
                        return station_name
                    else:
                        _LOGGER.warning("No station name found in response")
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