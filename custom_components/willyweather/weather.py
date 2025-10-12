"""Support for the WillyWeather Australia weather service."""
import logging
from datetime import datetime
from typing import Any

from homeassistant.components.weather import (
    ATTR_FORECAST_CONDITION,
    ATTR_FORECAST_NATIVE_PRECIPITATION,
    ATTR_FORECAST_NATIVE_TEMP,
    ATTR_FORECAST_NATIVE_TEMP_LOW,
    ATTR_FORECAST_PRECIPITATION_PROBABILITY,
    ATTR_FORECAST_TIME,
    Forecast,
    WeatherEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTRIBUTION,
    CONF_API_KEY,
    CONF_DAYS,
    CONF_STATION_ID,
    DEFAULT_DAYS,
    DOMAIN,
    MAP_CONDITION,
)
from .coordinator import WillyWeatherForecastCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up WillyWeather weather based on a config entry."""
    api_key = entry.data[CONF_API_KEY]
    station_id = entry.data[CONF_STATION_ID]
    days = entry.data.get(CONF_DAYS, DEFAULT_DAYS)

    coordinator = WillyWeatherForecastCoordinator(hass, api_key, station_id, days)
    await coordinator.async_config_entry_first_refresh()

    async_add_entities([WWWeatherForecast(coordinator, station_id)])


class WWWeatherForecast(CoordinatorEntity, WeatherEntity):
    """Implementation of the WillyWeather weather component."""

    _attr_attribution = ATTRIBUTION
    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_native_pressure_unit = "hPa"
    _attr_native_wind_speed_unit = "km/h"
    _attr_native_precipitation_unit = "mm"

    def __init__(
        self,
        coordinator: WillyWeatherForecastCoordinator,
        station_id: str,
    ) -> None:
        """Initialize the component."""
        super().__init__(coordinator)
        self._station_id = station_id
        self._attr_unique_id = f"{station_id}_weather"

    @property
    def name(self) -> str:
        """Return the name."""
        if self.coordinator.data:
            location_name = self.coordinator.data.get("location", {}).get("name")
            if location_name:
                return f"WillyWeather {location_name}"
        return f"WillyWeather {self._station_id}"

    @property
    def condition(self) -> str | None:
        """Return the weather condition."""
        if not self.coordinator.data:
            return None

        try:
            forecasts = self.coordinator.data.get("forecasts", {})
            weather_days = forecasts.get("weather", {}).get("days", [])
            if weather_days:
                precis_code = weather_days[0].get("entries", [{}])[0].get("precisCode")
                return MAP_CONDITION.get(precis_code)
        except (KeyError, IndexError, TypeError):
            return None

        return None

    @property
    def native_temperature(self) -> float | None:
        """Return the temperature."""
        if not self.coordinator.data:
            return None

        try:
            observational = self.coordinator.data.get("observational", {})
            return observational.get("observations", {}).get("temperature", {}).get("temperature")
        except (KeyError, TypeError):
            return None

    @property
    def native_pressure(self) -> float | None:
        """Return the pressure."""
        if not self.coordinator.data:
            return None

        try:
            observational = self.coordinator.data.get("observational", {})
            return observational.get("observations", {}).get("pressure", {}).get("pressure")
        except (KeyError, TypeError):
            return None

    @property
    def humidity(self) -> float | None:
        """Return the humidity."""
        if not self.coordinator.data:
            return None

        try:
            observational = self.coordinator.data.get("observational", {})
            return observational.get("observations", {}).get("humidity", {}).get("percentage")
        except (KeyError, TypeError):
            return None

    @property
    def native_wind_speed(self) -> float | None:
        """Return the wind speed."""
        if not self.coordinator.data:
            return None

        try:
            observational = self.coordinator.data.get("observational", {})
            return observational.get("observations", {}).get("wind", {}).get("speed")
        except (KeyError, TypeError):
            return None

    @property
    def wind_bearing(self) -> float | None:
        """Return the wind direction."""
        if not self.coordinator.data:
            return None

        try:
            observational = self.coordinator.data.get("observational", {})
            return observational.get("observations", {}).get("wind", {}).get("direction")
        except (KeyError, TypeError):
            return None

    @property
    def forecast(self) -> list[Forecast] | None:
        """Return the forecast array."""
        if not self.coordinator.data:
            return None

        try:
            forecasts = self.coordinator.data.get("forecasts", {})
            weather_days = forec
